from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from app.config import Config

notifications_router = Router(name="notifications")


@notifications_router.message(Command(commands=["notifications"]))
async def toggle_notifications(message: Message):
    if message.from_user is None:
        await message.answer("Не могу определить пользователя 🤷‍♂️")
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{Config.API_HOST}:{Config.API_PORT}/users/{message.from_user.id}/notifications"
        )
        response = response.json()

    return await message.answer(response["message"])
