from datetime import datetime
from typing import Optional

from spiders.base_spider import BaseSpider
from spiders.fetchers import JsonFetcher
from spiders.standard_format import create_standard_offer


class TrabajandoSpider(BaseSpider):
    BASE_URL = "https://www.trabajando.cl/api/searchjob"
    OFFER_URL = "https://www.trabajando.cl/api/ofertas/"
    JOB_URL = "https://www.trabajando.cl/trabajo-empleo/"

    HEADERS = {
        "Referer": "https://www.trabajando.cl/trabajo-empleo",
    }

    def _setup_fetchers(self):
        self.fetchers["json"] = JsonFetcher()

    async def _get_pages_for_keyword(self, keyword: str) -> list[str]:
        url = self._build_search_url(keyword)

        data = await self.fetch("json", url, headers=self.HEADERS)
        if not data:
            return []

        total_pages = data.get("cantidadPaginas", 0)
        return [f"{url}&pagina={i+1}" for i in range(total_pages)]

    async def _get_offers_from_page(self, page: str, keyword: str) -> list[dict]:
        data = await self.fetch("json", page, headers=self.HEADERS)
        if not data:
            return []

        # Filter offers by date & get offer urls
        offer_urls = self._extract_recent_offer_urls(data)

        # Fetch details for each offer url
        tasks = [self._fetch_offer_details(url, keyword) for url in offer_urls]
        offers = await self._gather_tasks(tasks)

        return [offer for offer in offers if offer is not None]

    # ============= AUX FUNCTIONS =============

    def _build_search_url(self, keyword: str) -> str:
        """Build the URL for the search endpoint with parameters"""
        orden = self.params.get("orden", "FECHA_PUBLICACION")
        tipo_orden = self.params.get("tipoOrden", "DESC")
        carreras = self.params.get("carreras", [])

        url = f"{self.BASE_URL}?palabraClave={keyword}&orden={orden}&tipoOrden={tipo_orden}"
        if len(carreras) > 0:
            url = f"{url}&{'&'.join(carreras)}"

        return url

    def _extract_recent_offer_urls(self, data: dict) -> list[str]:
        """Extact URLs offers from the search results by range of dates"""
        offers = data.get("ofertas", [])
        range_days = self.params.get("range_days", 1)

        recent_urls = []
        for offer in offers:
            offer_date = datetime.strptime(offer["fechaPublicacion"], "%Y-%m-%d %H:%M")

            if self._filter_by_date(offer_date, range_days):
                recent_urls.append(f"{self.OFFER_URL}{offer['idOferta']}")

        return recent_urls

    async def _fetch_offer_details(self, url: str, keyword: str) -> Optional[dict]:
        """Obtain offer details from the offer url"""
        data = await self.fetch("json", url, headers=self.HEADERS)
        if not data:
            return None

        return self._format_offer(data, keyword=keyword)

    def _format_offer(self, raw_data: dict, **kwargs) -> dict:
        """Fotmat Trabajando offer data to the standard format"""
        keyword = kwargs.get("keyword", "")

        return create_standard_offer(
            url=f"{self.JOB_URL}{keyword.replace(' ', '%20')}/trabajo/{raw_data['idOferta']}",
            title=raw_data["nombreCargo"],
            company=raw_data["nombreEmpresaFantasia"],
            location=raw_data["ubicacion"]["direccion"],
            modality=raw_data["nombreJornada"],
            created_at=datetime.strptime(raw_data["fechaPublicacionFormatoIngles"], "%Y-%m-%d").strftime("%d-%m-%Y"),
            description=f"{raw_data['descripcionOferta']}\n{raw_data['requisitosMinimos']}",
            applications="n/a",
            spider="Trabajando",
        )
