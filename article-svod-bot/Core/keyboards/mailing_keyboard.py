from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = 'Включить рассылку дайджестов')],
        [KeyboardButton(text = 'Выключить рассылку дайджестов')]
    ],
    resize_keyboard=True
)
