from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
class MailingStates(StatesGroup):
    ON = State()
    OFF = State()

class UserStates(StatesGroup):
    mode = State()  # Режим работы: scientific или news

class RequestStates(StatesGroup):
    sphere: str = State()
    start_date: datetime = State()
    end_date: datetime = State()
    source: str = State()
# Создаем хранилище состояний
storage = MemoryStorage()

# Словарь для хранения состояний пользователей
user_states = {}