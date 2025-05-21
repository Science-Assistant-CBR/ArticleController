from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class NewsArticle(BaseModel):
    id: int = Field(..., description="Id статьи в базе данных")
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
        validate_assignment = True
        from_attributes = True

class NewsArticleCreate(BaseModel):
    publication_datetime: datetime = Field(..., description="Дата и время публикации")
    url: str = Field(..., description="Ссылка на новость")
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
                "publication_datetime": "2025-04-12T12:00:00Z",
                "url": "https://example.com/news/123",
                "text": "В Москве открыли новый исследовательский центр...",
                "source_name": "РИА Новости",
                "news_id": "tg_456123",
                "tags": ["наука", "технологии"],
                "persons": ["Иван Иванов", "Мария Смирнова"],
                "title": "Открытие нового научного центра",
                "topic": "Образование"
            }
        }
        validate_assignment = True
        from_attributes = True


class NewsArticleUpdate(NewsArticle):
    pass
