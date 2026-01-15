import math
import os
from datetime import datetime

from spiders.base_spider import BaseSpider
from spiders.fetchers import ProxyFetcher
from spiders.standard_format import create_standard_offer


class LaborumSpider(BaseSpider):
    BASE_URL = "https://www.laborum.cl/api/avisos/searchV2?pageSize=100&sort=RECIENTES"
    JOB_URL = "https://www.laborum.cl/empleos/"

    HEADERS = {
        "Referer": "https://www.laborum.cl/empleos-busqueda.html?recientes=true",
        "Content-Type": "application/json",
        "X-Site-Id": "BMCL",
    }

    def _setup_fetchers(self):
        self.fetchers["proxy"] = ProxyFetcher(
            proxy_endpoint=os.getenv("PROXY_ENDPOINT", ""),
            proxy_api_key=os.getenv("PROXY_API_KEY", ""),
        )

    async def _get_pages_for_keyword(self, keyword: str) -> list[str]:
        body = self._build_search_body(keyword)

        data = await self.fetch("proxy", self.BASE_URL, method="POST", body=body, headers=self.HEADERS)
        if not data:
            return []

        total_pages = math.ceil(data["total"] / data["size"])
        return [f"{self.BASE_URL}&page={i}" for i in range(total_pages)]

    async def _get_offers_from_page(self, page: str, keyword: str) -> list[dict]:
        body = self._build_search_body(keyword)

        data = await self.fetch("proxy", page, method="POST", body=body, headers=self.HEADERS)
        if not data:
            return []

        return [self._format_offer(job) for job in data["content"]]

    def _format_offer(self, raw_data: dict, **kwargs) -> dict:
        return create_standard_offer(
            url=f"{self.JOB_URL}{raw_data['id']}",
            title=raw_data["titulo"],
            company=raw_data["empresa"],
            location=raw_data["localizacion"],
            modality=raw_data["modalidadTrabajo"],
            created_at=datetime.strptime(raw_data["fechaPublicacion"], "%d-%m-%Y").strftime("%d-%m-%Y"),
            description=raw_data["detalle"],
            applications="n/a",
            spider="Laborum",
        )

    # ============= AUX FUNCTIONS =============

    def _build_search_body(self, keyword: str) -> dict:
        """Build body for search request"""
        return {
            "query": keyword,
            "filtros": self.params.get("filtros", []),
        }
