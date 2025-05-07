from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from configs.environment import settings

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRESQL_MUSIC_ROOT_USER}:"
    f"{settings.POSTGRESQL_MUSIC_ROOT_PASSWORD}@"
    f"localhost:{settings.POSTGRESQL_MUSIC_PORT}/"
    f"{settings.POSTGRESQL_MUSIC_DB}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
