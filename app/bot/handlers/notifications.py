from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import async_session
from app.db.models import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload

notifications_router = Router(name="notifications")


@notifications_router.message(Command(commands=["notifications"]))
async def toggle_notifications(message: Message):
    async with async_session() as session:
        if message.from_user is None:
            return

        statement = (
            select(User)
            .options(selectinload(User.query_parameters))
            .where(User.telegram_id == message.from_user.id)
        )
        result = await session.execute(statement)
        user = result.scalar_one()
        if not user:
            return await message.answer("Сначала используйте /start")

        if not user.query_parameters:
            return await message.answer("Сначала используйте /setup")

        user.notifications = not user.notifications
        await session.commit()

        if user.notifications:
            return await message.answer(
                "Теперь вы будете получать уведомления о новых вакансиях!\nЧтобы их выключить используйте /notifications"
            )
        else:
            return await message.answer(
                "Вы выключили уведомления о новых вакансиях, чтобы их включить обратно используйте /notifications"
            )
