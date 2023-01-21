import time
import aiohttp
from aiohttp import ClientSession
import asyncio


async def get_html_by_movie_id_new(movie_id, session):
    url = f"https://www.imdb.com/title/{movie_id}/fullcredits"
    response = await session.request(method="GET", url=url)
    html = await response.text()
    return html


async def scrape_all_titles(movies_list):
    async with ClientSession() as session:
        tasks = []
        for movie_id in movies_list:
            tasks.append(get_html_by_movie_id_new(movie_id, session))
        result = await asyncio.gather(*tasks)
    return result

async def main(movies_list):
    s = time.perf_counter()
    result = await scrape_all_titles(movies_list)
    elapsed = time.perf_counter() - s
    print(f"Executed in {elapsed:0.2f} seconds.")


if __name__ == "__main__":

    movies_list = [
        "tt2935510",
        "tt7131622",
        "tt5463162",
        "tt4758646",
        "tt3640424",
        "tt6024606",
        "tt1596363",
        "tt3707106",
        "tt2713180",
        "tt2193215",
        "tt2024544",
        "tt0816711",
        "tt1764234",
        "tt1402488",
        "tt1210166",
        "tt0478304",
        "tt1001526",
        "tt0361748",
        "tt0421715",
        "tt0887883",
        "tt0443680",
        "tt0496806",
        "tt0449467",
        "tt0356910",
        "tt0349903",
        "tt0332452",
        "tt0165982",
        "tt0270288",
        "tt0240772",
        "tt0266987",
        "tt0236493",
        "tt0208092",
        "tt0137523",
        "tt0120601",
        "tt0119643",
        "tt0120102",
        "tt0118972",
        "tt0117665",
        "tt0114746",
        "tt0114369",
        "tt0110322",
        "tt0110148",
        "tt0109783",
        "tt0108399",
        "tt0107302",
        "tt0105265",
        "tt0104009",
        "tt0104567",
        "tt0103074",
        "tt0101268",
        "tt0097478",
        "tt0097136",
        "tt0118930",
        "tt0093407",
        "tt0093638",
        "tt0093640",
        "tt0093231",
    ]

    asyncio.run(main(movies_list))
