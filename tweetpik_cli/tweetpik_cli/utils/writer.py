"""Write to disk asynchronously."""
# https://github.com/hackersandslackers/asyncio-tutorial/blob/0f4c99776b61ca3eafd850c43202bc7c52349552/asyncio_tutorial/part_II_aiohttp_aiofiles/writer.py
import aiofiles
import logging
from tweetpik_cli.dbx_logger import (  # noqa: E402
    get_logger,
)

LOGGER = get_logger(__name__, provider="Writer", level=logging.DEBUG)

async def write_file(fname: str, body: bytes, filetype: str, directory: str):
    """
    Write contents of fetched URL to new file in local directory.
    :param str fname: URL which was fetched.
    :param bytes body: Source HTML of a single fetched URL.
    :param str filetype: File extension to save fetched data as.
    :param str directory: Local directory to save exports to.
    """
    try:
        filename = f"{directory}/{fname}.{filetype}"
        LOGGER.info(f"writing file -> {filename} ....")
        async with aiofiles.open(filename, mode="wb+") as f:
            await f.write(body)
            await f.close()
    except Exception as e:
        LOGGER.error(f"Unexpected error while writing from `{fname}`: {e}")
    return filename
