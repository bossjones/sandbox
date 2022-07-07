# pylint: disable=unused-import
from collections import defaultdict
import contextlib
import datetime
import logging
import os
import pathlib
import sys
import time
import traceback
import unicodedata

from typing import Union

import aiofiles
import aiohttp
import bpdb
from codetiming import Timer
import dropbox
from dropbox import (
    Dropbox,
    DropboxOAuth2Flow,
    DropboxOAuth2FlowNoRedirect,
    create_session,
    session,
)
from dropbox.dropbox_client import BadInputException
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode
from pydantic import BaseModel, BaseSettings, Field, validator
import rich
import six

# import aioscraper
from aioscraper.dbx_logger import get_logger  # noqa: E402

# autoflake --imports=dropbox,discord,unicodedata,six,uritools,aioscraper --in-place --remove-unused-variables aioscraper/utils/dropbox_.py


# NOTE: /Dropbox/Apps/cerebro_downloads

LOGGER = get_logger(__name__, provider="Dropbox", level=logging.DEBUG)

DROPBOX_AIOSCRAPER_APP_KEY = os.environ.get("DROPBOX_AIOSCRAPER_APP_KEY")
DROPBOX_AIOSCRAPER_APP_SECRET = os.environ.get("DROPBOX_AIOSCRAPER_APP_SECRET")

DROPBOX_AIOSCRAPER_TOKEN = os.environ.get("DROPBOX_AIOSCRAPER_TOKEN")
DEFAULT_DROPBOX_FOLDER = "/cerebro_downloads"
# LOCALFILE = 'data/croc.jpeg'
# BACKUPPATH = '/croc.jpeg'

# Establish connection


def get_dropbox_client(token=DROPBOX_AIOSCRAPER_TOKEN) -> Union[dropbox.Dropbox, None]:
    dbx = None
    try:
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        print("Connected to Dropbox successfully")
    except BadInputException as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise
    except AuthError:
        # print(str(ex))
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        # output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        # LOGGER.warning(output)
        # LOGGER.error("exc_type: {}".format(exc_type))
        # LOGGER.error("exc_value: {}".format(exc_value))
        # traceback.print_tb(exc_traceback)
        # raise
        sys.exit(
            "ERROR: Invalid access token; try re-generating an "
            "access token from the app console on the web."
        )
    except Exception as e:
        print(str(e))

    # # Check that the access token is valid
    # try:
    #     dbx.users_get_current_account()
    # except AuthError:
    #     sys.exit(
    #         "ERROR: Invalid access token; try re-generating an "
    #         "access token from the app console on the web."
    #     )

    return dbx


def list_files_in_remote_folder(dbx: dropbox.Dropbox) -> None:

    # here dbx is an object which is obtained
    # by connecting to dropbox via token
    # dbx = get_dropbox_client()

    try:
        folder_path = DEFAULT_DROPBOX_FOLDER

        # dbx object contains all functions that
        # are required to perform actions with dropbox
        files = dbx.files_list_folder(folder_path, recursive=True).entries
        rich.print("------------Listing Files in Folder------------ ")

        for file in files:

            # listing
            rich.print(file.name)

    except Exception as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise


def download_img(dbx: dropbox.Dropbox, short_file_name: str) -> None:

    # here dbx is an object which is obtained
    # by connecting to dropbox via token
    # dbx = get_dropbox_client()

    try:

        with open(f"{short_file_name}", "wb") as f:
            metadata, res = dbx.files_download(
                path=f"{DEFAULT_DROPBOX_FOLDER}/{short_file_name}"
            )
            f.write(res.content)

    except Exception as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise


@contextlib.contextmanager
def stopwatch(message: str):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print("Total elapsed time for %s: %.3f" % (message, t1 - t0))


# SOURCE: https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
def list_folder(dbx: dropbox.Dropbox, folder, subfolder):
    """List a folder.

    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = "/%s/%s" % (folder, subfolder.replace(os.path.sep, "/"))
    while "//" in path:
        path = path.replace("//", "/")
    path = path.rstrip("/")
    try:
        with stopwatch("list_folder"):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print("Folder listing failed for", path, "-- assumed empty:", err)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
        return rv


# SOURCE: https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
def download(dbx, folder, subfolder, name):
    """Download a file.

    Return the bytes of the file, or None if it doesn't exist.
    """
    path = "/%s/%s/%s" % (folder, subfolder.replace(os.path.sep, "/"), name)
    while "//" in path:
        path = path.replace("//", "/")
    with stopwatch("download"):
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print("*** HTTP error", err)
            return None
    data = res.content
    print(len(data), "bytes; md:", md)
    return data


# SOURCE: https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.

    Return the request response, or None in case of error.
    """
    path = "/%s/%s/%s" % (folder, subfolder.replace(os.path.sep, "/"), name)
    while "//" in path:
        path = path.replace("//", "/")
    mode = (
        dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add
    )
    mtime = os.path.getmtime(fullname)
    with open(fullname, "rb") as f:
        data = f.read()
    with stopwatch("upload %d bytes" % len(data)):
        try:
            res = dbx.files_upload(
                data,
                path,
                mode,
                client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                mute=True,
            )
        except dropbox.exceptions.ApiError as err:
            print("*** API error", err)
            return None
    print("uploaded as", res.name.encode("utf8"))
    return res


# SOURCE: https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
def iter_dir_and_upload(dbx: dropbox.Dropbox, remote_folder: str, local_folder: str):
    """Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.

    Args:
        dbx (dropbox.Dropbox): Dropbox client
        folder (str): Folder name in your Dropbox. Eg. "/20211127"
        local_folder (str): Local directory to upload. EG. "~/Downloads/dropbox_test"
    """

    folder = remote_folder
    rootdir = os.path.expanduser(local_folder)
    rich.print("Dropbox folder name:", folder)
    rich.print("Local directory:", rootdir)
    if not os.path.exists(rootdir):
        rich.print(rootdir, "does not exist on your filesystem")
        sys.exit(1)
    elif not os.path.isdir(rootdir):
        rich.print(rootdir, "is not a folder on your filesystem")
        sys.exit(1)

    for dn, dirs, files in os.walk(rootdir):
        rich.print(f" dn = {dn}")
        rich.print(f" dirs = {dirs}")
        rich.print(f" files = {files}")
        subfolder = dn[len(rootdir) :].strip(os.path.sep)
        listing = list_folder(dbx, folder, subfolder)
        rich.print("Descending into", subfolder, "...")

        # First do all the files.
        for name in files:
            fullname = os.path.join(dn, name)
            if not isinstance(name, six.text_type):
                name = name.decode("utf-8")
            nname = unicodedata.normalize("NFC", name)
            if name.startswith("."):
                rich.print("Skipping dot file:", name)
            elif name.startswith("@") or name.endswith("~"):
                rich.print("Skipping temporary file:", name)
            elif name.endswith(".pyc") or name.endswith(".pyo"):
                rich.print("Skipping generated file:", name)
            elif nname in listing:
                md = listing[nname]
                mtime = os.path.getmtime(fullname)
                mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
                size = os.path.getsize(fullname)
                if (
                    isinstance(md, dropbox.files.FileMetadata)
                    and mtime_dt == md.client_modified
                    and size == md.size
                ):
                    rich.print(name, "is already synced [stats match]")
                else:
                    rich.print(name, "exists with different stats, downloading")
                    res = download(dbx, folder, subfolder, name)
                    with open(fullname) as f:
                        data = f.read()
                    if res == data:
                        rich.print(name, "is already synced [content match]")
                    else:
                        rich.print(name, "has changed since last sync")
                        rich.print(
                            f"upload(dbx, fullname, folder, subfolder, name, overwrite=True) -> upload({dbx}, {fullname}, {folder}, {subfolder}, {name}, overwrite=True)"
                        )
                        # TODO: Re-enable this # upload(dbx, fullname, folder, subfolder, name, overwrite=True)
            # elif yesno('Upload %s' % name, True, args):
            #     upload(dbx, fullname, folder, subfolder, name)

        # Then choose which subdirectories to traverse.
        keep = []
        for name in dirs:
            if name.startswith("."):
                rich.print("Skipping dot directory:", name)
            elif name.startswith("@") or name.endswith("~"):
                rich.print("Skipping temporary directory:", name)
            elif name == "__pycache__":
                rich.print("Skipping generated directory:", name)
            # elif yesno('Descend into %s' % name, True, args):
            #     rich.print('Keeping directory:', name)
            #     keep.append(name)
            else:
                # rich.print('OK, skipping directory:', name)
                rich.print("Keeping directory:", name)
                keep.append(name)
        # override and replace list with slice
        dirs[:] = keep

    # dbx.close()


async def co_upload_to_dropbox(
    dbx: dropbox.Dropbox, path_to_local_file: str, path_to_remote_dir: str = "/"
):
    localfile_pathobj = pathlib.Path(f"{path_to_local_file}").absolute()
    try:
        assert localfile_pathobj.exists()
        assert localfile_pathobj.is_file()
    except Exception as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise

    _localfile = f"{localfile_pathobj}"
    _backuppath = f"{path_to_remote_dir}/{path_to_local_file}"

    async with aiofiles.open(_localfile, mode="rb") as f:
        rich.print("Uploading " + _localfile + " to Dropbox as " + _backuppath + "...")
        try:
            contents = await f.read()
            dbx.files_upload(contents, _backuppath, mode=WriteMode("overwrite"))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (
                err.error.is_path()
                and err.error.get_path().reason.is_insufficient_space()
            ):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                rich.print(err.user_message_text)
                sys.exit()
            else:
                rich.print(err)
                sys.exit()

    # with open(_localfile, "rb") as f:
    #     # We use WriteMode=overwrite to make sure that the settings in the file
    #     # are changed on upload
    #     rich.print("Uploading " + _localfile + " to Dropbox as " + _backuppath + "...")
    #     try:
    #         dbx.files_upload(f.read(), _backuppath, mode=WriteMode("overwrite"))
    #     except ApiError as err:
    #         # This checks for the specific error where a user doesn't have
    #         # enough Dropbox space quota to upload this file
    #         if (
    #             err.error.is_path()
    #             and err.error.get_path().reason.is_insufficient_space()
    #         ):
    #             sys.exit("ERROR: Cannot back up; insufficient space.")
    #         elif err.user_message_text:
    #             rich.print(err.user_message_text)
    #             sys.exit()
    #         else:
    #             rich.print(err)
    #             sys.exit()


def upload_to_dropbox(
    dbx: dropbox.Dropbox, path_to_local_file: str, path_to_remote_dir: str = "/"
):
    localfile_pathobj = pathlib.Path(f"{path_to_local_file}").absolute()
    try:
        assert localfile_pathobj.exists()
        assert localfile_pathobj.is_file()
    except Exception as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise

    _localfile = f"{localfile_pathobj}"
    _backuppath = f"{path_to_remote_dir}/{path_to_local_file}"

    with open(_localfile, "rb") as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        rich.print("Uploading " + _localfile + " to Dropbox as " + _backuppath + "...")
        try:
            dbx.files_upload(f.read(), _backuppath, mode=WriteMode("overwrite"))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (
                err.error.is_path()
                and err.error.get_path().reason.is_insufficient_space()
            ):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                rich.print(err.user_message_text)
                sys.exit()
            else:
                rich.print(err)
                sys.exit()


def select_revision(
    dbx: dropbox.Dropbox, filename: str = "", path_to_remote_file_or_dir: str = "/"
):
    # _localfile = f"{localfile_pathobj}"
    if filename:
        _backuppath = f"{path_to_remote_file_or_dir}/{filename}"
    else:
        _backuppath = f"{path_to_remote_file_or_dir}/"
    # Get the revisions for a file (and sort by the datetime object, "server_modified")
    rich.print("Finding available revisions on Dropbox...")
    entries = dbx.files_list_revisions(_backuppath, limit=30).entries
    revisions = sorted(entries, key=lambda entry: entry.server_modified)

    for revision in revisions:
        rich.print(revision.rev, revision.server_modified)

    # Return the oldest revision (first entry, because revisions was sorted oldest:newest)
    return revisions[0].rev


def cli_oauth():
    """
    This example walks through a basic oauth flow using the existing long-lived token type
    Populate your app key and app secret in order to run this locally
    """

    auth_flow = DropboxOAuth2FlowNoRedirect(
        DROPBOX_AIOSCRAPER_APP_KEY, DROPBOX_AIOSCRAPER_APP_SECRET
    )

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print('2. Click "Allow" (you might have to log in first).')
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print("Error: %s" % (e,))
        exit(1)

    with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
        dbx.users_get_current_account()
        rich.print("Successfully set up client!")
        # upload_to_dropbox()


# dbx = get_dropbox_client()

# bpdb.set_trace()

# print(dbx)
# # # for entry in dbx.files_list_folder('/cerebro_downloads').entries:
# # #     print(entry.name)
# # for entry in dbx.files_list_folder('').entries:
# #     print(entry.name)

# to_rev = select_revision()
# list_files_in_remote_folder()
# download_img()
# upload_to_dropbox()

# SOURCE: https://github.com/MadeByMads/fastapi-cloud-drives/blob/a245bb62c1c41f592549e2cfb7121a667003b41b/docs/dropbox.md
class DropBoxConfig(BaseSettings):

    DROPBOX_ACCESS_TOKEN: str = Field(None, env="DROPBOX_AIOSCRAPER_TOKEN")
    APP_KEY: str = Field(..., env="DROPBOX_AIOSCRAPER_APP_KEY")
    APP_SECRET: str = Field(..., env="DROPBOX_AIOSCRAPER_APP_SECRET")
    DROPBOX_REFRESH_TOKEN: str = Field(None, env="DROPBOX_REFRESH_TOKEN")

    class Config:
        case_sensitive = True


class AsyncDropBox:
    # SOURCE: https://github.com/MadeByMads/fastapi-cloud-drives/blob/a245bb62c1c41f592549e2cfb7121a667003b41b/fastapi_cloud_drives/fastapi_dropbox.py#L8

    def __init__(self, conf):
        self.DROPBOX_ACCESS_TOKEN = conf.DROPBOX_ACCESS_TOKEN
        self.APP_KEY = conf.APP_KEY
        self.APP_SECRET = conf.APP_SECRET
        self.DROPBOX_REFRESH_TOKEN = conf.DROPBOX_REFRESH_TOKEN

        self.client = self.auth()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.client.close()

    def auth(self):
        """
        Authentication done via OAuth2
        You can generate tken for yourself in the App Console.
        See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
        Authentication step  initially it is done with ACCESS_TOKEN, as it is short lived it will expire soon. Therefore better to have Refresh token
        """

        if not self.DROPBOX_REFRESH_TOKEN:

            # return dropbox.Dropbox(self.DROPBOX_ACCESS_TOKEN,app_key=self.APP_KEY,app_secret=self.APP_SECRET)
            return dropbox.Dropbox(self.DROPBOX_ACCESS_TOKEN)

        return dropbox.Dropbox(
            oauth2_access_token=self.DROPBOX_ACCESS_TOKEN,
            oauth2_refresh_token=self.DROPBOX_REFRESH_TOKEN,
            app_key=self.APP_KEY,
            app_secret=self.APP_SECRET,
        )

    async def account_info(self):
        """
        Account information of the current user
        """

        temp = defaultdict(dict)

        result = self.client.users_get_current_account()

        temp["abbreviated_name"] = result.name.abbreviated_name
        temp["display_name"] = result.name.display_name
        temp["familiar_name"] = result.name.familiar_name
        temp["given_name"] = result.name.given_name
        temp["surname"] = result.name.surname

        temp["account_id"] = result.account_id
        temp["country"] = result.country
        temp["disabled"] = result.disabled
        temp["email"] = result.email
        temp["email_verified"] = result.email_verified
        temp["is_paired"] = result.is_paired
        temp["locale"] = result.locale

        temp["profile_photo_url"] = result.profile_photo_url
        temp["referral_link"] = result.referral_link
        temp["team"] = result.team
        temp["team_member_id"] = result.team_member_id
        return temp

    async def list_files(
        self,
        path,
        recursive=False,
        include_media_info=False,
        include_deleted=False,
        include_has_explicit_shared_members=False,
        include_mounted_folders=True,
        limit=None,
        shared_link=None,
        include_property_groups=None,
        include_non_downloadable_files=True,
    ):

        """
        path:
        recursive:
        include_media_info:
        include_deleted:
        include_has_explicit_shared_members:
        include_mounted_folders:
        limit:
        shared_link:
        include_property_groups:
        include_non_downloadable_files:
        """

        response = self.client.files_list_folder(
            path=path,
            recursive=recursive,
            include_media_info=include_media_info,
            include_deleted=include_deleted,
            include_has_explicit_shared_members=include_has_explicit_shared_members,
            include_mounted_folders=include_mounted_folders,
            limit=limit,
            shared_link=shared_link,
            include_property_groups=include_property_groups,
            include_non_downloadable_files=include_non_downloadable_files,
        )
        temp = {}

        try:
            for file in response.entries:

                link = self.client.sharing_create_shared_link(file.path_display)

                path = link.url.replace("0", "1")
                temp[file.path_display] = path

            return temp

        except Exception as er:
            print(er)

    async def upload_file(self, file_from, file_to):

        with open(file_from, "rb") as f:

            self.client.files_upload(f.read(), file_to, mode=WriteMode("overwrite"))

    async def save_file_localy(self, file_path, filename):

        metadata, res = self.client.files_download(file_path + filename)

        with open(metadata.name, "wb") as f:
            f.write(res.content)

    async def get_link_of_file(self, file_path, filename, dowload=False):

        path = self.client.sharing_create_shared_link(file_path + filename)
        if dowload:
            path = path.url.replace("0", "1")

        return {"file": path.url}


async def co_upload_to_dropbox2(path_to_local_file: str, path_to_remote_dir: str = "/"):
    localfile_pathobj = pathlib.Path(f"{path_to_local_file}").absolute()
    try:
        assert localfile_pathobj.exists()
        assert localfile_pathobj.is_file()
    except Exception as ex:
        print(str(ex))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOGGER.error("Error Class: {}".format(str(ex.__class__)))
        output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
        LOGGER.warning(output)
        LOGGER.error("exc_type: {}".format(exc_type))
        LOGGER.error("exc_value: {}".format(exc_value))
        traceback.print_tb(exc_traceback)
        raise

    _localfile = f"{localfile_pathobj}"
    _backuppath = f"{path_to_remote_dir}/{path_to_local_file}"

    dbxconf = DropBoxConfig()
    try:
        async with AsyncDropBox(dbxconf) as drop:
            await drop.upload_file(file_from=_localfile, file_to=_backuppath)
    except ApiError as err:
        # This checks for the specific error where a user doesn't have
        # enough Dropbox space quota to upload this file
        if err.error.is_path() and err.error.get_path().reason.is_insufficient_space():
            sys.exit("ERROR: Cannot back up; insufficient space.")
        elif err.user_message_text:
            rich.print(err.user_message_text)
            sys.exit()
        else:
            rich.print(err)
            sys.exit()
