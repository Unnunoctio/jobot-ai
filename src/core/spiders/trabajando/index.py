import asyncio
from datetime import datetime, timedelta
from itertools import chain

from aiohttp import ClientSession

## SPIDER CONFIG
BASE_URL = "https://www.trabajando.cl/api/searchjob"
OFFER_URL = "https://www.trabajando.cl/api/ofertas/"
JOB_URL = "https://www.trabajando.cl/trabajo-empleo/"

HEADERS = {"Referer": "https://www.trabajando.cl/trabajo-empleo"}


def handler(event, context):
    # TODO: Get spider config
    spider_config = event.get("config", {})

    keywords = spider_config.get("keywords", [])
    params = spider_config.get("params", {})

    # TODO: Get offers from Trabajando
    offers = asyncio.run(get_offers(keywords, params))

    # TODO: Return offers
    return offers


# GET OFFERS
async def get_offers(keywords: list[str], params: dict):
    async with ClientSession() as session:
        all_jobs = []
        unique_job_titles = set()
        for keyword in keywords:
            pages = await _get_pages(session, keyword, params)

            offers_tasks = [_get_offers(session, page, params) for page in pages]
            block_offers = await asyncio.gather(*offers_tasks, return_exceptions=False)
            unique_offer_urls = set(chain.from_iterable(block_offers))

            job_tasks = [_get_job(session, offer_url, keyword) for offer_url in unique_offer_urls]
            jobs = await asyncio.gather(*job_tasks, return_exceptions=False)
            for j in jobs:
                if j["title"] not in unique_job_titles:
                    all_jobs.append(j)
                    unique_job_titles.add(j["title"])

        return all_jobs


async def _fetch_url(session: ClientSession, url: str):
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                return None

            data = await response.json()
            return data
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


async def _get_pages(session: ClientSession, keyword: str, params: dict) -> list[str]:
    url = f"{BASE_URL}?palabraClave={keyword}&orden={params.get('orden', 'FECHA_PUBLICACION')}&tipoOrden={params.get('tipoOrden', 'DESC')}"
    carreras = params.get("carreras", [])
    if len(carreras) > 0:
        url = f"{url}&{'&'.join(carreras)}"

    data = await _fetch_url(session, url)
    if data is None:
        return []

    total_pages = data["cantidadPaginas"]
    return [f"{url}&pagina={i + 1}" for i in range(total_pages)]


async def _get_offers(session: ClientSession, page: str, params: dict) -> list[str]:
    data = await _fetch_url(session, page)
    if data is None:
        return []

    min_date = datetime.now() - timedelta(days=int(params.get("range_days", 1)))

    offers = []
    for o in data["ofertas"]:
        offer_date = datetime.strptime(o["fechaPublicacion"], "%Y-%m-%d %H:%M")
        if offer_date >= min_date:
            offers.append(f"{OFFER_URL}{o['idOferta']}")

    return offers


async def _get_job(session: ClientSession, url: str, keyword: str) -> dict:
    data = await _fetch_url(session, url)
    if data is None:
        return None

    return {
        "url": f"{JOB_URL}{keyword.replace(' ', '%20')}/trabajo/{data['idOferta']}",
        "title": data["nombreCargo"],
        "company": data["nombreEmpresaFantasia"],
        "location": data["ubicacion"]["direccion"],
        "modality": data["nombreJornada"],
        "created_at": datetime.strptime(data["fechaPublicacionFormatoIngles"], "%Y-%m-%d").strftime("%d-%m-%Y"),
        "applications": "n/a",
        "description": f"{data['descripcionOferta']}\n{data['requisitosMinimos']}",
    }
