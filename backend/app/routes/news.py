from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.news_article import NewsArticle
from backend.app.schemas.news_article import NewsArticleCreate, NewsArticleUpdate

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/articles")
async def get_news(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    topic: Optional[str] = None,
    tags: List[str] = Query(default=None),
    order_by: Optional[str] = None,
):
    """
    Get list of news with optional filtering.
    """
    stmt = select(NewsArticle)
    
    if source_name:
        stmt = stmt.where(NewsArticle.source_name == source_name)
    if start_date:
        stmt = stmt.where(NewsArticle.publication_datetime >= start_date)
    if end_date:
        stmt = stmt.where(NewsArticle.publication_datetime <= end_date)
    if topic:
        stmt = stmt.where(NewsArticle.topic == topic)
    if tags:
        stmt = stmt.where(NewsArticle.tags.overlap(tags))

    if not order_by or order_by == "publication_datetime":
        stmt = stmt.order_by(desc(NewsArticle.publication_datetime))
    elif order_by == "id":
        stmt = stmt.order_by(desc(NewsArticle.id))
        
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/articles")
async def create_news(
    news_data: NewsArticleCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new news article and store its embedding.
    """
    db_news = NewsArticle(**(news_data.model_dump(exclude_unset=True)))
    db.add(db_news)
    await db.commit()
    await db.flush()
    await db.refresh(db_news)

    metadata = {"news_id": int(db_news.id)}
    await request.app.state.text_embedder.store_embedding(
        text=str(db_news.text), point_id=db_news.id, metadata=metadata
    )

    return db_news


@router.get("/articles/{news_id}")
async def get_news_by_id(news_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific news article by ID.
    """
    stmt = select(NewsArticle).where(NewsArticle.news_id == news_id)
    result = await db.execute(stmt)
    news = result.scalars().first()
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.put("/{news_id}")
async def update_news(
    news_id: str, news_update: NewsArticleUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update a news article by ID.
    """
    stmt = select(NewsArticle).where(NewsArticle.news_id == news_id)
    result = await db.execute(stmt)
    db_news = result.scalars().first()
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")

    update_data = news_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_news, field, value)

    await db.commit()
    await db.flush()
    await db.refresh(db_news)
    return db_news


@router.delete("/{id}")
async def delete_news(id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a news article by ID.
    """
    stmt = select(NewsArticle).where(NewsArticle.id == id)
    result = await db.execute(stmt)
    db_news = result.scalars().first()
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_news)
    await db.commit()
    return {"message": "News deleted successfully"}
