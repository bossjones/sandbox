from __future__ import annotations

import concurrent.futures

import asyncio
import time
import aiohttp
import os
import errno
from hashlib import md5
import os
import shutil
import tempfile
import ssl
import certifi
import rich
import uritools
import aiofile
import pathlib
import functools
import gc
import aiorwlock
import requests
from tqdm.auto import tqdm

# from tqdm.asyncio import tqdm
from urllib.request import urlretrieve


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
            finally:
                rwlock.reader_lock.release()
            url = f"{base_authority}/{url}"
            await rwlock.reader_lock.acquire()
            try:
                # rich.print(f"uri.authority = {uri.authority}, manually setting url variable")
                rich.print(f"url = {url}")
            finally:
                rwlock.reader_lock.release()

        if dest_override:
            filename = dest_override
            await rwlock.reader_lock.acquire()
            try:
                rich.print(f"filename = {dest_override}")
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
            "/Users/malcolm/dev/bossjones/sandbox/aioscraper/aioscraper/advanced/asyncio_demo.png",
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
