# https://github.com/ebai101/aiodbx
# MIT License

# Copyright (c) 2021 Ethan Bailey

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import base64
import json
import logging
import os

import typing

import aiofiles
import aiohttp
import rich


from aiopillow.dbx_logger import get_logger  # noqa: E402
from aiopillow import settings

LOGGER = get_logger(__name__, provider="AIODBX", level=logging.DEBUG)

class DropboxAPIError(Exception):
    """
    Exception for errors thrown by the API. Contains the HTTP status code and the returned error message.
    """

    def __init__(self, status: int, message: typing.Union[str, dict]):
        self.status = status
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if isinstance(self.message, str):
            try:
                self.message = json.loads(self.message)
                return f'{self.status} {self.message["error_summary"]}'
            except:
                return f"{self.status} {self.message}"
        else:
            return f"{self.status} {self.message}"


class Request:
    """
    Wrapper for a ClientResponse object that allows automatic retries for a certain list of statuses.

    request:
        session method to call that returns a ClientResponse (e.g. session.post)
    url:
        url to request
    ok_statuses:
        list of statuses that will return without an error (default is [200])
    retry_count:
        number of times that the request will be retried (default is 5)
    retry_statuses:
        list of statuses that will cause the request to be automatically retried (default is [429])
    **kwargs:
        Arbitrary keyword arguments, passed thru to the `request` Callable.
    """

    def __init__(
        self,
        request: typing.Callable[..., typing.Any],
        url: str,
        ok_statuses: list[int] = [200],
        retry_count: int = 5,
        retry_statuses: list[int] = [429],
        **kwargs: typing.Any,
    ):
        self.request = request
        self.url = url
        self.ok_statuses = ok_statuses
        self.retry_count = retry_count
        self.retry_statuses = retry_statuses
        self.kwargs = kwargs
        self.trace_request_ctx = kwargs.pop("trace_request_ctx", {})

        self.current_attempt = 0
        self.resp: typing.Optional[aiohttp.ClientResponse] = None

    async def _do_request(self) -> aiohttp.ClientResponse:
        """
        Performs a request. Automatically retries the request for specific return statuses.
        Should not be called directly. Instead, use an `async with` block with a Request object to manage the response context properly.

        Returns:
            aiohttp.ClientResponse: response returned from the `self.request` callable.

        Raises:
            DropboxAPIError: If the response status is >= 400 and if it is not in `self.ok_statuses`
        """

        self.current_attempt += 1
        if self.current_attempt > 1:
            LOGGER.debug(f"Attempt {self.current_attempt} out of {self.retry_count}")

        resp: aiohttp.ClientResponse = await self.request(
            self.url,
            **self.kwargs,
            trace_request_ctx={
                "current_attempt": self.current_attempt,
                **self.trace_request_ctx,
            },
        )

        if resp.status in self.ok_statuses or resp.status < 400:
            endpoint_name = self.url[self.url.index("2") + 1 :]
            LOGGER.debug(f"Request OK: {endpoint_name} returned {resp.status}")
        else:
            raise DropboxAPIError(resp.status, await resp.text())

        if (
            self.current_attempt < self.retry_count
            and resp.status in self.retry_statuses
        ):
            if "Retry-After" in resp.headers:
                sleep_time = int(resp.headers["Retry-After"])
            else:
                sleep_time = 1
            await asyncio.sleep(sleep_time)
            return await self._do_request()

        self.resp = resp
        return resp

    def __await__(self) -> typing.Generator[typing.Any, None, aiohttp.ClientResponse]:
        return self.__aenter__().__await__()

    async def __aenter__(self) -> aiohttp.ClientResponse:
        return await self._do_request()

    async def __aexit__(self, *excinfo) -> None:
        if self.resp is not None:
            if not self.resp.closed:
                self.resp.close()


class AsyncDropboxAPI:
    """
    Dropbox API client using asynchronous HTTP requests.

    Args:
        token:
            a Dropbox API access token
        retry_statuses:
            list of statuses that will automatically be retried (default is [429])
    """

    def __init__(
        self, token: str, retry_statuses: list[int] = [429]
    ):
        self.token = token
        self.retry_statuses = retry_statuses
        self.client_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=50)
        )
        self.upload_session: list[dict] = []


    async def validate(self):
        """
        Validates the user authentication token.
        https://www.dropbox.com/developers/documentation/http/documentation#check-user

        Returns:
            bool:
                True if the API returns the same string (thus the token is valid)
        Raises:
            DropboxApiError:
                If the token is invalid
        """

        LOGGER.debug("Validating token")



        # resp_data = await self.files_list_folder(settings.DEFAULT_DROPBOX_FOLDER)

        # LOGGER.debug(resp_data)

        nonce = base64.b64encode(os.urandom(8), altchars=b"-_").decode("utf-8")
        url = "https://api.dropboxapi.com/2/check/user"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        # rich.print(headers)
        data = json.dumps({"query": nonce})

        async with Request(
            self.client_session.post, url, headers=headers, data=data
        ) as resp:
            resp_data = await resp.json()
            if resp_data["result"] == nonce:
                LOGGER.debug("Token is valid")
                return True
            else:
                raise DropboxAPIError(resp.status, "Token is invalid")

    async def download_file(self, dropbox_path: str, local_path: str = None) -> str:
        """
        Downloads a single file.
        https://www.dropbox.com/developers/documentation/http/documentation#files-download

        Args:
            dropbox_path:
                File path on Dropbox to download from
            local_path:
                Path on the local disk to download to (defaults to None, which downloads to the current directory)
        Returns:
            str:
                `local_path` where the file was downloaded to
        """

        # default to current directory
        if local_path == None:
            local_path = os.path.basename(dropbox_path)

        LOGGER.info(f"Downloading {os.path.basename(local_path)}")
        LOGGER.debug(f"from {dropbox_path}")

        url = "https://content.dropboxapi.com/2/files/download"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
        }

        async with Request(
            self.client_session.post, url, headers=headers
        ) as resp:
            async with aiofiles.open(local_path, "wb") as f:
                async for chunk, _ in resp.content.iter_chunks():
                    await f.write(chunk)
                return local_path

    async def download_folder(self, dropbox_path: str, local_path: str = None) -> str:
        """
        Downloads a folder as a zip file.
        https://www.dropbox.com/developers/documentation/http/documentation#files-download_zip

        Args:
            dropbox_path:
                Folder path on Dropbox to download from
            local_path:
                Path on the local disk to download to (defaults to None, which downloads to the current directory)
        Returns:
            str:
                `local_path` where the zip file was downloaded to
        """

        # default to current directory
        if local_path == None:
            local_path = os.path.basename(dropbox_path)

        LOGGER.info(f"Downloading {os.path.basename(local_path)}")
        LOGGER.debug(f"from {dropbox_path}")

        url = "https://content.dropboxapi.com/2/files/download_zip"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
        }

        async with Request(
            self.client_session.post, url, headers=headers
        ) as resp:
            async with aiofiles.open(local_path, "wb") as f:
                async for chunk, _ in resp.content.iter_chunks():
                    await f.write(chunk)
                return local_path

    async def download_shared_link(
        self, shared_link: str, local_path: str = None
    ) -> str:
        """
        Downloads a file from a shared link.
        https://www.dropbox.com/developers/documentation/http/documentation#sharing-get_shared_link_file

        Args:
            shared_link:
                Shared link to download from
            local_path:
                Path on the local disk to download to (defaults to None, which downloads to the current directory)
        Returns:
            str:
                `local_path` where the file was downloaded to
        """

        # default to current directory, with the path in the shared link
        if local_path == None:
            local_path = os.path.basename(shared_link[: shared_link.index("?")])

        LOGGER.info(f"Downloading {os.path.basename(local_path)}")
        LOGGER.debug(f"from {shared_link}")

        url = "https://content.dropboxapi.com/2/sharing/get_shared_link_file"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps({"url": shared_link}),
        }

        async with Request(
            self.client_session.post, url, headers=headers
        ) as resp:
            async with aiofiles.open(local_path, "wb") as f:
                async for chunk, _ in resp.content.iter_chunks():
                    await f.write(chunk)
                return local_path

    async def upload_start(self, local_path: str, dropbox_path: str) -> dict:
        """
        Uploads a single file to an upload session. This should be used when uploading large quantities of files.
        https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-start

        Args:
            local_path:
                Local path to upload from.
            dropbox_path:
                Dropbox path to upload to.
        Returns:
            dict:
                UploadSessionFinishArg dict with information on the upload.
                This dict is automatically stored in `self.upload_session` to be committed later with `upload_finish`.
                It is returned here anyways so that the commit information can be used for other purposes.
        Raises:
            ValueError:
                If `local_path` does not exist.
            RuntimeError:
                If the current upload session is larger than 1000 files.
                To avoid this, call `upload_finish` regularly to split high quantity uploads into batches.
        """

        if not os.path.exists(local_path):
            raise ValueError(f"local_path {local_path} does not exist")
        if len(self.upload_session) >= 1000:
            raise RuntimeError(
                "upload_session is too large, you must call upload_finish to commit the batch"
            )

        LOGGER.info(f"Uploading {os.path.basename(local_path)}")
        LOGGER.debug(f"to {dropbox_path}")

        url = "https://content.dropboxapi.com/2/files/upload_session/start"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps({"close": True}),
            "Content-Type": "application/octet-stream",
        }

        async with aiofiles.open(local_path, "rb") as f:
            data = await f.read()
            async with Request(
                self.client_session.post, url, headers=headers, data=data
            ) as resp:
                resp_data = await resp.json()

                # construct commit entry for finishing batch later
                commit = {
                    "cursor": {
                        "session_id": resp_data["session_id"],
                        "offset": os.path.getsize(local_path),
                    },
                    "commit": {
                        "path": dropbox_path,
                        "mode": "add",
                        "autorename": False,
                        "mute": False,
                    },
                }
                self.upload_session.append(commit)
                return commit

    async def upload_finish(self, check_interval: float = 3) -> list[dict]:
        """
        Finishes an upload batch.
        https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-finish_batch

        Args:
            check_interval:
                how often to check on the upload completion status (default is 3)
        Returns:
            list[dict]:
                List of FileMetadata dicts containing metadata on each uploaded file
        Raises:
            DropboxAPIError:
                If an unknown response is returned from the API.
        """

        if len(self.upload_session) == 0:
            raise RuntimeError(
                "upload_session is empty, have you uploaded any files yet?"
            )

        LOGGER.info("Finishing upload batch")
        LOGGER.debug(f"Batch size is {len(self.upload_session)}")

        url = "https://api.dropboxapi.com/2/files/upload_session/finish_batch"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"entries": self.upload_session})

        async with Request(
            self.client_session.post, url, headers=headers, data=data
        ) as resp:
            resp_data = await resp.json()
            self.upload_session = []  # empty the local upload session

            if resp_data[".tag"] == "async_job_id":
                # check regularly for job completion
                return await self._upload_finish_check(
                    resp_data["async_job_id"], check_interval=check_interval
                )
            elif resp_data[".tag"] == "complete":
                LOGGER.info("Upload batch finished")
                return resp_data["entries"]
            else:
                err = await resp.text()
                raise DropboxAPIError(
                    resp.status, f"Unknown upload_finish response: {err}"
                )

    async def _upload_finish_check(
        self, job_id: str, check_interval: float = 5
    ) -> list[dict]:
        """
        Checks on an `upload_finish` async job every `check_interval` seconds.
        Should not be called directly, this is automatically called from `upload_finish`.
        https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-finish_batch-check:w

        Args:
            job_id:
                the job ID to check the status of
            check_interval:
                how often in seconds to check the status
        Returns:
            list[dict]:
                List of FileMetadata dicts containing metadata on each uploaded file
        """

        LOGGER.debug(f"Batch not finished, checking every {check_interval} seconds")

        url = "https://api.dropboxapi.com/2/files/upload_session/finish_batch/check"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"async_job_id": job_id})

        while True:
            await asyncio.sleep(check_interval)
            async with Request(
                self.client_session.post, url, headers=headers, data=data
            ) as resp:
                resp_data = await resp.json()

                if resp_data[".tag"] == "complete":
                    LOGGER.info("Upload batch finished")
                    return resp_data["entries"]
                elif resp_data[".tag"] == "in_progress":
                    LOGGER.debug(f"Checking again in {check_interval} seconds")
                    continue

    async def upload_single(
        self,
        local_path: str,
        dropbox_path: str,
        args: dict = {"mode": "add", "autorename": False, "mute": False},
    ) -> dict:
        """
        Uploads a single file. This should only be used for small quantities of files, for larger quantities use `upload_start` and `upload_finish`.
        https://www.dropbox.com/developers/documentation/http/documentation#files-upload

        Args:
            local_path:
                Local path to upload from.
            dropbox_path:
                Dropbox path to upload to.
            args:
                Dictionary of arguments to pass to the API.
        Returns:
            dict:
                FileMetadata of the uploaded file, if successful.
        Raises:
            ValueError:
                If `local_path` does not exist.
        """

        if not os.path.exists(local_path):
            raise ValueError(f"local_path {local_path} does not exist")
        args["path"] = dropbox_path

        LOGGER.info(f"Uploading {os.path.basename(local_path)}")
        LOGGER.debug(f"to {dropbox_path}")

        url = "https://content.dropboxapi.com/2/files/upload"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps(args),
            "Content-Type": "application/octet-stream",
        }

        async with aiofiles.open(local_path, "rb") as f:
            data = await f.read()
            async with Request(
                self.client_session.post, url, headers=headers, data=data
            ) as resp:
                resp_data = await resp.json()
                return resp_data

    async def create_shared_link(self, dropbox_path: str) -> str:
        """
        Create a shared link for a file in Dropbox.
        https://www.dropbox.com/developers/documentation/http/documentation#sharing-create_shared_link_with_settings

        Args:
            dropbox_path:
                Path of a file on Dropbox to create a shared link for.
        Returns:
            str:
                A shared link for the given file.
                If a shared link already exists, the existing one is returned, otherwise a new one is created.
        Raises:
            DropboxAPIError:
                If `dropbox_path` does not exist on Dropbox, or if an otherwise unknown status is returned.
        """

        LOGGER.info(f"Creating shared link for file {os.path.basename(dropbox_path)}")
        LOGGER.debug(f"Full path is {dropbox_path}")

        url = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"path": dropbox_path})

        # accept 409 status to check for existing shared link
        async with Request(
            self.client_session.post,
            url,
            LOGGER,
            headers=headers,
            data=data,
            ok_statuses=[200, 409],
        ) as resp:
            resp_data = await resp.json()

            if resp.status == 200:
                return resp_data["url"]
            else:
                if "shared_link_already_exists" in resp_data["error_summary"]:
                    LOGGER.warning(
                        f"Shared link already exists for {os.path.basename(dropbox_path)}, using existing link"
                    )
                    return resp_data["error"]["shared_link_already_exists"]["metadata"][
                        "url"
                    ]
                elif "not_found" in resp_data["error_summary"]:
                    raise DropboxAPIError(
                        resp.status, f"Path {dropbox_path} does not exist"
                    )
                else:
                    err = await resp.text()
                    raise DropboxAPIError(resp.status, f"Unknown Dropbox error: {err}")

    async def get_shared_link_metadata(self, shared_link: str) -> dict:
        """
        Gets the metadata for the file/folder behind a shared link.
        https://www.dropbox.com/developers/documentation/http/documentation#sharing-get_shared_link_metadata

        Args:
            shared_link:
                A shared link which points to the file or folder to get metadata from.
        Returns:
            dict:
                FileMetadata or FolderMetadata for the file/folder behind the shared link
        """

        LOGGER.info(f"Getting metadata from shared link {shared_link}")

        url = "https://api.dropboxapi.com/2/sharing/get_shared_link_metadata"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"url": shared_link})

        async with Request(
            self.client_session.post, url, headers=headers, data=data
        ) as resp:
            resp_data = await resp.json()
            return resp_data

    async def files_list_folder(self, path: str,
    recursive=False,
    include_media_info=False,
    include_deleted=False,
    include_has_explicit_shared_members=False,
    include_mounted_folders=True,
    limit=None,
    shared_link=None,
    include_property_groups=None,
    include_non_downloadable_files=True) -> dict:
        """
        Starts returning the contents of a folder. If the result's
        ``ListFolderResult.has_more`` field is ``True``, call
        :meth:`files_list_folder_continue` with the returned
        ``ListFolderResult.cursor`` to retrieve more entries. If you're using
        ``ListFolderArg.recursive`` set to ``True`` to keep a local cache of the
        contents of a Dropbox account, iterate through each entry in order and
        process them as follows to keep your local state in sync: For each
        :class:`dropbox.files.FileMetadata`, store the new entry at the given
        path in your local state. If the required parent folders don't exist
        yet, create them. If there's already something else at the given path,
        replace it and remove all its children. For each
        :class:`dropbox.files.FolderMetadata`, store the new entry at the given
        path in your local state. If the required parent folders don't exist
        yet, create them. If there's already something else at the given path,
        replace it but leave the children as they are. Check the new entry's
        ``FolderSharingInfo.read_only`` and set all its children's read-only
        statuses to match. For each :class:`dropbox.files.DeletedMetadata`, if
        your local state has something at the given path, remove it and all its
        children. If there's nothing at the given path, ignore this entry. Note:
        :class:`dropbox.auth.RateLimitError` may be returned if multiple
        :meth:`files_list_folder` or :meth:`files_list_folder_continue` calls
        with same parameters are made simultaneously by same API app for same
        user. If your app implements retry logic, please hold off the retry
        until the previous request finishes.

        :param str path: A unique identifier for the file.
        :param bool recursive: If true, the list folder operation will be
            applied recursively to all subfolders and the response will contain
            contents of all subfolders.
        :param bool include_media_info: If true, ``FileMetadata.media_info`` is
            set for photo and video. This parameter will no longer have an
            effect starting December 2, 2019.
        :param bool include_deleted: If true, the results will include entries
            for files and folders that used to exist but were deleted.
        :param bool include_has_explicit_shared_members: If true, the results
            will include a flag for each file indicating whether or not  that
            file has any explicit members.
        :param bool include_mounted_folders: If true, the results will include
            entries under mounted folders which includes app folder, shared
            folder and team folder.
        :param Nullable[int] limit: The maximum number of results to return per
            request. Note: This is an approximate number and there can be
            slightly more entries returned in some cases.
        :param Nullable[:class:`dropbox.files.SharedLink`] shared_link: A shared
            link to list the contents of. If the link is password-protected, the
            password must be provided. If this field is present,
            ``ListFolderArg.path`` will be relative to root of the shared link.
            Only non-recursive mode is supported for shared link.
        :param Nullable[:class:`dropbox.files.TemplateFilterBase`]
            include_property_groups: If set to a valid list of template IDs,
            ``FileMetadata.property_groups`` is set if there exists property
            data associated with the file and each of the listed templates.
        :param bool include_non_downloadable_files: If true, include files that
            are not downloadable, i.e. Google Docs.
        :rtype: :class:`dropbox.files.ListFolderResult`
        :raises: :class:`.exceptions.ApiError`

        If this raises, ApiError will contain:
            :class:`dropbox.files.ListFolderError`
        https://www.dropbox.com/developers/documentation/http/documentation

        Args:
            shared_link:
                A shared link which points to the file or folder to get metadata from.
        Returns:
            dict:
                FileMetadata or FolderMetadata for the file/folder behind the shared link
        """

        # curl -X POST https://api.dropboxapi.com/2/files/list_folder \
        # --header "Authorization: Bearer " \
        # --header "Content-Type: application/json" \
        # --data "{\"path\": \"/Homework/math\",\"recursive\": false,\"include_media_info\": false,\"include_deleted\": false,\"include_has_explicit_shared_members\": false,\"include_mounted_folders\": true,\"include_non_downloadable_files\": true}"

        LOGGER.info(f"Getting contents of folder {path}")

        url = "https://api.dropboxapi.com/2/files/list_folder"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        args = {
            "path": path,
            "recursive": recursive,
            "include_media_info": include_media_info,
            "include_deleted": include_deleted,
            "include_has_explicit_shared_members": include_has_explicit_shared_members,
            "include_mounted_folders": include_mounted_folders,
            "include_non_downloadable_files": include_non_downloadable_files,
            # "limit": limit,
            # "shared_link": shared_link,
            # "include_property_groups": include_property_groups,
        }

        data = json.dumps(args)

        async with Request(
            self.client_session.post, url, headers=headers, data=data
        ) as resp:
            resp_data = await resp.json()
            return resp_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.client_session.close()
