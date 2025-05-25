from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import httpx
import asyncio
from datetime import datetime
import re

from Core.keyboards.content_type_keyboard import main_kb, settings_kb
from Core.keyboards.source_keyboard import get_source_keyboard, SOURCES
from Core.settings import settings
from Core.utils.states import user_states, RequestStates
from Core.keyboards.filter_keyboard import filter_kb

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
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {}
        
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

@router.message(F.text == "Научные статьи")
async def set_science_mode(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["mode"] = "science"

    await message.answer(
        f"Режим установлен: {message.text}\n"
        "Выберите параметры фильтрации или нажмите 'Назад' для возврата в главное меню:",
        reply_markup=filter_kb
    )

@router.message(F.text == "Аналитика")
async def set_analytics_sphere(message: Message):
    user_id = message.from_user.id
    user_states[user_id]["sphere"] = "analytics"
    await show_current_settings(message)

@router.message(F.text == "Наука")
async def set_science_sphere(message: Message):
    user_id = message.from_user.id
    user_states[user_id]["sphere"] = "science"
    await show_current_settings(message)

@router.message(F.text == "Дата публикации")
async def set_publication_date(message: Message, state: FSMContext):
    await state.set_state(RequestStates.start_date)
    await message.answer(
        "Введите дату начала в формате ДД.ММ.ГГГГ (например, 01.01.2023):\n"
        "Или отправьте 'пропустить' для пропуска этого параметра"
    )

@router.message(RequestStates.start_date)
async def process_start_date(message: Message, state: FSMContext):
    if message.text.lower() == "пропустить":
        await state.set_state(RequestStates.end_date)
        await message.answer(
            "Введите дату окончания в формате ДД.ММ.ГГГГ (например, 31.12.2023):\n"
            "Или отправьте 'пропустить' для пропуска этого параметра"
        )
        return

    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
        user_id = message.from_user.id
        user_states[user_id]["start_date"] = date.strftime("%Y-%m-%d")
        await state.set_state(RequestStates.end_date)
        await message.answer(
            "Введите дату окончания в формате ДД.ММ.ГГГГ (например, 31.12.2023):\n"
            "Или отправьте 'пропустить' для пропуска этого параметра"
        )
    except ValueError:
        await message.answer(
            "Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ или отправьте 'пропустить':"
        )

@router.message(RequestStates.end_date)
async def process_end_date(message: Message, state: FSMContext):
    if message.text.lower() == "пропустить":
        await state.clear()
        await show_current_settings(message)
        return

    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
        user_id = message.from_user.id
        user_states[user_id]["end_date"] = date.strftime("%Y-%m-%d")
        await state.clear()
        await show_current_settings(message)
    except ValueError:
        await message.answer(
            "Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ или отправьте 'пропустить':"
        )

@router.message(F.text == "Источник публикации")
async def set_source(message: Message, state: FSMContext):
    keyboard = get_source_keyboard()
    await message.answer(
        "Выберите источник публикации:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("source_"))
async def process_source_selection(callback: CallbackQuery, state: FSMContext):
    source_key = callback.data
    source_name = SOURCES.get(source_key)
    
    if source_name:
        user_id = callback.from_user.id
        user_states[user_id]["source"] = source_key.split("_")[1]
        
        # Удаляем сообщение с выбором источника
        await callback.message.delete()
        
        # Отправляем новое сообщение с настройками
        user_settings = user_states.get(user_id, {})
        settings_text = "Текущие настройки фильтрации:\n"
        
        if user_settings.get("sphere"):
            settings_text += f"• Сфера: {'Аналитика' if user_settings['sphere'] == 'analytics' else 'Наука'}\n"
        
        if user_settings.get("start_date") or user_settings.get("end_date"):
            settings_text += "• Период: "
            if user_settings.get("start_date"):
                settings_text += f"с {user_settings['start_date']} "
            if user_settings.get("end_date"):
                settings_text += f"по {user_settings['end_date']}"
            settings_text += "\n"
        
        if user_settings.get("source"):
            source_key = f"source_{user_settings['source']}"
            settings_text += f"• Источник: {SOURCES[source_key]}\n"
        
        if not any([user_settings.get("sphere"), user_settings.get("start_date"), 
                    user_settings.get("end_date"), user_settings.get("source")]):
            settings_text += "Фильтры не установлены\n"
        
        # Сначала очищаем состояние
        await state.clear()
        
        # Затем отправляем сообщение с настройками
        await callback.message.answer(
            f"{settings_text}\n"
            "Выберите параметры фильтрации или нажмите 'Назад' для возврата в главное меню:",
            reply_markup=filter_kb
        )
    else:
        await callback.answer("Ошибка: неизвестный источник")

async def show_current_settings(message: Message):
    user_id = message.from_user.id
    user_settings = user_states.get(user_id, {})
    
    settings_text = "Текущие настройки фильтрации:\n"
    
    if user_settings.get("sphere"):
        settings_text += f"• Сфера: {'Аналитика' if user_settings['sphere'] == 'analytics' else 'Наука'}\n"
    
    if user_settings.get("start_date") or user_settings.get("end_date"):
        settings_text += "• Период: "
        if user_settings.get("start_date"):
            settings_text += f"с {user_settings['start_date']} "
        if user_settings.get("end_date"):
            settings_text += f"по {user_settings['end_date']}"
        settings_text += "\n"
    
    if user_settings.get("source"):
        source_key = f"source_{user_settings['source']}"
        settings_text += f"• Источник: {SOURCES[source_key]}\n"
    
    if not any([user_settings.get("sphere"), user_settings.get("start_date"), 
                user_settings.get("end_date"), user_settings.get("source")]):
        settings_text += "Фильтры не установлены\n"
    
    await message.answer(
        f"{settings_text}\n"
        "Выберите параметры фильтрации или нажмите 'Назад' для возврата в главное меню:",
        reply_markup=filter_kb
    )

@router.message(F.text == "Cбросить настройки")
async def reset_settings(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id].update({
            "sphere": None,
            "start_date": None,
            "end_date": None,
            "source": None
        })
    await state.clear()
    await message.answer(
        "Настройки фильтрации сброшены",
        reply_markup=filter_kb
    )

@router.message()
async def handle_message(message: Message):
    try:
        # Проверяем, не является ли сообщение командой или кнопкой
        if message.text in ["Настройки", "Научные статьи", "Новости", "Назад", "Cбросить настройки", "Аналитика", "Наука"]:
            return
        
        # Получаем текущие настройки пользователя
        user_id = message.from_user.id
        user_settings = user_states.get(user_id, {})
        
        # Формируем сообщение о текущих настройках
        settings_info = "Текущие настройки фильтрации:\n"
        if user_settings.get("sphere"):
            settings_info += f"• Сфера: {'Аналитика' if user_settings['sphere'] == 'analytics' else 'Наука'}\n"
        if user_settings.get("start_date") or user_settings.get("end_date"):
            settings_info += "• Период: "
            if user_settings.get("start_date"):
                settings_info += f"с {user_settings['start_date']} "
            if user_settings.get("end_date"):
                settings_info += f"по {user_settings['end_date']}"
            settings_info += "\n"
        if user_settings.get("source"):
            source_key = f"source_{user_settings['source']}"
            settings_info += f"• Источник: {SOURCES[source_key]}\n"
        
        # Отправляем и сохраняем сообщение о процессе с настройками
        processing_msg = await message.reply(
            f"Cообщение обрабатывается...\n\n{settings_info}"
        )
        
        # Подготавливаем данные для запроса
        request_data = {
            "raw_return": False,
            "query_text": message.text,
            "queries_count": 1,
            "top_k": 5,
            "source_name": user_settings.get("source"),
            "start_date": user_settings.get("start_date"),
            "end_date": user_settings.get("end_date"),
            "sphere": user_settings.get("sphere")
        }
        
        try:
            response = await client.post(
                f"http://acontroller:8000/api/v1/vectors/science", 
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
            
            # Форматируем текст с использованием Markdown
            formatted_text = format_markdown_text(str(response_data))
            
            try:
                await message.answer(formatted_text, parse_mode="MarkdownV2")
            except Exception as e:
                # Если возникла ошибка с Markdown, отправляем текст без форматирования
                await message.answer(str(response_data))

    except Exception as e:
        if 'processing_msg' in locals():
            await processing_msg.delete()
        await message.answer(f"Произошла ошибка: {str(e)}")

def format_markdown_text(text: str) -> str:
    """
    Форматирует текст для MarkdownV2
    """
    # Экранируем только те специальные символы, которые не используются в форматировании
    special_chars = ['[', ']', '(', ')', '~', '`', '>', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    # Форматируем заголовки
    text = re.sub(r'^#\s+(.+)$', r'*\\# \1*', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'*\\## \1*', text, flags=re.MULTILINE)
    
    # Форматируем жирный текст (сохраняем звездочки)
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    
    # Форматируем курсив (сохраняем подчеркивания)
    text = re.sub(r'_(.+?)_', r'_\1_', text)
    
    # Форматируем списки
    text = re.sub(r'^\s*[-*+]\s+(.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Форматируем ссылки
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'[\1](\2)', text)
    
    return text

async def close_client():
    await client.aclose()

