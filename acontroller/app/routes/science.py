from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acontroller.app.database import get_db
from common.common.science_article import ScienceArticle as SchemasScienceArticle
from common.common.science_article import ScienceArticleCreate as SchemasScienceArticleCreate
from acontroller.app.models.science_article import ScienceArticle as ModelsScienceArticle
from common.common.routes_science import ScienceArticleFilter
from common.common.routes_actual import ActualList, ActualItem

router = APIRouter(prefix="/science", tags=["science"])


@router.get("/articles", response_model=List[SchemasScienceArticle])
async def get_articles(
    filters: Annotated[ScienceArticleFilter, Query()],
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ModelsScienceArticle)

    if filters.title:
        stmt = stmt.where(ModelsScienceArticle.title.ilike(f"%{filters.title}%"))
    if filters.source_name:
        stmt = stmt.where(ModelsScienceArticle.sphere == filters.sphere)
    if filters.source_name:
        stmt = stmt.where(ModelsScienceArticle.source_name == filters.source_name)
    if filters.start_date:
        stmt = stmt.where(ModelsScienceArticle.published_date >= filters.start_date)
    if filters.end_date:
        stmt = stmt.where(ModelsScienceArticle.published_date <= filters.end_date)
    if filters.section:
        stmt = stmt.where(ModelsScienceArticle.section == filters.section)

    result = await db.execute(stmt.offset(filters.skip).limit(filters.limit))
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


@router.get("/articles/{input_id}", response_model=SchemasScienceArticle)
async def get_science_article_by_id(input_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific science article by ID.
    """
    stmt = select(ModelsScienceArticle).where(ModelsScienceArticle.id == input_id)
    result = await db.execute(stmt)
    articles = result.scalars().first()
    if articles is None:
        raise HTTPException(status_code=404, detail="Science Articles not found")
    return articles


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


@router.get("/actual", response_model=ActualList)
async def get_actual(
    skip: int = 0,
    limit: int = 20,
):
    # --- Временные моковые данные ---
    mock_actual = [
        ActualItem(
            id=1,
            title="Банк России: мониторинг отраслевых финансовых потоков - рост деловой активности продолжается",
            body="В марте объем финансовых поступлений, проведенных через Банк России, оказался близок к февральскому значению и на 8,2% выше среднего уровня IV квартала 2024 года. Без учета добывающих отраслей, производства нефтепродуктов и государственного управления входящие платежи увеличились на 17,1%, в то время как в среднем за I квартал рост составил 14,8%."
        ),
        ActualItem(
            id=2,
            title="ECB Consumer Expectations Survey results – February 2025",
            body="Median consumer perceptions of inflation over the previous 12 months decreased, while median inflation expectations for the next 12 months and for three years ahead remained unchanged. Expectations for nominal income growth over the next 12 months increased, while expectations for spending growth over the next 12 months decreased."
        ),
        ActualItem(
            id=3,
            title="ECB launches pilot project for research access to confidential statistical data",
            body="Anonymised data on individual banks in the entire euro area will be available to academic researchers. Several access modes will be tested with a view to establishing a permanent framework for research access to ECB data."
        ),
    ]

    total_mock = len(mock_actual)
    paginated_mocks = mock_actual[skip : skip + limit]

    return ActualList(items=paginated_mocks, total=total_mock, skip=skip, limit=limit)

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
