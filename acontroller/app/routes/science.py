from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acontroller.app.database import get_db
from common.common.science_article import ScienceArticle as SchemasScienceArticle
from common.common.science_article import ScienceArticleCreate as SchemasScienceArticleCreate
from acontroller.app.models.science_article import ScienceArticle as ModelsScienceArticle
from common.common.routes_science import ScienceArticleFilter

router = APIRouter(prefix="/science", tags=["science"])


@router.get("/articles", response_model=List[SchemasScienceArticle])
async def get_articles(
    filters: ScienceArticleFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ModelsScienceArticle)

    if filters.title:
        stmt = stmt.where(ModelsScienceArticle.title.ilike(f"%{filters.title}%"))
    if filters.sphere:
        stmt = stmt.where(ModelsScienceArticle.sphere.ilike(filters.sphere))
    if filters.source_name:
        stmt = stmt.where(ModelsScienceArticle.source_name.ilike(filters.source_name))
    if filters.start_date:
        stmt = stmt.where(ModelsScienceArticle.published_date >= filters.start_date)
    if filters.end_date:
        stmt = stmt.where(ModelsScienceArticle.published_date <= filters.end_date)
    if filters.section:
        stmt = stmt.where(ModelsScienceArticle.section.ilike(filters.section))
    if filters.id:
        stmt = stmt.where(ModelsScienceArticle.id == filters.id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/articles", response_model=SchemasScienceArticle)
async def create_articles(
    article_data: SchemasScienceArticleCreate, request: Request, db: AsyncSession = Depends(get_db)
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



@router.delete("/articles/{input_id}")
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
