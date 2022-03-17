"""Gathers environment settings and loads them into global attributes for Api service."""
from datetime import timedelta
import logging
import os
import platform
import uuid

from pydantic import EmailStr  # pylint: disable=no-name-in-module
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from upscale_cli.dbx_logger import get_logger  # noqa: E402
from upscale_cli.utils.parser import get_domain_from_fqdn

LOGGER = get_logger(__name__, provider="Settings", level=logging.DEBUG)


LOG_LEVEL_MAP = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "WARNING": logging.WARN,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "FATAL": logging.FATAL,
    "CRITICAL": logging.CRITICAL,
}

PLATFORM_ULTRON_SYSTEM_BASE_PATH_MAP = {
    "Darwin": "/usr/local/opt/ultron8",
    "Linux": "/opt/ultron8",
}

CURRENT_PLATFORM = platform.system()


def getenv_boolean(var_name: str, default_value: bool = False) -> bool:
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


DROPBOX_AIODROPBOX_APP_KEY = os.environ.get("DROPBOX_AIODROPBOX_APP_KEY")
DROPBOX_AIODROPBOX_APP_SECRET = os.environ.get("DROPBOX_AIODROPBOX_APP_SECRET")

DROPBOX_AIODROPBOX_TOKEN = os.environ.get("DROPBOX_AIODROPBOX_TOKEN")
DEFAULT_DROPBOX_FOLDER = "/cerebro_downloads"

API_V1_STR = "/v1"

DEFAULT_SECRET_KEY = "supersecretkey"

SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = os.getenv("SERVER_HOST", default="http://localhost:11267")
PROJECT_NAME = os.getenv("PROJECT_NAME")
SENTRY_DSN = os.getenv("SENTRY_DSN")

SMTP_TLS = getenv_boolean("SMTP_TLS", True)
SMTP_PORT = None
_SMTP_PORT = os.getenv("SMTP_PORT")
if _SMTP_PORT is not None:
    SMTP_PORT = int(_SMTP_PORT)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")
EMAILS_FROM_NAME = PROJECT_NAME
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48
EMAIL_TEMPLATES_DIR = "/app/app/email-templates/build"
EMAILS_ENABLED = bool(SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL)

USERS_OPEN_REGISTRATION = getenv_boolean("USERS_OPEN_REGISTRATION")

DEBUG = getenv_boolean("DEBUG", default_value=False)
TESTING = getenv_boolean("TESTING", default_value=False)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", None)

if TESTING and TEST_DATABASE_URL:
    DATABASE_URL = TEST_DATABASE_URL
else:
    DATABASE_URL = os.environ.get("DATABASE_URL", None)

BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS", "*"
)  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"

FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER", "admin")
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "password")

_USER_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = LOG_LEVEL_MAP[_USER_LOG_LEVEL]
MASK_SECRETS = getenv_boolean("MASK_SECRETS", default_value=True)
DEBUG_REQUESTS = getenv_boolean("DEBUG_REQUESTS", default_value=False)
# Avoid uvicorn error: https://github.com/simonw/datasette/issues/633
# WORKERS = os.environ.get("WORKERS", "1")
CLUSTER_UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, get_domain_from_fqdn(SERVER_HOST)))

EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore

# ~~~~~ JWT ~~~~~
JWT_EXPIRATION_DELTA = timedelta(
    hours=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10))
)  # in hours
JWT_REFRESH_EXPIRATION_DELTA = timedelta(
    hours=int(os.environ.get("JWT_REFRESH_EXPIRATION_DELTA", 10))
)  # in hours
JWT_AUTH_HEADER_PREFIX = os.environ.get("JWT_AUTH_HEADER_PREFIX", "JWT")
JWT_SECRET_KEY = SECRET_KEY

# ~~~~~ OAUTH 2 ~~~~~

SCOPES = {"read": "Read", "write": "Write"}


# ~~~~~ SYSTEM CONFIG OPTIONS ~~~~~
SYSTEM_BASE_PATH = os.getenv(
    "ULTRON_SYSTEM_BASE_PATH", PLATFORM_ULTRON_SYSTEM_BASE_PATH_MAP[CURRENT_PLATFORM]
)
SYSTEM_VALIDATE_TRIGGER_PARAMETERS = getenv_boolean(
    "ULTRON_SYSTEM_VALIDATE_TRIGGER_PARAMETERS", default_value=False
)
SYSTEM_VALIDATE_TRIGGER_PAYLOAD = getenv_boolean(
    "ULTRON_SYSTEM_VALIDATE_TRIGGER_PAYLOAD", default_value=False
)
SYSTEM_VALIDATE_OUTPUT_SCHEMA = getenv_boolean(
    "ULTRON_SYSTEM_VALIDATE_OUTPUT_SCHEMA", default_value=False
)
SYSTEM_PACKS_BASE_PATH = os.path.join(SYSTEM_BASE_PATH, "packs")
SYSTEM_RUNNERS_BASE_PATH = os.path.join(SYSTEM_BASE_PATH, "runners")

# ~~~~~ SYSTEM CONFIG OPTIONS ~~~~~
CONTENT_PACK_GROUP = os.getenv("ULTRON_CONTENT_PACK_GROUP", "u8packs")
CONTENT_SYSTEM_PACKS_BASE_PATH = os.getenv(
    "ULTRON_CONTENT_SYSTEM_PACKS_BASE_PATH", SYSTEM_PACKS_BASE_PATH
)
CONTENT_SYSTEM_RUNNERS_BASE_PATH = os.getenv(
    "ULTRON_CONTENT_SYSTEM_RUNNERS_BASE_PATH", SYSTEM_RUNNERS_BASE_PATH
)
# Paths which will be searched for integration packs.
CONTENT_PACKS_BASE_PATHS = os.getenv("ULTRON_CONTENT_PACKS_BASE_PATHS", None)
# Paths which will be searched for runners. NOTE: This option has been deprecated and it's unused since Ultron8 v3.0.0
CONTENT_RUNNERS_BASE_PATHS = os.getenv("ULTRON_CONTENT_RUNNERS_BASE_PATHS", None)
# A URL pointing to the pack index. StackStorm Exchange is used by  default.
# Use a comma-separated list for multiple indexes if you  want to get other packs discovered with "st2 pack search".
CONTENT_INDEX_URL = [f"{SERVER_HOST}/v1/index.json"]


class SettingsConfig:
    DEBUG = DEBUG
    API_V1_STR = API_V1_STR
    DEFAULT_SECRET_KEY = DEFAULT_SECRET_KEY
    SECRET_KEY = SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    SERVER_NAME = SERVER_NAME
    SERVER_HOST = SERVER_HOST
    PROJECT_NAME = PROJECT_NAME
    SENTRY_DSN = SENTRY_DSN
    SMTP_TLS = getenv_boolean("SMTP_TLS", True)
    SMTP_PORT = SMTP_PORT
    SMTP_HOST = SMTP_HOST
    SMTP_USER = SMTP_USER
    SMTP_PASSWORD = SMTP_PASSWORD
    EMAILS_FROM_EMAIL = EMAILS_FROM_EMAIL
    EMAILS_FROM_NAME = EMAILS_FROM_NAME
    EMAIL_RESET_TOKEN_EXPIRE_HOURS = EMAIL_RESET_TOKEN_EXPIRE_HOURS
    EMAIL_TEMPLATES_DIR = EMAIL_TEMPLATES_DIR
    EMAILS_ENABLED = EMAILS_ENABLED
    USERS_OPEN_REGISTRATION = USERS_OPEN_REGISTRATION
    DEBUG = DEBUG
    TESTING = TESTING
    TEST_DATABASE_URL = TEST_DATABASE_URL
    DATABASE_URL = DATABASE_URL
    BACKEND_CORS_ORIGINS = BACKEND_CORS_ORIGINS
    FIRST_SUPERUSER = FIRST_SUPERUSER
    FIRST_SUPERUSER_PASSWORD = FIRST_SUPERUSER_PASSWORD
    LOG_LEVEL = LOG_LEVEL
    MASK_SECRETS = MASK_SECRETS
    DEBUG_REQUESTS = DEBUG_REQUESTS
    # WORKERS = WORKERS
    CLUSTER_UUID = CLUSTER_UUID
    JWT_EXPIRATION_DELTA = JWT_EXPIRATION_DELTA
    JWT_REFRESH_EXPIRATION_DELTA = JWT_REFRESH_EXPIRATION_DELTA
    JWT_AUTH_HEADER_PREFIX = JWT_AUTH_HEADER_PREFIX
    JWT_SECRET_KEY = JWT_SECRET_KEY
    SCOPES = SCOPES


if __name__ == "__main__":
    from upscale_cli.debugger import debug_dump_exclude

    SC = SettingsConfig()
    debug_dump_exclude(SC)
