from sqlalchemy import select
from app.db.models import User, QueryParameters
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import User as UserSchema
from ..schemas import QueryParametersPayload
from fastapi.exceptions import HTTPException
from fastapi import status


class UserService:
    async def get_user_by_id(self, id: str, session: AsyncSession) -> User | None:
        query = select(User).where(User.telegram_id == int(id))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_and_params(self, id: str, session: AsyncSession) -> User | None:
        query = (
            select(User)
            .options(selectinload(User.query_parameters))
            .where(User.telegram_id == int(id))
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserSchema, session: AsyncSession):
        user = await self.get_user_by_id(str(user_data.telegram_id), session)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "User already exists"},
            )

        new_user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
        )

        session.add(new_user)
        await session.commit()
        return new_user

    async def get_user_params(
        self, user_id: str, session: AsyncSession
    ) -> QueryParameters | None:
        user = await self.get_user_and_params(user_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "User not found"},
            )

        if not user.query_parameters:
            return None

        return user.query_parameters[0]

    async def set_user_params(
        self, user_id: str, payload: QueryParametersPayload, session: AsyncSession
    ) -> QueryParameters:
        user = await self.get_user_by_id(user_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "User not found"},
            )

        existing_query_params = await self.get_user_params(user_id, session)

        if existing_query_params:
            await session.delete(existing_query_params)

        new_query = QueryParameters(
            user_id=int(user_id),
            **payload.model_dump(),
        )
        session.add(new_query)
        await session.commit()
        return new_query

    async def toggle_notifications(self, user_id, session: AsyncSession):
        user = await self.get_user_and_params(user_id, session)

        if not user:
            return {"message": "Сначала используйте /start"}

        if not user.query_parameters:
            return {"message": "Сначала настройте фильтры при помощи /setup"}

        user.notifications = not user.notifications
        await session.commit()

        if user.notifications:
            return {
                "message": "Теперь вы будете получать уведомления о новых вакансиях!\nЧтобы их выключить используйте /notifications"
            }
        else:
            return {
                "message": "Вы выключили уведомления о новых вакансиях, чтобы их включить обратно используйте /notifications"
            }

    async def update_params_page(
        self, user_id: str, action: str, session: AsyncSession
    ):
        user = await self.get_user_and_params(user_id, session)

        if not user:
            return {"message": "Сначала используйте /start", "page": None}

        if not user.query_parameters:
            return {
                "message": "Сначала настройте фильтры при помощи /setup",
                "page": None,
            }

        params = user.query_parameters[0]

        page = params.page or 0
        if action == "back" and page > 0:
            page -= 1
        elif action == "next":
            page += 1
        else:
            page = 0

        params.page = page
        await session.commit()

        return {
            "page": page,
            "new_params": params.to_dict(exclude=["id", "user_id"]),
        }
