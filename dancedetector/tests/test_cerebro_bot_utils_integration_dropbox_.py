# #!/usr/bin/env python

# from __future__ import absolute_import, division, print_function, unicode_literals

# import warnings

# warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

# import datetime
# # from datetime import datetime
# from io import BytesIO
# import os
# import random
# import string
# import sys

# from _pytest.fixtures import (
#     FixtureRequest,
#     SubRequest,
#     _FixtureCachedResult,
#     _FixtureFunc,
#     _FixtureFunction,
#     _FixtureValue,
# )
# from _pytest.monkeypatch import MonkeyPatch
# import dropbox
# from dropbox.common import PathRoot, PathRoot_validator
# from dropbox.dropbox_client import PATH_ROOT_HEADER, SELECT_USER_HEADER
# from dropbox.exceptions import ApiError, AuthError, BadInputError, PathRootError
# from dropbox.files import DeleteResult, ListFolderError, PathOrLink, SharedLinkFileInfo
# import mock
# # from freezegun import freeze_time
# import pytest
# from pytest_mock import MockerFixture
# from pytest_mock.plugin import MockerFixture
# import requests

# from dancedetector.utils import dropbox_
# from dancedetector.utils.dropbox_ import (
#     ApiError,
#     AuthError,
#     BadInputException,
#     DropboxOAuth2FlowNoRedirect,
#     WriteMode,
#     create_session,
# )

# # Key Types
# REFRESH_TOKEN_KEY = "REFRESH_TOKEN"
# ACCESS_TOKEN_KEY = "TOKEN"
# CLIENT_ID_KEY = "APP_KEY"
# CLIENT_SECRET_KEY = "APP_SECRET"
# # App Types
# SCOPED_KEY = "DROPBOX"
# LEGACY_KEY = "LEGACY"
# # User Types
# USER_KEY = "CEREBRO"
# TEAM_KEY = "TEAM"
# # Misc types
# SHARED_LINK_KEY = "DROPBOX_SHARED_LINK"


# def format_env_name(
#     app_type: str = SCOPED_KEY,
#     user_type: str = USER_KEY,
#     key_type: str = ACCESS_TOKEN_KEY,
# ) -> str:
#     return "{}_{}_{}".format(app_type, user_type, key_type)


# def _value_from_env_or_die(env_name: str) -> str:
#     value = os.environ.get(env_name)
#     if value is None:
#         print(
#             "Set {} environment variable to a valid value.".format(env_name),
#             file=sys.stderr,
#         )
#         sys.exit(1)
#     return value


# @pytest.fixture()
# def dbx_from_env() -> dropbox.Dropbox:
#     oauth2_token = _value_from_env_or_die(format_env_name())
#     return dropbox_.get_dropbox_client(token=oauth2_token)


# MALFORMED_TOKEN = "asdf"
# INVALID_TOKEN = "z" * 62

# # Need bytes type for Python3
# DUMMY_PAYLOAD = string.ascii_letters.encode("ascii")

# RANDOM_FOLDER = random.sample(string.ascii_letters, 15)
# TIMESTAMP = str(datetime.datetime.utcnow())
# STATIC_FILE = "/test.txt"


# @pytest.fixture(scope="module", autouse=True)
# def pytest_setup() -> None:
#     print("Setup")
#     dbx = dropbox_.get_dropbox_client(token=_value_from_env_or_die(format_env_name()))

#     try:
#         dbx.files_delete_v2(STATIC_FILE)  # type: ignore
#     except Exception:
#         print(f"File not found in dropbox remote -> {STATIC_FILE}")

#     try:
#         dbx.files_delete_v2("/Test/%s" % TIMESTAMP)  # type: ignore
#     except Exception:
#         print(f"File not found in dropbox remote -> /Test/{TIMESTAMP}")


# # pylint: disable=protected-access

# if os.environ.get("GITHUB_ACTOR"):
#     is_running_in_github = True
# else:
#     is_running_in_github = False


# @pytest.mark.filterwarnings("ignore:unclosed <ssl.SSLSocket ")
# @pytest.mark.dropboxonly
# @pytest.mark.integration
# @pytest.mark.usefixtures(
#     "dbx_from_env",
# )
# class TestDropboxIntegration:
#     # def test_rpc(self, dbx_from_env: FixtureRequest) -> None:
#     #     dbx_from_env.files_list_folder("")

#     #     # Test API error
#     #     random_folder_path = "/" + "".join(RANDOM_FOLDER)
#     #     with pytest.raises(ApiError) as cm:
#     #         dbx_from_env.files_list_folder(random_folder_path)
#     #     assert isinstance(cm.value.error, ListFolderError)

#     @pytest.mark.flaky(reruns=5, reruns_delay=2)
#     def test_upload_download(self, dbx_from_env: FixtureRequest) -> None:
#         # Upload file
#         random_filename = "".join(RANDOM_FOLDER)
#         random_path = "/Test/%s/%s" % (TIMESTAMP, random_filename)
#         test_contents = DUMMY_PAYLOAD
#         dbx_from_env.files_upload(test_contents, random_path)  # type: ignore

#         # Download file
#         _, resp = dbx_from_env.files_download(random_path)  # type: ignore
#         assert DUMMY_PAYLOAD == resp.content

#         # Cleanup folder
#         dbx_from_env.files_delete_v2("/Test/%s" % TIMESTAMP)  # type: ignore

#     def test_bad_upload_types(self, dbx_from_env: FixtureRequest) -> None:
#         with pytest.raises(TypeError):
#             dbx_from_env.files_upload(BytesIO(b"test"), "/Test")  # type: ignore

#     def test_clone_when_user_linked(self, dbx_from_env: FixtureRequest) -> None:
#         new_dbx = dbx_from_env.clone()  # type: ignore
#         assert dbx_from_env is not new_dbx
#         assert isinstance(new_dbx, dbx_from_env.__class__)

#     def test_versioned_route(self, dbx_from_env: FixtureRequest) -> None:
#         # Upload a test file
#         dbx_from_env.files_upload(DUMMY_PAYLOAD, STATIC_FILE)  # type: ignore

#         # Delete the file with v2 route
#         resp = dbx_from_env.files_delete_v2(STATIC_FILE)  # type: ignore
#         # Verify response type is of v2 route
#         assert isinstance(resp, DeleteResult)
