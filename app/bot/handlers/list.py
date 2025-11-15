from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from app.api.vacancies import get_vacancies_data
from sqlalchemy import select
from app.db.models import QueryParameters
from app.db.database import async_session
from app.bot.chat_templates.vacancies import create_vacancies_template

list_router = Router(name="list")


@list_router.message(Command(commands=["list"]))
async def list_vacancies(message: types.Message):
    statement = select(QueryParameters).where(
        QueryParameters.user_id == message.from_user.id  # type: ignore
    )
    async with async_session() as session:
        res = await session.execute(statement)
        params = res.scalar_one_or_none()
        vacancies_data = await get_vacancies_data(
            params.to_dict(exclude=["id", "user_id"])  # type: ignore
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="В начало", callback_data="first")
        kb.button(text="Назад", callback_data="back")
        kb.button(text="Дальше", callback_data="next")
        kb.adjust(3)

        template = create_vacancies_template(vacancies_data)

        await message.answer(template, parse_mode="HTML", reply_markup=kb.as_markup())


@list_router.callback_query()
async def handle_pagination(callback: CallbackQuery):
    statement = select(QueryParameters).where(
        QueryParameters.user_id == callback.from_user.id
    )
    async with async_session() as session:
        res = await session.execute(statement)
        params = res.scalar_one_or_none()
        new_params = params.to_dict(exclude=["id", "user_id"])  # type: ignore
        if callback.data == "back" and new_params["page"] > 0:
            vacancies_data = await get_vacancies_data(
                {**new_params, "page": (new_params["page"] - 1)}  # type: ignore
            )
            params.page -= 1  # type: ignore
            await session.commit()
        elif callback.data == "next":
            vacancies_data = await get_vacancies_data(
                {**new_params, "page": (new_params["page"] + 1)}  # type: ignore
            )
            params.page += 1  # type: ignore
            await session.commit()
        else:
            vacancies_data = await get_vacancies_data(
                {**new_params, "page": 0}  # type: ignore
            )
            params.page = 0  # type: ignore
            await session.commit()

        kb = InlineKeyboardBuilder()
        kb.button(text="В начало", callback_data="first")
        kb.button(text="Назад", callback_data="back")
        kb.button(text="Дальше", callback_data="next")
        kb.adjust(3)

        template = create_vacancies_template(vacancies_data)

        await callback.message.edit_text(  # type: ignore
            template, parse_mode="HTML", reply_markup=kb.as_markup()
        )
