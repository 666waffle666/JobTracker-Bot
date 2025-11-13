from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import async_session
from app.db.models import User
from sqlalchemy import select

start_router = Router(name="start")


@start_router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    async with async_session() as session:
        statement = select(User).where(User.telegram_id == message.from_user.id)  # type: ignore
        result = await session.execute(statement)
        user = result.fetchone()
        if not user:
            new_user = User(
                telegram_id=message.from_user.id,  # type: ignore
                username=message.from_user.username,  # type: ignore
            )
            session.add(new_user)
            await session.commit()
    await message.answer(
        "Привет! Я JobTracker. Чтобы получать уведомления о новых вакансиях на HH.ru настрой меня /setup"
    )
