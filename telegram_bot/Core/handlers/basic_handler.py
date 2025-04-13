from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import httpx
import asyncio

from Core.keyboards.content_type_keyboard import main_kb, settings_kb
from Core.settings import settings
from Core.utils.states import user_states

client = httpx.AsyncClient(timeout=30.0)

router = Router()
router.message.filter(F.chat.type != 'supergroup')

@router.message(CommandStart())
async def get_start(message: Message):
    # Устанавливаем режим по умолчанию для нового пользователя
    user_states[message.from_user.id] = {"mode": "science"}  # По умолчанию научные статьи
    await message.answer(
        f'Здравствуйте, {message.from_user.first_name}!\n'
        'Напишите Ваш вопрос в чат.\n'
        '/help -  для справки',
        reply_markup=main_kb
    )

@router.message(Command(commands=['help']))
async def get_help(message: Message):
    await message.answer(
        'Отправьте мне текстовое сообщение, и я сформулирую ответ по релевантным статьям.\n'
        'Используйте кнопку "Настройки" для выбора типа статей (научные/новостные).')

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
        if message.text in ["Настройки", "Научные статьи", "Новости", "Назад"]:
            return
        
        # Отправляем и сохраняем сообщение о процессе
        processing_msg = await message.reply("Cообщение обрабатывается...")
        
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
        
        try:
            response = await client.post(
                f"http://acontroller:8000/api/v1/vectors/{user_states[message.from_user.id]['mode']}", 
                json=request_data
            )
        except httpx.ConnectError as e:
            await processing_msg.delete()
            await message.answer(f"Ошибка подключения к серверу: {str(e)}")
            return
        except httpx.TimeoutException as e:
            await processing_msg.delete()
            await message.answer(f"Таймаут при подключении к серверу: {str(e)}")
            return
        except httpx.RequestError as e:
            await processing_msg.delete()
            await message.answer(f"Ошибка при отправке запроса: {str(e)}")
            return
            
        await processing_msg.delete()

        if response.status_code != 200:
            error_message = f"Ошибка сервера. Код: {response.status_code}"
            try:
                error_details = response.json()
                error_message += f"Детали: {error_details}"
            except:
                error_message += f"Текст ответа: {response.text}"
            await message.answer(error_message)
        else:
            response_data = response.json()
            result_message = f"{response_data}"
            await message.answer(result_message)

    except Exception as e:
        if 'processing_msg' in locals():
            await processing_msg.delete()
        await message.answer(f"Произошла ошибка: {str(e)}")

async def close_client():
    await client.aclose()

