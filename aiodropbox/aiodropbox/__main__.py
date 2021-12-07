#!/usr/bin/env python

# NOTE: 11/19/2021 - still not working 100%. Hangs when finished processing.
import logging
import os
import os.path

rootlogger = logging.getLogger()
handler_logger = logging.getLogger("handler")

name_logger = logging.getLogger(__name__)
asyncio_logger = logging.getLogger("asyncio").setLevel(logging.DEBUG)

DROPBOX_AIODROPBOX_APP_KEY = os.environ.get("DROPBOX_AIODROPBOX_APP_KEY")
DROPBOX_AIODROPBOX_APP_SECRET = os.environ.get("DROPBOX_AIODROPBOX_APP_SECRET")

DROPBOX_AIODROPBOX_TOKEN = os.environ.get("DROPBOX_AIODROPBOX_TOKEN")
DEFAULT_DROPBOX_FOLDER = "/cerebro_downloads"
