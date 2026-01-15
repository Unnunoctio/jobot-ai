import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from aiohttp import ClientSession


class IFetcher(ABC):
    """Interface for all fetchers"""

    @abstractmethod
    async def fetch(self, session: ClientSession, url: str, **kwargs) -> Any:
        """Fetch data from a given url"""
        pass


class JsonFetcher(IFetcher):
    """Fetcher for APIs JSON"""

    async def fetch(self, session: ClientSession, url: str, headers: dict = {}, **kwargs) -> Optional[dict]:
        """Fetch JSON from a given url."""
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None
                return await response.json()
        except Exception as e:
            print(f"Error fetching JSON from {url}: {e}")
            return None


class HtmlFetcher(IFetcher):
    """Fetcher for static HTML"""

    async def fetch(self, session: ClientSession, url: str, headers: dict = {}, **kwargs) -> Optional[str]:
        """Fetch static HTML from a given url."""
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None
                return await response.text()
        except Exception as e:
            print(f"Error fetching HTML from {url}: {e}")
            return None


class ProxyFetcher(IFetcher):
    """Fetcher with proxy support for bypassing cloudflare challenge"""

    def __init__(self, proxy_endpoint: str, proxy_api_key: str):
        self.proxy_endpoint = proxy_endpoint
        self.proxy_api_key = proxy_api_key

    async def fetch(
        self, session: ClientSession, url: str, method: str = "GET", headers: dict = {}, body: Optional[dict] = None, **kwargs
    ) -> Optional[dict]:
        """Fetch data from a given url with proxy support."""
        proxy_body = {
            "url": url,
            "method": method,
            "headers": headers,
        }

        if body:
            proxy_body["body"] = json.dumps(body)

        proxy_headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.proxy_api_key,
        }

        try:
            async with session.post(self.proxy_endpoint, data=json.dumps(proxy_body), headers=proxy_headers) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                return data["data"]
        except Exception as e:
            print(f"Error fetching data from {url} with proxy: {e}")
            return None
