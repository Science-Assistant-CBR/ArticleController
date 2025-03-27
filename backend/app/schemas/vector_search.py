from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional
from datetime import datetime

class VectorSearch(BaseModel):
    article_type: str = Field(..., description="Тип статьи: 'news' или 'science'")
    raw_return: bool = Field(False, description="Возвращаем сырые тексты points "
                                                "или готовый сформулированный ответ от OpenAI")
    query_text: str = Field(..., description="Текст запроса")
    top_k: int = Field(5, gt=0, description="Количество релевантных points")
    source_name: Optional[str] = Field(..., description="Источник")
    start_date: Optional[str] = Field(..., description="Дата начала")
    end_date: Optional[str] = Field(..., description="Дата конца")

    # TODO: Добавить метаданные для научных статей
    relevance: Optional[float] = Field(..., description="Релевантность научной статьи")

    @validator('article_type')
    def validate_article_type(cls, v):
        if v not in ['news', 'science']:
            raise ValueError('article_type должен быть либо "news", либо "science"')
        return v

    class Config:
        validate_assignment = True