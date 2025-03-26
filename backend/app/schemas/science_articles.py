from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class ScienceArticles(BaseModel):
    publication_datetime: datetime = Field(..., description="Дата и время публикации")
    url: HttpUrl = Field(..., description="Ссылка на статью")
    source_name: str = Field(..., description="Название источника")
    id: int = Field(
        ..., description="ID научной статьи"
    )
    keywords: Optional[List[str]] = Field(
        None, description="Теги статьи (может быть несколько)"
    )
    authors: Optional[List[str]] = Field(None, description="Авторы научной статьи")
    title: str = Field(..., description="Заголовок научной статьи")
    section: Optional[str] = Field(None, description="Раздел научной статьи")

    downloads_count: Optional[int] = Field(None, description="Количество скачиваний научной статьи")
    views_count: Optional[int] = Field(None, description= "Количество просмотров научной статьи")
    citations_count: Optional[int] = Field(None, description="Количество цитирований научной статьи")

    abstract: Optional[str] = Field(None, description="Краткое резюме статьи")

    annotation: str = Field(..., description= "Аннотация научной статьи")
    affiliation: str = Field(..., description= "Аффилиация научной статьи")
    policy_conclusions: str = Field(..., description= "Выводы")
    research_motivation: str = Field(...,description="Мотивация исследования")
    contribution: str = Field(..., description="Contribution")
    research_question: str = Field(...,description="Research Question")
    data_description: str = Field(...,description="Data Description")
    model_description: str = Field(..., description="Описание модели")
    results: str = Field(..., description="Результаты")
    critique: str = Field(..., description="Критика научной статьи")
    relevance_explanation: str = Field(..., description= "Объяснение релевантности научной статьи")

    relevance_score: float = Field(..., description="Оценка релевантности научной статьи")

    processed_at: datetime = Field(..., description= "Дата обработки")
    report_path: Optional[str] = Field(None, description="Путь к файлу отчета")
    report_generated_at: Optional[datetime] = Field(None, description="Дата генерации отчета")

class ArticlesCreate(ScienceArticles):
    pass


class ArticlesUpdate(ScienceArticles):
    pass
