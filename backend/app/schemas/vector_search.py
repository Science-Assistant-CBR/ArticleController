from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class VectorSearch(BaseModel):
    article_type: bool = Field(..., description="True - научные статьи, False - новости")
    query_text: str = Field(..., description="Текст запроса")
    top_k: int = Field(5, gt=0, description="Количество релевантных points")
    source_name: Optional[str] = Field(..., description="Источник")
    start_date: Optional[str] = Field(..., description="Дата начала")
    end_date: Optional[str] = Field(..., description="Дата конца")
    # TODO: Добавить метаданные для научных статей


    class Config:
        validate_assignment = True