from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

filter_kb = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text = "Аналитика"),
            KeyboardButton(text = "Наука"),
        ],

        [
            KeyboardButton(text = "Дата публикации"),
            KeyboardButton(text = "Источник публикации"),
        ],

        [
            KeyboardButton(text = "Cбросить настройки"),
            KeyboardButton(text = "Назад")
        ]
    ],
    resize_keyboard=True
)