import time
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram import types


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.REQUEST_LIMIT = 5
        self.TIME_WINDOW = 10

    async def __call__(self, handler, event: types.Update, data: dict):
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            current_time = time.time()
            user_requests = defaultdict(list)

            if user_id in user_requests:
                user_requests[user_id] = [timestamp for timestamp in user_requests[user_id] if
                                          current_time - timestamp < self.TIME_WINDOW]

                if len(user_requests[user_id]) >= self.REQUEST_LIMIT:
                    await event.reply(
                        "Подождите, мне поступает слишком много запросов. Пожалуйста, повторите попытку позже.",
                        parse_mode="Markdown"
                    )
                    return
            else:
                user_requests[user_id] = []

            user_requests[user_id].append(current_time)
        return await handler(event, data)
