from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    telegram_id = Column(Integer, unique=True, index=True, primary_key=True)
    username = Column(String, nullable=True)

    query_parameters = relationship("QueryParameters", back_populates="user")


class QueryParameters(Base):
    __tablename__ = "query_parameters"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))

    per_page = Column(Integer, default=5)
    page = Column(Integer, default=0)
    text = Column(String)
    experience = Column(String)
    area = Column(String)
    only_with_salary = Column(Boolean)
    period = Column(Integer)
    order_by = Column(String)
    accept_temporary = Column(Boolean)
    employment_form = Column(String)
    work_format = Column(String)
    salary = Column(Integer)

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
