# utils.py

# Python script containing the helper and webdriver functions

import datetime
import email.header
import email.utils
import glob
import itertools
import logging
## Required packages
import os
import pathlib
import re
from time import sleep
from urllib.request import Request, urlopen

from typing import Union

from PIL import ImageGrab
from selenium import webdriver
from termcolor import colored
from webdriver_manager.chrome import ChromeDriverManager

from aioscraper.dbx_logger import (  # noqa: E402
    generate_tree,
    get_lm_from_tree,
    get_logger,
    intercept_all_loggers,
)

# Importing the constants defined in config.py
# from ffmpeg_tools.scraper.utils.config import DOWNLOAD_DIRECTORY, GOOGLE, TEAM_STAMA

TEAM_STAMA = "https://www.teamstama.com/"
GOOGLE = "https://www.google.com/"

HERE = os.path.abspath(os.path.dirname(__file__))
_DIR = pathlib.Path(HERE).resolve()

DOWNLOAD_DIRECTORY = f"{_DIR.parent}/downloads"  # getting the path leading to the current working directory


LOGGER = get_logger(__name__, provider="Utils", level=logging.DEBUG)

# needed for sanitizing filenames in restricted mode
ACCENT_CHARS = dict(
    zip(
        "ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ",
        itertools.chain(
            "AAAAAA",
            ["AE"],
            "CEEEEIIIIDNOOOOOOO",
            ["OE"],
            "UUUUUY",
            ["TH", "ss"],
            "aaaaaa",
            ["ae"],
            "ceeeeiiiionooooooo",
            ["oe"],
            "uuuuuy",
            ["th"],
            "y",
        ),
    )
)


def timeconvert(timestr: Union[str, None]):
    """Convert RFC 2822 defined time string into system timestamp"""
    timestamp = None
    timetuple = email.utils.parsedate_tz(timestr)
    if timetuple is not None:
        timestamp = email.utils.mktime_tz(timetuple)
    return timestamp


def sanitize_filename(s, restricted=True, is_id=False) -> str:
    """Sanitizes a string so it could be used as part of a filename.
    If restricted is set, use a stricter subset of allowed characters.
    Set is_id if this is not an arbitrary string, but an ID that should be kept
    if possible.
    """

    def replace_insane(char):
        if restricted and char in ACCENT_CHARS:
            return ACCENT_CHARS[char]
        if char == "?" or ord(char) < 32 or ord(char) == 127:
            return ""
        elif char == '"':
            return "" if restricted else "'"
        elif char == ":":
            return "_-" if restricted else " -"
        elif char in "\\/|*<>":
            return "_"
        if restricted and (char in "!&'()[]{}$;`^,#" or char.isspace()):
            return "_"
        if restricted and ord(char) > 127:
            return "_"
        return char

    # Handle timestamps
    s = re.sub(r"[0-9]+(?::[0-9]+)+", lambda m: m.group(0).replace(":", "_"), s)
    result = "".join(map(replace_insane, s))
    if not is_id:
        while "__" in result:
            result = result.replace("__", "_")
        result = result.strip("_")
        # Common case of "Foreign band name - English song title"
        if restricted and result.startswith("-_"):
            result = result[2:]
        if result.startswith("-"):
            result = "_" + result[len("-") :]
        result = result.lstrip(".")
        if not result:
            result = "_"
    return result


## Removing empty lines from text file
def remove_empty_lines(file_path):
    with open(file_path) as in_file, open(file_path, "r+") as out_file:
        out_file.writelines(line for line in in_file if line.strip())
        out_file.truncate()


## Sorting the URLs by platform
def sort_urls(file_path):

    # Reading the text file
    with open(file_path, "r+") as file:
        lines = file.readlines()
        file.close()

        # Initializing the different lists
        youtu_list = []
        instagram_list = []
        twitter_list = []
        facebook_list = []
        facebook_story_list = []
        fb_list = []
        linkedin_list = []
        tiktok_list = []
        twitch_list = []
        vimeo_list = []
        dailymotion_list = []
        zwanzig_minuten_list = []
        pinterest_list = []
        others_list = []

        # Going through the lines and populating each list
        for i in range(len(lines)):
            if "youtu" in lines[i]:
                youtu_list.append(lines[i])
                continue
            elif "instagram" in lines[i]:
                instagram_list.append(lines[i])
                continue
            elif "twitter" in lines[i]:
                twitter_list.append(lines[i])
                continue
            elif "facebook" in lines[i]:
                if "story" in lines[i]:
                    facebook_story_list.append(lines[i])
                else:
                    facebook_list.append(lines[i])
                continue
            elif "fb" in lines[i]:
                fb_list.append(lines[i])
                continue
            elif "linkedin" in lines[i]:
                linkedin_list.append(lines[i])
                continue
            elif "tiktok" in lines[i]:
                tiktok_list.append(lines[i])
                continue
            elif "twitch" in lines[i]:
                twitch_list.append(lines[i])
                continue
            elif "vimeo" in lines[i]:
                vimeo_list.append(lines[i])
                continue
            elif "dailymotion" in lines[i]:
                dailymotion_list.append(lines[i])
                continue
            elif "www.20min.ch/video/" in lines[i]:
                zwanzig_minuten_list.append(lines[i])
                continue
            elif "https://pin" in lines[i]:
                pinterest_list.append(lines[i])
            else:
                others_list.append(lines[i])

        # Composing the final list of sorted URLs
        lines_sorted = (
            facebook_story_list
            + fb_list
            + facebook_list
            + tiktok_list
            + instagram_list
            + youtu_list
            + linkedin_list
            + dailymotion_list
            + twitter_list
            + twitch_list
            + vimeo_list
            + zwanzig_minuten_list
            + pinterest_list
            + others_list
        )

        # Adding a '\n' at the end of each line
        for i in range(len(lines_sorted)):
            if lines_sorted[i][-1] != "\n":
                lines_sorted[i] = lines_sorted[i] + "\n"

        # Removing the '\n' of the last element of the list
        lines_sorted[-1] = lines_sorted[-1].replace("\n", "")

    # Writing the sorted URLs in the text file
    with open(file_path, "w") as file:
        file.writelines(lines_sorted)
        file.close()


# ## Writing in log text file
# def write_in_log_text_file(log_message):
#     logAllFilesTXT = open(str(DOWNLOAD_DIRECTORY) + "/" + "log.txt", "a")
#     logAllFilesTXT.write(log_message)
#     logAllFilesTXT.close()


## Checking internet connection
def connected_to_internet():
    """
    Function returning 'True' if the computer is connected to internet and
    'False otherwise'
    Cf.: https://stackoverflow.com/questions/3764291/checking-network-connection
    """
    try:
        test_link = "http://google.com"
        req = Request(test_link, headers={"User-Agent": "XYZ/3.0"})
        urlopen(req, timeout=20).read()
        return True
    except Exception:
        return False


## Logging error
def log_error(e, number_of_unrecognized_urls, url, textFileAsInput):
    # Printing the error to the console
    print(
        "\n\n⚠️",
        colored("URL issue n°{0}".format(number_of_unrecognized_urls).strip(), "red")
        + ":\n"
        + url
        + "\nError message: {0}\n".format(e),
    )
    # if textFileAsInput:
    #     # Adding this URL to the log text file
    #     write_in_log_text_file(
    #         "\n\n⚠️ URL issue n°{0}:\n".format(number_of_unrecognized_urls)
    #         + url
    #         + "\nError message: {0}".format(e)
    #     )


## Retrieving URL from line of text file
def retrieve_url(lines, number_of_lines, iter):
    """
    Function to get rid of the "\n" at the end of all lines except the last one
    :param lines: list containing all the URLs present in the "urls.txt" text file
    :param number_of_lines: length of the "lines" list
    :param iter: iteration at which we are currently situated in the elements of the "lines" list
    :return: url string
    """
    if iter < (number_of_lines - 1):
        url = lines[iter]
        url = url[:-1]
    else:
        url = lines[-1]

    return url


## Getting path of lastly downloaded video
def get_last_vid_path(DOWNLOAD_DIRECTORY):
    list_of_files_in_DOWNLOAD_DIRECTORY = glob.glob(DOWNLOAD_DIRECTORY + "/*")
    video_path = max(list_of_files_in_DOWNLOAD_DIRECTORY, key=os.path.getctime)

    return video_path


## Adding the current date in front of video name and writing comment in metadata "Comments" part of file
def add_date_and_metadata(
    DOWNLOAD_DIRECTORY,
    url,
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
    number_of_videos_to_download,
):

    # Computing the current date
    date = str(datetime.datetime.now()).split(" ")[0]

    # Waiting until (all) the video(s) of the current post is (are) downloaded
    current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY = len(
        glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4")
    )
    time_slept = 0
    while (
        current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY
        != number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY
        + number_of_videos_to_download
    ):
        # Re-checking the current total number of ".mp4" files in DOWNLOAD_DIRECTORY
        current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY = len(
            glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4")
        )
        print(" video still downloading...")
        sleep(1)
        time_slept += 1
        if (
            time_slept > 3600
        ):  # If after 1 hour, we still don't have the expected number of video(s)
            print(
                colored("Error!", "red"),
                "Time exceeded while trying to download current video ({0}).".format(
                    url
                ),
            )
            break

    if (
        current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY
        == number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY
        + number_of_videos_to_download
    ):
        # Getting (all) the new video file(s) of the current post
        video_files = glob.glob(DOWNLOAD_DIRECTORY + "/*.mp4")
        video_files.sort(key=os.path.getctime, reverse=True)
        new_video_files = video_files[0:number_of_videos_to_download]

        for i in range(number_of_videos_to_download):
            # Renaming the video(s)
            current_video_name = new_video_files[i]
            new_video_name = (
                DOWNLOAD_DIRECTORY
                + "/"
                + date
                + "_"
                + new_video_files[i].replace(DOWNLOAD_DIRECTORY + "/", "")
            )
            os.rename(current_video_name, new_video_name)
            # Writing comment in metadata "Comments" part of file
            # write_metadata_comment(new_video_name, url)


def setup_chrome_options():
    options = get_web_driver_options()
    # LOGGER.debug(f"options = {options}")
    # LOGGER.debug(f"options.binary_location = {options.binary_location}")
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    return options


def default_chrome_options():
    options = setup_chrome_options()
    chromeOptions = {"args": options.arguments}
    # chromeOptions = {"goog:chromeOptions": {"args": options.arguments}}

    # LOGGER.debug(f"chromeOptions = {chromeOptions}")
    return options, chromeOptions


## Webdriver setting functions
def get_latest_webdriver():
    options, chromeOptions = default_chrome_options()
    LOGGER.debug(f"options = {options}")
    LOGGER.debug(f"options.binary_location = {options.binary_location}")
    # set_automation_as_head_less(options) # uncommenting this line makes the web driver run in the background (/!\ dvid.py is NOT conceived to work with the web driver running in the background, it has to be visible during the whole process! So please, leave this line commented!)
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    driver = get_chrome_web_driver(options)
    LOGGER.debug(f"driver = {driver}")
    # Getting the resolution of the screen
    img = ImageGrab.grab()
    screen_width = img.size[0]
    screen_height = img.size[1]

    LOGGER.debug(f"screen_width = {screen_width}")
    LOGGER.debug(f"screen_height = {screen_height}")

    # Setting the size of the web driver window to half the size of the screen
    window_width = int(screen_width / 4)
    window_height = screen_height
    LOGGER.debug(f"window_width = {window_width}")
    LOGGER.debug(f"window_height = {window_height}")

    driver.set_window_size(
        window_width, window_height
    )  # (240, 160) # driver.minimize_window() # driver.maximize_window()
    # Positioning the web driver window on the right-hand side of the screen
    driver.set_window_position(window_width, 0)
    # Navigating to GOOGLE
    driver.get(TEAM_STAMA)

    return driver


def get_latest_chrome_driver():
    return ChromeDriverManager().install()


def get_chrome_web_driver(options):
    # Using automatically the correct chromedriver by using the webdrive-manager (cf.: https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)
    driver_path = get_latest_chrome_driver()
    return webdriver.Chrome(driver_path, chrome_options=options)


def get_web_driver_options():
    return webdriver.ChromeOptions()


def set_ignore_certificate_error(options):
    options.add_argument("--ignore-certificate-errors")


def set_browser_as_incognito(options):
    options.add_argument("--incognito")


# A headless browser is a web-browser without a graphical user interface.
# This program will behave just like a browser but will not show any GUI.
# Running WebDriver Automated Tests in headless mode provides advantages in
# terms of speed of execution of tests
# (With this enabled, everything will run in the BACKGROUND)
def set_automation_as_head_less(options):
    options.add_argument("--headless")
