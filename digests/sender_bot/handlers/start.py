import os
from datetime import datetime

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import (State,
                               StatesGroup)
from aiogram.types import Message, FSInputFile

from digests.sender_bot.createbot import (bot,
                                          logger)

start_router = Router()


class HelpState(StatesGroup):
    S = State()


@start_router.message(Command("start"))
async def start_command(message: Message, state):
    await state.clear()
    await message.delete()
    greeting_message = (
        "Привет! 👋\n"
        "Как только я получаю дайджесты я сразу отправляю их сюда 📣"
    )
    await message.answer(greeting_message)


async def download_file(url: str, dest_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(dest_path, 'wb') as f:
                    f.write(await response.read())
            else:
                logger.error(msg=f"Не удалось скачать файл: {response.status} {response.reason}")


async def get_url():
    return "https://pdfobject.com/pdf/sample.pdf"


async def send_new():
    # users = [984877321, 998308449, 824228308, 955749974]
    # users = [984877321, 998308449]
    users = [984877321]

    current_date = datetime.now().strftime("%Y-%m-%d")
    temp_file_path = f"temp_digest_{current_date}.pdf"

    pdf_url = await get_url()

    for user_id in users:
        try:
            await download_file(pdf_url, temp_file_path)

            await bot.send_document(
                chat_id=user_id,
                document=FSInputFile(temp_file_path),
                caption=f"Дайджест на {current_date} 📄"
            )
        except Exception as e:
            logger.error(msg=f"Не удалось отправить сообщение пользователю {user_id}: \n"
                             f"Ошибка: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
