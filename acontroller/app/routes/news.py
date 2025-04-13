from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acontroller.app.database import get_db
from acontroller.app.models.news_article import NewsArticle as ModelsNewsArticle
from common.common.news_article import NewsArticleCreate as SchemasNewsArticleCreate
from common.common.news_article import NewsArticle as SchemasNewsArticle


router = APIRouter(prefix="/news", tags=["news"])


@router.post("/articles", response_model=SchemasNewsArticle)
async def create_news(
    news_data: SchemasNewsArticleCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new news article and store its embedding.
    """
    db_news = ModelsNewsArticle(**news_data.model_dump())
    db.add(db_news)
    await db.commit()
    await db.flush()
    await db.refresh(db_news)
    text = db_news.text

    metadata = {"id": int(db_news.id)}
    await request.app.state.rag.news_embedder.store_embedding(
        text=text, point_id=db_news.id, metadata=metadata
    )

    return db_news


@router.get("/articles", response_model=List[SchemasNewsArticle])
async def get_articles(
    input_id: Optional[int] = Query(None, description="Фильтрация по id статьи"),
    title: Optional[str] = Query(None, description="Фильтрация по заголовку"),
    source_name: Optional[str] = Query(None, description="Фильтрация по источнику"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата публикации"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата публикации"),
    section: Optional[str] = Query(None, description="Раздел новости"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ModelsNewsArticle)

    if input_id:
        stmt = stmt.where(ModelsNewsArticle.id == input_id)
    if title:
        stmt = stmt.where(ModelsNewsArticle.title.ilike(f"%{title}%"))
    if source_name:
        stmt = stmt.where(ModelsNewsArticle.source_name == source_name)
    if start_date:
        stmt = stmt.where(ModelsNewsArticle.publication_datetime >= start_date)
    if end_date:
        stmt = stmt.where(ModelsNewsArticle.publication_datetime <= end_date)
    if section:
        stmt = stmt.where(ModelsNewsArticle.topic == section)

    result = await db.execute(stmt)
    return result.scalars().all()




@router.delete("/")
async def delete_news(
    input_id: int = Query(description="Input article ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a news article by ID.
    """
    stmt = select(ModelsNewsArticle).where(ModelsNewsArticle.id == input_id)
    result = await db.execute(stmt)
    db_news = result.scalars().first()
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_news)
    await db.commit()
    return {"message": "News deleted successfully"}


# @router.put("/")
# async def update_news(
#     news_id: int = Query(description="Input article ID"),
#     news_update: SchemasNewsArticleUpdate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Update a news article by ID.
#     """
#     stmt = select(ModelsNewsArticle).where(ModelsNewsArticle.news_id == news_id)
#     result = await db.execute(stmt)
#     db_news = result.scalars().first()
#     if db_news is None:
#         raise HTTPException(status_code=404, detail="News not found")
#
#     update_data = news_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(db_news, field, value)
#
#     await db.commit()
#     await db.flush()
#     await db.refresh(db_news)
#     return db_news
