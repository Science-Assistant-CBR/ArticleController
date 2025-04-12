from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import httpx
import asyncio

from Core.keyboards.content_type_keyboard import main_kb, settings_kb
from Core.utils.scheduler import add_user_to_mailing, remove_user_from_mailing
from Core.settings import settings
from Core.utils.states import user_states

# Создаем клиент один раз при запуске
client = httpx.AsyncClient(timeout=30.0)

router = Router()
router.message.filter(F.chat.type != 'supergroup')

@router.message(CommandStart())
async def get_start(message: Message):
    # Устанавливаем режим по умолчанию для нового пользователя
    user_states[message.from_user.id] = {"mode": "science"}  # По умолчанию научные статьи
    await message.answer(
        f'Здравствуйте, {message.from_user.first_name}!\n'
        'Выберите действие:',
        reply_markup=main_kb
    )

@router.message(F.text == 'Включить рассылку дайджестов')
async def enable_mailing(message: Message, bot: Bot):
    user_id = message.from_user.id
    if add_user_to_mailing(bot, user_id):
        await message.answer('Рассылка успешно включена!')
    else:
        await message.answer('Рассылка уже включена.')

@router.message(F.text == 'Выключить рассылку дайджестов')
async def disable_mailing(message: Message):
    user_id = message.from_user.id
    if remove_user_from_mailing(user_id):
        await message.answer('Рассылка отключена.')
    else:
        await message.answer('Рассылка уже была отключена.')

@router.message(Command(commands=['help']))
async def get_help(message: Message):
    await message.answer(
        f'Включите рассылку дайджестов, чтобы получать их каждые {settings.bots.timedelta} дней.\n')

@router.message(F.text == 'Настройки')
async def show_settings(message: Message):
    await message.answer(
        "Выберите режим работы:",
        reply_markup=settings_kb
    )

@router.message(F.text == 'Назад')
async def back_to_main(message: Message):
    await message.answer(
        "Возвращаемся в главное меню",
        reply_markup=main_kb
    )

@router.message(F.text.in_(["Научные статьи", "Новости"]))
async def set_mode(message: Message):
    user_id = message.from_user.id
    mode = "science" if message.text == "Научные статьи" else "news"
    
    # Обновляем состояние пользователя
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["mode"] = mode
    
    await message.answer(
        f"Режим установлен: {message.text}\n",
        reply_markup=main_kb
    )

@router.message()
async def handle_message(message: Message):
    try:
        # Проверяем, не является ли сообщение командой или кнопкой
        if message.text in ["Настройки", "Включить рассылку дайджестов", "Выключить рассылку дайджестов", "Научные статьи", "Новости", "Назад"]:
            return
        await message.answer(f"Cообщение отправляется...")
        
        # Подготавливаем данные для запроса
        request_data = {
            "raw_return": False,
            "query_text": message.text,
            "queries_count": 1,
            "top_k": 5,
            "source_name": None,
            "start_date": None,
            "end_date": None,
            "relevance": 0
        }
        
        await message.answer(f"Подготовлены данные для запроса: {request_data}")
        
        try:
            response = await client.post(
                "http://api:8000/api/v1/vectors/science",  # Изменено на имя сервиса в Docker сети
                json=request_data
            )
            await message.answer(f"Получен ответ от сервера. Код: {response.status_code}")
        except httpx.ConnectError as e:
            await message.answer(f"Ошибка подключения к серверу: {str(e)}")
            return
        except httpx.TimeoutException as e:
            await message.answer(f"Таймаут при подключении к серверу: {str(e)}")
            return
        except httpx.RequestError as e:
            await message.answer(f"Ошибка при отправке запроса: {str(e)}")
            return

        if response.status_code != 200:
            error_message = f"Ошибка сервера. Код: {response.status_code}\n"
            try:
                error_details = response.json()
                error_message += f"Детали: {error_details}"
            except:
                error_message += f"Текст ответа: {response.text}"
            await message.answer(error_message)
        else:
            # Получаем данные из ответа
            response_data = response.json()
            
            # Формируем сообщение с результатами
            result_message = f"Результаты поиска:\n {response_data}\n"
            
            await message.answer(result_message)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}\nТип ошибки: {type(e).__name__}\nМесто ошибки: {e.__traceback__.tb_lineno}")

# Функция для закрытия клиента при завершении работы
async def close_client():
    await client.aclose()

