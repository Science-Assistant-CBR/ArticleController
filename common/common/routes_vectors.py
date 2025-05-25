from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional
from datetime import datetime

class VectorSearch(BaseModel):

    raw_return: Optional[bool] = Field(False, description="Возвращаем сырые тексты points "
                                                "или готовый сформулированный ответ от OpenAI")
    query_text: str = Field(..., description="Текст запроса")
    sphere: Optional[str] = Field(None, description="analysis or science")
    queries_count: Optional[int] = Field(1, gt=0, description="Количество запросов с учетом перефразировок")
    top_k: Optional[int] = Field(5, gt=0, description="Количество релевантных points")
    source_name: Optional[str] = Field(None, description="Источник")
    start_date: Optional[datetime] = Field(None, description="Дата начала")
    end_date: Optional[datetime] = Field(None, description="Дата конца")
    relevance: Optional[float] = Field(None, description="Релевантность научной статьи")

    class Config:
        schema_extra = {
            "example": {
                "raw_return": False,
                "query_text": "Как ИИ влияет на обучение в университетах?",
                "queries_count": 1,
                "top_k": 5,
                "source_name": "Nature",
                "start_date": "2024-01-01",
                "end_date": "2025-04-10",
                "relevance": 0.8
            }
        }

        validate_assignment = True