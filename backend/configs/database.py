from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

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


engines: dict[str, AsyncEngine] = {
    name: create_async_engine(get_psql_url(name), future=True) for name in DBS
}

session_makers: dict[str, async_sessionmaker[AsyncSession]] = {
    name: async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    for name, engine in engines.items()
}


async def get_session_generator(db_name: str) -> async_sessionmaker[AsyncSession]:
    return session_makers[db_name]


async def ensure_tables(Base, db_name: str) -> None:
    async with engines[db_name].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
