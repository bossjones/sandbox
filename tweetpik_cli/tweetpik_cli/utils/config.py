from logging import DEBUG, ERROR, INFO, WARN
import os

from tweetpik_cli import constants

DROPBOX_AIODROPBOX_APP_KEY = os.environ.get("DROPBOX_AIODROPBOX_APP_KEY")
DROPBOX_AIODROPBOX_APP_SECRET = os.environ.get("DROPBOX_AIODROPBOX_APP_SECRET")

DROPBOX_AIODROPBOX_TOKEN = os.environ.get("DROPBOX_AIODROPBOX_TOKEN")
DEFAULT_DROPBOX_FOLDER = "/cerebro_downloads"
default_config = {"token": "", "prefix": constants.PREFIX}

# SOURCE: discord-bot-heroku
def if_env(str):
    if str is None or str.upper() != "TRUE":
        return False
    else:
        return True


# SOURCE: discord-bot-heroku
def get_log_level(str):
    if str is None:
        return WARN
    upper_str = str.upper()
    if upper_str == "DEBUG":
        return DEBUG
    elif upper_str == "INFO":
        return INFO
    elif upper_str == "ERROR":
        return ERROR
    else:
        return WARN


# SOURCE: discord-bot-heroku
def num_env(param):
    if str is None or not str(param).isdecimal():
        return 5
    else:
        return int(param)


class Config:
    def __init__(self):
        self.config = {
            "token": DROPBOX_AIODROPBOX_TOKEN,
            "prefix": constants.PREFIX,
        }
        self.prefix = self.config.get("prefix", default_config.get("prefix"))
        self.token = self.config.get("token", default_config.get("token"))
