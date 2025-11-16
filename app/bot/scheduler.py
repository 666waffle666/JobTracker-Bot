from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.bot.chat_templates.vacancies import create_vacancies_template
from app.db.database import async_session
from app.db.models import User
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.external_api.vacancies import get_vacancies_data
from app.db.cache import get_last_check, set_last_check
from datetime import datetime, timezone


async def check_new_vacancies(bot: Bot):
    async with async_session() as session:
        users = (
            (
                await session.execute(
                    select(User).options(selectinload(User.query_parameters))
                )
            )
            .scalars()
            .all()
        )
        for user in users:
            params = user.query_parameters[0]
            allow_notifications = user.notifications

            if not allow_notifications:
                continue

            if not params:
                continue

            vacancies = (
                await get_vacancies_data(
                    {
                        **params.to_dict(exclude=["id", "user_id"]),
                        "period": 1,
                        "order_by": "publication_time",
                        "per_page": 5,
                        "page": 0,
                    }
                )
            ).get("items")
            if not vacancies:
                continue

            last_check = await get_last_check(str(user.telegram_id))
            new_vacancies = []
            for vacancy in vacancies:
                s = vacancy["published_at"]
                dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
                dt_utc = dt.astimezone(timezone.utc)
                if dt_utc > last_check:
                    new_vacancies.append(vacancy)

            if new_vacancies:
                template = create_vacancies_template(new_vacancies)
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"<b>🔥 Новые вакансии 🔥</b>\n\n{template}",
                    parse_mode="HTML",
                )

                await set_last_check(user.telegram_id)


def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_new_vacancies, "interval", minutes=30, args=[bot])
    scheduler.start()
