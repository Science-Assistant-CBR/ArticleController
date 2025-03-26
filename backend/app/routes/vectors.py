from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.news import News
from backend.app.models.science_articles import ScienceArticles

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.get("/search")
async def vector_search(
    query: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    top_k: int = Query(default=5, gt=0),
    source_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Search for similar news articles using RAG with filtering options.
    
    The top_k parameter is limited to the configured maximum value.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        source_name: Filter by news source
        start_date: Filter by start date
        end_date: Filter by end date
        topic: Filter by topic
        tags: Filter by tags
    
    Returns:
        List of similar news articles
    """
    # Apply max_top_k limit
    top_k = min(top_k, request.app.state.text_embedder.max_top_k)
    stmt = select(News)
    
    if source_name:
        stmt = stmt.where(News.source_name == source_name)
    if start_date:
        stmt = stmt.where(News.publication_datetime >= start_date)
    if end_date:
        stmt = stmt.where(News.publication_datetime <= end_date)

    # Exclude titles starting with "Что произошло за день"
    stmt = stmt.where(~News.title.startswith("Что произошло за день"))

    # Order by url and then by publication_datetime descending
    stmt = stmt.order_by(News.url, News.publication_datetime.desc())

    # Apply DISTINCT ON (url)
    stmt = stmt.distinct(News.url)

    # Fetch all results and collect ids
    result = await db.execute(stmt)
    news_ids = [cur.id for cur in result.scalars().all()]

    similar_docs = await request.app.state.text_embedder.search_similar(
        text=query, top_k=top_k, filter_ids=news_ids
    )

    similar_docs_ids = [item.payload["news_id"] for item in similar_docs]
    result = await db.execute(select(News).where(News.id.in_(similar_docs_ids)))
    return result.scalars().all()
