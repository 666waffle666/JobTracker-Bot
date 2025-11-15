from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import async_session
from app.db.models import User
from app.db.crud import get_user_by_telegram_id

start_router = Router(name="start")


@start_router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    if message.from_user is None:
        await message.answer("Не могу определить пользователя 🤷‍♂️")
        return

    async with async_session() as session:
        user = get_user_by_telegram_id(message.from_user.id)
        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
            )
            session.add(new_user)
            await session.commit()
    await message.answer(
        "Привет! Я JobTracker. Чтобы получать уведомления о новых вакансиях на HH.ru настрой меня /setup"
    )
