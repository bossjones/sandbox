from contextlib import contextmanager
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
import uritools
from aiopillow.factories import cmd_factory
import logging
from aiopillow.dbx_logger import get_logger  # noqa: E402
from aiopillow import shell
import tempfile
from tempfile import TemporaryDirectory
import traceback

from functools import wraps
from pathlib import Path

from codetiming import Timer
import pytesseract
import aiopath

# Standard PySceneDetect imports:
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.scene_manager import save_images
from aiopillow.utils import file_functions

# For content-aware scene detection:
from scenedetect.detectors import ContentDetector

VIDEO_TEST_DIR = "/Users/malcolm/dev/bossjones/sandbox/aiopillow/processed"

LOGGER = get_logger(__name__, provider="MLModels", level=logging.DEBUG)

# Python Asyncio Timing Decorator
def timeit(func):
    # SOURCE: https://gist.github.com/Integralist/77d73b2380e4645b564c28c53fae71fb
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print('this function is a coroutine: {}'.format(func.__name__))
            return await func(*args, **params)
        else:
            print('this is not a coroutine')
            return func(*args, **params)

    async def helper(*args, **params):
        print('{}.time'.format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)

        print('>>>', time.time() - start)
        return result

    return helper

# https://realpython.com/lessons/what-are-python-coroutines/
# Generator = producer
# Coroutines = consumers

# sys.excepthook = ultratb.FormattedTB(
#     mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
# )

# SOURCE: https://kimmosaaskilahti.fi/blog/2021-01-03-asyncio-workers/
MAX_WORKERS = 4
RAISE_EXCEPTION = True

_SHUTDOWN = False


def get_cmd_metadata(CMD: str, uri: str, cmd_name: str = "screendetect") -> cmd_factory.CmdSerializer:
    dl_uri = uritools.urisplit(uri)
    cmd_args = [cmd_name]
    cmd_kargs = {
        "cmd": CMD.format(dl_uri=dl_uri.geturi()),
        "uri": f"{dl_uri.geturi()}",
    }

    cmd_metadata = cmd_factory.CmdSerializer(*cmd_args, **cmd_kargs)

    return cmd_metadata

# https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html
# Multiple context managers
@contextmanager
def tmpdir_and_timer(TemporaryDirectory, Timer):
    with TemporaryDirectory() as tmpdirname, Timer(text="\nTotal elapsed time: {:.1f}") as timer:
        print("created temporary directory", tmpdirname)
        yield (tmpdirname, timer)


async def aio_shell_runner(CMD: str, uri: str, cmd_name: str = "screendetect"):
    cmd_metadata: cmd_factory.CmdSerializer
    cmd_metadata = get_cmd_metadata(CMD, uri, cmd_name=cmd_name)


    with tempfile.TemporaryDirectory() as tmpdirname:
            print("created temporary directory", tmpdirname)
            with Timer(text="\nTotal elapsed time: {:.1f}"):

                try:
                    dbg = await asyncio.gather(
                        asyncio.create_task(
                            shell.run_coroutine_subprocess(
                                cmd=cmd_metadata.cmd,
                                uri=cmd_metadata.uri,
                                working_dir=f"{tmpdirname}",
                            )
                        ),
                    )

                except Exception as ex:
                    print(str(ex))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    LOGGER.error("Error Class: {}".format(str(ex.__class__)))
                    output = "[{}] {}: {}".format("UNEXPECTED", type(ex).__name__, ex)
                    LOGGER.warning(output)
                    LOGGER.error("exc_type: {}".format(exc_type))
                    LOGGER.error("exc_value: {}".format(exc_value))
                    traceback.print_tb(exc_traceback)


def execute_classify_text_in_image(ind: int, path_to_file: str):
    print(f"Thread {threading.current_thread().name}: Starting task: {ind}...")

    # time.sleep(1)
    image = Image.open(path_to_file)
    (width, height) = image.size  # im.size returns (width,height) tuple
    words_in_image_str = pytesseract.image_to_string(image)
    words = words_in_image_str.split("\n")
    rich.print(words)

    # if ind == 2 and RAISE_EXCEPTION:
    #     print("BOOM!")
    #     raise Exception("Boom!")

    print(f"Thread {threading.current_thread().name}: Finished task {ind}!")
    return words


def execute_with_shutdown_check(f, *args, **kwargs):
    if _SHUTDOWN:
        print(f"Skipping task as shutdown was requested")
        return None

    return f(*args, **kwargs)

async def main_gather():
    loop = asyncio.get_running_loop()
    global _SHUTDOWN

    tree_list = file_functions.tree(Path(VIDEO_TEST_DIR))
    rich.print(tree_list)

    file_to_inspect = []

    for p in tree_list:
        file_to_inspect.append(f"{p}")


    rich.print(file_to_inspect)

    files_to_classify = file_functions.filter_images(file_to_inspect)
    # tasks = len(files_to_classify)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            loop.run_in_executor(pool, execute_with_shutdown_check, execute_classify_text_in_image, task, path_to_img)
            for task, path_to_img in enumerate(files_to_classify)
        ]
        try:
            results = await asyncio.gather(*futures, return_exceptions=False)
        except Exception as ex:
            print("Caught exception", ex)
            # _SHUTDOWN = True
            raise
    rich.print(f"Finished processing, got results: {results}")


# asyncio.run(main_wait())
if __name__ == "__main__":
    asyncio.run(main_gather())
