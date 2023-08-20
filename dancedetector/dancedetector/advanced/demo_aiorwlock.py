# SOURCE: https://github.com/aio-libs/aiorwlock/blob/master/examples/simple.py
import asyncio

import aiorwlock
import logging
from loguru import logger
from dancedetector.dbx_logger import (
    get_logger,
    intercept_all_loggers,
    global_log_config
)

global_log_config(
    log_level=logging.getLevelName("DEBUG"),
    json=False,
)


async def go():
    rwlock = aiorwlock.RWLock()

    # acquire reader lock
    await rwlock.reader_lock.acquire()
    try:
        print("inside reader lock")

        await asyncio.sleep(0.1)
    finally:
        rwlock.reader_lock.release()

    # acquire writer lock
    await rwlock.writer_lock.acquire()
    try:
        print("inside writer lock")

        await asyncio.sleep(0.1)
    finally:
        rwlock.writer_lock.release()


loop = asyncio.get_event_loop()
loop.run_until_complete(go())
