from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from app.config import Config

start_router = Router(name="start")


@start_router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    if message.from_user is None:
        await message.answer("Не могу определить пользователя 🤷‍♂️")
        return

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{Config.API_HOST}:{Config.API_PORT}",
            json={
                "telegram_id": message.from_user.id,
                "username": message.from_user.username,
            },
        )
    await message.answer(
        "Привет! Я JobTracker. Чтобы получать уведомления о новых вакансиях на HH.ru настрой меня /setup"
    )
