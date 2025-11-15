from sqlalchemy import select
from .models import User, QueryParameters
from .database import async_session
from sqlalchemy.orm import selectinload


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with async_session() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_and_params(telegram_id: int) -> User | None:
    async with async_session() as session:
        query = (
            select(User)
            .options(selectinload(User.query_parameters))
            .where(User.telegram_id == telegram_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_params(telegram_id: int) -> QueryParameters | None:
    async with async_session() as session:
        statement = select(QueryParameters).where(
            QueryParameters.user_id == telegram_id
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
