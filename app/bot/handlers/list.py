from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from app.api.vacancies import get_vacancies_data
from app.db.crud import get_user_params
from app.db.database import async_session
from app.bot.chat_templates.vacancies import create_vacancies_template

list_router = Router(name="list")


@list_router.message(Command(commands=["list"]))
async def list_vacancies(message: types.Message):
    if message.from_user is None:
        await message.answer("Не могу определить пользователя 🤷‍♂️")
        return

    params = await get_user_params(message.from_user.id)
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
    async with async_session() as session:
        params = await get_user_params(callback.from_user.id)

        if not params:
            await callback.answer(
                "Сначала настройте фильтры при помощи /setup", show_alert=True
            )
            return

        page = params.page or 0

        if callback.data == "back" and page > 0:
            page -= 1
        elif callback.data == "next":
            page += 1
        else:
            page = 0

        params.page = page
        await session.commit()

        new_params = params.to_dict(exclude=["id", "user_id"])  # type: ignore
        vacancies_data = await get_vacancies_data({**new_params, "page": page})

        kb = InlineKeyboardBuilder()
        kb.button(text="В начало", callback_data="first")
        kb.button(text="Назад", callback_data="back")
        kb.button(text="Дальше", callback_data="next")
        kb.adjust(3)

        template = create_vacancies_template(vacancies_data)

        await callback.message.edit_text(  # type: ignore
            template, parse_mode="HTML", reply_markup=kb.as_markup()
        )
