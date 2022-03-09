from markdownify import MarkdownConverter
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
# from markdownify import markdownify as md
from lxml import html
import pytablewriter
from pytablewriter import TableWriterFactory
from pytablewriter.style import Cell, Style
from pytablewriter.writer import AbstractTableWriter
import sys
import rich
import snoop
from IPython.core import ultratb
from IPython.core.debugger import set_trace  # noqa

import html5lib
# from urllib import urlopen

import typing

# sys.excepthook = ultratb.FormattedTB(
#     mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
# )

VALID_TABLE_HEADERS = ["Model Name", "author", "Scale", "Purpose (short)", "sample"]

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
    fuzzy_table_name = fuzzy_match_model_string(table_name)
    n = MODEL_TABLE_LOOKUP[fuzzy_table_name]
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

# @snoop
def get_result_set_sublist(records: bs4.element.ResultSet) -> typing.List[str]:
    # VALID_TABLE_HEADERS = ["Model Name", "author", "Scale", "Purpose (short)", "sample"]
    rows = []
    for count, row in enumerate(records):
        # bpdb.set_trace()
        row_parser = row.find_all("td")
        # print(f" count = {count}, row = {row}")
        rows.append([md_from_beautifulsoup(row_parser[0]), row_parser[1].get_text(strip=True), row_parser[2].get_text(
            strip=True), row_parser[5].get_text(strip=True), md_from_beautifulsoup(row_parser[9])])

    # print(rows)
    return rows

# SOURCE: https://stackoverflow.com/questions/35755153/extract-only-specific-rows-and-columns-from-a-table-td-in-beautifulsoup-pytho
def get_html_table_headers(res_table: bs4.element.ResultSet):
    """Parse a result set and return only the values we care about

    Args:
        res_table (bs4.element.ResultSet): _description_
    """
    headers = [c.get_text(strip=True) for c in res_table[0].find("tr").find_all("th")]

    # only include the ones we care about
    final_headers = [f"{h}" for h in headers if h in VALID_TABLE_HEADERS]

    # get all table records and nuke the headers only
    all_table_records = res_table[0].find_all('tr')
    del all_table_records[0]

    table_rows_list = get_result_set_sublist(all_table_records)
    # # now we should only the models and their descriptions
    # for count, row in enumerate(all_table_records):
    #     print(f" count = {count}, row = {row}")

    # print(all_table_records)

    # data = [[cell.get_text(strip=True) for cell in row.find_all('td')] for row in res_table.find_all("tr", class_=True)]
    # data = [[cell.get_text(strip=True) for cell in row.find_all('td')] for row in anime_table.find_all("tr", class_=True)]
    # for h in headers:
    #     if h in VALID_TABLE_HEADERS:
    #         final_headers.append[h]

    # headers = [c.get_text(strip=True) for c in anime_table[0].find("tr").find_all("th")]
    # res_table[0].find("tr").find_all("th")[0].tex
    # headers = [c.get_text() for c in res_table[0].find("tr").find_all("th")[0]]
    return final_headers, table_rows_list

# Create shorthand method for conversion


def md_from_beautifulsoup(sites_soup: BeautifulSoup, **options):
    """Converting BeautifulSoup objects"""
    return MarkdownConverter(**options).convert_soup(sites_soup)


def generate_markdown_table(table_name, final_table_headers, table_table_rows_list, margin):
    # SOURCE: https://github.com/thombashi/pytest-md-report/blob/aeff356c0b0831ad594cf5af45fca9e08dd1f92d/pytest_md_report/plugin.py
    writer = TableWriterFactory.create_from_format_name("md")
    writer.table_name = fuzzy_match_model_string(table_name)
    writer.headers = final_table_headers
    writer.margin = margin
    writer.value_matrix = table_table_rows_list
    # writer = MarkdownTableWriter(
    #     table_name="example_table",
    #     headers=["int", "float", "str", "bool", "mix", "time"],
    #     value_matrix=[
    #         [0,   0.1,      "hoge", True,   0,      "2017-01-01 03:04:05+0900"],
    #         [2,   "-2.23",  "foo",  False,  None,   "2017-12-23 45:01:23+0900"],
    #         [3,   0,        "bar",  "true",  "inf", "2017-03-03 33:44:55+0900"],
    #         [-10, -9.9,     "",     "FALSE", "nan", "2017-01-01 00:00:00+0900"],
    #     ],
    #     margin=1  # add a whitespace for both sides of each cell
    # )
    # writer.write_table()
    return writer.dumps()

def generate_html_table(table_name, final_table_headers, table_table_rows_list, margin):
    # SOURCE: https://github.com/thombashi/pytest-md-report/blob/aeff356c0b0831ad594cf5af45fca9e08dd1f92d/pytest_md_report/plugin.py
    writer = TableWriterFactory.create_from_format_name("html")
    writer.table_name = fuzzy_match_model_string(table_name)
    writer.headers = final_table_headers
    writer.margin = margin
    writer.value_matrix = table_table_rows_list
    # writer = MarkdownTableWriter(
    #     table_name="example_table",
    #     headers=["int", "float", "str", "bool", "mix", "time"],
    #     value_matrix=[
    #         [0,   0.1,      "hoge", True,   0,      "2017-01-01 03:04:05+0900"],
    #         [2,   "-2.23",  "foo",  False,  None,   "2017-12-23 45:01:23+0900"],
    #         [3,   0,        "bar",  "true",  "inf", "2017-03-03 33:44:55+0900"],
    #         [-10, -9.9,     "",     "FALSE", "nan", "2017-01-01 00:00:00+0900"],
    #     ],
    #     margin=1  # add a whitespace for both sides of each cell
    # )
    # writer.write_table()
    return writer.dumps()


def chunk_md_output(table_table_rows_list):
    pass

loop = asyncio.get_event_loop()
sites_soup = loop.run_until_complete(get_site_content())
loop.close()


# print(sites_soup)

# section_universal_model = sites_soup.find(id="Universal_Models")

# section = sites_soup.find(text="Art/Pixel Art")
# all_tables = sites_soup.find_all('table')[4]
all_tables = sites_soup.find_all('table')

# all_model_headlines = sites_soup.find_all(class="mw-headline")

fuzzy_search_str = "anime"


model_sections_list = get_sections(sites_soup)
all_th_list = sites_soup.find_all('th')
anime_table = get_tables_by_name(sites_soup, fuzzy_search_str)
anime_markdown = md_from_beautifulsoup(anime_table[0])
final_table_headers, table_table_rows_list = get_html_table_headers(anime_table)
markdown_str_final = generate_markdown_table(fuzzy_search_str, final_table_headers, table_table_rows_list, 1)
html_str_final = generate_html_table(fuzzy_search_str, final_table_headers, table_table_rows_list, 1)

# bpdb.set_trace()

print(markdown_str_final)

with open('toc.md', 'w') as f:
    f.write(markdown_str_final)

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
