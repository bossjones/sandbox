# SOURCE: https://github.com/tiangolo/typer-cli#user-content-awesome-cli
import typer
import asyncio
# from aioscraper.tweetpik import TweetpikHTTPClient, HTTPException, async_download_file
import sys
import rich
import snoop
import signal
import multiprocessing as mp
# from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import traceback
import json
from arsenic import get_session
from arsenic.browsers import Firefox, Chrome
from arsenic.services import Geckodriver, Chromedriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver
from aioscraper.utils import utils


from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa
import logging
from aioscraper.dbx_logger import (  # noqa: E402
    generate_tree,
    get_lm_from_tree,
    get_logger,
    intercept_all_loggers,
)

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)

# https://github.com/whoisandy/k2s3/blob/6e0d24abb837add1d7fcc20619533c603ea76b22/k2s3/cli.py#L114

LOGGER = get_logger(__name__, provider="CLI", level=logging.DEBUG)
intercept_all_loggers()

# Enable connection pool logging
# SOURCE: https://docs.sqlalchemy.org/en/13/core/engines.html#dbengine-logging
SELENIUM_LOGGER = logging.getLogger("selenium")
SELENIUM_LOGGER.setLevel(logging.DEBUG)

WEBDRIVER_MANAGER_LOGGER = logging.getLogger("webdriver_manager")
WEBDRIVER_MANAGER_LOGGER.setLevel(logging.DEBUG)

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


async def example_get_page(uri: str = "https://snaptik.app/en"):
    options, chromeOptions = utils.default_chrome_options()
    # Runs geckodriver and starts a firefox session
    # LOGGER.info(f"binary_location = {driver_options.binary_location}")
    # driver_manager = utils.get_chrome_web_driver(options)
    driver_path = utils.get_latest_chrome_driver()
    scaper_service = Chromedriver(binary=f"{driver_path}")
    print("chromeOptions chromeOptions chromeOptions chromeOptions chromeOptions chromeOptions")
    print(chromeOptions)
    # source: https://github.com/cobypress/TrailblazerCommunityWebScraper/blob/59113f05a9c1d977b2bd059d9b9b31c9b0e04946/SalesforceWebScraper/cogs/scraper.py
    scraper_browser = Chrome(**{"goog:chromeOptions": {"args": ['--ignore-certificate-errors', '--incognito', "--ignore-certificate-errors"]}})
    async with get_session(scaper_service, scraper_browser) as session:
        # go to example.com
        await session.get(f"{uri}")
        # wait up to 5 seconds to get the h1 element from the page
        h1 = await session.wait_for_element(5, 'h1')
        # print the text of the h1 element
        print(await h1.get_text())

async def aio_get_latest_webdriver():
    driver = utils.get_latest_webdriver()


@app.command()
def create(username: str):
    """
    Create a new user with USERNAME.
    """
    typer.echo(f"Creating user: {username}")

# # @snoop
# async def _aimages(tiktok_uri: str):
#     client = TweetpikHTTPClient()
#     res = await client.aimages(tiktok_uri)
#     return res

# async def _write_files_to_disk(data: dict) -> None:
#     await async_download_file(data)

# @app.command()
# def images(tiktok_uri: str):
#     """
#     Creating screenshot with tiktok_uri.
#     """
#     typer.echo(f"Screenshotting tweet: {tiktok_uri}")
#     # client = TweetpikHTTPClient()
#     # res = asyncio.run(client.aimages(tiktok_uri))
#     # # res = client.images(tiktok_uri)
#     # rich.print_json(res)
#     # try:
#     res = asyncio.run(_aimages(tiktok_uri))
#     rich.print(res)
#     data = json.loads(res)
#     asyncio.run(_write_files_to_disk(data))

@app.command()
def example(tiktok_uri: str):
    """
    Creating screenshot with tiktok_uri.
    """
    typer.echo(f"Running example: {tiktok_uri}")
    res = asyncio.run(example_get_page(uri=tiktok_uri))
    rich.print(res)

@app.command()
def delete(
    username: str,
    force: bool = typer.Option(
        ...,
        prompt="Are you sure you want to delete the user?",
        help="Force deletion without confirmation.",
    ),
):
    """
    Delete a user with USERNAME.

    If --force is not used, will ask for confirmation.
    """
    if force:
        typer.echo(f"Deleting user: {username}")
    else:
        typer.echo("Operation cancelled")


@app.command()
def delete_all(
    force: bool = typer.Option(
        ...,
        prompt="Are you sure you want to delete ALL users?",
        help="Force deletion without confirmation.",
    )
):
    """
    Delete ALL users in the database.

    If --force is not used, will ask for confirmation.
    """
    if force:
        typer.echo("Deleting all users")
    else:
        typer.echo("Operation cancelled")


@app.command()
def init():
    """
    Initialize the users database.
    """
    typer.echo("Initializing user database")


if __name__ == "__main__":
    app()
