from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from app.api.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from ..schemas import User, QueryParameters, UserWithParameters, QueryParametersPayload

user_router = APIRouter(prefix="/users")
user_service = UserService()


@user_router.get("/{id}")
async def get_user(
    id: str, params: bool = False, session: AsyncSession = Depends(get_session)
) -> User | UserWithParameters:
    if params:
        user = await user_service.get_user_and_params(id, session)
    else:
        user = await user_service.get_user_by_id(id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User was not found"},
        )

    return user


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: User, session: AsyncSession = Depends(get_session)
) -> User:
    return await user_service.create_user(user_data, session)


@user_router.get("/{id}/params")
async def get_user_params(
    id: str, session: AsyncSession = Depends(get_session)
) -> QueryParameters:
    return await user_service.get_user_params(id, session)


@user_router.post("/{id}/params")
async def set_user_params(
    id: str,
    payload: QueryParametersPayload,
    session: AsyncSession = Depends(get_session),
) -> QueryParameters:
    return await user_service.set_user_params(id, payload, session)


@user_router.post("/{id}/notifications")
async def toggle_notifications(id: str, session: AsyncSession = Depends(get_session)):
    return await user_service.toggle_notifications(id, session)


@user_router.put("/{id}/params")
async def update_params_page(
    id: str, action: str, session: AsyncSession = Depends(get_session)
):
    return await user_service.update_params_page(id, action, session)
