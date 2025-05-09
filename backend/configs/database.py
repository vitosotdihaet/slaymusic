from typing import AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from configs.environment import settings

DBS = ["accounts", "user-activity", "music"]


def get_psql_url(db_name: str) -> str:
    DB_NAME = db_name.upper().replace("-", "_")
    user = getattr(settings, f"POSTGRESQL_{DB_NAME}_ROOT_USER")
    password = getattr(settings, f"POSTGRESQL_{DB_NAME}_ROOT_PASSWORD")
    host = f"postgres-{db_name}-service"
    port = getattr(settings, f"POSTGRESQL_{DB_NAME}_PORT")
    db = getattr(settings, f"POSTGRESQL_{DB_NAME}_DB")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


engines: Dict[str, any] = {
    name: create_async_engine(get_psql_url(name), future=True) for name in DBS
}

sessions: Dict[str, async_sessionmaker[AsyncSession]] = {
    name: async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    for name, engine in engines.items()
}


async def get_session(db_name: str):
    async with sessions[db_name]() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_music_session():
    async with sessions["music"]() as session:
        try:
            yield session
        finally:
            await session.close()

async def ensure_tables(Base, name: str) -> None:
    async with engines[name].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
