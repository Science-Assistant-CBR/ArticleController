from sqlalchemy import Column, String, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.models.base import Base


class ScienceArticles(Base):
    __tablename__ = "science_articles"

    id = Column(Integer, primary_key=True)

    # Основная информация
    title = Column(String)
    url = Column(String, unique=True)
    section = Column(String, nullable=True)
    source_name = Column(String)

    # Метаданные
    published_date = Column(DateTime, nullable=True)
    authors = Column(ARRAY(String), nullable=True)  # Список авторов с аффилиациями

    # Статистика
    downloads_count = Column(Integer, nullable=True)
    views_count = Column(Integer, nullable=True)
    citations_count = Column(Integer, nullable=True)

    # Оригинальные метаданные
    abstract = Column(String, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)  # Список ключевых слов

    # Результаты анализа
    annotation = Column(String)
    affiliation = Column(String)
    policy_conclusions = Column(String)
    research_motivation = Column(String)
    contribution = Column(String)
    research_question = Column(String)
    data_description = Column(String)
    model_description = Column(String)
    results = Column(String)
    critique = Column(String)
    relevance_explanation = Column(String)

    # Оценки
    relevance_score = Column(Float)

    # Технические данные
    processed_at = Column(DateTime, default=datetime.utcnow)
    report_path = Column(String, nullable=True)
    report_generated_at = Column(DateTime, nullable=True)


    def __repr__(self):
        return f"<Science(article_id='{self.id}', title='{self.title}')>"
