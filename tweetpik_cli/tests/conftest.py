"""
Global test fixtures definitions.
"""
# Taken from tedi and guid_tracker

import datetime
import os
import posixpath

from _pytest import nodes as pytest_nodes
from _pytest.config import Config as pytest_Config
from _pytest.config.argparsing import Parser as pytest_Parser
from _pytest.fixtures import (
    FixtureRequest,
    SubRequest,
    _FixtureCachedResult,
    _FixtureFunc,
    _FixtureFunction,
    _FixtureValue,
)
from _pytest.monkeypatch import MonkeyPatch
import pytest
from pytest_mock import MockerFixture
from pytest_mock.plugin import MockerFixture
import requests

IS_RUNNING_ON_GITHUB_ACTIONS = bool(os.environ.get("GITHUB_ACTOR"))

HERE = os.path.abspath(os.path.dirname(__file__))
FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)

print("HERE: {}".format(HERE))

#######################################################################
# only run slow tests when we want to
#######################################################################
# SOURCE: https://doc.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
#######################################################################


@pytest.fixture(name="posixpath_fixture")
def posixpath_fixture(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(os, "path", posixpath)


@pytest.fixture(name="user_homedir")
def user_homedir() -> str:
    if os.environ.get("GITHUB_ACTOR"):
        return "/Users/runner"
    else:
        return "/Users/malcolm"
