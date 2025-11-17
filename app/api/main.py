from fastapi import FastAPI
from .routers import user_router, vacancies_router

app = FastAPI()

app.include_router(user_router, tags=["user"])
app.include_router(vacancies_router, tags=["vacancies"])
