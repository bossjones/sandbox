#!/usr/bin/env python

# NOTE: 11/19/2021 - still not working 100%. Hangs when finished processing.
import logging
import os
import os.path

rootlogger = logging.getLogger()
handler_logger = logging.getLogger("handler")

name_logger = logging.getLogger(__name__)
asyncio_logger = logging.getLogger("asyncio").setLevel(logging.DEBUG)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_ADMIN = os.environ.get("DISCORD_ADMIN_USER_ID")
DISCORD_GUILD = os.environ.get("DISCORD_SERVER_ID")
DISCORD_GENERAL_CHANNEL = 908894727779258390
