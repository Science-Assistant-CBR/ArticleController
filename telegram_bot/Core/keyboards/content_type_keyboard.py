from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Включить рассылку дайджестов")
        ],
        [
            KeyboardButton(text="Выключить рассылку дайджестов")
        ]
    ],
    resize_keyboard=True
)

settings_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Научные статьи"),
            KeyboardButton(text="Новости")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)