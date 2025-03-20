import asyncio
import locale
import os
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser
from common.schemas import News

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


class PresidentParser(BaseParser):
    def __init__(
        self,
        base_url: str = "http://www.kremlin.ru/events/president/news",
        proxies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: int = 30,
        LAST_NEWS_API: str = "https://news-api.pshakhmin.ru/api/v1",
    ):
        super().__init__(
            "Президент России",
            base_url,
            proxies,
            max_retries,
            timeout,
            os.getenv("NEWS_BACKEND_URL") or LAST_NEWS_API,
        )

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        clean_date_str = date_str.replace(" года", "")
        date_obj = datetime.strptime(clean_date_str, "%d %B %Y, %H:%M")
        return date_obj

    async def fetch_links(self) -> List[Dict]:
        response = await super()._make_request(self.base_url)

        if not response:
            print("Ошибка при запросе страницы")
            return []

        soup = BeautifulSoup(response, "html.parser")
        news_data = []

        for news_item in soup.select(".hentry"):
            link = (
                news_item.select_one("h3.hentry__title").select_one("a").get("href", "")
            )
            date = self._parse_date(news_item.select_one(".published").contents[0])
            news_data.append({"link": f"http://www.kremlin.ru{link}", "datetime": date})
        return news_data

    async def parse_news_item(self, link: str) -> News:
        response = await super()._make_request(link)

        if not response:
            print("Ошибка при запросе страницы:", link)
            return []

        soup = BeautifulSoup(response, "html.parser")

        news_title = soup.select_one("h1.entry-title").contents[0].replace("\xa0", " ")
        news_content = ""
        news_faces = []
        news_tags = []

        content_div = soup.select_one("div.entry-content")
        for p in content_div.find_all("p"):
            news_content += p.text.replace("\xa0", " ") + "\n"

        tags = soup.find_all("div", {"class": "read__tagscol"})
        for tag in tags:
            if tag.h3.text == "Лица":
                news_faces = [x.text.strip() for x in tag.find_all("a")]
            if tag.h3.text == "Темы":
                news_tags = [x.text.strip() for x in tag.find_all("a")]

        news_item = News(
            publication_datetime=datetime.now(),
            url=link,
            text=news_content,
            source_name="Президент России",
            title=news_title,
            news_id=link.split("/")[-1],
            tags=news_tags,
            persons=news_faces,
        )
        return news_item

    async def parse(self) -> List[News]:
        last_news = await super()._get_last_parsed_news()
        if not last_news:
            last_news = datetime.fromtimestamp(0)
        else:
            last_news = last_news.get("publication_datetime", "")
            last_news = datetime.fromisoformat(last_news)

        print(last_news)
        links = await self.fetch_links()
        links = links[:3]

        if last_news:
            links = list(filter(lambda x: x["datetime"] > last_news, links))

        news_items = await asyncio.gather(
            *[self.parse_news_item(link["link"]) for link in links]
        )

        for i in range(len(news_items)):
            news_items[i].publication_datetime = links[i]["datetime"]

        await asyncio.gather(*[self._submit_news(news) for news in news_items])
        return news_items


if __name__ == "__main__":
    print("started")
    parser = PresidentParser()
    asyncio.run(parser.parse())
