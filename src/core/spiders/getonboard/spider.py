from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup, ResultSet, Tag
from spiders.base_spider import BaseSpider
from spiders.fetchers import HtmlFetcher
from spiders.standard_format import create_standard_offer


class GetOnBoardSpider(BaseSpider):
    BASE_URL = "https://www.getonbrd.com/empleos"

    def _setup_fetchers(self):
        self.fetchers["html"] = HtmlFetcher()

    async def _get_pages_for_keyword(self, keyword: str) -> list[str]:
        # only one page for each keyword
        return [f"{self.BASE_URL}/{keyword}"]

    async def _get_offers_from_page(self, page: str, keyword: str) -> list[dict]:
        html = await self.fetch("html", page)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        offer_items = soup.select("a.gb-results-list__item")
        if not offer_items:
            return []

        offer_urls = self._extract_recent_offer_urls(offer_items)

        tasks = [self._fetch_offer_details(url, keyword) for url in offer_urls]
        offers = await self._gather_tasks(tasks)

        return [offer for offer in offers if offer is not None]

    def _format_offer(self, raw_data: BeautifulSoup, **kwargs) -> dict:
        url: str = kwargs.get("url", "")
        keyword: str = kwargs.get("keyword", "")

        location, modality = self._parse_location_modality(raw_data)
        created_at = self._parse_created_date(raw_data)
        applications = self._parse_applications(raw_data)

        title = raw_data.select_one("div.gb-container.gb-container--medium.gb-cover-layout h1.gb-landing-cover__title span:first-child")
        # div.gb-container.gb-container--medium.gb-cover-layout h3 a.tooltipster strong
        company = raw_data.select_one("div.gb-landing-cover h3 a.tooltipster strong")
        description = raw_data.select_one("div#job-body")

        return create_standard_offer(
            url=f"{self.BASE_URL}/{keyword}/{url.split('/')[-1]}",
            title=title.text.strip() if title else "n/a",
            company=company.text.strip() if company else "n/a",
            location=location,
            modality=modality,
            created_at=created_at,
            description=description.text.strip() if description else "n/a",
            applications=applications,
            spider="GetOnBoard",
        )

    # ============= AUX FUNCTIONS =============

    def _extract_recent_offer_urls(self, offer_items: ResultSet[Tag]) -> list[str]:
        range_days = self.params.get("range_days", 1)
        offer_urls = []

        for offer in offer_items:
            offer_date = self._parse_offer_date(offer)

            if offer_date and self._filter_by_date(offer_date, range_days):
                offer_urls.append(offer.get("href"))

        return offer_urls

    def _parse_offer_date(self, offer: Tag) -> Optional[datetime]:
        date_elem = offer.select_one("div.opacity-half.size0")
        if not date_elem:
            return None

        date_str = date_elem.text.strip().lower()
        date_parts = date_str.split(" ")

        months_map = {
            "ene": 1,
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "abr": 4,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "ago": 8,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dic": 12,
            "dec": 12,
        }

        try:
            month = months_map.get(date_parts[0], 1)
            day = int(date_parts[1])
            year = datetime.now().year

            return datetime(year, month, day)
        except Exception as e:
            print(f"Error parsing offer date: {e}")
            return None

    async def _fetch_offer_details(self, url: str, keyword: str) -> Optional[dict]:
        html = await self.fetch("html", url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        range_days = self.params.get("range_days", 1)
        offer_formatted = self._format_offer(soup, url=url, keyword=keyword)
        return offer_formatted if self._filter_by_date(datetime.strptime(offer_formatted["created_at"], "%d-%m-%Y"), range_days=range_days) else None

    def _parse_location_modality(self, raw_data: BeautifulSoup) -> tuple[str, str]:
        # div.gb-container.gb-container--medium.gb-cover-layout span.location
        location_elem = raw_data.select_one("div.gb-cover-layout span.location")
        if not location_elem:
            return "n/a", "n/a"

        parts = location_elem.text.strip().split("\n")

        if parts[0] == "Remote":
            modality = parts[0]
            location = parts[-1].replace("(", "").replace(")", "") if len(parts) > 1 else "n/a"
        else:
            location = parts[0]
            modality = parts[-1].replace("(", "").replace(")", "") if len(parts) > 1 else "n/a"

        return location, modality

    def _parse_created_date(self, raw_data: BeautifulSoup) -> str:
        # div.gb-container.gb-container--medium.gb-cover-layout time
        date_elem = raw_data.select_one("div.gb-cover-layout time")
        if not date_elem:
            return "n/a"

        date_str = date_elem.text.strip().lower()
        date_parts = date_str.split(" ")

        months_map = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        try:
            if len(date_parts) == 3:
                month = months_map.get(date_parts[0], 1)
                day = int(date_parts[1].replace(",", ""))
                year = int(date_parts[2])
            else:
                month = months_map.get(date_parts[2], 1)
                day = int(date_parts[0])
                year = int(date_parts[4])

            return datetime(year, month, day).strftime("%d-%m-%Y")
        except Exception as e:
            print(f"Error parsing created date: {e}")
            return "n/a"

    def _parse_applications(self, raw_data: BeautifulSoup) -> str:
        # div.gb-container.gb-container--medium.gb-cover-layout div.size0.mt1
        app_elem = raw_data.select_one("div.gb-cover-layout div.size0.mt1")
        if not app_elem:
            return "n/a"

        parts = app_elem.text.strip().split("\n")
        return parts[0] if parts else "n/a"
