import asyncio
from datetime import datetime
from itertools import chain

from aiohttp import ClientSession

## SPIDER CONFIG
BASE_URL = "https://www.bne.cl/data/ofertas/buscarListas"
OFFER_URL = "https://www.bne.cl/oferta/"


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})

    keywords = spider_config.get("keywords", [])
    params = spider_config.get("params", {})

    # TODO: Get offers from bne

    # TODO: Return offers
    pass


# GET OFFERS
async def get_offers(keywords: list[str], params: dict):
    async with ClientSession() as session:
        all_offers = []
        unique_job_urls = set()
        for keyword in keywords:
            pages = await _get_pages(session, keyword, params)

async def _fetch_url(session: ClientSession, url: str):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            data = await response.json()
            return data
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None