import bpdb
import asyncio
import aiohttp
import html5lib
import bs4
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from markdownify import markdownify as md

import html5lib
# from urllib import urlopen

import typing

MODEL_TABLE_LOOKUP = {
    "Universal Models": 8,
    "Realistic Photos": 10,
    "Art/Pixel Art": 13,
    "Anime": 16,
    "Manga": 18,
    "Cartoons": 20,
    # document.querySelector("#mw-content-text > div > table:nth-child(22)")
    "Digital Animation": 22,
    "Drawings": 24,
    # document.querySelector("#mw-content-text > div > table:nth-child(26)")
    "General Animation": 26,
    # document.querySelector("#mw-content-text > div > table:nth-child(29)")
    "Traditional Animation": 29,
    # document.querySelector("#mw-content-text > div > table:nth-child(34)")
    "JPEG Artifacts": 34,
    "Aliasing": 36,
    "GIF": 38,
    "DDS (BC1/DXT1, BC3/DXT5 Compression)": 40,
    "Dithering": 42,
    "Blurring": 44,
    "Banding": 46,
    "Halo Removal": 48,
    "Noise": 50,
    # document.querySelector("#mw-content-text > div > table:nth-child(53)")
    "Oversharpening": 53,
    "DeToon": 55,
    "Image De/Colorization": 59,
    "Images": 62,
    "Text": 65,
    "Inpainting": 67,
    "Fabric/Cloth": 69,
    "Alphas": 72,
    "CGI": 74,
    "Luminance/Chroma": 76,
    "Cats": 78,
    "Coins": 80,
    "Faces": 82,
    "Foliage/Ground": 84,
    "Game Screenshots": 87,
    "Normal Map/Bump Map Generation": 90,
    "Video Game Textures": 92,
    "Video Compression": 96,
    "VHS Tapes": 98,
    "Model Collections": 100,
    # document.querySelector("#mw-content-text > div > table:nth-child(113)")
    "CAIN Models": 113,
}

SELECTED_URL = 'https://upscale.wiki/wiki/Model_Database'

async def get_site_content():
    async with aiohttp.ClientSession() as session:
        async with session.get(SELECTED_URL) as resp:
            text = await resp.read()

    return BeautifulSoup(text.decode('utf-8'), 'lxml')

# SOURCE: https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)



def get_all_tables(sites_soup: BeautifulSoup) -> bs4.element.ResultSet:
    """Find all h3 tags on page, and add them to an array, all of these items are the headers for model sections.

    Args:
        sites_soup (BeautifulSoup): BeautifulSoup parser object

    Returns:
        bs4.element.ResultSet: List containing string representations of the h3 names, eg "Universal Models"
    """
    all_tables_via_css = sites_soup.select("#mw-content-text > div > table:nth-child(n)")

    return all_tables_via_css

def get_tables_by_name(sites_soup: BeautifulSoup, table_name: str) -> bs4.element.ResultSet:
    """Get html from table based on section name

    Args:
        sites_soup (BeautifulSoup): BeautifulSoup parser
        table_name (str): Name of section, eg. "CAIN Models"

    Returns:
        bs4.element.ResultSet: result set html
    """
    n = MODEL_TABLE_LOOKUP[table_name]
    js_path = f"#mw-content-text > div > table:nth-child({n})"
    table = sites_soup.select(js_path)

    return table

def get_h3s(sites_soup: BeautifulSoup) -> bs4.element.ResultSet:
    """Find all h3 tags on page, and add them to an array, all of these items are the headers for model sections.

    Args:
        sites_soup (BeautifulSoup): BeautifulSoup parser object

    Returns:
        bs4.element.ResultSet: List containing string representations of the h3 names, eg "Universal Models"
    """
    all_model_sections = sites_soup.find_all("h3")

    return all_model_sections

def get_sections(sites_soup: BeautifulSoup) -> typing.List[str]:
    """Find all h3 tags on page, and add them to an array, all of these items are the headers for model sections.

    Args:
        sites_soup (BeautifulSoup): BeautifulSoup parser object

    Returns:
        typing.List[str]: List containing string representations of the h3 names, eg "Universal Models"
    """
    all_model_sections = get_h3s(sites_soup)

    sections_text = []
    for sec in all_model_sections:
        sections_text.append(sec.text)

    return sections_text

def list_all_model_types():
    model_list = []
    for key in MODEL_TABLE_LOOKUP.keys():
        model_list.append(key)

    return model_list

def fuzzy_match_model_string(lookup: str) -> str:
    """Get the Levenshtein Distance of a string and return the correct value.

    Args:
        lookup (str): substring to look up, eg "anime"

    Returns:
        str: Returns actual value, eg "Anime"
    """
    model_list = list_all_model_types()
    res = process.extractOne(lookup, model_list)
    return res[0]

loop = asyncio.get_event_loop()
sites_soup = loop.run_until_complete(get_site_content())
loop.close()


print(sites_soup)

# section_universal_model = sites_soup.find(id="Universal_Models")

# section = sites_soup.find(text="Art/Pixel Art")
# all_tables = sites_soup.find_all('table')[4]
all_tables = sites_soup.find_all('table')

# all_model_headlines = sites_soup.find_all(class="mw-headline")


model_sections_list = get_sections(sites_soup)
all_th_list = sites_soup.find_all('th')

bpdb.set_trace()

print(all_th_list)

# //*[@id="mw-content-text"]/div/table[3]
# soup.select_one('p:is(.a, .b, .c)')
# document.querySelector("#mw-content-text > div > table:nth-child(8)")
# document.querySelector("#mw-content-text > div > table:nth-child(10)")

# /html/body/div[3]/div[2]/div[4]/div/table[3]
# all_tables = sites_soup.find_all(class_="wikitable sortable jquery-tablesorter")

# table_headers = []
# for tx in sites_soup.find_all('th'):
#     table_headers.append(tx['data-colname'])

# class MyHTMLParser(HTMLParser):
#     def handle_starttag(self, tag, attrs):
#         print("Encountered a start tag:", tag)

#     def handle_endtag(self, tag):
#         print("Encountered an end tag :", tag)

#     def handle_data(self, data):
#         print("Encountered some data  :", data)
