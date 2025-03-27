from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.science_article import ScienceArticle
from backend.app.schemas.science_article import ArticleCreate, ArticleUpdate

router = APIRouter(prefix="/science", tags=["science"])


@router.get("/articles")
async def get_articles(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        source_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        section: Optional[str] = None,
        keywords: Optional[List[str]] = Query(default=None),
        order_by: Optional[str] = None,
):
    """
    Get list of news with optional filtering.
    """
    stmt = select(ScienceArticle)

    if source_name:
        stmt = stmt.where(ScienceArticle.source_name == source_name)
    if start_date:
        stmt = stmt.where(ScienceArticle.published_date >= start_date)
    if end_date:
        stmt = stmt.where(ScienceArticle.published_date <= end_date)
    if section:
        stmt = stmt.where(ScienceArticle.section == section)
    if keywords:
        stmt = stmt.where(ScienceArticle.keywords.overlap(keywords))

    if not order_by or order_by == "publication_datetime":
        stmt = stmt.order_by(desc(ScienceArticle.published_date))
    elif order_by == "id":
        stmt = stmt.order_by(desc(ScienceArticle.id))

    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/articles")
async def create_articles(
        article_data: ArticleCreate, request: Request, db: AsyncSession = Depends(get_db)
):

    db_science_article = ScienceArticle(**(article_data.model_dump(exclude_unset=True)))
    db.add(db_science_article)
    await db.commit()
    await db.flush()
    await db.refresh(db_science_article)

    metadata = {"id": int(db_science_article.id)}
    text = (
        f"{db_science_article.title}."
        f"{db_science_article.annotation} "
        f"{db_science_article.policy_conclusions} "
        f"{db_science_article.research_motivation} "
        f"{db_science_article.results}.")

    await request.app.state.text_embedder.store_embedding(
        text=str(text), point_id=db_science_article.id, metadata=metadata
    )

    return db_science_article


@router.get("/articles/{science_article_id}")
async def get_science_article_by_id(article_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific science article by ID.
    """
    stmt = select(ScienceArticle).where(ScienceArticle.id == article_id)
    result = await db.execute(stmt)
    articles = result.scalars().first()
    if articles is None:
        raise HTTPException(status_code=404, detail="Science Articles not found")
    return articles


@router.delete("/articles/{id}")
async def delete_article(id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an article by ID.
    """
    stmt = select(ScienceArticle).where(ScienceArticle.id == id)
    result = await db.execute(stmt)
    db_science = result.scalars().first()
    if db_science is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_science)
    await db.commit()
    return {"message": "News deleted successfully"}


@router.put("/{science_article_id}")
async def update_articles(
    id: str, articles_update: ArticleUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an articles article by ID.
    """
    stmt = select(ScienceArticle).where(ScienceArticle.id == id)
    result = await db.execute(stmt)
    db_articles = result.scalars().first()
    if db_articles is None:
        raise HTTPException(status_code=404, detail="Articles not found")

    update_data = articles_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_articles, field, value)

    await db.commit()
    await db.flush()
    await db.refresh(db_articles)
    return db_articles
