from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, primary_key=True
    )
    username: Mapped[str] = mapped_column(String, nullable=True)
    notifications: Mapped[bool] = mapped_column(Boolean, default=False)

    query_parameters = relationship("QueryParameters", back_populates="user")


class QueryParameters(Base):
    __tablename__ = "query_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.telegram_id"))

    per_page: Mapped[int] = mapped_column(Integer, default=5, nullable=True)
    page: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=True)
    experience: Mapped[str] = mapped_column(String, nullable=True)
    area: Mapped[str] = mapped_column(String, nullable=True)
    only_with_salary: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )
    period: Mapped[int] = mapped_column(Integer, nullable=True)
    order_by: Mapped[str] = mapped_column(String, nullable=True)
    accept_temporary: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    employment_form: Mapped[str] = mapped_column(String, nullable=True)
    work_format: Mapped[str] = mapped_column(String, nullable=True)
    salary: Mapped[int] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="query_parameters")

    def to_dict(self, exclude: list[str] | None = None, skip_none: bool = True):
        result = {}
        for c in inspect(self).mapper.column_attrs:
            key = c.key
            if key in exclude:
                continue
            value = getattr(self, key)
            if skip_none and value is None:
                continue
            result[key] = value
        return result
