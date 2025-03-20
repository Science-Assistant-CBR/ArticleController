from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class News(BaseModel):
    publication_datetime: datetime = Field(..., description="Дата и время публикации")
    url: HttpUrl = Field(..., description="Ссылка на новость")
    text: str = Field(..., description="Текст новости")
    source_name: str = Field(..., description="Название источника")
    news_id: str = Field(
        ..., description="ID новости (например, ID сообщения в ТГ или ID на сайте)"
    )

    tags: Optional[List[str]] = Field(
        None, description="Теги новости (может быть несколько)"
    )
    persons: Optional[List[str]] = Field(None, description="Лица, упомянутые в новости")
    title: Optional[str] = Field(None, description="Заголовок новости")
    topic: Optional[str] = Field(None, description="Тема новости")

    class Config:
        schema_extra = {
            "example": {
                "publication_datetime": "2024-11-26T10:00:00",
                "url": "https://example.com/news/12345",
                "text": "Важная новость о событиях в мире.",
                "source_name": "Example News",
                "tags": ["Политика", "Экономика"],
                "persons": ["Иванов", "Петров"],
                "news_id": "12345",
                "title": "События дня",
                "topic": "Политика",
            }
        }
