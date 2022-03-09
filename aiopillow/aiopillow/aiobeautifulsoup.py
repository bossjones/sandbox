import asyncio
import aiohttp
import html5lib
from bs4 import BeautifulSoup

SELECTED_URL = 'https://upscale.wiki/wiki/Model_Database'

async def get_site_content():
    async with aiohttp.ClientSession() as session:
        async with session.get(SELECTED_URL) as resp:
            text = await resp.read()

    return BeautifulSoup(text.decode('utf-8'), 'html5lib')

loop = asyncio.get_event_loop()
sites_soup = loop.run_until_complete(get_site_content())
print(sites_soup)
loop.close()
