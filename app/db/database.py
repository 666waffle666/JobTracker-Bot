from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import Config

engine = create_async_engine(Config.POSTGRES_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
