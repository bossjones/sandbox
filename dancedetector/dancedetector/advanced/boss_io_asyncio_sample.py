#!/usr/bin/env python
# NOTE: For more examples tqdm + aiofile, search https://github.com/search?l=Python&q=aiofile+tqdm&type=Code
from __future__ import annotations

import asyncio
import concurrent.futures
import functools
from hashlib import md5
import logging
import os
import pathlib
import shutil
import ssl
import tempfile
import time
from urllib.request import urlretrieve

import aiofile
import aiohttp
import aiorwlock
import certifi
from loguru import logger
import requests
import rich
from tqdm.auto import tqdm
import uritools

from dancedetector.dbx_logger import global_log_config

global_log_config(
    log_level=logging.getLevelName("DEBUG"),
    json=False,
)
LOGGER = logger


VERIFY_SSL = False

PHOTO_OUTPUT_DIRS = [
    {
        "EXTENSIONS": ["jpg", "jpeg", "mov", "mp4", "m4v", "3gp"],
        "PATH": "./data/photos",
    },
    {
        "EXTENSIONS": ["cr2"],
        "PATH": "./data/raw-photos",
    },
]

# ------------------------------------------------------------------------------
# SOURCE: https://github.com/dream2globe/CleanCodeInPython/blob/e759773c95e7485f004b629fcf7fb4a662c95794/Ch7-2_ConcurrencyTest.py
DEFAULT_FMT = "[{elapsed:0.8f}s] {name}({args}, {kwargs}) -> {result}"


def clock(fmt=DEFAULT_FMT):
    def decorate(func):
        @functools.wraps(func)
        def clocked(*_args, **_kwargs):  # clocked에서 *, ** 키워드를 통해 설정된 인수를 변수화
            t0 = time.time()
            _result = func(*_args)
            elapsed = time.time() - t0
            name = func.__name__
            args = ", ".join(repr(arg) for arg in _args)
            pairs = ["%s=%r" % (k, w) for k, w in sorted(_kwargs.items())]
            kwargs = ", ".join(pairs)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result  # clocked()는 데커레이트된 함수를 대체하므로, 원래 함수가 반환하는 값을 반환해야 한다.

        return clocked  # decorate()는 clocked()를 반환한다.

    return decorate  # clock()은 decorate()를 반환한다.


# ------------------------------------------------------------------------------


def get_folder_size(filepath: str) -> int:
    """Get size of folder in bytes

    Args:
        filepath (str): path to directory

    Returns:
        int: folder size in bytes
    """
    total_size = 0
    for root, _dirs, files in os.walk(filepath):
        for img in files:
            total_size += os.path.getsize(os.path.join(root, img))

    return total_size


def determine_destination(fn: str):
    extension = os.path.splitext(fn)[1][1:].lower()
    for output_filter in PHOTO_OUTPUT_DIRS:
        if extension in output_filter["EXTENSIONS"]:
            return output_filter["PATH"]
    return None


def find_new_file_name(path):
    """
    If a file already exists in the same place with the same name, this
    function will find a new name to use, changing the extension to
    '_1.jpg' or similar.
    """
    counter = 1
    fn, extension = os.path.splitext(path)
    attempt = path
    while os.path.exists(attempt):
        attempt = "{}_{}{}".format(fn, counter, extension)
        counter += 1
    return attempt


# def download_file(url, destination_path):
#     temp_path = tempfile.mktemp()
#     with requests.get(url, stream=True) as r:
#         with open(temp_path, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=32768):
#                 if chunk:
#                     f.write(chunk)
#     shutil.move(temp_path, destination_path)
#     return destination_path


def handle_download_file(url: str, destination_path: str):
    temp_path = tempfile.mktemp()
    with requests.get(url, stream=True) as r:
        with open(temp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
    shutil.move(temp_path, destination_path)
    return destination_path


async def download_and_save(url: str, dest_override=False, base_authority=""):
    rwlock = aiorwlock.RWLock()
    # SOURCE: https://github.com/aio-libs/aiohttp/issues/955
    # SOURCE: https://stackoverflow.com/questions/35388332/how-to-download-images-with-aiohttp
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=sslcontext if VERIFY_SSL else None)
    ) as http:
        url_file_api = pathlib.Path(url)
        filename = f"{url_file_api.name}"

        uri = uritools.urisplit(url)

        if not uri.authority:
            await rwlock.reader_lock.acquire()
            try:
                rich.print(
                    f"uri.authority = {uri.authority}, manually setting url variable"
                )
                LOGGER.debug(f"uri.authority = {uri.authority}, manually setting url variable")
            finally:
                rwlock.reader_lock.release()
            url = f"{base_authority}/{url}"
            await rwlock.reader_lock.acquire()
            try:
                # rich.print(f"uri.authority = {uri.authority}, manually setting url variable")
                rich.print(f"url = {url}")
                LOGGER.debug(f"url = {url}")
            finally:
                rwlock.reader_lock.release()

        if dest_override:
            filename = dest_override
            await rwlock.reader_lock.acquire()
            try:
                rich.print(f"filename = {dest_override}")
                LOGGER.debug(f"filename = {dest_override}")
            finally:
                rwlock.reader_lock.release()
        # breakpoint()
        async with http.request(
            "GET", url, ssl=sslcontext if VERIFY_SSL else None
        ) as resp:
            if resp.status == 200:
                # SOURCE: https://stackoverflow.com/questions/72006813/python-asyncio-file-write-after-request-getfile-not-working
                size = 0
                try:
                    async with aiofile.async_open(filename, "wb+") as afp:
                        async for chunk in resp.content.iter_chunked(
                            1024 * 512
                        ):  # 500 KB
                            await afp.write(chunk)
                            size += len(chunk)
                except asyncio.TimeoutError:
                    # rich.print(f"A timeout ocurred while downloading '{filename}'")
                    pass

                return filename, size


def md5sum(path):
    hash_md5 = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


#################################################################################################################################3
# Define functions to download an archived dataset and unpack it
class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url: str, filepath: str):
    directory = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(directory, exist_ok=True)
    if os.path.exists(filepath):
        print("Filepath already exists. Skipping download.")
        LOGGER.debug("Filepath already exists. Skipping download.")
        return

    with TqdmUpTo(
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        desc=os.path.basename(filepath),
    ) as t:
        urlretrieve(url, filename=filepath, reporthook=t.update_to, data=None)
        t.total = t.n


#################################################################################################################################3


async def go_partial(loop):
    test_images = [
        [
            "https://i.imgur.com/kvSAxmy.png",
            "/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/asyncio_demo.png",
        ]
    ]

    # handle_download_file_func = functools.partial(handle_download_file, test_images[0][0], test_images[0][1])
    handle_download_file_func = functools.partial(
        download_url, test_images[0][0], test_images[0][1]
    )

    # 2. Run in a custom thread pool:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        dest = await loop.run_in_executor(pool, handle_download_file_func)

    return dest


if __name__ == "__main__":
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go_partial(loop))
    duration = time.time() - start_time
    print(f"Downloaded 1 site in {duration} seconds")
    LOGGER.debug(f"Downloaded 1 site in {duration} seconds")
