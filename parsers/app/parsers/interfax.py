import asyncio
import locale
import os
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from dateutil.parser import parse

from app.parsers.base import BaseParser
from common.schemas import News

# locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


class InterfaxParser(BaseParser):
    def __init__(
        self,
        base_url: str = "https://www.interfax.ru/rss.asp",
        proxies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: int = 30,
        LAST_NEWS_API: str = "https://news-api.pshakhmin.ru/api/v1",
    ):
        super().__init__(
            "Интерфакс",
            base_url,
            proxies,
            max_retries,
            timeout,
            os.getenv("NEWS_BACKEND_URL") or LAST_NEWS_API,
        )

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        date_str = date_str.split("+")[0].strip()
        return parse(date_str)

    async def fetch_links(self) -> List[Dict]:
        response = await super()._make_request(self.base_url)

        if not response:
            print("Ошибка при запросе страницы")
            return []

        soup = BeautifulSoup(response, features="xml")
        news_data = []

        for news_item in soup.find_all("item"):
            link = news_item.find("link").text
            title = news_item.find("title").text
            description = news_item.find("description").text
            category = news_item.find("category").text
            date = self._parse_date(news_item.find("pubDate").text)
            news_data.append(
                {
                    "link": link,
                    "title": title,
                    "description": description,
                    "category": category,
                    "datetime": date,
                }
            )
        return news_data

    async def parse_news_item(self, link: str, **kwargs) -> News:
        response = await super()._make_request(link)

        if not response:
            print("Ошибка при запросе страницы:", link)
            return []

        soup = BeautifulSoup(response, "html.parser")
        article = soup.find("article")
        news_content = ""
        for p in article.find_all("p"):
            news_content += p.text + "\n"

        news_item = News(
            publication_datetime=kwargs["datetime"],
            url=link,
            text=news_content,
            source_name="Интерфакс",
            title=kwargs["title"],
            news_id=link.split("/")[-1],
            tags=None,
            persons=None,
            topic=kwargs["category"],
        )
        return news_item

    async def parse(self) -> List[News]:
        last_news = await super()._get_last_parsed_news()
        if not last_news:
            last_news = datetime.fromtimestamp(0)
        else:
            last_news = last_news.get("publication_datetime", "")
            last_news = datetime.fromisoformat(last_news)

        links = await self.fetch_links()

        if last_news:
            links = list(filter(lambda x: x["datetime"] > last_news, links))

        news_items = await asyncio.gather(
            *[self.parse_news_item(**link) for link in links]
        )

        await asyncio.gather(*[self._submit_news(news) for news in news_items])
        return news_items


if __name__ == "__main__":
    print("started")
    parser = InterfaxParser()
    asyncio.run(parser.parse())
