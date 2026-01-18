from datetime import datetime, timedelta
from typing import Optional

from bs4 import BeautifulSoup
from spiders.base_spider import BaseSpider
from spiders.fetchers import HtmlFetcher, JsonFetcher
from spiders.standard_format import create_standard_offer


class BNESpider(BaseSpider):
    BASE_URL = "https://www.bne.cl/data/ofertas/buscarListas"
    JOB_URL = "https://www.bne.cl/oferta/"

    def _setup_fetchers(self):
        self.fetchers["json"] = JsonFetcher()
        self.fetchers["html"] = HtmlFetcher()

    async def _get_pages_for_keyword(self, keyword: str) -> list[str]:
        url = self._build_search_url(keyword)

        data = await self.fetch("json", url)
        if not data:
            return []

        total_pages = data.get("paginaOfertas", {}).get("numPaginasTotal", 1)
        return [f"{url}&numPaginaRecuperar={i+1}" for i in range(total_pages)]

    async def _get_offers_from_page(self, page: str, keyword: str) -> list[dict]:
        data = await self.fetch("json", page)
        if not data:
            return []

        offer_urls = self._extract_offer_urls(data)

        # Fetch details for each offer url
        tasks = [self._fetch_offer_details(url) for url in offer_urls]
        offers = await self._gather_tasks(tasks)

        return [offer for offer in offers if offer is not None]

    def _format_offer(self, raw_data: BeautifulSoup, **kwargs) -> dict:
        url: str = kwargs.get("url", "")

        title = raw_data.select_one("span#nombreOferta span")

        panels = raw_data.select("article.panel")

        company_block = panels[0].select(
            "div.panel-body div.row:first-child div.panel-body div.row:first-child div.col-sm-6 div.row:first-child div.col-sm-12 span"
        )
        company = company_block[1]

        location = panels[1].select_one("div.panel-body div.row:last-child div.col-sm-3:first-child span")
        date_str = panels[1].select_one("div.panel-body div.row:last-child span:nth-child(3)")
        description = panels[1].select_one("div.panel-body div.row:first-child div.col-sm-12 p")

        return create_standard_offer(
            url=url,
            title=title.text.strip() if title else "n/a",
            company=company.text.strip() if company else "n/a",
            location=location.text.strip() if location else "n/a",
            modality="n/a",
            created_at=datetime.strptime(date_str.text.strip(), "%d/%m/%Y").strftime("%d-%m-%Y") if date_str else datetime.now().strftime("%d-%m-%Y"),
            description=description.text.strip() if description else "n/a",
            applications="n/a",
            spider="BNE",
        )

    # ============= AUX FUNCTIONS =============

    def _build_search_url(self, keyword: str) -> str:
        mostrar = self.params.get("mostrar", "empleo")
        ocupaciones = self.params.get("idOcupacion", [])
        num_Pagina = self.params.get("numResultadosPorPagina", "20")
        clasificar = self.params.get("clasificarYPaginar", "true")

        range_days = self.params.get("range_days", 1)
        filter_date = datetime.now() - timedelta(days=range_days)

        url = f"{self.BASE_URL}?mostrar={mostrar}&fechaIniPublicacion={filter_date.strftime("%d/%m/%Y")}&numResultadosPorPagina={num_Pagina}&clasificarYPaginar={clasificar}&textoLibre={keyword}"
        if len(ocupaciones) > 0:
            url = f"{url}&idOcupacion={'&idOcupacion='.join(map(str, ocupaciones))}"

        return url

    def _extract_offer_urls(self, data: dict) -> list[str]:
        offers = data.get("paginaOfertas", {}).get("resultados", [])

        urls = []
        for offer in offers:
            urls.append(f"{self.JOB_URL}{offer['codigo']}")

        return urls

    async def _fetch_offer_details(self, url: str) -> Optional[dict]:
        html = await self.fetch("html", url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        return self._format_offer(soup, url=url)
