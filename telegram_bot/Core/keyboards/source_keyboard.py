from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Словарь с источниками: ключ - callback_data, значение - отображаемое имя
SOURCES = {
    "source_imf": "International Monetary Fund(IMF)",
    "source_ssrn": "Social Science Research Network(SSRN)",
    "source_bis": "Bank for International Settlements(BIS)"
}

def get_source_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором источников публикации
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=callback_data)]
        for callback_data, name in SOURCES.items()
    ])
    return keyboard 