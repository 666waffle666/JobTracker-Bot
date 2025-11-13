from sqlalchemy import select
from app.db.database import async_session
from app.db.models import User
from app.api.vacancies import search_vacancies
from app.bot.bot import bot


async def check_new_vacancies():
    async with async_session() as session:
        statement = select(User)
        users = (await session.execute(statement)).fetchall()
        for user in users:
            filters = user.filters
            for f in filters:
                vacancies = await search_vacancies(f.keywords, f.city)
                for vac in vacancies:
                    # проверка, была ли вакансия уже отправлена
                    if not await vacancy_already_sent(vac, user.id, session):
                        await bot.send_message(
                            user.telegram_id, f"{vac['name']}\n{vac['alternate_url']}"
                        )
                        await save_vacancy_cache(vac, user.id, session)
