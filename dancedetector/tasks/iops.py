from __future__ import annotations

import glob
import pathlib
import string
import sys

from typing import List, Tuple, Union

import pandas as pd

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

# https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
# python convert string to safe filename
VALID_FILENAME_CHARS = f"-_.() {string.ascii_letters}{string.digits}"
CHAR_LIMIT = 255

JSON_EXTENSIONS = [".json", ".JSON"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".MP4", ".MOV"]
AUDIO_EXTENSIONS = [".mp3", ".MP3"]
GIF_EXTENSIONS = [".gif", ".GIF"]
MKV_EXTENSIONS = [".mkv", ".MKV"]
M3U8_EXTENSIONS = [".m3u8", ".M3U8"]
WEBM_EXTENSIONS = [".webm", ".WEBM"]
IMAGE_EXTENSIONS = [".png", ".jpeg", ".jpg", ".gif", ".PNG", ".JPEG", ".JPG", ".GIF"]
TORCH_MODEL_EXTENSIONS = [".pth", ".PTH"]


def filter_pth(working_dir: List[str]) -> List[str]:
    return [
        f
        for f in working_dir
        if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in TORCH_MODEL_EXTENSIONS
    ]


def filter_json(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in JSON_EXTENSIONS
    ]


def filter_videos(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in VIDEO_EXTENSIONS
    ]


def filter_audio(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in AUDIO_EXTENSIONS
    ]


def filter_gif(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in GIF_EXTENSIONS
    ]


def filter_mkv(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in MKV_EXTENSIONS
    ]


def filter_m3u8(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in M3U8_EXTENSIONS
    ]


def filter_webm(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in WEBM_EXTENSIONS
    ]


def filter_images(working_dir: List[str]) -> List[str]:
    return [
        f for f in working_dir if (pathlib.Path(f"{f}").is_file()) and pathlib.Path(f"{f}").suffix in IMAGE_EXTENSIONS
    ]


def filter_media(working_dir: List[str]) -> List[str]:
    imgs = filter_images(working_dir)
    videos = filter_videos(working_dir)
    return imgs + videos


def get_dataframe_from_csv(filename: str, return_parent_folder_name: bool = False) -> pd.core.frame.DataFrame:
    """Open csv files and return a dataframe from pandas

    Args:
        filename (str): path to file
    """
    src = pathlib.Path(f"{filename}").resolve()
    df = pd.read_csv(f"{src}")

    # import bpdb
    # bpdb.set_trace()

    return (df, f"{src.parent.stem}") if return_parent_folder_name else df


def sort_dataframe(df: pd.core.frame.DataFrame, columns: list = None, ascending: Tuple = ()) -> pd.core.frame.DataFrame:
    """Return dataframe sorted via columns

    Args:
        df (pd.core.frame.DataFrame): existing dataframe
        columns (list, optional): [description]. Defaults to []. Eg. ["Total Followers", "Total Likes", "Total Comments", "ERDay", "ERpost"]
        ascending (Tuple, optional): [description]. Defaults to (). Eg. (False, False, False, False, False)

    Returns:
        pd.core.frame.DataFrame: [description]
    """
    if columns is None:
        columns = []
    df = df.sort_values(columns, ascending=ascending)
    return df


def glob_file_by_extension(working_dir: List[str], extension: str = "*.mp4") -> List[str]:
    print(f"Searching dir -> {working_dir}/{extension}")
    return glob.glob(f"{working_dir}/{extension}")


def print_and_append(dir_listing: list, tree_str: str, silent: bool = False) -> None:
    if not silent:
        print(tree_str)
    dir_listing.append(tree_str)


def tree(directory: Union[pathlib.PosixPath, pathlib.Path], silent: bool = False) -> List[pathlib.PosixPath]:
    """"""
    # from ffmpeg_tools import fileobject

    file_system = []
    _tree = []
    print_and_append(_tree, f"+ {directory}", silent=silent)
    for path in sorted(directory.rglob("*")):
        file_system.append(pathlib.Path(f"{path.resolve()}"))
        depth = len(path.relative_to(directory).parts)
        spacer = "    " * depth
        print_and_append(_tree, f"{spacer}+ {path.name}", silent=silent)
    return file_system


# SOURCE: https://python.hotexamples.com/site/file?hash=0xda3708e60cd1ddb3012abd7dba205f48214aee7366f452e93807887c6a04db42&fullName=spring_cleaning.py&project=pambot/SpringCleaning
def format_size(a_file: str):
    if a_file > 1024**3:
        return "{:.0f} GB".format(a_file / float(2**30))
    elif a_file > 1024**2:
        return "{:.0f} MB".format(a_file / float(2**20))
    elif a_file > 1024:
        return "{:.0f} KB".format(a_file / float(2**10))
    else:
        return "{:.0f} B".format(a_file)


def read_file(filename: str, mode="r") -> List[str]:
    contents_list = []
    with open(filename, mode, encoding="utf8") as f:
        contents_list = f.readlines()
        print(f"[contents_list] -> {contents_list}")
        # contents_list.append(lines)
    return contents_list


def write_file(filename: str, mode="w", contents_list=None) -> List[str]:
    if contents_list is None:
        contents_list = []
    with open(filename, mode) as f:
        for line in contents_list:
            f.write(line)
            f.write("\n")

    return read_file(filename)


# smoke tests
