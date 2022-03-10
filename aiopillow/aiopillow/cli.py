# SOURCE: https://github.com/tiangolo/typer-cli#user-content-awesome-cli
import typer
import asyncio
# from aiopillow.tweetpik import TweetpikHTTPClient, HTTPException, async_download_file
import sys
import rich
import snoop
import signal
import multiprocessing as mp
# from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import traceback
import json

from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa
import logging
from aiopillow.dbx_logger import (  # noqa: E402
    generate_tree,
    get_lm_from_tree,
    get_logger,
    intercept_all_loggers,
)

from aiopillow import aiotesseract, aiopil

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)

# https://github.com/whoisandy/k2s3/blob/6e0d24abb837add1d7fcc20619533c603ea76b22/k2s3/cli.py#L114

LOGGER = get_logger(__name__, provider="CLI", level=logging.DEBUG)
intercept_all_loggers()

app = typer.Typer(help="Awesome CLI user manager.")
signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT)

async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        LOGGER.info(f"Received exit signal {signal.name}...")

    LOGGER.info("Nacking outstanding messages")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    LOGGER.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)

    LOGGER.info(f"Flushing metrics")
    loop.stop()

@app.command()
def create(username: str):
    """
    Create a new user with USERNAME.
    """
    typer.echo(f"Creating user: {username}")

# # @snoop
# async def _aimages(tweet_url: str):
#     client = TweetpikHTTPClient()
#     res = await client.aimages(tweet_url)
#     return res

# async def _write_files_to_disk(data: dict) -> None:
#     await async_download_file(data)

@app.command()
def classify(media: str):
    """
    Creating screenshot with media.
    """
    typer.echo(f"Screenshotting tweet: {media}")
    # TODO: Enable this, and chain it up
    # res = asyncio.run(_aimages(tweet_url))
    # rich.print(res)
    # data = json.loads(res)
    # asyncio.run(_write_files_to_disk(data))


if __name__ == "__main__":
    app()
