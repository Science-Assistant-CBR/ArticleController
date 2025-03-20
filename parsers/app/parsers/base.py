import asyncio
import aiohttp
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from common.schemas import News
import chardet
import os


class ProxyManager:
    """Manages proxy rotation and health checking."""

    def __init__(
        self,
        proxies: List[str],
        max_failures: int = 3,
    ):
        """
        Initialize ProxyManager.

        Args:
            proxies: List of proxy URLs (e.g. ['http://proxy1:8080', 'http://proxy2:8080'])
            max_failures: Maximum number of failures before removing a proxy
        """
        self.proxies = {proxy: {"failures": 0, "last_used": 0.0} for proxy in proxies}
        self.max_failures = max_failures
        self.lock = asyncio.Lock()

    async def get_proxy(self) -> Optional[str]:
        """
        Select a healthy proxy, prioritizing least recently used and with fewer failures.

        Returns:
            A proxy URL or None if no proxy is available
        """
        async with self.lock:
            available_proxies = [
                proxy
                for proxy, info in self.proxies.items()
                if info["failures"] < self.max_failures
            ]

            if not available_proxies:
                return None
            return random.choice(available_proxies)

    async def mark_proxy_success(self, proxy: str):
        """Mark a proxy as successful."""
        async with self.lock:
            if proxy in self.proxies:
                self.proxies[proxy]["failures"] = 0
                self.proxies[proxy]["last_used"] = asyncio.get_event_loop().time()

    async def mark_proxy_failure(self, proxy: str):
        """
        Mark a proxy as failed.

        If a proxy fails too many times, it will be effectively removed from rotation.
        """
        async with self.lock:
            if proxy in self.proxies:
                self.proxies[proxy]["failures"] += 1


class BaseParser(ABC):
    """
    Abstract base class for async website parsing with proxy support.

    Provides a robust framework for web scraping with:
    - Proxy rotation
    - Configurable retry mechanism
    - Async request handling
    - Error logging
    """

    def __init__(
        self,
        source_name: str,
        base_url: str,
        proxies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: int = 30,
        news_backend_url: str = "",
    ):
        """
        Initialize the parser.

        Args:
            source_name: Name of the news source
            base_url: Base URL of the website
            proxies: List of proxy URLs
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.source_name = source_name
        self.base_url = base_url
        self.proxy_manager = ProxyManager(proxies or []) if proxies else None
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.news_backend_url = news_backend_url or os.getenv("NEWS_BACKEND_URL")

    async def _make_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Make an async HTTP request with proxy rotation and retry mechanism.

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            params: URL parameters
            data: Request body data

        Returns:
            Response text or None if all attempts fail
        """
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        headers = {**default_headers, **(headers or {})}

        for attempt in range(self.max_retries):
            proxy = None
            try:
                if self.proxy_manager:
                    proxy = await self.proxy_manager.get_proxy()

                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=headers,
                        params=params,
                        data=data,
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ) as response:
                        if response.status == 200:
                            if self.proxy_manager and proxy:
                                await self.proxy_manager.mark_proxy_success(proxy)
                            content_bytes = await response.read()

                            result = chardet.detect(content_bytes)
                            encoding = result["encoding"]

                            content = content_bytes.decode(encoding)
                            return content
                        self.logger.warning(
                            f"Request to {url} failed with status {response.status}"
                        )

                        if self.proxy_manager and proxy:
                            await self.proxy_manager.mark_proxy_failure(proxy)

            except Exception as e:
                self.logger.error(f"Request error (attempt {attempt+1}): {e}")

                if self.proxy_manager and proxy:
                    await self.proxy_manager.mark_proxy_failure(proxy)

                await asyncio.sleep(2**attempt)

        self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    @abstractmethod
    async def fetch_links(self) -> List[Dict]:
        """
        Abstract method to fetch news links from the website.
        """
        raise NotImplementedError("Subclasses must implement link fetching logic")

    @abstractmethod
    async def parse_news_item(self, link: str, **kwargs) -> News:
        """
        Abstract method to parse a single news item from the website.
        """
        raise NotImplementedError("Subclasses must implement parsing logic")

    @abstractmethod
    async def parse(self) -> List[News]:
        """
        Abstract method to parse news from the website.
        """
        raise NotImplementedError("Subclasses must implement parsing logic")

    async def _get_last_parsed_news(self) -> Optional[str]:
        """
        Fetch the ID of the last parsed news from the API.

        Returns:
            Last parsed news ID or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                print(
                    self.news_backend_url + "/news/",
                )
                async with session.get(
                    self.news_backend_url + "/news/",
                    params={
                        "source_name": self.source_name,
                        "limit": 1,
                        "order_by": "publication_datetime",
                    },
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            return data[0]
                        else:
                            return None
                    self.logger.warning(
                        f"Failed to get last news. Status: {response.status}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching last news ID: {e}")
            return None

    async def _submit_news(self, news_item: News) -> bool:
        """
        Submit parsed news item to the API.
        """
        try:
            payload = news_item.dict()
            payload["publication_datetime"] = (
                payload["publication_datetime"].isoformat() + "Z"
            )
            payload["url"] = str(payload["url"])

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.news_backend_url + "/news",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status in [200, 201]:
                        self.logger.info(
                            f"Successfully submitted news: {news_item.url}"
                        )
                        return True
                    else:
                        self.logger.warning(
                            f"Failed to submit news. Status: {response.status}, "
                            f"Response: {await response.text()}"
                        )
                    return False
        except Exception as e:
            self.logger.error(f"Error submitting news: {e}")
            return False


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
