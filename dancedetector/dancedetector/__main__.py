#!/usr/bin/env python

# NOTE: 11/19/2021 - still not working 100%. Hangs when finished processing.
import logging
import os
import os.path

from dancedetector.dbx_logger import get_logger, intercept_all_loggers  # noqa: E402

LOGGER = get_logger(__name__, provider="dancedetector", level=logging.DEBUG)
# intercept_all_loggers()

# handler_logger = LOGGER.add("handler")
# name_logger = LOGGER.add("asyncio")
# name_logger = LOGGER.add("tensorflow")
# name_logger = LOGGER.add("keras")
# name_logger = LOGGER.add(__name__)

# # rootlogger = logging.getLogger()
# handler_logger = logging.getLogger("handler")

# name_logger = logging.getLogger(__name__)
# asyncio_logger = logging.getLogger("asyncio").setLevel(logging.DEBUG)

DROPBOX_AIOSCRAPER_APP_KEY = os.environ.get("DROPBOX_AIOSCRAPER_APP_KEY")
DROPBOX_AIOSCRAPER_APP_SECRET = os.environ.get("DROPBOX_AIOSCRAPER_APP_SECRET")

DROPBOX_AIOSCRAPER_TOKEN = os.environ.get("DROPBOX_AIOSCRAPER_TOKEN")
DEFAULT_DROPBOX_FOLDER = "/dancedetector_downloads"
