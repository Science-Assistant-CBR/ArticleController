from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


class MailingStates(StatesGroup):
    ON = State()
    OFF = State()

class UserStates(StatesGroup):
    mode = State()  # Режим работы: scientific или news

# Создаем хранилище состояний
storage = MemoryStorage()

# Словарь для хранения состояний пользователей
user_states = {}