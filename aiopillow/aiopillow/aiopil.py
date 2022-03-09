import bpdb
import asyncio
import aiohttp

import bs4

from bs4 import BeautifulSoup
from html.parser import HTMLParser
import sys
import rich
import snoop
from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa
import typing
import concurrent.futures
import concurrent

from typing import List, Optional, Tuple, Union

import PIL
from PIL import Image
from PIL.ExifTags import TAGS
import threading
import time

# sys.excepthook = ultratb.FormattedTB(
#     mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
# )

# SOURCE: https://kimmosaaskilahti.fi/blog/2021-01-03-asyncio-workers/
MAX_WORKERS = 4
RAISE_EXCEPTION = True

_SHUTDOWN = False


def execute_hello(ind: int):
    print(f"Thread {threading.current_thread().name}: Starting task: {ind}...")

    time.sleep(1)

    if ind == 2 and RAISE_EXCEPTION:
        print("BOOM!")
        raise Exception("Boom!")

    print(f"Thread {threading.current_thread().name}: Finished task {ind}!")
    return ind


def execute_with_shutdown_check(f, *args, **kwargs):
    if _SHUTDOWN:
        print(f"Skipping task as shutdown was requested")
        return None

    return f(*args, **kwargs)


async def main_wait():
    loop = asyncio.get_running_loop()
    tasks = range(20)
    global _SHUTDOWN
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [loop.run_in_executor(pool, execute_hello, task) for task in tasks]
        done, pending = await asyncio.wait(
            futures, return_when=asyncio.FIRST_EXCEPTION, timeout=3600
        )
        _SHUTDOWN = True

    results = [done_.result() for done_ in done]

    if len(pending) > 0:
        raise Exception(f"{len(pending)} tasks did not finish")

    print(f"Finished processing, got results: {results}")


async def main_gather(tasks=20):
    loop = asyncio.get_running_loop()
    global _SHUTDOWN
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            loop.run_in_executor(pool, execute_with_shutdown_check, execute_hello, task)
            for task in range(tasks)
        ]
        try:
            results = await asyncio.gather(*futures, return_exceptions=False)
        except Exception as ex:
            print("Caught exception", ex)
            # _SHUTDOWN = True
            raise
    print(f"Finished processing, got results: {results}")


# asyncio.run(main_wait())
if __name__ == "__main__":
    asyncio.run(main_gather(tasks=10))
