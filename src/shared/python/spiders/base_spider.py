import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from itertools import chain
from typing import Any, Dict, Optional

from aiohttp import ClientSession

from spiders.fetchers import IFetcher


class BaseSpider(ABC):
    """
    Base class for all spiders.
    Use COMPOSITION of fetchers to fetch data from different sources.
    """

    def __init__(self, config: dict):
        self.keywords = config.get("keywords", [])
        self.params = config.get("params", {})
        self.session: Optional[ClientSession] = None

        self.fetchers: Dict[str, IFetcher] = {}
        self._setup_fetchers()

    # ============= FETCHER =============
    @abstractmethod
    def _setup_fetchers(self):
        """
        Every spider configures its fetchers needed.
        Example:
            self.fetchers['json'] = JsonFetcher()
            self.fetchers['html'] = HtmlFetcher()
        """
        pass

    async def fetch(self, fetcher_name: str, url: str, **kwargs) -> Any:
        """
        Fetch data from a given url using a specific fetcher.

        Args:
            fetcher_name (str): Name of the fetcher to use ('json', 'html', 'proxy', etc).
            url (str): URL to fetch.
            **kwargs: Additional arguments to pass to the fetcher.
        """

        if fetcher_name not in self.fetchers:
            raise ValueError(f"Fetcher {fetcher_name} not configured for this spider")

        try:
            if self.session is None:
                raise ValueError("Session not initialized")

            return await self.fetchers[fetcher_name].fetch(self.session, url, **kwargs)
        except Exception as e:
            print(f"Error fetching data from {url} with {fetcher_name}: {e}")
            return None

    # ============= SPIDER =============

    async def run(self) -> list[dict]:
        """Execute the spider and return unique offers"""

        async with ClientSession() as session:
            self.session = session

            # TODO: Get pages for each keyword
            all_pages = await self._get_all_pages()

            # TODO: Get offers from each page
            all_offers = await self._fetch_all_offers(all_pages)

            # TODO: Deduplicate offers
            unique_offers = self._deduplicate_offers(all_offers)

            # TODO: Sort offers by created_at
            return sorted(
                unique_offers,
                key=lambda x: datetime.strptime(x["created_at"], "%d-%m-%Y"),
                reverse=True,
            )

    async def _get_all_pages(self) -> list[tuple[str, list[str]]]:
        """Get URLs of paginated pages for each keyword"""

        tasks = [self._get_pages_for_keyword(keyword) for keyword in self.keywords]
        pages_per_keyword = await self._gather_tasks(tasks)
        return list(zip(self.keywords, pages_per_keyword))

    async def _fetch_all_offers(self, pages_data: list[tuple[str, list[str]]]) -> list[dict]:
        """Fetch all offers from all pages"""

        tasks = [self._get_offers_from_page(page, keyword) for keyword, pages in pages_data for page in pages]
        offers_per_page = await self._gather_tasks(tasks)
        return list(chain.from_iterable(offers_per_page))

    def _deduplicate_offers(self, offers: list[dict]) -> list[dict]:
        """Delete duplicate offers based on url"""
        seen_urls = set()
        unique_offers = []

        for offer in offers:
            if offer["url"] not in seen_urls:
                seen_urls.add(offer["url"])
                unique_offers.append(offer)

        return unique_offers

    async def _gather_tasks(self, tasks: list, return_exceptions: bool = False) -> list:
        """Wrapper around asyncio.gather to handle exceptions"""
        try:
            return await asyncio.gather(*tasks, return_exceptions=return_exceptions)
        except Exception as e:
            print(f"Error gathering tasks: {e}")
            return []

    def _filter_by_date(self, offer_date: datetime, range_days: Optional[int] = None) -> bool:
        """Filter offers by range of days"""
        try:
            if range_days is None:
                range_days = self.params.get("range_days", 1)

            if type(range_days) is not int:
                raise TypeError("range_days must be an integer")

            min_date = datetime.now() - timedelta(days=range_days)
            return offer_date >= min_date
        except Exception as e:
            print(f"Error filtering offers by date: {e}")
            return False

    # TODO: ABSTRACT METHODS (IMPLEMENT IN SUBCLASS)

    @abstractmethod
    async def _get_pages_for_keyword(self, keyword: str) -> list[str]:
        """Return URLs of paginated pages for a given keyword"""
        pass

    @abstractmethod
    async def _get_offers_from_page(self, page: str, keyword: str) -> list[dict]:
        """Return offers from a given page"""
        pass

    @abstractmethod
    def _format_offer(self, raw_data: Any, **kwargs) -> dict:
        """Format offer data into a standard format"""
        pass
