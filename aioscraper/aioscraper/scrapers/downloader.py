# downloader.py

# Python script containing the different algorithms used to download videos from
# various sources


import asyncio
import glob
import logging
import pathlib
import ssl

# ###############################################################################
# Catch exceptions and go into ipython/ipdb
import sys

from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa
import aiofile
import aiofiles
import aiohttp
from arsenic import get_session, stop_session
from arsenic.browsers import Chrome, Firefox
from arsenic.constants import SelectorType, WindowType
from arsenic.services import Chromedriver, Geckodriver
from arsenic.session import Session as ArsenicSession

# SOURCE: https://github.com/Fogapod/KiwiBot/blob/49743118661abecaab86388cb94ff8a99f9011a8/modules/utils/module_screenshot.py
from async_timeout import timeout
import certifi

## Required packages
import rich

# -- To work with web pages
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored
from webdriver_manager.chrome import ChromeDriverManager

from aioscraper.dbx_logger import get_logger  # noqa: E402
from aioscraper.shell import (
    _popen,
    _popen_communicate,
    _popen_stdout,
    _popen_stdout_lock,
    _stat_y_file,
    pquery,
)
from aioscraper.utils import filenames
import uuid
from urllib.parse import urlparse
from slugify import slugify
import uritools

from rich.console import Console

console = Console()

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)
# ssl._create_default_https_context = ssl._create_unverified_context
# ###############################################################################

LOGGER = get_logger(__name__, provider="Downloader", level=logging.DEBUG)

VERIFY_SSL = False

SNAP_TIK = "https://snaptik.app"
FDOWN = "https://fdown.net"
SNAPSAVE = "https://snapsave.app/"

FB_DOWNLOAD_METHOD = {
    "savevideo": {
        "url": "https://savevideo.me/",
        "python_field": '//*[@class="url_input"]',
        "submit_url": '//*[@class="submit"]',
        "source_element": '//*[@id="search_results"]/div[1]/p/a',
    },
    "fdown": {
        "url": "https://fdown.net/index.php",
        "python_field": '//*[@class="form-control input-lg"]',
        "submit_url": '//*[@class="btn btn-primary input-lg"]',
        "source_element": '//*[@id="hdlink"]',
    },
    "snapsave": {
        "url": "https://snapsave.app",
        "python_field": '//*[@class="input input-url"]',
        "submit_url": '//*[@class="button is-download"]',
        "source_element": '//*[@id="download-section"]/section/div/div[1]/div[2]/div/table/tbody/tr[1]/td[3]/a',
    },
    "bigbangram": {
        "url": "",
        "python_field": "",
        "submit_url": "",
        "source_element": "",
    },
    "toolzu": {
        "url": "",
        "python_field": "",
        "submit_url": "",
        "source_element": "",
    },
    "fdownloader": {
        "url": "https://fdownloader.net",
        "python_field": '//*[@id="s_input"]',
        "submit_url": '//*[@class="btn-red"]',
        "source_element": '//*[@id="hdlink"]',
    },
}

# SOURCE: https://stackoverflow.com/questions/35388332/how-to-download-images-with-aiohttp


async def download_and_save(url: str, dest_override=False, base_authority=""):
    # SOURCE: https://github.com/aio-libs/aiohttp/issues/955
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
            rich.print(
                f"uri.authority = {uri.authority}, manually setting url variable"
            )
            url = f"{base_authority}/{url}"
            rich.print(f"url = {url}")

        if dest_override:
            filename = dest_override
            rich.print(f"filename = {dest_override}")
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
                    LOGGER.error(f"A timeout ocurred while downloading '{filename}'")

                return filename, size


## TikTok downloader
async def tiktok_downloader(
    url: str,
    scraper_service: Chromedriver,
    scraper_browser: Chrome,
    dest: str,
    dl_link_num: int = 1,
):

    try:
        LOGGER.debug(f"url = {url}")

        base_authority = f"{SNAP_TIK}"

        session: ArsenicSession

        async with get_session(scraper_service, scraper_browser) as session:
            # 1) Navigating to SNAP_TIK
            print("1) Navigating to SNAP_TIK")

            await session.get(base_authority)

            # breakpoint()

            # 2) Entering the url under "Please insert a valid video URL"
            print('2) Entering the url under "Please insert a valid video URL"')

            python_field = await session.get_element(
                '//*[@id="url"]',
                selector_type=SelectorType.xpath,
            )

            await python_field.send_keys(url)

            # 3) Clicking on the "DOWNLOAD" button
            print('3) Clicking on the "DOWNLOAD" button')

            submit_url = await session.wait_for_element(
                10,
                '//*[@id="hero"]/div/div[2]/form/div/div[4]/button',
                selector_type=SelectorType.xpath,
            )

            await submit_url.click()

            print("4) Getting source link from video tag")

            source_link: str
            # #download > div > div > div.col-12.col-md-4.offset-md-2 > div > a.btn.btn-main.active.mb-2

            source_element = await session.wait_for_element(
                15,
                # f"#snaptik-video > article > div.snaptik-right > div > a:nth-child({dl_link_num})",
                f"#download > div > div > div.col-12.col-md-4.offset-md-2 > div > a:nth-child({dl_link_num})",
                selector_type=SelectorType.css_selector,
            )

            # breakpoint()
            # source_element = await session.wait_for_element(
            #     15,
            #     f"//*[@id='snaptik-video']/article/div[2]/div/a[{dl_link_num}]",
            #     selector_type=SelectorType.xpath,
            # )
            # #snaptik-video > article > div.snaptik-right > div > a:nth-child(2)
            # //*[@id="snaptik-video"]/article/div[2]/div/a[{dl_link_num}]
            # snaptik-video > article > div.snaptik-right > div > a:nth-child(2)
            source_link = await source_element.get_attribute("href")

            # 5) Retrieving video using urllib.request
            # (I.e. downloading the TikTok post)
            print("5) Retrieving video using urllib.request")
            number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(
                glob.glob1(f"{dest}", "*.mp4")
            )
            # # //*[@id="snaptik-video"]/article/div[3]/h3
            # author_name_encoded = await session.get_element(
            #     '//*[@id="snaptik-video"]/article/div[3]/h3',
            #     selector_type=SelectorType.xpath,
            # )
            # await author_name_encoded.get_text()

            # full_description_encoded = await session.get_element(
            #     "/html/body/main/section[2]/div/div/article/div[3]/p[1]/span",
            #     selector_type=SelectorType.xpath,
            # )
            # await full_description_encoded.get_text()

            # breakpoint()

            username = urlparse(f"{url}").path.split("/")[1].replace("@", "")

            safe_username = slugify(username)

            dest_filename = f"{safe_username}_{str(uuid.uuid4())}.mp4"

            rich.print(f"dest_filename = {dest_filename}")

            try:
                filename, size = await download_and_save(
                    source_link,
                    dest_override=dest_filename,
                    base_authority=base_authority,
                )
            except Exception:
                console.print_exception(show_locals=True)

            rich.print(f"filename = {filename}")

            # # 6) Adding the current date in front of the lastly downloaded video name
            # # and writing url to metadata "Comments" part of the downloaded file
            print("6) Adding date and metadata")

            await stop_session(session)
    except Exception:
        try:
            await stop_session(session)
        except:
            pass


async def facebook_downloader(
    url: str, scraper_service: Chromedriver, scraper_browser: Chrome, dest: str
):
    # DEMO: https://fb.watch/e8fQAu19R4/
    # SOURCE: https://github.com/dibasdauliya/youtube-facebook-vids-downloader/blob/f071006d9da3ef5364f587c91b47af27cac3037d/fb_vid.py
    UA = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "https://fdown.net/",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "_ga=GA1.2.2094519438.1640138973; _gid=GA1.2.1078295655.1640138975; _gat_gtag_UA_44090370_1=1",
    }
    DOWNLOAD_PARAMS = FB_DOWNLOAD_METHOD["savevideo"]

    try:
        LOGGER.debug(f"url = {url}")

        session: ArsenicSession

        async with get_session(scraper_service, scraper_browser) as session:
            # 1) Navigating to downloader website
            print(f"1) Navigating to {DOWNLOAD_PARAMS['url']}")

            await session.get(DOWNLOAD_PARAMS["url"])

            await asyncio.sleep(30)

            # 2) Entering the url under "Please insert a valid video URL"
            print('2) Entering the url under "Please insert a valid video URL"')

            python_field = await session.wait_for_element(
                50,
                DOWNLOAD_PARAMS["python_field"],
                selector_type=SelectorType.xpath,
            )

            await python_field.send_keys(url)

            # 3) Clicking on the "DOWNLOAD" button
            print('3) Clicking on the "DOWNLOAD" button')

            # /html/body/div[3]/div/div/div/center/form/div/span/button

            submit_url = await session.wait_for_element(
                50, DOWNLOAD_PARAMS["submit_url"], selector_type=SelectorType.xpath
            )

            await submit_url.click()

            print("4) Getting source link from video tag")

            source_link: str

            source_element_hd = await session.wait_for_element(
                50,
                DOWNLOAD_PARAMS["source_element"],
                selector_type=SelectorType.xpath,
            )
            source_link = await source_element_hd.get_attribute("href")

            # 5) Retrieving video using urllib.request
            # (I.e. downloading the TikTok post)
            print("5) Retrieving video using urllib.request")
            number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(
                glob.glob1(f"{dest}", "*.mp4")
            )

            # author_name_encoded = await session.get_element(
            #     "/html/body/main/section[2]/div/div/article/div[3]/h3",
            #     selector_type=SelectorType.xpath,
            # )
            # await author_name_encoded.get_text()

            # full_description_encoded = await session.get_element(
            #     "/html/body/main/section[2]/div/div/article/div[3]/p[1]/span",
            #     selector_type=SelectorType.xpath,
            # )
            # await full_description_encoded.get_text()

            p = pathlib.Path(source_link)
            dest_override = p.name.split("?")[0]

            # breakpoint()
            # breakpoint()

            filename, size = await download_and_save(source_link, dest_override)

            # # 6) Adding the current date in front of the lastly downloaded video name
            # # and writing url to metadata "Comments" part of the downloaded file
            print("6) Adding date and metadata")

            await stop_session(session)
    except Exception:
        try:
            await stop_session(session)
        except:
            pass


# async def facebook_downloader(
#     url: str, scraper_service, scraper_browser: Chrome, dest: str
# ):
#     # DEMO: https://fb.watch/e8fQAu19R4/
#     try:
#         LOGGER.debug(f"url = {url}")

#         session: ArsenicSession

#         async with get_session(scraper_service, scraper_browser) as session:
#             # 1) Navigating to SNAPSAVE
#             print("1) Navigating to SNAPSAVE")

#             await session.get(f"{SNAPSAVE}")

#             # 2) Entering the url under "Please insert a valid video URL"
#             print('2) Entering the url under "Please insert a valid video URL"')

#             # <input name = "url" class = "input input-url" id = "url" type = "text" placeholder = "Paste video URL Facebook" >
#             # <button class="button is-download" id="send" type="submit">Download</button>

#             python_field = await session.get_element(
#                 '//*[@class="button is-download"]',
#                 selector_type=SelectorType.xpath,
#             )

#             await python_field.send_keys(url)

#             # 3) Clicking on the "DOWNLOAD" button
#             print('3) Clicking on the "DOWNLOAD" button')

#             # /html/body/div[3]/div/div/div/center/form/div/span/button

#             submit_url = await session.wait_for_element(
#                 50, '//*[@class="btn btn-primary input-lg"]', selector_type=SelectorType.xpath
#             )

#             await submit_url.click()

#             print("4) Getting source link from video tag")

#             source_link: str

#             source_element_hd = await session.wait_for_element(
#                 50,
#                 '//*[@id="hdlink"]',
#                 selector_type=SelectorType.xpath,
#             )
#             source_link = await source_element_hd.get_attribute("href")

#             # 5) Retrieving video using urllib.request
#             # (I.e. downloading the TikTok post)
#             print("5) Retrieving video using urllib.request")
#             number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(
#                 glob.glob1(f"{dest}", "*.mp4")
#             )

#             # author_name_encoded = await session.get_element(
#             #     "/html/body/main/section[2]/div/div/article/div[3]/h3",
#             #     selector_type=SelectorType.xpath,
#             # )
#             # await author_name_encoded.get_text()

#             # full_description_encoded = await session.get_element(
#             #     "/html/body/main/section[2]/div/div/article/div[3]/p[1]/span",
#             #     selector_type=SelectorType.xpath,
#             # )
#             # await full_description_encoded.get_text()

#             p = pathlib.Path(source_link)
#             dest_override = p.name.split("?")[0]

#             # breakpoint()
#             breakpoint()

#             filename, size = await download_and_save(source_link, dest_override)

#             # # 6) Adding the current date in front of the lastly downloaded video name
#             # # and writing url to metadata "Comments" part of the downloaded file
#             print("6) Adding date and metadata")

#             await stop_session(session)
#     except Exception:
#         try:
#             await stop_session(session)
#         except:
#             pass
