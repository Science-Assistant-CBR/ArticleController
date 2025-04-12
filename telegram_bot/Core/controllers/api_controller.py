from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot
from Core.settings import settings

app = FastAPI()
bot = Bot(token=settings.bots.bot_token)

class MessageRequest(BaseModel):
    user_id: int
    text: str
    content_type: str
    mode: str

@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        # Формируем сообщение с указанием типа контента и режима
        formatted_message = (
            f"Режим: {'Научные статьи' if request.mode == 'scientific' else 'Новости'}\n"
            f"Тип: {request.content_type}\n\n"
            f"{request.text}"
        )
        await bot.send_message(chat_id=request.user_id, text=formatted_message)
        return {"status": "success", "message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 