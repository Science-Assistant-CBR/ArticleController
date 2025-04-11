import tiktoken


def trim_prompt_to_tokens(prompt: str, max_tokens: int = 8192, model: str = "gpt-4") -> str:
    """
    Урезает текст до определенного числа токенов для запроса к OpenAI
    """

    # Выбираем нужный tokenizer
    encoding = tiktoken.encoding_for_model(model)

    # Преобразуем текст в токены
    tokens = encoding.encode(prompt)

    # Обрезаем, если нужно
    if len(tokens) <= max_tokens:
        return prompt  # ничего не обрезаем

    # Обрезаем токены и декодируем обратно в текст
    trimmed_tokens = tokens[:max_tokens]
    trimmed_prompt = encoding.decode(trimmed_tokens)

    return trimmed_prompt
