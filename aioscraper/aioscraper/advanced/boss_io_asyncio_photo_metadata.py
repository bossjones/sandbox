# NOTE: For more examples tqdm + aiofile, search https://github.com/search?l=Python&q=aiofile+tqdm&type=Code

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
from icecream import ic
import argparse
from typing import List, Union, Optional, Tuple

# from tqdm.asyncio import tqdm
from urllib.request import urlretrieve


VERIFY_SSL = False

PHOTO_OUTPUT_DIRS = [
    {
        "EXTENSIONS": ["jpg", "jpeg", "mov", "mp4", "m4v", "3gp", "png"],
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

DEFAULT_DIR = "./data/photos"


parser = argparse.ArgumentParser(description="Asyncio io concurrency testing")
parser.add_argument(
    "data",
    metavar="DIR",
    # '?'. One argument will be consumed from the command line if possible, and produced as a single item. If no command-line argument is present, the value from default will be produced. Note that for optional arguments, there is an additional case - the option string is present but not followed by a command-line argument. In this case the value from const will be produced. Some examples to illustrate this:
    nargs="?",
    default=f"{DEFAULT_DIR}",
    help=f"path to dataset (default: {DEFAULT_DIR})",
)
parser.add_argument(
    "-u",
    "--urls",
    metavar="URL",
    nargs="*",
    help="urls to download. "
)



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


# ------------------------------------------------------------
# NOTE: MOVE THIS TO A FILE UTILITIES LIBRARY
# ------------------------------------------------------------
# SOURCE: https://github.com/tgbugs/pyontutils/blob/05dc32b092b015233f4a6cefa6c157577d029a40/ilxutils/tools.py
def is_file(path: str):
    """Check if path contains a file

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    if pathlib.Path(path).is_file():
        return True
    return False


def is_directory(path: str):
    """Check if path contains a dir

    Args:
        path (str): _description_

    Returns:
        _type_: _description_
    """
    if pathlib.Path(path).is_dir():
        return True
    return False


def tilda(obj):
    """wrapper for linux ~/ shell notation

    Args:
        obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    if isinstance(obj, list):
        return [
            str(pathlib.Path(o).expanduser()) if isinstance(o, str) else o for o in obj
        ]
    elif isinstance(obj, str):
        return str(pathlib.Path(obj).expanduser())
    else:
        return obj


def fix_path(path: str):
    """Automatically convert path to fully qualifies file uri.

    Args:
        path (_type_): _description_
    """

    def __fix_path(path):
        if not isinstance(path, str):
            return path
        elif "~" == path[0]:
            tilda_fixed_path = tilda(path)
            if is_file(tilda_fixed_path):
                return tilda_fixed_path
            else:
                exit(path, ": does not exit.")
        elif is_file(pathlib.Path.home() / path):
            return str(pathlib.Path().home() / path)
        elif is_directory(pathlib.Path.home() / path):
            return str(pathlib.Path().home() / path)
        else:
            return path

    if isinstance(path, str):
        return __fix_path(path)
    elif isinstance(path, list):
        return [__fix_path(p) for p in path]
    else:
        return path


def get_folder_size(filepath: str) -> int:
    """Get size of folder in bytes

    Args:
        filepath (str): path to directory

    Returns:
        int: folder size in bytes
    """
    total_size = 0
    for root, dirs, files in os.walk(filepath):
        for img in files:
            total_size += os.path.getsize(os.path.join(root, img))

    return total_size

def determine_destination(fn: str):
    ic(fn)
    extension = os.path.splitext(fn)[1][1:].lower()
    ic(extension)
    for output_filter in PHOTO_OUTPUT_DIRS:
        if extension in output_filter["EXTENSIONS"]:
            ic(output_filter["PATH"])
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

def get_filename_and_dest_from_url(url: str):
    """Get filename from URL

    Args:
        url (str): url string

    Returns:
        _type_: string, string, string
    """
    dest_dir = determine_destination(url)
    fn = url.split('/')[-1]
    dest_path = str(pathlib.Path(dest_dir) / fn)

    return dest_dir, fn, dest_path

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


async def go_partial(loop, urls: List[str]):
    # progress bar
    pbar = tqdm(urls)

    for url in pbar:
        pbar.set_description("Processing -> %s" % url)
        test_dest_dir, test_fn, test_dest_path = get_filename_and_dest_from_url(url)

        # handle_download_file_func = functools.partial(handle_download_file, test_images[0][0], test_images[0][1])
        handle_download_file_func = functools.partial(
            download_url, url, test_dest_path
        )

        # Run in a custom thread pool:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            dest = await loop.run_in_executor(pool, handle_download_file_func)

    return dest

def main():
    args = parser.parse_args()
    print()
    ic(args)
    print()
    return args



if __name__ == "__main__":
    start_time = time.time()

    args = main()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go_partial(loop, args.urls))

    duration = time.time() - start_time
    print(f"Downloaded 1 site in {duration} seconds")


    # # single_file = "/Users/malcolm/dev/bossjones/sandbox/aioscraper/aioscraper/advanced/asyncio_demo.png"
    # dd = determine_destination("https://i.imgur.com/kvSAxmy.png")
    # alt_file_path = find_new_file_name("/Users/malcolm/dev/bossjones/sandbox/aioscraper/aioscraper/advanced/asyncio_demo.png")
    # rich.print(f"dd, alt_file_path = {dd}, {alt_file_path}")

    # test_dest_dir, test_fn, test_dest_path = get_filename_and_dest_from_url("https://i.imgur.com/kvSAxmy.png")
    # ic(test_dest_dir, test_fn, test_dest_path)
