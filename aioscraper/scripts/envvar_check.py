#!/usr/bin/env python

import os

ENV_VARS_TO_CHECK = [
    "DEBUG",
    "TESTING",
    "SECRET_KEY",
    "REDIS_URL",
    "REDIS_ENDPOINT",
    "REDIS_PORT",
    "REDIS_DB",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "DEFAULT_MODULE_NAME",
    "VARIABLE_NAME",
    "MODULE_NAME",
    "VARIABLE_NAME",
    "APP_MODULE",
    "DEFAULT_GUNICORN_CONF",
    "PRE_START_PATH",
    "HOST",
    "PORT",
    "LOG_LEVEL",
    "SERVER_NAME",
    "SERVER_HOST",
]

for e in ENV_VARS_TO_CHECK:
    _env_var = os.environ.get(e)
    print(f"{e}={_env_var}")
