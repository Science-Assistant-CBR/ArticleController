from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class ScienceArticle(BaseModel):
    """
    Представляет обработанную статью с результатами анализа.
    """
    id: int = Field(default=None, description="Article ID in DB")
    title: str = Field(..., description="Заголовок статьи")
    sphere: str = Field(..., description="Sphere - analytics or science")
    url: str = Field(..., description="URL статьи")
    file_path: str = Field(..., description="Путь к локальному PDF-файлу статьи")
    section: Optional[str] = Field(None, description="Раздел или категория статьи")
    published_date: Optional[datetime] = Field(None, description="Дата публикации")
    authors: Optional[List[str]] = Field(None, description="Список авторов")
    affiliation: Optional[str] = Field(None, description="Аффилиация авторов")
    source_name: str = Field(..., description="Название источника")
    annotation: str = Field(..., description="Аннотация")
    policy_conclusions: str = Field(..., description="Выводы для политики")
    research_motivation: str = Field(..., description="Мотивация исследования")
    contribution: str = Field(..., description="Вклад исследования")
    research_question: str = Field(..., description="Основной исследовательский вопрос")
    data_description: str = Field(..., description="Описание данных")
    model_description: str = Field(..., description="Описание модели")
    results: str = Field(..., description="Основные результаты исследования")
    critique: str = Field(..., description="Критический анализ")
    relevance_explanation: str = Field(..., description="Обоснование релевантности")
    relevance_score: float = Field(..., description="Оценка релевантности")
    full_summary: Optional[str] = Field(None, description="Краткое содержание (резюме) статьи")
    downloads_count: Optional[int] = Field(None, description="Количество скачиваний")
    views_count: Optional[int] = Field(None, description="Количество просмотров")
    abstract: Optional[str] = Field(None, description="Краткое содержание статьи")
    categories: Optional[List[str]] = Field(None, description="Список категорий")
    parsed_at: datetime = Field(default_factory=datetime.utcnow, description="Время обработки")

    class Config:
        validate_assignment = True
        from_attributes = True




class ScienceArticleCreate(BaseModel):
    title: str = Field(..., description="Заголовок статьи")
    sphere: str = Field(..., description="Sphere - analysis or science")
    url: str = Field(..., description="URL статьи")
    file_path: str = Field(..., description="Путь к локальному PDF-файлу статьи")
    section: Optional[str] = Field(None, description="Раздел или категория статьи")
    published_date: Optional[datetime] = Field(None, description="Дата публикации")
    authors: Optional[List[str]] = Field(None, description="Список авторов")
    affiliation: Optional[str] = Field(None, description="Аффилиация (организация авторов)")
    source_name: str = Field(..., description="Название источника")

    # Summary
    annotation: str = Field(..., description="Аннотация")
    policy_conclusions: str = Field(..., description="Выводы для политики")
    research_motivation: str = Field(..., description="Мотивация исследования")
    contribution: str = Field(..., description="Вклад исследования")
    research_question: str = Field(..., description="Основной исследовательский вопрос")
    data_description: str = Field(..., description="Описание данных")
    model_description: str = Field(..., description="Описание модели")
    results: str = Field(..., description="Основные результаты исследования")
    critique: str = Field(..., description="Критический анализ")
    relevance_explanation: str = Field(..., description="Объяснение релевантности")
    # Полный текст summary
    full_summary: str = Field(..., description="Полный текст саммари статьи")

    relevance_score: float = Field(..., description="Оценка релевантности")
    downloads_count: Optional[int] = Field(None, description="Количество скачиваний")
    views_count: Optional[int] = Field(None, description="Количество просмотров")
    abstract: Optional[str] = Field(None, description="Краткое содержание статьи")
    categories: Optional[List[str]] = Field(None, description="Категории (теги)")
    parsed_at: datetime = Field(default_factory=datetime.utcnow, description="Время обработки")

    class Config:
        validate_assignment = True
        from_attributes = True
        schema_extra = {
            "example": {
                "title": "AI in Education",
                "url": "https://journals.org/article/ai-edu",
                "file_path": "/files/articles/ai-edu.pdf",
                "section": "Technology",
                "published_date": "2025-03-15T00:00:00Z",
                "authors": ["John Doe", "Jane Smith"],
                "affiliation": "Harvard University",
                "source_name": "Nature",
                "annotation": "This paper discusses the role of AI in education systems...",
                "policy_conclusions": "Investments in AI tools for schools can improve access and outcomes.",
                "research_motivation": "Growing use of AI without clear framework...",
                "contribution": "Introduces a new model of adaptive AI for learning",
                "research_question": "How does AI influence learning efficiency?",
                "data_description": "Surveys from 20 universities, 1500 students",
                "model_description": "Multi-layer transformer with attention on user feedback",
                "results": "Improved test scores by 15%",
                "critique": "Lack of long-term data and diverse regions",
                "relevance_explanation": "Education is critical and AI is rapidly evolving",
                "full_summary": "This article summarizes how artificial intelligence is changing education...",
                "relevance_score": 0.92,
                "downloads_count": 1220,
                "views_count": 4321,
                "abstract": "The article explores adaptive learning systems powered by AI...",
                "categories": ["education", "AI"],
                "parsed_at": "2025-04-12T01:00:00Z"
            }
        }

class ScienceArticleUpdate(BaseModel):
    pass