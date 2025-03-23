from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.science_articles import ScienceArticles
from backend.app.schemas.articles import ArticlesCreate, ArticlesUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/")
async def get_articles(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        source_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        section: Optional[str] = None,
        keywords: List[str] = Query(default=None),
        order_by: Optional[str] = None,
):
    """
    Get list of news with optional filtering.
    """
    stmt = select(ScienceArticles)

    if source_name:
        stmt = stmt.where(ScienceArticles.source_name == source_name)
    if start_date:
        stmt = stmt.where(ScienceArticles.publication_datetime >= start_date)
    if end_date:
        stmt = stmt.where(ScienceArticles.publication_datetime <= end_date)
    if section:
        stmt = stmt.where(ScienceArticles.section == section)
    if keywords:
        stmt = stmt.where(ScienceArticles.keywords.overlap(keywords))

    if not order_by or order_by == "publication_datetime":
        stmt = stmt.order_by(desc(ScienceArticles.publication_datetime))
    elif order_by == "id":
        stmt = stmt.order_by(desc(ScienceArticles.id))

    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{science_article_id}")
async def get_science_articles_by_id(article_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific science article by ID.
    """
    stmt = select(ScienceArticles).where(ScienceArticles.id == article_id)
    result = await db.execute(stmt)
    articles = result.scalars().first()
    if articles is None:
        raise HTTPException(status_code=404, detail="Science Articles not found")
    return articles


@router.delete("/{id}")
async def delete_articles(id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a news article by ID.
    """
    stmt = select(ScienceArticles).where(ScienceArticles.id == id)
    result = await db.execute(stmt)
    db_news = result.scalars().first()
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_news)
    await db.commit()
    return {"message": "News deleted successfully"}


@router.post("/")
async def create_articles(
        articles_data: ArticlesCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new news article and store its embedding.
    """
    db_news = ScienceArticles(
        id=articles_data.id,
        publication_datetime=articles_data.publication_datetime,
        url=str(articles_data.url),
        text=articles_data.text,
        source_name=articles_data.source_name,
        keywords=articles_data.keywords,
        authors=articles_data.authors,
        title=articles_data.title,
        section=articles_data.section,
    )
    db.add(db_news)
    await db.commit()
    await db.flush()
    await db.refresh(db_news)

    metadata = {"id": int(db_news.id)}
    await request.app.state.text_embedder.store_embedding(
        text=str(db_news.text), point_id=db_news.id, metadata=metadata
    )

    return db_news


@router.put("/{news_id}")
async def update_news(
    id: str, articles_update: ArticlesUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update a articles article by ID.
    """
    stmt = select(ScienceArticles).where(ScienceArticles.id == id)
    result = await db.execute(stmt)
    db_news = result.scalars().first()
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")

    update_data = articles_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_news, field, value)

    await db.commit()
    await db.flush()
    await db.refresh(db_news)
    return db_news
