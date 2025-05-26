from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from acontroller.app.database import get_db
from acontroller.app.models.news_article import NewsArticle as ModelsNewsArticle
from acontroller.app.models.science_article import ScienceArticle as ModelsScienceArticle

from common.common.routes_vectors import VectorSearch
from acontroller.app.services.rag import OpenAIMessage
from acontroller.app.utils.utils import trim_prompt_to_tokens

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.post("/science")
async def vector_search(
        search_params: VectorSearch,
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    """
    Search for similar news articles using RAG with filtering options.

    Returns:
        List of similar news articles' {"id": "score"}  where score is how relevant it is from 0 to 1.
        Or a complete OpenAI LLM answer based on raw_return argument.
        Raw means without OpenAI completion.
    """

    table = ModelsScienceArticle
    search_params.query_text = trim_prompt_to_tokens(search_params.query_text,
                                                     8191,
                                                     "text-embedding-3-large")
    query_text_openai_message = OpenAIMessage(
        role="user", content=search_params.query_text)

    stmt = select(table)
    if search_params.source_name:
        stmt = stmt.where(table.source_name == search_params.source_name)
    if search_params.start_date:
        stmt = stmt.where(table.published_date >= search_params.start_date)
    if search_params.end_date:
        stmt = stmt.where(table.published_date <= search_params.end_date)

    # Получаем все результаты и собираем id
    result_filter_ids = await db.execute(stmt)
    article_ids = [cur.id for cur in result_filter_ids.scalars().all()]

    # Применяем ограничение max_top_k
    top_k = min(search_params.top_k,
                request.app.state.rag.science_embedder.max_top_k)

    top_similar_points: list[dict] = []

    similar_points = await request.app.state.rag.science_embedder.search_similar(
        text=search_params.query_text, top_k=top_k, filter_ids=article_ids
    )

    top_similar_points.extend(similar_points)
    # logger.info(f"first len found: {len(top_similar_docs)}")
    # for docs in top_similar_points:
    #     logger.info(f"id: {docs["id"]}")
    for i in range(1, search_params.queries_count):
        rephrase_query_prompt_text = request.app.state.rag.generate_rephrase_promt()
        rephrase_query_prompt_text = trim_prompt_to_tokens(rephrase_query_prompt_text,
                                                           8191,
                                                           "text-embedding-3-large"
                                                           )
        rephrase_query_prompt_openai_message = OpenAIMessage(
            role="user", content=rephrase_query_prompt_text)
        rephrase_query_prompt_list = [
            rephrase_query_prompt_openai_message, query_text_openai_message]
        rephrase_query_result_text = await request.app.state.rag.llm.create_completion(chat=rephrase_query_prompt_list)
        similar_points = await request.app.state.rag.science_embedder.search_similar(
            text=rephrase_query_result_text, top_k=top_k, filter_ids=article_ids
        )
        # logger.info(f"each len found: {len(similar_docs)}")
        top_similar_points.extend(similar_points)

    best_unique_points = {}

    for point in top_similar_points:
        doc_id = point["id"]
        if doc_id not in best_unique_points or point["score"] > best_unique_points[doc_id]["score"]:
            best_unique_points[doc_id] = point

    # Берём top_k лучших по score после удаления дублей
    final_top_similar_points = sorted(
        best_unique_points.values(),
        key=lambda x: x["score"],
        reverse=True
    )[:top_k]

    # logger.info(f"final_top: {len(final_top_similar_points)}")

    # for points in final_top_similar_points:
    #     logger.info(f"id: {points["id"]}, score: {points["score"]}")
    # logger.info(f"ids: {len(final_top_similar_points_ids)}")

    # logger.info(f"objects: {len(result_rows)}")

    if search_params.raw_return:
        result_dict = [
            {
                "id": point["id"],
                "score": point["score"]
            }
            for point in final_top_similar_points
        ]
        return result_dict

    final_top_similar_points_ids = [item["id"]
                                    for item in final_top_similar_points]
    result_objects = await db.execute(select(table).where(table.id.in_(final_top_similar_points_ids)))
    result_rows = result_objects.scalars().all()
    text_result_rows = [row.full_summary for row in result_rows]
    sum_up_prompt_text = request.app.state.rag.generate_prompt()
    full_relevant_articles_texts = "\n".join(text_result_rows)
    full_relevant_articles_texts = trim_prompt_to_tokens(full_relevant_articles_texts,
                                                         100000,
                                                         "gpt-4o")
    sum_up_prompt_text_openai_message = OpenAIMessage(
        role="user", content=sum_up_prompt_text)
    full_relevant_articles_texts_openai_message = OpenAIMessage(
        role="user", content=full_relevant_articles_texts)

    # Перефразируем пользовательский запрос на всякий случай для лучшего ответа
    rephrase_query_prompt_text = request.app.state.rag.generate_rephrase_promt()
    rephrase_query_prompt_text_openai_message = OpenAIMessage(
        role="user", content=rephrase_query_prompt_text)
    rephrase_query_prompt_list = [
        rephrase_query_prompt_text_openai_message,
        query_text_openai_message,
    ]
    rephrase_query_result_text = await request.app.state.rag.llm.create_completion(rephrase_query_prompt_list)
    rephrase_query_result_text_openai_message = OpenAIMessage(
        role="user", content=rephrase_query_result_text)

    sum_up_prompt_list = [sum_up_prompt_text_openai_message,
                          rephrase_query_result_text_openai_message,
                          full_relevant_articles_texts_openai_message]

    # for object in sum_up_prompt_list:
    #     logger.info(f"object of prompt list: {object.content}")
    sum_up_llm_answer = await request.app.state.rag.llm.create_completion(chat=sum_up_prompt_list)

    return sum_up_llm_answer


@router.post("/news")
async def vector_search_news(
        search_params: VectorSearch,
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    """
    Search for similar news articles using RAG with filtering options.

    The top_k parameter is limited to the configured maximum value.

    Returns:
        List of similar news articles
    """

    table = ModelsNewsArticle
    search_params.query_text = trim_prompt_to_tokens(search_params.query_text,
                                                     8191,
                                                     "text-embedding-3-large")
    query_text_openai_message = OpenAIMessage(
        role="user", content=search_params.query_text)

    stmt = select(table)
    if search_params.source_name:
        stmt = stmt.where(table.source_name == search_params.source_name)
    if search_params.start_date:
        stmt = stmt.where(table.publication_datetime >=
                          search_params.start_date)
    if search_params.end_date:
        stmt = stmt.where(table.publication_datetime <= search_params.end_date)

    # Получаем все результаты и собираем id
    result_filter_ids = await db.execute(stmt)
    article_ids = [cur.id for cur in result_filter_ids.scalars().all()]

    # Применяем ограничение max_top_k
    top_k = min(search_params.top_k,
                request.app.state.rag.news_embedder.max_top_k)

    top_similar_points: list[dict] = []

    similar_points = await request.app.state.rag.news_embedder.search_similar(
        text=search_params.query_text, top_k=top_k, filter_ids=article_ids
    )

    top_similar_points.extend(similar_points)
    # logger.info(f"first len found: {len(top_similar_docs)}")
    # for docs in top_similar_points:
    #     logger.info(f"id: {docs["id"]}")
    for i in range(1, search_params.queries_count):
        rephrase_query_prompt_text = request.app.state.rag.generate_rephrase_promt()
        rephrase_query_prompt_text = trim_prompt_to_tokens(rephrase_query_prompt_text,
                                                           8191,
                                                           "text-embedding-3-large"
                                                           )
        rephrase_query_prompt_openai_message = OpenAIMessage(
            role="user", content=rephrase_query_prompt_text)
        rephrase_query_prompt_list = [
            rephrase_query_prompt_openai_message, query_text_openai_message]
        rephrase_query_result_text = await request.app.state.rag.llm.create_completion(chat=rephrase_query_prompt_list)
        similar_points = await request.app.state.rag.news_embedder.search_similar(
            text=rephrase_query_result_text, top_k=top_k, filter_ids=article_ids
        )
        # logger.info(f"each len found: {len(similar_docs)}")
        top_similar_points.extend(similar_points)

    best_unique_points = {}

    for point in top_similar_points:
        doc_id = point["id"]
        if doc_id not in best_unique_points or point["score"] > best_unique_points[doc_id]["score"]:
            best_unique_points[doc_id] = point

    # Берём top_k лучших по score после удаления дублей
    final_top_similar_points = sorted(
        best_unique_points.values(),
        key=lambda x: x["score"],
        reverse=True
    )[:top_k]

    # logger.info(f"final_top: {len(final_top_similar_points)}")

    # for points in final_top_similar_points:
    #     logger.info(f"id: {points["id"]}, score: {points["score"]}")
    # logger.info(f"ids: {len(final_top_similar_points_ids)}")

    # logger.info(f"objects: {len(result_rows)}")

    if search_params.raw_return:
        result_dict = [
            {
                "id": point["id"],
                "score": point["score"]
            }
            for point in final_top_similar_points
        ]
        return result_dict

    final_top_similar_points_ids = [item["id"]
                                    for item in final_top_similar_points]
    result_objects = await db.execute(select(table).where(table.id.in_(final_top_similar_points_ids)))
    result_rows = result_objects.scalars().all()
    text_result_rows = [row.text for row in result_rows]

    sum_up_prompt_text = request.app.state.rag.generate_prompt()
    full_relevant_articles_texts = "\n".join(text_result_rows)
    full_relevant_articles_texts = trim_prompt_to_tokens(full_relevant_articles_texts,
                                                         100000,
                                                         "gpt-4o")
    sum_up_prompt_text_openai_message = OpenAIMessage(
        role="user", content=sum_up_prompt_text)
    full_relevant_articles_texts_openai_message = OpenAIMessage(
        role="user", content=full_relevant_articles_texts)

    # Перефразируем пользовательский запрос на всякий случай для лучшего ответа
    rephrase_query_prompt_text = request.app.state.rag.generate_rephrase_promt()
    rephrase_query_prompt_text_openai_message = OpenAIMessage(
        role="user", content=rephrase_query_prompt_text)
    rephrase_query_prompt_list = [
        rephrase_query_prompt_text_openai_message,
        query_text_openai_message,
    ]
    rephrase_query_result_text = await request.app.state.rag.llm.create_completion(rephrase_query_prompt_list)
    rephrase_query_result_text_openai_message = OpenAIMessage(
        role="user", content=rephrase_query_result_text)

    sum_up_prompt_list = [sum_up_prompt_text_openai_message,
                          rephrase_query_result_text_openai_message,
                          full_relevant_articles_texts_openai_message]

    # for object in sum_up_prompt_list:
    #     logger.info(f"object of prompt list: {object.content}")
    sum_up_llm_answer = await request.app.state.rag.llm.create_completion(chat=sum_up_prompt_list)

    return sum_up_llm_answer
