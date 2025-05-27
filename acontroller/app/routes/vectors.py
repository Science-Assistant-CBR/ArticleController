from fastapi import APIRouter, Depends, Request, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from acontroller.app.database import get_db
from acontroller.app.models.news_article import NewsArticle as ModelsNewsArticle
from acontroller.app.models.science_article import ScienceArticle as ModelsScienceArticle

from common.common.routes_vectors import VectorSearch
from acontroller.app.services.rag import OpenAIMessage, logger
from acontroller.app.utils.utils import trim_prompt_to_tokens

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.post("/science")
async def vector_search(
    request: Request,
    search_params: VectorSearch = Body(),        # получаем параметры поиска из тела запроса
    db: AsyncSession = Depends(get_db),           # асинхронная сессия SQLAlchemy
):
    """
    Поиск похожих научных статей через RAG с фильтрацией и опцией «raw_return».
    - Если raw_return=True, возвращаем только список {"id": ..., "score": ...}.
    - Иначе — генерируем итоговый текст с помощью LLM и даём URL-источники.
    """

    # 1) Определяем модель таблицы
    table = ModelsScienceArticle

    # 2) Обрезаем исходный запрос до лимита токенов для текстового энкодера
    search_params.query_text = trim_prompt_to_tokens(
        search_params.query_text,
        max_tokens=8191,
        model="text-embedding-3-large",
    )
    # 2.1) Упаковываем запрос в сообщение для OpenAI
    query_text_openai_message = OpenAIMessage(
        role="user",
        content=search_params.query_text,
    )

    # 3) Собираем базовый SQL-запрос с фильтрами по source_name и sphere
    stmt = select(table)
    if search_params.source_name:
        stmt = stmt.where(table.source_name.ilike(search_params.source_name))
    if search_params.sphere:
        stmt = stmt.where(table.sphere.ilike(search_params.sphere))
    if search_params.start_date:
        stmt = stmt.where(table.published_date >= search_params.start_date)
    if search_params.end_date:
        stmt = stmt.where(table.published_date <= search_params.end_date)

    # 4) Выполняем запрос и извлекаем все id статей, соответствующих фильтрам
    result_filter_ids = await db.execute(stmt)
    article_ids = [row.id for row in result_filter_ids.scalars().all()]

    # 5) Если по фильтрам ничего не найдено — 404
    if not article_ids:
        raise HTTPException(
            status_code=404,
            detail="По вашему запросу не найдено релевантных статей",
        )

    # 6) Ограничиваем top_k с учётом настроек энкодера
    top_k = min(
        search_params.top_k,
        request.app.state.rag.science_embedder.max_top_k,
    )

    # 7) Первый проход поиска похожих embedding-точек
    top_similar_points: list[dict] = []
    similar_points = await request.app.state.rag.science_embedder.search_similar(
        text=search_params.query_text,
        top_k=top_k,
        filter_ids=article_ids,
    )
    top_similar_points.extend(similar_points)

    # 8) Повторяем поиск с перефразированием для повышения охвата
    for _ in range(1, search_params.queries_count):
        # 8.1) Генерируем текст-подсказку для перефразирования
        rephrase_text = request.app.state.rag.generate_rephrase_promt()
        rephrase_text = trim_prompt_to_tokens(
            rephrase_text,
            max_tokens=8191,
            model="text-embedding-3-large",
        )
        # 8.2) Упаковываем исходный и перефразированный тексты для LLM
        rephrase_messages = [
            OpenAIMessage(role="user", content=rephrase_text),
            query_text_openai_message,
        ]
        # 8.3) Получаем перефразированный запрос
        rephrase_result = await request.app.state.rag.llm.create_completion(
            chat=rephrase_messages
        )
        # 8.4) Ищем похожие документы по новому тексту
        similar_points = await request.app.state.rag.science_embedder.search_similar(
            text=rephrase_result,
            top_k=top_k,
            filter_ids=article_ids,
        )
        top_similar_points.extend(similar_points)

    # 9) Убираем дубли, оставляя запись с максимальным score для каждого id
    best_unique_points: dict[int, dict] = {}
    for point in top_similar_points:
        doc_id = point["id"]
        score = point["score"]
        if doc_id not in best_unique_points or score > best_unique_points[doc_id]["score"]:
            best_unique_points[doc_id] = point

    # 10) Сортируем по убыванию score и берём top_k
    final_top_similar = sorted(
        best_unique_points.values(),
        key=lambda x: x["score"],
        reverse=True,
    )[:top_k]

    # 11) Если raw_return=True — возвращаем только id и score, без LLM
    if search_params.raw_return:
        return [
            {"id": point["id"], "score": point["score"]}
            for point in final_top_similar
        ]

    # 12) Иначе — собираем полные объекты по id из БД
    final_ids = [item["id"] for item in final_top_similar]
    result_objects = await db.execute(
        select(table).where(table.id.in_(final_ids))
    )
    result_rows = result_objects.scalars().all()

    # 13) Готовим тексты для промпта суммаризации
    text_result_rows = [
        f"Название – {row.title}, Текст – {row.full_summary}"
        for row in result_rows
    ]
    full_texts = "\n".join(text_result_rows)
    full_texts = trim_prompt_to_tokens(
        full_texts,
        max_tokens=100000,
        model="gpt-4o",
    )

    # 14) Формируем список «Источники: Название [URL] [дата]»
    relevant_articles_names_and_links = [
        f"{row.title} [{row.url}]{f' [{row.published_date.date()}]' if row.published_date else ''}"
        for row in result_rows
    ]

    # 15) Генерируем промпт для итоговой LLM-композиции
    sum_up_prompt = request.app.state.rag.generate_prompt()
    sum_up_messages = [
        OpenAIMessage(role="user", content=sum_up_prompt),
        query_text_openai_message,
        OpenAIMessage(role="user", content=full_texts),
    ]

    # 16) Получаем финальный ответ от LLM
    sum_up_llm_answer = await request.app.state.rag.llm.create_completion(
        chat=sum_up_messages
    )

    # 17) Добавляем блок «Источники» к ответу и возвращаем
    final_answer = (
        sum_up_llm_answer
        + "\n\n\n\nИсточники:\n\n"
        + "\n\n".join(relevant_articles_names_and_links)
    )
    return final_answer


@router.post("/news")
async def vector_search(
    search_params: VectorSearch,              # параметры поиска: текст, фильтры по дате и источнику, топ-K и число итераций
    request: Request,                         # объект запроса FastAPI, из него берём доступ к RAG-энкодеру и LLM
    db: AsyncSession = Depends(get_db),       # асинхронная сессия SQLAlchemy для доступа к базе
):
    """
    Поиск похожих новостных статей через RAG с возможностью фильтрации по дате и источнику.
    - search_params.top_k ограничивается максимальным значением энкодера.
    - Возвращает строку с итоговым ответом и списком источников.
    """

    # 1. Выбираем таблицу для запросов
    table = ModelsNewsArticle

    # 2. Обрезаем исходный запрос под лимит токенов модели энкодера
    search_params.query_text = trim_prompt_to_tokens(
        search_params.query_text,
        max_tokens=8191,
        model="text-embedding-3-large",
    )
    # Упаковываем текст в формат сообщения OpenAI
    query_text_openai_message = OpenAIMessage(
        role="user",
        content=search_params.query_text,
    )

    # 3. Строим SQL-запрос с базовой выборкой всех записей
    stmt = select(table)
    # 3.1. Фильтр по источнику, если задан
    if search_params.source_name:
        stmt = stmt.where(table.source_name == search_params.source_name)
    # 3.2. Фильтр по дате начала, если задан
    if search_params.start_date:
        stmt = stmt.where(table.publication_datetime >= search_params.start_date)
    # 3.3. Фильтр по дате конца, если задан
    if search_params.end_date:
        stmt = stmt.where(table.publication_datetime <= search_params.end_date)

    # 4. Выполняем фильтрованный запрос и собираем все id статей
    result_filter_ids = await db.execute(stmt)
    article_ids = [cur.id for cur in result_filter_ids.scalars().all()]

    # 5. Если ничего не найдено — возвращаем 404
    if not article_ids:
        raise HTTPException(
            status_code=404,
            detail="По вашему запросу не найдено релевантных статей",
        )

    # 6. Ограничиваем топ-K пользователем и конфигурацией энкодера
    top_k = min(
        search_params.top_k,
        request.app.state.rag.news_embedder.max_top_k,
    )

    # 7. Первый проход поиска похожих точек (embedding search)
    top_similar_points: list[dict] = []
    similar_points = await request.app.state.rag.news_embedder.search_similar(
        text=search_params.query_text,
        top_k=top_k,
        filter_ids=article_ids,
    )
    top_similar_points.extend(similar_points)

    # 8. Дополнительные перефразирования и повторный поиск (для повышения recall)
    for _ in range(1, search_params.queries_count):
        # 8.1. Генерируем новый запрос для перефразирования
        rephrase_text = request.app.state.rag.generate_rephrase_promt()
        rephrase_text = trim_prompt_to_tokens(
            rephrase_text, 8191, "text-embedding-3-large"
        )
        # 8.2. Упаковываем оба сообщения для LLM
        rephrase_messages = [
            OpenAIMessage(role="user", content=rephrase_text),
            query_text_openai_message,
        ]
        # 8.3. Получаем перефразированный текст от LLM
        rephrase_result = await request.app.state.rag.llm.create_completion(
            chat=rephrase_messages
        )
        # 8.4. Ищем похожие документы по новому тексту
        similar_points = await request.app.state.rag.news_embedder.search_similar(
            text=rephrase_result,
            top_k=top_k,
            filter_ids=article_ids,
        )
        top_similar_points.extend(similar_points)

    # 9. Убираем дубли, оставляя для каждого id запись с максимальным скором
    best_unique_points: dict[int, dict] = {}
    for point in top_similar_points:
        doc_id = point["id"]
        score = point["score"]
        if doc_id not in best_unique_points or score > best_unique_points[doc_id]["score"]:
            best_unique_points[doc_id] = point

    # 10. Сортируем по скору и берём топ-K
    final_top_similar = sorted(
        best_unique_points.values(),
        key=lambda x: x["score"],
        reverse=True,
    )[:top_k]

    # 11. Извлекаем только id для финального выборочного SQL-запроса
    final_ids = [item["id"] for item in final_top_similar]
    result_objects = await db.execute(
        select(table).where(table.id.in_(final_ids))
    )
    result_rows = result_objects.scalars().all()

    # 12. Формируем тексты статей для итогового промпта LLM
    text_result_rows = [
        f"Название - {row.title}, Текст - {row.text}"
        for row in result_rows
    ]

    # 13. Готовим список источников для вывода
    relevant_articles_names_and_links = [
        f"{row.title} [{row.url}]{f' [{row.publication_datetime.date()}]' if row.publication_datetime else ''}"
        for row in result_rows
    ]

    # 14. Генерируем промпт для суммаризации
    sum_up_prompt = request.app.state.rag.generate_prompt()
    full_texts = "\n".join(text_result_rows)
    # 14.1. Обрезаем до лимита токенов для модели диалога (gpt-4o)
    full_texts = trim_prompt_to_tokens(full_texts, 100000, "gpt-4o")

    # 15. Упаковываем сообщения для LLM: суммаризация + исходный запрос + тексты статей
    sum_up_messages = [
        OpenAIMessage(role="user", content=sum_up_prompt),
        query_text_openai_message,
        OpenAIMessage(role="user", content=full_texts),
    ]

    # 16. Получаем от LLM итоговый ответ
    sum_up_llm_answer = await request.app.state.rag.llm.create_completion(
        chat=sum_up_messages
    )

    # 17. Добавляем в конец списка «Источники»
    final_answer = (
        sum_up_llm_answer
        + "\n\n\n\nИсточники:\n\n"
        + "\n\n".join(relevant_articles_names_and_links)
    )

    # 18. Возвращаем финальный текст клиенту
    return final_answer
