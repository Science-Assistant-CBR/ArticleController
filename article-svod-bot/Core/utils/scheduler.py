import yadisk
import asyncio
import os
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.methods.send_media_group import SendMediaGroup
from aiogram.types import InputMediaDocument
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Core.settings import settings

scheduler = AsyncIOScheduler()

async def send_weekly_pdfs(bot: Bot, user_id: int):
    try:
        client = yadisk.AsyncClient(token=settings.bots.yadisk_token)
        pdfs = [f async for f in client.listdir(settings.bots.digest_directory) 
                if f.name.lower().endswith('.pdf')]
        print(f"- there are {len(pdfs)} files to download\n")
        
        if not pdfs:
            next_date = datetime.now() + timedelta(days=settings.bots.timedelta)
            await bot.send_message(
                user_id, 
                f"На данный момент нет новых дайджестов.\n"
                f"Следующая отправка дайджестов: {next_date.strftime('%d.%m.%Y в %H:%M')}"
            )
            return
        
        # Список для хранения временных путей к файлам
        temp_files = []
        # Список для медиагруппы
        media_group = []
        
        try:
            # Скачиваем все файлы
            for pdf in pdfs:
                temp_path = f"{pdf.name}"
                await client.download(pdf.path, temp_path)
                temp_files.append(temp_path)
                print("- file downloaded")
                # Добавляем файл в медиагруппу
                media_group.append(
                    InputMediaDocument(
                        media=FSInputFile(temp_path),
                        caption=pdf.name
                    )
                )
            
            # Отправляем все файлы одним сообщением
            await bot.send_media_group(user_id, media=media_group)
            
            # Отправляем сообщение о следующей отправке
            next_date = datetime.now() + timedelta(days=settings.bots.timedelta)
            await bot.send_message(
                user_id,
                f"Следующая отправка дайджестов: {next_date.strftime('%d.%m.%Y в %H:%M')}"
            )
            
        finally:
            # Удаляем все временные файлы
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
    except Exception as e:
        await bot.send_message(user_id, f"Ошибка при отправке файлов: {str(e)}")

def setup_scheduler(bot: Bot):
    return scheduler

def add_user_to_mailing(bot: Bot, user_id: int):
    job_id = f"mailing_{user_id}"
    if scheduler.get_job(job_id):
        return False
    
    # Сначала выполняем задачу немедленно
    asyncio.create_task(send_weekly_pdfs(bot, user_id))
    
    # Затем добавляем периодическую задачу
    scheduler.add_job(
        send_weekly_pdfs,
        'interval',
        days=settings.bots.timedelta,
        args=(bot, user_id),
        id=job_id,
        max_instances=1,
        coalesce=True
    )
    return True

def remove_user_from_mailing(user_id: int):
    job_id = f"mailing_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        return True
    return False 