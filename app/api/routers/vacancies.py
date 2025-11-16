from fastapi import APIRouter
from app.external_api.vacancies import get_vacancies_data

vacancies_router = APIRouter(prefix="/vacancies")


@vacancies_router.get("/")
async def get_vacancies(params: dict):
    return await get_vacancies_data(params)
