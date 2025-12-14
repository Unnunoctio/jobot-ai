import asyncio
from datetime import datetime, timedelta
from itertools import chain

from aiohttp import ClientSession
from bs4 import BeautifulSoup

## SPIDER CONFIG
BASE_URL = "https://www.getonbrd.com/empleos"


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})

    keywords = spider_config.get("keywords", [])
    params = spider_config.get("params", {})

    # TODO: Get offers
    offers = asyncio.run(get_offers(keywords, params))

    # TODO: Return new offers
    return offers


async def get_offers(keywords: list[str], params: dict):
    async with ClientSession() as session:
        tasks = [_get_job_urls(session, keyword, params) for keyword in keywords]
        block_urls = await asyncio.gather(*tasks, return_exceptions=False)

        unique_urls = set(chain.from_iterable(block_urls))
        all_tasks = [_get_job(session, url) for url in list(unique_urls)]
        jobs = await asyncio.gather(*all_tasks, return_exceptions=False)

        return [job for job in jobs if job is not None]


async def _fetch_url(session: ClientSession, url: str):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            return await response.text()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


async def _get_job_urls(session: ClientSession, keyword: str, params: dict) -> list[str]:
    url = f"{BASE_URL}/{keyword}"

    html_text = await _fetch_url(session, url)
    if html_text is None:
        return []

    soup = BeautifulSoup(html_text, "html.parser")

    job_items = soup.select("a.gb-results-list__item")
    if job_items is None or len(job_items) == 0:
        return []

    min_date = datetime.now() - timedelta(days=int(params["range_days"]))

    job_urls = []
    for job in job_items:
        job_date_string = job.select_one("div.gb-results-list__secondary div.opacity-half.size0").text.strip()
        # date format: short-month day
        date_split = job_date_string.lower().split(" ")
        months_es = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        months_en = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

        month = months_es.index(date_split[0]) + 1 if date_split[0] in months_es else months_en.index(date_split[0]) + 1
        day = int(date_split[1])
        year = datetime.now().year

        job_date = datetime(year, month, day)
        if job_date >= min_date:
            job_urls.append(job.get("href"))

    return job_urls


async def _get_job(session: ClientSession, url: str) -> dict:
    html_text = await _fetch_url(session, url)
    if html_text is None:
        return None

    soup = BeautifulSoup(html_text, "html.parser")

    full_location_raw = soup.select_one("div.gb-container.gb-container--medium.gb-cover-layout span.location").text.strip()
    full_location_split = full_location_raw.split("\n")

    location = "n/a"
    modality = "n/a"
    if full_location_split[0] == "Remote":
        modality = full_location_split[0]
        if len(full_location_split) > 1:
            location = full_location_split[len(full_location_split) - 1].replace("(", "").replace(")", "")
    else:
        location = full_location_split[0]
        if len(full_location_split) > 1:
            modality = full_location_split[len(full_location_split) - 1].replace("(", "").replace(")", "")

    # date es format: dd de month de yyyy
    # date en format: month dd, yyyy
    date_string = soup.select_one("div.gb-container.gb-container--medium.gb-cover-layout time").text.strip()
    date_split = date_string.lower().split(" ")
    months_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    months_en = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

    if len(date_split) == 3:
        month = months_en.index(date_split[0]) + 1
        day = int(date_split[1].replace(",", ""))
        year = int(date_split[2])
    else:
        month = months_es.index(date_split[2]) + 1
        day = int(date_split[0])
        year = int(date_split[3])

    applications_raw = soup.select_one("div.gb-container.gb-container--medium.gb-cover-layout div.size0.mt1").text.strip()
    applications_split = applications_raw.split("\n")

    return {
        "url": url,
        "title": soup.select_one("div.gb-container.gb-container--medium.gb-cover-layout h1.gb-landing-cover__title span:first-child").text.strip(),
        "company": soup.select_one("div.gb-container.gb-container--medium.gb-cover-layout h3 a.tooltipster strong").text.strip(),
        "location": location,
        "modality": modality,
        "created_at": datetime(year, month, day).strftime("%d-%m-%Y"),
        "applications": applications_split[0],
        "description": soup.select_one("div#job-body").text.strip(),
    }
