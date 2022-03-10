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

# For content-aware scene detection:
from scenedetect.detectors import ContentDetector

VIDEO_TEST = "/Users/malcolm/dev/bossjones/sandbox/aiopillow/tests/fixtures/2615941409654231233_2615928388126090410.mp4"

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

def classify_text_in_image():
    words_in_image_str = pytesseract.image_to_string(Image.open(VIDEO_TEST))
    words = words_in_image_str.split("\n")
    return words


def execute_classify_text_in_image(ind: int, path_to_file: str):
    print(f"Thread {threading.current_thread().name}: Starting task: {ind}...")

    # time.sleep(1)
    words_in_image_str = pytesseract.image_to_string(Image.open(VIDEO_TEST))
    words = words_in_image_str.split("\n")

    # if ind == 2 and RAISE_EXCEPTION:
    #     print("BOOM!")
    #     raise Exception("Boom!")

    print(f"Thread {threading.current_thread().name}: Finished task {ind}!")
    return words

def copy_to_tempdir(files=None, **kw):
    # SOURCE: https://gist.github.com/waylan/50a067d79386aabf9073dbab7beb2950
    """
    A decorator for building a temporary directory with prepopulated files.
    The temproary directory and files are created just before the wrapped function is called and are destroyed
    imediately after the wrapped function returns.
    The `files` keyword should be a dict of file paths as keys and strings of file content as values.
    If `files` is a list, then each item is assumed to be a path of an empty file. All other
    keywords are passed to `tempfile.TemporaryDirectory` to create the parent directory.
    In the following example, two files are created in the temporary directory and then are destroyed when
    the function exits:
        @tempdir(files={
            'foo.txt': 'foo content',
            'bar.txt': 'bar content'
        })
        def example(dir):
            assert Path(dir, 'foo.txt').is_file()
            p = Path(dir, 'bar.txt')
            assert p.is_file()
            assert p.read_text(encoding='utf-8') == 'bar content'
    """
    files = {f: '' for f in files} if isinstance(files, (list, tuple)) else files or {}
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with TemporaryDirectory(**kw) as td:
                for path, content in files.items():
                    Path(td, path).write_text(content, encoding='utf-8')
                return fn(td, *args, **kwargs)
        return wrapper
    return decorator


def execute_hello(ind: int):
    print(f"Thread {threading.current_thread().name}: Starting task: {ind}...")

    time.sleep(1)

    if ind == 2 and RAISE_EXCEPTION:
        print("BOOM!")
        raise Exception("Boom!")

    print(f"Thread {threading.current_thread().name}: Finished task {ind}!")
    return ind

# io bound feature, open video and save
def execute_find_scenes(ind: int, video_path: str, threshold=30.0):
    print(f"Thread {threading.current_thread().name}: Starting task: {ind}...")

    # Create our video & scene managers, then add the detector.
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold))

    # Improve processing speed by downscaling before processing.
    video_manager.set_downscale_factor()

    # Start the video manager and perform the scene detection.
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scenes = scene_manager.get_scene_list()

    res = scene_manager.save_images(scenes, num_images=3, output_dir="./processed")

    # Each returned scene is a tuple of the (start, end) timecode.
    print(f"Thread {threading.current_thread().name}: Finished task {ind}!")
    return res

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
            loop.run_in_executor(pool, execute_with_shutdown_check, s, task, VIDEO_TEST)
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
