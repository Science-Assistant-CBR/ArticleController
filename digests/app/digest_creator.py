import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

import aiohttp
from openai import AsyncOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class DigestSection:
    query: str
    content: str
    links: List[str]
    title: str
    article_ids: List[int]


@dataclass
class Digest:
    title: str
    body: str
    start_datetime: datetime
    end_datetime: datetime
    sections: List[DigestSection]
    pdf_file: str

    # TODO: теперь надо научиться создавать саммари для дайджеста, это логика расписана в digests/app
    #  там в dataclass Digest надо тоже добавить поле summary
    summary: str


class NewsFetcher:
    def __init__(self, backend_url: str, session: aiohttp.ClientSession):
        self.backend_url = backend_url
        self.session = session

    async def fetch_news(self, query: str, top_k: int = 10) -> List[Dict[str, any]]:
        logger.info(f"Запрос новостей по теме: {query}")
        params = {"query": query, "top_k": top_k}
        try:
            async with self.session.get(
                    f"{self.backend_url}/vectors/search", params=params
            ) as response:
                response.raise_for_status()
                news = await response.json()
                logger.info(f"Успешно получено {len(news)} новостей по теме: {query}")
                return news
        except Exception as e:
            logger.error(f"Ошибка при запросе новостей по теме {query}: {str(e)}")
            raise


class ContentGenerator:
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    async def prettify_news(self, text: str) -> str:
        logger.debug(f"Суммаризация новости: {text[:100]}...")
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": 'Суммаризуй следующую новость, выдай не более 3 предложений. Не пиши ничего, кроме суммаризации. Важные слова в новостях выделяй жирным с помощью {\\bfseries}, например, {\\bfseries Жирный текст}, и ни в коем случае не используй **, asterisk или другие способы выделения. Экранируй символ доллара и символ процента с помощью \\$ и \\% соответственно. Вместо заключения текста в кавычки (") используй << >>.',
                    },
                    {
                        "role": "user",
                        "content": "Текст новости: " + text,
                    },
                    {"role": "assistant", "content": "\\item"},
                ],
                max_tokens=500,
                temperature=0.1,
            )
            summary = response.choices[0].message.content.strip()
            logger.debug(f"Суммаризация завершена: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Ошибка при суммаризации новости: {str(e)}")
            raise

    async def create_summary(self, sections: List[DigestSection]) -> str:
        # TODO:
        #  в ContentGenerator надо добавить метод для создания summary по всему дайджесту,
        #  который будет принимать список DigestSection и выдавать строкой саммари

        logger.debug("Суммаризация дайджеста по разделам...")

        all_summaries = ""

        for section in sections:
            try:
                text = section.content
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": 'Суммаризуй следующую новость, выдай не более 3 предложений. '
                                       'Не пиши ничего, кроме суммаризации. Важные слова в новостях выделяй жирным с помощью {\\bfseries}, '
                                       'например, {\\bfseries Жирный текст}, и ни в коем случае не используй **, asterisk или другие способы выделения. '
                                       'Экранируй символ доллара и символ процента с помощью \\$ и \\% соответственно. '
                                       'Вместо заключения текста в кавычки (") используй << >>.',
                        },
                        {
                            "role": "user",
                            "content": "Текст новости: " + text,
                        },
                        {"role": "assistant", "content": "\\item"},
                    ],
                    max_tokens=500,
                    temperature=0.1,
                )
                summary = response.choices[0].message.content.strip()
                s = f"Суммаризация раздела {section.title}: {summary}. "
                all_summaries += s
                logger.debug(f"Суммаризация раздела {section.title} завершена: {summary}")
            except Exception as e:
                logger.error(f"Ошибка при суммаризации дайждеста, раздел - {section.title}: {str(e)}")
                raise

        logger.debug("Суммаризация всех разделов...")
        try:
            text = section.content
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": 'Это суммаризация дайджеста новостей по разделам.'
                                   'Сделай текст более связным. Не нарушай структуру разделов'
                                   'Не пиши ничего, кроме суммаризации. Важные слова в новостях выделяй жирным с помощью {\\bfseries}, '
                                   'например, {\\bfseries Жирный текст}, и ни в коем случае не используй **, asterisk или другие способы выделения. '
                                   'Экранируй символ доллара и символ процента с помощью \\$ и \\% соответственно. '
                                   'Вместо заключения текста в кавычки (") используй << >>.',
                    },
                    {
                        "role": "user",
                        "content": "Дайджест новостей по разделам: " + text,
                    },
                    {"role": "assistant", "content": "\\item"},
                ],
                max_tokens=500,
                temperature=0.1,
            )
            summary = response.choices[0].message.content.strip()
            joined_summary = summary
            logger.debug(f"Суммаризация дайджеста по разделам завершена: {summary}")
            return joined_summary
        except Exception as e:
            logger.error(f"Ошибка при суммаризации дайждеста по разделам: {str(e)}")
            raise


class PDFCompiler:
    def compile_pdf(self, digest: Digest, template_path: str, output_path: str):
        logger.info(f"Компиляция PDF для дайджеста: {digest.title}")
        try:
            with open(template_path, "r", encoding="utf-8") as template_file:
                template = template_file.read()
            template = template.replace("{{title}}", digest.title)
            template = template.replace("{{body}}", digest.body)
            tex_path = output_path.replace(".pdf", ".tex")

            os.chdir("latex_source")

            with open(tex_path, "w", encoding="utf-8") as tex_file:
                tex_file.write(template)

            logger.debug(f"Создан TeX файл: {tex_path}")

            os.system(f"lualatex --interaction=nonstopmode {tex_path} {output_path}")
            logger.info(f"PDF успешно скомпилирован: {output_path}")

            os.remove(tex_path)
            os.remove(output_path.replace(".pdf", ".log"))
            os.remove(output_path.replace(".pdf", ".aux"))
            logger.debug("Временные файлы удалены")
        except Exception as e:
            logger.error(f"Ошибка при компиляции PDF: {str(e)}")
            raise


class DigestBuilder:
    # TODO:
    #  В DigestBuilder надо добавить вызов функции создания саммари
    def __init__(
            self,
            news_fetcher: NewsFetcher,
            content_generator: ContentGenerator,
            pdf_compiler: PDFCompiler,
            backend_url: str,
            session: aiohttp.ClientSession,
    ):
        self.news_fetcher = news_fetcher
        self.content_generator = content_generator
        self.pdf_compiler = pdf_compiler
        self.backend_url = backend_url
        self.session = session

    async def build_digest(
            self,
            day: date,
            digest_structure: List[Dict[str, str]],
            template_path: str,
            output_path: str,
    ) -> Digest:
        logger.info(f"Начало создания дайджеста за {day}")
        try:
            start, end = self._get_time_period(day)
            title = self._get_digest_title(day)
            logger.debug(f"Период дайджеста: {start} - {end}")

            sections = await self._build_sections(digest_structure)
            logger.info(f"Создано {len(sections)} разделов")

            # TODO:
            #  Создание саммари
            summary = await self.content_generator.create_summary(sections)

            digest = Digest(
                title=title,
                body="",
                start_datetime=start,
                end_datetime=end,
                sections=sections,
                pdf_file=output_path,
                summary=summary,
            )

            digest.body = await self._compile_digest_body(sections)
            logger.debug("Тело дайджеста скомпилировано")

            self.pdf_compiler.compile_pdf(digest, template_path, output_path)
            logger.info(f"Дайджест успешно создан: {output_path}")

            # Upload digest to backend
            await self._upload_digest(digest, output_path)
            logger.info("Дайджест успешно загружен на сервер")

            return digest
        except Exception as e:
            logger.error(f"Ошибка при создании дайджеста: {str(e)}")
            raise

    def _get_time_period(self, day: date) -> Tuple[datetime, datetime]:
        dt = datetime.combine(day, datetime.min.time())
        start = dt.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(
            days=1
        )
        end = dt.replace(hour=20, minute=0, second=0, microsecond=0)
        return start, end

    def _get_digest_title(self, day: date) -> str:
        return f"Дайджест за {day.day}.{day.month}.{day.year}"

    async def _build_sections(
            self, digest_structure: List[Dict[str, str]]
    ) -> List[DigestSection]:
        sections = []
        logger.info(
            f"Создание разделов из структуры ({len(digest_structure)} элементов)"
        )

        for section in digest_structure:
            query = section.get("query", "")
            title = section.get("title", "")
            if not query:
                logger.warning(f"Пропущен раздел без запроса: {title}")
                continue

            try:
                logger.info(f"Обработка раздела: {title} (запрос: {query})")
                news = await self.news_fetcher.fetch_news(query, 1)

                if not news:
                    logger.warning(f"Нет новостей для раздела: {title}")
                    continue

                content = "\\begin{itemize}\n"
                for item in news:
                    summary = await self.content_generator.prettify_news(item["text"])
                    source = f"\\underline{{\\href{{{item['url']}}}{{{item['source_name']}}}}}"
                    content += "\\item " + summary + " " + source + "\n"
                content += "\\end{itemize}\n"

                links = [item["url"] for item in news]
                ids = [item["id"] for item in news]

                new_section = DigestSection(
                    query=query,
                    content=content,
                    links=links,
                    title=title,
                    article_ids=ids,
                )
                sections.append(new_section)
                logger.debug(f"Раздел '{title}' успешно создан")

            except Exception as e:
                logger.error(f"Ошибка при обработке раздела '{title}': {str(e)}")
                continue

        logger.info(f"Создано {len(sections)} разделов")
        return sections

    async def _upload_digest(self, digest: Digest, pdf_path: str) -> bool:
        """Upload digest to backend using multipart/form-data"""
        try:
            data = aiohttp.FormData()
            data.add_field(
                "pdf_file",
                open(pdf_path, "rb"),
                filename=f"digest_{digest.start_datetime.date()}.pdf",
                content_type="application/pdf",
            )
            data.add_field("title", digest.title)
            data.add_field("body", digest.body)
            # Format datetime fields as strings
            data.add_field("start_datetime", digest.start_datetime.isoformat())
            data.add_field("end_datetime", digest.end_datetime.isoformat())

            # Collect all article IDs from sections and convert to strings
            article_ids = []
            for section in digest.sections:
                article_ids.extend(str(id) for id in section.article_ids)
            data.add_field("article_ids", json.dumps(article_ids))

            # Add required body field
            data.add_field("body", digest.body)

            async with self.session.post(
                    f"{self.backend_url}/api/v1/digests/",
                    data=data,
                    headers={"Accept": "application/json"}
            ) as response:
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Ошибка при загрузке дайджеста: {str(e)}")
            raise

    async def _compile_digest_body(self, sections: List[DigestSection]) -> str:
        body = ""
        for idx, section in enumerate(sections, start=1):
            body += f"\n\n\\section{{{section.title}}}\n"
            body += f"{section.content}\n"
        return body


async def main():
    day = date.today()
    backend_url = os.getenv("NEWS_BACKEND_URL", "")
    # backend_url = "https://news-api.pshakhmin.ru/api/v1"
    openai_client = AsyncOpenAI()
    async with aiohttp.ClientSession() as session:
        news_fetcher = NewsFetcher(backend_url, session)
        content_generator = ContentGenerator(openai_client)
        pdf_compiler = PDFCompiler()
        digest_builder = DigestBuilder(
            news_fetcher, content_generator, pdf_compiler, backend_url, session
        )
        with open("sections.json") as f:
            digest_structure = json.load(f)
        template_path = "latex_source/template.tex"
        output_path = f"digest_{day.isoformat()}.pdf"
        digest = await digest_builder.build_digest(
            day, digest_structure, template_path, output_path
        )
        print(digest.body)
        print(f"Digest created: {digest.pdf_file}")


if __name__ == "__main__":
    asyncio.run(main())
