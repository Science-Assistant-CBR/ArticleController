import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from digests.sender_bot.createbot import dp, bot
from digests.sender_bot.handlers.start import (start_router,
                                               send_new)


async def main():
    dp.include_router(start_router)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_new, 'cron', hour=20, minute=5)
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
