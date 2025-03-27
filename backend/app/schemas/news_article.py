from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class NewsArticle(BaseModel):
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

class NewsArticleCreate(NewsArticle):
    pass

class NewsArticleUpdate(NewsArticle):
    pass
