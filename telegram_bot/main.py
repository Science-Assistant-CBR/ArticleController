from aiogram import Bot, Dispatcher
import asyncio

from Core.handlers.basic_handler import router as basic_router, close_client
from Core.settings import settings
from Core.utils.commands import set_commands
from Core.utils.scheduler import setup_scheduler

token = settings.bots.bot_token

async def on_startup(bot: Bot):
    await set_commands(bot)
    print('- bot started')

async def on_shutdown():
    await close_client()
    print('- bot stopped')

async def main():
    bot = Bot(token=token, timeout=10)
    dp = Dispatcher()
    
    # Настраиваем и запускаем планировщик
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    dp.include_routers(
        basic_router
    )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('- bot disabled.')