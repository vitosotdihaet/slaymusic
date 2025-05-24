from typing import Callable
import redis.asyncio
import redis.asyncio.client
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy import text

from configs.environment import settings
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie


DBS = ["accounts", "music"]


def get_db_creds(db_name: str) -> dict[str, str]:
    DB_NAME = db_name.upper().replace("-", "_")
    return {
        "user": getattr(settings, f"{DB_NAME}_ROOT_USER"),
        "password": getattr(settings, f"{DB_NAME}_ROOT_PASSWORD"),
        "port": getattr(settings, f"{DB_NAME}_PORT"),
        "db": getattr(settings, f"{DB_NAME}_DB"),
    }


def get_psql_url(db_name: str) -> str:
    creds = get_db_creds(db_name)
    host = f"postgres-{db_name}-service"
    return f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{host}:{creds['port']}/{creds['db']}"


def get_mongo_url(db_name: str) -> str:
    creds = get_db_creds(db_name)
    host = f"mongodb-{db_name}-service"
    return f"mongodb://{creds['user']}:{creds['password']}@{host}:{creds['port']}?authSource=admin"


def get_redis_url(db_name: str) -> str:
    creds = get_db_creds(db_name)
    host = f"redis-{db_name}-service"
    return f"redis://{creds['user']}:{creds['password']}@{host}:{creds['port']}/{creds['db']}?decode_responses=True&health_check_interval=2&protocol=3"


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


async def ensure_extensions(db_name: str) -> None:
    async with session_makers[db_name]() as session:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        await session.commit()


async def init_mongo_db(models: list[type[Document]], db_name: str):
    client = AsyncIOMotorClient(get_mongo_url(db_name))
    DB_NAME = db_name.upper().replace("-", "_")
    await init_beanie(
        database=getattr(client, getattr(settings, f"{DB_NAME}_DB")),
        document_models=models,
    )


def get_redis_client_generator(
    db_name: str,
) -> Callable[[], redis.asyncio.client.Redis]:
    return lambda: redis.asyncio.Redis.from_url(get_redis_url(db_name))


async def ensure_scripts(db_name: str, scripts: dict[str, str]) -> dict[str, str]:
    sha1s = {}
    async with get_redis_client_generator(db_name)() as client:
        for k, v in scripts.items():
            sha1s[k] = await client.script_load(v)
    return sha1s
