from pydantic import BaseModel


class User(BaseModel):
    telegram_id: int
    username: str
    notifications: bool | None = None


class UserWithParameters(User):
    query_parameters: list["QueryParameters"]


class QueryParametersPayload(BaseModel):
    per_page: int | None = None
    page: int | None = None
    text: str | None = None
    experience: str | None = None
    area: str | None = None
    only_with_salary: bool | None = None
    period: int | None = None
    order_by: str | None = None
    accept_temporary: bool | None = None
    employment_form: str | None = None
    work_format: str | None = None
    salary: int | None = None


class QueryParameters(BaseModel):
    id: int
    user_id: int

    per_page: int | None
    page: int | None
    text: str | None
    experience: str | None
    area: str | None
    only_with_salary: bool | None
    period: int | None
    order_by: str | None
    accept_temporary: bool | None
    employment_form: str | None
    work_format: str | None
    salary: int | None
