import asyncio
import json
import math
import os
from datetime import datetime
from itertools import chain

import boto3
from aiohttp import ClientSession

## AWS
DYNAMO_CLIENT = boto3.client("dynamodb")
CONFIG_TABLE = boto3.resource("dynamodb").Table(os.getenv("CONFIG_TABLE"))
SEEN_OFFERS_TABLE = boto3.resource("dynamodb").Table(os.getenv("SEEN_OFFERS_TABLE"))

## PROXY
PROXY_ENDPOINT = os.getenv("PROXY_ENDPOINT")

## SPIDER CONFIG
BASE_URL = "https://www.laborum.cl/api/avisos/searchV2?pageSize=100&sort=RECIENTES"
JOB_URL = "https://www.laborum.cl/empleos/"

HEADERS = {
    "Referer": "https://www.laborum.cl/empleos-busqueda.html?recientes=true",
    "Content-Type": "application/json",
    "X-Site-Id": "BMCL"
}


def handler(event, context):
    # TODO: Get spider config from Config Table
    spider_config = CONFIG_TABLE.get_item(Key={"id": "laborum"})["Item"]

    # TODO: Get offers from Laborum
    offers = asyncio.run(get_offers(spider_config["keywords"], spider_config["params"]))

    # TODO: Filter new offers
    new_offers = filter_new_offers(offers)

    # TODO: Return new offers
    return {
        "spider": "laborum",
        "total_offers_found": len(offers),
        "new_offers_found": len(new_offers),
        "new_offers": new_offers,
    }


# GET OFFERS
async def get_offers(keywords: list[str], params: dict):
    async with ClientSession() as session:
        tasks = [_get_pages(session, keyword, params) for keyword in keywords]
        block_pages = await asyncio.gather(*tasks, return_exceptions=False)

        all_tasks = [_get_jobs(session, page, keyword, params) for keyword, pages in zip(keywords, block_pages) for page in pages]
        block_jobs = await asyncio.gather(*all_tasks, return_exceptions=False)

        # Filtrar mientras se aplana
        seen_urls = set()
        offers = []
        for job in chain.from_iterable(block_jobs):
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                offers.append(job)

        return offers


async def _fetch_url(session: ClientSession, url: str, body: dict):
    proxy_body = {
        "url": url,
        "method": "POST",
        "headers": HEADERS,
        "data": json.dumps(body)
    }
    
    try:
        async with session.post(PROXY_ENDPOINT, data=json.dumps(proxy_body)) as response:
            if response.status != 200:
                return None

            data = await response.json()
            return data["data"]
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


async def _get_pages(session: ClientSession, keyword: str, params: dict) -> list[str]:
    try:
        body = {"query": keyword, "filtros": params.get("filtros", [])}

        data = await _fetch_url(session, BASE_URL, body)
        if data is None:
            return []

        total_pages = math.ceil(data["total"] / data["size"])
        return [f"{BASE_URL}&page={i}" for i in range(total_pages)]
    except Exception as e:
        print(f"Error getting pages: {e}")
        return []


async def _get_jobs(session: ClientSession, page: str, keyword: str, params: dict) -> list[dict]:
    try:
        body = {"query": keyword, "filtros": params.get("filtros", [])}

        data = await _fetch_url(session, page, body)
        if data is None:
            return []

        return [_format_job(job) for job in data["content"]]
    except Exception as e:
        print(f"Error getting jobs: {e}")
        return []


def _format_job(data: dict) -> dict:
    return {
        "url": f"{JOB_URL}{data['id']}",
        "title": data["titulo"],
        "company": data["empresa"],
        "location": data["localizacion"],
        "modality": data["modalidadTrabajo"],
        "created_at": datetime.strptime(data["fechaPublicacion"], "%d-%m-%Y").strftime("%d-%m-%Y"),
        "description": data["detalle"],
    }


# FILTER NEW OFFERS
def filter_new_offers(offers: list[dict]) -> list[dict]:
    # Filter offers that are not in seen_offers_table
    BATCH_SIZE = 100
    offer_urls = [o["url"] for o in offers]
    seen_offers = set()

    for i in range(0, len(offers), BATCH_SIZE):
        chunk = offer_urls[i : i + BATCH_SIZE]

        response = DYNAMO_CLIENT.batch_get_item(RequestItems={SEEN_OFFERS_TABLE.name: {"Keys": [{"url": {"S": url}} for url in chunk]}})

        items = response.get("Responses", {}).get(SEEN_OFFERS_TABLE.name, [])
        for item in items:
            seen_offers.add(item["url"]["S"])

    return [o for o in offers if o["url"] not in seen_offers]
