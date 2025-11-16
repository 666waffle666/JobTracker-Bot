from fastapi import FastAPI
from .routers import user_router, vacancies_router

app = FastAPI()

app.include_router(user_router)
app.include_router(vacancies_router)
