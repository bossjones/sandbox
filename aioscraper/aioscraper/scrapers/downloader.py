# downloader.py

# Python script containing the different algorithms used to download videos from
# various sources


import glob
import logging
## Required packages
import os
import re
import shutil
import rich
from time import sleep
import urllib.request
from urllib.request import Request, urlopen
import ssl
import certifi
import asyncio
import aiofile



# -- To work with web pages
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored
from webdriver_manager.chrome import ChromeDriverManager
from arsenic import get_session, stop_session
from arsenic.browsers import Chrome, Firefox
from arsenic.services import Chromedriver, Geckodriver
from arsenic.session import Session as ArsenicSession
# SOURCE: https://github.com/Fogapod/KiwiBot/blob/49743118661abecaab86388cb94ff8a99f9011a8/modules/utils/module_screenshot.py
from async_timeout import timeout
from arsenic.constants import SelectorType, WindowType
import pathlib


from aioscraper.dbx_logger import get_logger  # noqa: E402
from aioscraper.utils import filenames

from aioscraper.shell import (
    _popen,
    _popen_communicate,
    _popen_stdout,
    _popen_stdout_lock,
    _stat_y_file,
    pquery,
)

import aiohttp
import aiofiles

# ###############################################################################
# Catch exceptions and go into ipython/ipdb
import sys

from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)
# ssl._create_default_https_context = ssl._create_unverified_context
# ###############################################################################

LOGGER = get_logger(__name__, provider="Downloader", level=logging.DEBUG)

VERIFY_SSL = False

SNAP_TIK = "https://snaptik.app"
# SSLCONTEXT = ssl.create_default_context(cafile=certifi.where())
# print(f"SSLCONTEXT -> {SSLCONTEXT}")
# rich.inspect(SSLCONTEXT, methods=True)
# session = aiohhtp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
# SOURCE: https://stackoverflow.com/questions/35388332/how-to-download-images-with-aiohttp
async def download_and_save(url: str):
    # SOURCE: https://github.com/aio-libs/aiohttp/issues/955
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    # ERROR: ValueError: verify_ssl, ssl_context, fingerprint and ssl parameters are mutually exclusive
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=sslcontext if VERIFY_SSL else None)) as http:
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=sslcontext,ssl=False)) as http:
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as http:
        # url = "http://host/file.img"
        # <class 'aiohttp.client.ClientSession'>
        url_file_api = pathlib.Path(url)
        filename = f"{url_file_api.name}"
        # breakpoint()
        async with http.request("GET", url, ssl=sslcontext if VERIFY_SSL else None) as resp:
            # <class 'aiohttp.client_reqrep.ClientResponse'
        # async with http.request("GET", url, ssl=False) as resp:
            if resp.status == 200:
                # SOURCE: https://stackoverflow.com/questions/72006813/python-asyncio-file-write-after-request-getfile-not-working
                size = 0
                try:
                    async with aiofile.async_open(filename, "wb+") as afp:
                        async for chunk in resp.content.iter_chunked(1024 * 512):   # 500 KB
                            await afp.write(chunk)
                            size += len(chunk)
                except asyncio.TimeoutError:
                    LOGGER.error(f"A timeout ocurred while downloading '{filename}'")

                # reader = await resp.multipart()

                # # /!\ Don't forget to validate your inputs /!\

                # # reader.next() will `yield` the fields of your form

                # field = await reader.next()
                # assert field.name == 'name'
                # name = await field.read(decode=True)

                # field = await reader.next()
                # assert field.name == 'mp4'
                # filename = field.filename
                # # You cannot rely on Content-Length if transfer is chunked.
                # size = 0
                # with open(os.path.join(f"./{filename}"), 'wb') as f:
                #     while True:
                #         chunk = await field.read_chunk()  # 8192 bytes by default.
                #         if not chunk:
                #             break
                #         size += len(chunk)
                #         f.write(chunk)

                # # # return web.Response(text='{} sized of {} successfully stored'
                # # #                          ''.format(filename, size))

                # # f = await aiofiles.open(filename, mode='wb')
                # # await f.write(await resp.read())
                # # await f.close()
                return filename, size

## TikTok downloader
async def tiktok_downloader(
    url: str, scraper_service, scraper_browser: Chrome, dest: str, dl_link_num: int = 1
):

    try:
        LOGGER.debug(f"url = {url}")
        # LOGGER.debug(f"driver = {driver}")
        # LOGGER.debug(f"type(driver) = {type(driver)}")

        session: ArsenicSession

        async with get_session(scraper_service, scraper_browser) as session:
            #     # go to example.com
            #     await session.get(f"{uri}")
            #     # wait up to 5 seconds to get the h1 element from the page
            #     h1 = await session.wait_for_element(5, "h1")
            #     # print the text of the h1 element
            #     print(await h1.get_text())

            # 1) Navigating to SNAP_TIK
            print("1) Navigating to SNAP_TIK")

            await session.get(f"{SNAP_TIK}")
            # driver.get(SNAP_TIK)

            # 2) Entering the url under "Please insert a valid video URL"
            print('2) Entering the url under "Please insert a valid video URL"')

            python_field = await session.get_element("/html/body/main/section[1]/div[3]/div/div/form/div[2]/input", selector_type=SelectorType.xpath)
            # python_field = await session.get_element("html > body > main > section:nth-of-type(1) > div:nth-of-type(3) > div > div > form > div:nth-of-type(2) > input")
            # python_field = driver.find_element_by_xpath(
            #     "/html/body/main/section[1]/div[3]/div/div/form/div[2]/input"
            # )
            await python_field.send_keys(url)

            # 3) Clicking on the "DOWNLOAD" button
            print('3) Clicking on the "DOWNLOAD" button')
            # python_button = driver.find_element_by_xpath('//*[@id="icondl"]')
            # python_button.click()
            # INFO: EC = expected_conditions
            # INFO: BC = Set of supported locator strategies.

            submit_url = await session.wait_for_element(10, '//*[@id="submiturl"]', selector_type=SelectorType.xpath)
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, '//*[@id="submiturl"]'))
            # ).click()
            await submit_url.click()
            # NOTE: Orig is below
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, '//*[@id="icondl"]'))
            # ).click()

            # //*[@id="snaptik-video"]/article/div[2]/div/a[1]
            # 4) Getting source link from video tag
            # css=#download-block .abutton:nth-child(1) > .span-icon > span
            print("4) Getting source link from video tag")
            # source_link = (
            #     WebDriverWait(driver, 10)
            #     .until(
            #         EC.presence_of_element_located(
            #             (By.CSS_SELECTOR, "#download-block .abutton:nth-child(1) > .span-icon > span")
            #         )
            #     )
            #     .get_attribute("href")
            # )
            source_link: str

            source_element = await session.wait_for_element(10, f"#download-block > div > a:nth-child({dl_link_num})", selector_type=SelectorType.css_selector)
            source_link = await source_element.get_attribute("href")

            # 5) Retrieving video using urllib.request
            # (I.e. downloading the TikTok post)
            print("5) Retrieving video using urllib.request")
            number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(
                glob.glob1(f"{dest}", "*.mp4")
            )

            # req = await session.request(url=source_link)
            # req = Request(source_link, headers={"User-Agent": "XYZ/3.0"})
            # response = urlopen(req, timeout=20).read()

            # author_name_encoded = driver.find_element_by_xpath(
            #     "/html/body/main/section[2]/div/div/article/div[3]/h3"
            # )
            # author_name = author_name_encoded.text
            author_name_encoded = await session.get_element("/html/body/main/section[2]/div/div/article/div[3]/h3", selector_type=SelectorType.xpath)
            author_name = await author_name_encoded.get_text()


            # full_description_encoded = driver.find_element_by_xpath(
            #     "/html/body/main/section[2]/div/div/article/div[3]/p[1]/span"
            # )
            # full_description = full_description_encoded.text

            full_description_encoded = await session.get_element("/html/body/main/section[2]/div/div/article/div[3]/p[1]/span", selector_type=SelectorType.xpath)
            full_description = await full_description_encoded.get_text()

            # breakpoint()

            filename, size = await download_and_save(source_link)


            # LOGGER.debug(f"full_description = {full_description}")
            # # Bounding the size of "full_description"
            # if len(full_description) > 50:
            #     full_description_short = full_description[0:50]
            # else:
            #     full_description_short = full_description
            # video_name = author_name + " - " + full_description_short

            # sanitized_file_name = filenames.format_filename(video_name)
            # LOGGER.debug(f"sanitized_file_name = {sanitized_file_name}")

            # file_name = f"{dest}" + "/" + sanitized_file_name + ".mp4"
            # LOGGER.debug(f"file_name = {file_name}")

            # f = open(file_name, "wb")
            # f.write(response)
            # f.close()

            # # 6) Adding the current date in front of the lastly downloaded video name
            # # and writing url to metadata "Comments" part of the downloaded file
            print("6) Adding date and metadata")
            # add_date_and_metadata(
            #     f"{dest}",
            #     url,
            #     number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
            #     number_of_videos_to_download=1,
            # )
            await stop_session(session)
    except Exception as e:
        try:
            await stop_session(session)
        except:
            pass
