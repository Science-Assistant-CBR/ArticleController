from datetime import datetime
from fastapi import Query
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from common.common.science_article import ScienceArticle as SchemasScienceArticle
from common.common.science_article import ScienceArticleCreate as SchemasScienceArticleCreate
from app.models.science_article import ScienceArticle as ModelsScienceArticle
from common.common.routes_science import ScienceArticleFilter

router = APIRouter(prefix="/science", tags=["science"])


@router.post("/articles", response_model=SchemasScienceArticle)
async def create_articles(
    article_data: SchemasScienceArticleCreate,
    request: Request, db: AsyncSession = Depends(get_db)
):

    db_science_article = ModelsScienceArticle(**article_data.model_dump())
    db.add(db_science_article)
    await db.commit()
    await db.flush()
    await db.refresh(db_science_article)


    text = db_science_article.full_summary
    metadata = {"id": int(db_science_article.id)}

    await request.app.state.rag.science_embedder.store_embedding(
        text=text, point_id=db_science_article.id, metadata=metadata
    )

    return db_science_article


@router.get("/articles", response_model=List[SchemasScienceArticle])
async def get_articles(
    input_id: Optional[int] = Query(None, description="Фильтрация по id статьи"),
    title: str = Query(None, description="Filter by article title (partial match)"),
    source_name: str = Query(None, description="Filter by source name"),
    start_date: datetime = Query(None, description="Start of publication date range"),
    end_date: datetime = Query(None, description="End of publication date range"),
    section: str = Query(None, description="Filter by article section"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ModelsScienceArticle)

    if input_id:
        stmt = stmt.where(ModelsScienceArticle.id == input_id)
    if title:
        stmt = stmt.where(ModelsScienceArticle.title.ilike(f"%{title}%"))
    if source_name:
        stmt = stmt.where(ModelsScienceArticle.source_name == source_name)
    if start_date:
        stmt = stmt.where(ModelsScienceArticle.published_date >= start_date)
    if end_date:
        stmt = stmt.where(ModelsScienceArticle.published_date <= end_date)
    if section:
        stmt = stmt.where(ModelsScienceArticle.section == section)


    result = await db.execute(stmt)
    return result.scalars().all()



@router.delete("/articles")
async def delete_article(input_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an article by ID.
    """
    stmt = select(ModelsScienceArticle).where(ModelsScienceArticle.id == input_id)
    result = await db.execute(stmt)
    db_science = result.scalars().first()
    if db_science is None:
        raise HTTPException(status_code=404, detail="News not found")

    await db.delete(db_science)
    await db.commit()
    return {"message": "News deleted successfully"}


#
#
# @router.put("/{input_id}")
#
# async def update_articles(
#     input_id: int, articles_update: SchemasScienceArticleUpdate, db: AsyncSession = Depends(get_db)
# ):
#     """
#     Update an articles article by ID.
#     """
#     stmt = select(ModelsScienceArticle).where(ModelsScienceArticle.id == input_id)
#     result = await db.execute(stmt)
#     db_articles = result.scalars().first()
#     if db_articles is None:
#         raise HTTPException(status_code=404, detail="Articles not found")
#
#     update_data = articles_update.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(db_articles, field, value)
#
#     await db.commit()
#     await db.flush()
#     await db.refresh(db_articles)
#     return db_articles
