from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, not_
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.news import News
from backend.app.models.science_articles import ScienceArticles
from backend.app.schemas.vector_search import VectorSearch

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.post("/search")
async def vector_search(
    search_params: VectorSearch, request: Request, db: AsyncSession = Depends(get_db),
):
    """
    Search for similar news articles using RAG with filtering options.
    
    The top_k parameter is limited to the configured maximum value.
    
    Returns:
        List of similar news articles
    """
    # Применяем ограничение max_top_k
    top_k = min(search_params.top_k, request.app.state.text_embedder.max_top_k)
    
    if search_params.article_type == "news":
        stmt = select(News)
        if search_params.source_name is not None:
            stmt = stmt.where(News.source_name == search_params.source_name)
        if search_params.start_date is not None:
            stmt = stmt.where(News.publication_datetime >= search_params.start_date)
        if search_params.end_date is not None:
            stmt = stmt.where(News.publication_datetime <= search_params.end_date)
        
        # Исключаем заголовки, начинающиеся с "Что произошло за день"
        stmt = stmt.where(not_(News.title.startswith("Что произошло за день")))
        
        # Сортируем по url и дате публикации по убыванию
        stmt = stmt.order_by(News.url, News.publication_datetime.desc())
        
        # Применяем DISTINCT ON (url)
        stmt = stmt.distinct(News.url)
        
        # Получаем все результаты и собираем id
        result = await db.execute(stmt)
        article_ids = [cur.id for cur in result.scalars().all()]
        
        similar_docs = await request.app.state.text_embedder.search_similar(
            text=search_params.query_text, top_k=top_k, filter_ids=article_ids
        )
        
        similar_docs_ids = [item.payload["news_id"] for item in similar_docs]
        result = await db.execute(select(News).where(News.id.in_(similar_docs_ids)))
        return result.scalars().all()
    
    else:  # science
        stmt = select(ScienceArticles)
        if search_params.source_name is not None:
            stmt = stmt.where(ScienceArticles.source_name == search_params.source_name)
        if search_params.start_date is not None:
            stmt = stmt.where(ScienceArticles.published_date >= search_params.start_date)
        if search_params.end_date is not None:
            stmt = stmt.where(ScienceArticles.published_date <= search_params.end_date)
        
        # Сортируем по url и дате публикации по убыванию
        stmt = stmt.order_by(ScienceArticles.url, ScienceArticles.published_date.desc())
        
        # Применяем DISTINCT ON (url)
        stmt = stmt.distinct(ScienceArticles.url)
        
        # Получаем все результаты и собираем id
        result = await db.execute(stmt)
        article_ids = [cur.id for cur in result.scalars().all()]
        
        similar_docs = await request.app.state.text_embedder.search_similar(
            text=search_params.query_text, top_k=top_k, filter_ids=article_ids
        )
        
        similar_docs_ids = [item.payload["science_id"] for item in similar_docs]
        result = await db.execute(select(ScienceArticles).where(ScienceArticles.id.in_(similar_docs_ids)))
        # Сортируем результаты по relevance_score по убыванию
        return sorted(result.scalars().all(), key=lambda x: x.relevance_score, reverse=True)
