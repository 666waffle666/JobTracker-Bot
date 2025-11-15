from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, Router
from aiogram.filters import Command
from app.db.database import async_session
from app.db.models import QueryParameters
from app.db.crud import get_user_by_telegram_id
from sqlalchemy import select
from app.api.areas import get_area_id


class QueryStates(StatesGroup):
    text = State()  # ключевые слова
    area = State()  # город/регион
    experience = State()  # опыт
    work_format = State()  # формат работы (удалёнка/офис/гибрид)
    salary = State()  # зарплата
    period = State()  # период публикации
    only_with_salary = State()  # только вакансии с зарплатой


setup_router = Router(name="setup")


@setup_router.message(Command(commands=["setup"]))
async def setup(message: types.Message, state: FSMContext):
    await state.set_state(QueryStates.text)
    await message.answer(
        "Введите ключевые слова для поиска (например: Python, FastAPI):"
    )


@setup_router.message(QueryStates.text)
async def get_text(message: types.Message, state: FSMContext):
    keywords = [k.strip() for k in message.text.split(",")]  # type: ignore
    await state.update_data(text=", ".join(keywords))
    await state.set_state(QueryStates.area)

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="skip_area")

    await message.answer(
        "Введите город или регион (например: Москва)", reply_markup=kb.as_markup()
    )


@setup_router.message(QueryStates.area)
async def get_area(message: types.Message, state: FSMContext):
    area_id = await get_area_id(message.text.strip())  # type: ignore
    await state.update_data(area=area_id)
    await state.set_state(QueryStates.experience)

    kb = InlineKeyboardBuilder()
    kb.button(text="Без опыта", callback_data="noExperience")
    kb.button(text="1–3 года", callback_data="between1And3")
    kb.button(text="3–6 лет", callback_data="between3And6")
    kb.button(text="Более 6 лет", callback_data="moreThan6")
    kb.adjust(2)

    await message.answer("Выберите уровень опыта:", reply_markup=kb.as_markup())


@setup_router.callback_query(QueryStates.area)
async def skip_area(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(area=None)
    await state.set_state(QueryStates.experience)

    kb = InlineKeyboardBuilder()
    kb.button(text="Без опыта", callback_data="noExperience")
    kb.button(text="1–3 года", callback_data="between1And3")
    kb.button(text="3–6 лет", callback_data="between3And6")
    kb.button(text="Более 6 лет", callback_data="moreThan6")
    kb.adjust(2)

    await callback.message.answer(  # type: ignore
        "Выберите уровень опыта:", reply_markup=kb.as_markup()
    )


@setup_router.callback_query(QueryStates.experience)
async def get_experience(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(experience=callback.data)
    await state.set_state(QueryStates.work_format)

    kb = InlineKeyboardBuilder()
    kb.button(text="На месте работодателя", callback_data="ON_SITE")
    kb.button(text="Из дома", callback_data="REMOTE")
    kb.button(text="Гибрид", callback_data="HYBRID")
    kb.button(text="Разъездная", callback_data="FIELD_WORK")
    kb.adjust(2)

    await callback.message.answer(  # type: ignore
        "Выберите формат работы:", reply_markup=kb.as_markup()
    )


@setup_router.callback_query(QueryStates.work_format)
async def get_work_format(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(work_format=callback.data)
    await state.set_state(QueryStates.salary)

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="skip_work_format")

    await callback.message.answer(  # type: ignore
        "Введите желаемую зарплату (числом)",
        reply_markup=kb.as_markup(),
    )


@setup_router.message(QueryStates.salary)
async def get_salary(message: types.Message, state: FSMContext):
    text = message.text.strip()  # type: ignore
    salary = int(text) if text.isdigit() else None
    await state.update_data(salary=salary)
    await state.set_state(QueryStates.period)

    kb = InlineKeyboardBuilder()
    kb.button(text="1 день", callback_data="1")
    kb.button(text="3 дня", callback_data="3")
    kb.button(text="7 дней", callback_data="7")
    kb.button(text="30 дней", callback_data="30")
    kb.adjust(2)

    await message.answer(
        "Выберите за какой период искать вакансии:", reply_markup=kb.as_markup()
    )


@setup_router.callback_query(QueryStates.salary)
async def skip_salary(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(salary=None)
    await state.set_state(QueryStates.period)

    kb = InlineKeyboardBuilder()
    kb.button(text="1 день", callback_data="1")
    kb.button(text="3 дня", callback_data="3")
    kb.button(text="7 дней", callback_data="7")
    kb.button(text="30 дней", callback_data="30")
    kb.adjust(2)

    await callback.message.answer(  # type: ignore
        "Выберите за какой период искать вакансии:", reply_markup=kb.as_markup()
    )


@setup_router.callback_query(QueryStates.period)
async def get_period(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(period=int(callback.data))  # type: ignore
    await state.set_state(QueryStates.only_with_salary)

    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="true")
    kb.button(text="Нет", callback_data="false")
    kb.adjust(2)

    await callback.message.answer(  # type: ignore
        "Искать только вакансии с зарплатой?", reply_markup=kb.as_markup()
    )


@setup_router.callback_query(QueryStates.only_with_salary)
async def get_only_with_salary(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(only_with_salary=callback.data)

    data = await state.get_data()

    async with async_session() as session:
        user = await get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.answer("Сначала используйте /start")  # type: ignore
            await state.clear()
            return

        result = await session.execute(
            select(QueryParameters).where(QueryParameters.user_id == user.telegram_id)
        )
        existing_query_params = result.scalar_one_or_none()
        if existing_query_params:
            await session.delete(existing_query_params)

        only_with_salary = True if data.get("only_with_salary") == "true" else False

        new_query = QueryParameters(
            user_id=user.telegram_id,
            text=data.get("text"),
            area=data.get("area"),
            experience=data.get("experience"),
            work_format=data.get("work_format"),
            salary=data.get("salary"),
            period=data.get("period"),
            only_with_salary=only_with_salary,
            page=0,
            per_page=5,
            order_by="publication_time",
            accept_temporary=None,
            employment_form=None,
        )
        session.add(new_query)
        await session.commit()

    await callback.message.answer(  # type: ignore
        "Фильтры для поиска вакансий сохранены ✅\nЧтобы посмотреть вакансии на данный момент используйте /list\nВключите уведомления /notifications чтобы вам приходили уведомления о новых вакансиях"
    )
    await state.clear()
