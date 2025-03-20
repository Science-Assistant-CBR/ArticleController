import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from dateutil.parser import parse

from app.parsers.base import BaseParser
from common.schemas import News

# locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


# TODO: select the sanctions category
#
class RBCParser(BaseParser):
    def __init__(
        self,
        base_url: str = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
        proxies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: int = 30,
        LAST_NEWS_API: str = "https://news-api.pshakhmin.ru/api/v1",
    ):
        super().__init__(
            "РБК",
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
        response_story = await super()._make_request(
            "https://www.rbc.ru/story/5422bb83cbb20f63f25fb481"
        )
        response = await super()._make_request(self.base_url)

        if not response or not response_story:
            print("Ошибка при запросе страницы")
            return []

        soup_story = BeautifulSoup(response_story, features="html.parser")
        sanctions_links = []
        for link in soup_story.find_all(
            "a",
            {
                "class": "item__link rm-cm-item-link js-rm-central-column-item-link js-story-item-link js-rm-cm-item js-rm-cm-item-click js-rm-cm-item-href"
            },
        ):
            sanctions_links.append(link["href"])

        # print(sanctions_links)

        soup = BeautifulSoup(response, features="xml")
        news_data = []

        for news_item in soup.find_all("item"):
            link = news_item.find("link").text
            title = news_item.find("title").text

            description = ""
            if news_item.find("description"):
                description = news_item.find("description").text

            category = news_item.find_all("category")
            date = self._parse_date(news_item.find("pubDate").text)
            if "Санкции в отношении России" in [x.text for x in category]:
                news_data.append(
                    {
                        "link": link,
                        "title": title,
                        "description": description,
                        "category": "Санкции в отношении России",
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
            source_name="РБК",
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
    parser = RBCParser()
    asyncio.run(parser.parse())
