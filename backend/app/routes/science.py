from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.science_articles import ScienceArticles
from backend.app.schemas.science_articles import ArticlesCreate, ArticlesUpdate

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
    stmt = select(ScienceArticles)

    if source_name:
        stmt = stmt.where(ScienceArticles.source_name == source_name)
    if start_date:
        stmt = stmt.where(ScienceArticles.published_date >= start_date)
    if end_date:
        stmt = stmt.where(ScienceArticles.published_date <= end_date)
    if section:
        stmt = stmt.where(ScienceArticles.section == section)
    if keywords:
        stmt = stmt.where(ScienceArticles.keywords.overlap(keywords))

    if not order_by or order_by == "publication_datetime":
        stmt = stmt.order_by(desc(ScienceArticles.published_date))
    elif order_by == "id":
        stmt = stmt.order_by(desc(ScienceArticles.id))

    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/articles")
async def create_articles(
        articles_data: ArticlesCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new news article and store its embedding.
    """
    db_science_articles = ScienceArticles(
        id=articles_data.id,
        annotation=articles_data.annotation,
        policy_conclusions= articles_data.policy_conclusions,
        research_motivation=articles_data.research_motivation,
        results = articles_data.results,
        published_date=articles_data.publication_datetime,
        url=str(articles_data.url),
        source_name=articles_data.source_name,
        keywords=articles_data.tags,
        authors=articles_data.persons,
        title=articles_data.title,
        section=articles_data.section,
    )
    db.add(db_science_articles)
    await db.commit()
    await db.flush()
    await db.refresh(db_science_articles)

    metadata = {"id": int(db_science_articles.id)}
    text = (
        f"{db_science_articles.title}."
        f"{db_science_articles.annotation} "
        f"{db_science_articles.policy_conclusions} "
        f"{db_science_articles.research_motivation} "
        f"{db_science_articles.results}")

    await request.app.state.text_embedder.store_embedding(
        text=str(text), point_id=db_science_articles.id, metadata=metadata
    )

    return db_science_articles


@router.get("/articles/{science_article_id}")
async def get_science_article_by_id(article_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific science article by ID.
    """
    stmt = select(ScienceArticles).where(ScienceArticles.id == article_id)
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
    stmt = select(ScienceArticles).where(ScienceArticles.id == id)
    result = await db.execute(stmt)
    db_science = result.scalars().first()
    if db_science is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_science)
    await db.commit()
    return {"message": "News deleted successfully"}


@router.put("/{science_article_id}")
async def update_articles(
    id: str, articles_update: ArticlesUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an articles article by ID.
    """
    stmt = select(ScienceArticles).where(ScienceArticles.id == id)
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
