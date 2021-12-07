#!/usr/bin/env python

from datetime import datetime, timedelta
import os

from _pytest.fixtures import (
    FixtureRequest,
    SubRequest,
    _FixtureCachedResult,
    _FixtureFunc,
    _FixtureFunction,
    _FixtureValue,
)
# from _pytest.fixtures import (
#     FixtureRequest,
#     SubRequest,
#     _FixtureCachedResult,
#     _FixtureFunc,
#     _FixtureFunction,
#     _FixtureValue,
# )
from _pytest.monkeypatch import MonkeyPatch
import dropbox
import mock
# from freezegun import freeze_time
import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockerFixture
import requests

from aiodropbox.utils import dropbox_
from aiodropbox.utils.dropbox_ import (
    ApiError,
    AuthError,
    BadInputException,
    DropboxOAuth2FlowNoRedirect,
    WriteMode,
    create_session,
)

# Tests OAuth Flow
# from dropbox import DropboxOAuth2Flow, session, Dropbox, create_session
# from dropbox.dropbox_client import BadInputException, DropboxTeam
# from dropbox.exceptions import AuthError
# from dropbox.oauth import OAuth2FlowNoRedirectResult, DropboxOAuth2FlowNoRedirect
# from datetime import datetime, timedelta


APP_KEY = "dummy_app_key"
APP_SECRET = "dummy_app_secret"
ACCESS_TOKEN = "dummy_access_token"
REFRESH_TOKEN = "dummy_refresh_token"
EXPIRES_IN = 14400
ACCOUNT_ID = "dummy_account_id"
USER_ID = "dummy_user_id"
ADMIN_ID = "dummy_admin_id"
TEAM_MEMBER_ID = "dummy_team_member_id"
SCOPE_LIST = ["files.metadata.read", "files.metadata.write"]
EXPIRATION = datetime.utcnow() + timedelta(seconds=EXPIRES_IN)

EXPIRATION_BUFFER = timedelta(minutes=5)

# pylint: disable=protected-access

if os.environ.get("GITHUB_ACTOR"):
    is_running_in_github = True
else:
    is_running_in_github = False


# TODO: mock this correctly
@pytest.mark.dropboxonly
@pytest.mark.unittest
class TestDropboxClient:
    @pytest.fixture(scope="function")
    def session_instance(self, mocker: MockerFixture) -> requests.Session:
        session_obj = create_session()
        post_response = mock.MagicMock(status_code=200)
        post_response.json.return_value = {
            "access_token": ACCESS_TOKEN,
            "expires_in": EXPIRES_IN,
        }
        mocker.patch.object(session_obj, "post", return_value=post_response)
        return session_obj

    @pytest.fixture(scope="function")
    def invalid_grant_session_instance(self, mocker: MockerFixture) -> requests.Session:
        session_obj = create_session()
        post_response = mock.MagicMock(status_code=400)
        post_response.json.return_value = {"error": "invalid_grant"}
        mocker.patch.object(session_obj, "post", return_value=post_response)
        return session_obj

    def test_default_Dropbox_raises_assertion_error(self) -> None:
        with pytest.raises(BadInputException):
            # Requires either access token or refresh token
            dropbox_.get_dropbox_client(token="")
