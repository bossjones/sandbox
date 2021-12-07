from logging import DEBUG, ERROR, INFO, WARN
import os

from aiodropbox import constants

# from dotenv import load_dotenv


DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
default_config = {"token": "", "prefix": constants.PREFIX}


# DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
# LOG_LEVEL = get_log_level(os.environ.get('LOG_LEVEL'))
# AUDIT_LOG_SEND_CHANNEL = os.environ.get('AUDIT_LOG_SEND_CHANNEL')
AUDIT_LOG_SEND_CHANNEL = os.environ.get("AUDIT_LOG_SEND_CHANNEL")
# IS_HEROKU = if_env(os.environ.get('IS_HEROKU'))
# SAVE_FILE_MESSAGE = os.environ.get('SAVE_FILE_MESSAGE')
# FIRST_REACTION_CHECK = if_env(os.environ.get('FIRST_REACTION_CHECK'))
# SCRAPBOX_SID_AND_PROJECTNAME = os.environ.get('SCRAPBOX_SID_AND_PROJECTNAME')
# COUNT_RANK_SETTING = num_env(os.environ.get('COUNT_RANK_SETTING'))
# PURGE_TARGET_IS_ME_AND_BOT = if_env(os.environ.get('PURGE_TARGET_IS_ME_AND_BOT'))
# OHGIRI_JSON_URL = os.environ.get('OHGIRI_JSON_URL')
# REACTION_CHANNELER_PERMIT_WEBHOOK_ID = os.environ.get('REACTION_CHANNELER_PERMIT_WEBHOOK_ID')
# WORDWOLF_JSON_URL = os.environ.get('WORDWOLF_JSON_URL')
# NGWORD_GAME_JSON_URL = os.environ.get('NGWORD_GAME_JSON_URL')

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
            "token": DISCORD_TOKEN,
            "prefix": constants.PREFIX,
        }
        self.prefix = self.config.get("prefix", default_config.get("prefix"))
        self.token = self.config.get("token", default_config.get("token"))
