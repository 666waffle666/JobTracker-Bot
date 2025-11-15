# app/bot/handlers/notify.py
from aiogram import Bot
from sqlalchemy import select
from app.bot.chat_templates.vacancies import create_vacancies_template
from app.db.database import async_session
from app.db.models import User, QueryParameters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.vacancies import get_vacancies_data
from app.db.cache import get_seen_vacancies, set_seen_vacancies


async def check_new_vacancies(bot: Bot):
    async with async_session() as session:
        users = (await session.execute(select(User))).scalars().all()
        for user in users:
            params = (
                await session.execute(
                    select(QueryParameters).where(
                        QueryParameters.user_id == user.telegram_id
                    )
                )
            ).scalar_one_or_none()

            if not params:
                continue

            vacancies = (
                await get_vacancies_data(
                    {**params.to_dict(exclude=["id", "user_id"]), "search_period": 1}
                )
            ).get("items")
            if not vacancies:
                continue

            seen = await get_seen_vacancies(str(user.telegram_id))
            new_vacancies = [v for v in vacancies if v["id"] not in seen]

            if new_vacancies:
                template = create_vacancies_template(new_vacancies)
                await bot.send_message(
                    chat_id=user.telegram_id,  # type: ignore
                    text=f"<b>🔥 Новые вакансии 🔥</b>\n\n{template}",
                    parse_mode="HTML",
                )

                # Обновляем список последних вакансий
                await set_seen_vacancies(
                    str(user.telegram_id), [v["id"] for v in new_vacancies]
                )


def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_new_vacancies, "interval", minutes=0.1, args=[bot])
    scheduler.start()
