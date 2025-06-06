from typing import Callable
import redis.asyncio
import redis.asyncio.client
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie
import hashlib

from configs.environment import settings


DBS = ["music"]


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
    name: create_async_engine(
        get_psql_url(name),
        future=True,
        isolation_level="READ COMMITTED",
        pool_size=20,
        max_overflow=30,
        pool_timeout=60,
    )
    for name in DBS
}

session_makers: dict[str, async_sessionmaker[AsyncSession]] = {
    name: async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    for name, engine in engines.items()
}


async def get_session_generator(db_name: str) -> async_sessionmaker[AsyncSession]:
    return session_makers[db_name]


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


def get_scripts(scripts_dir: str = "scripts/") -> dict[str, str]:
    sha1s = {}
    for filename in os.listdir(scripts_dir):
        script_name = os.path.splitext(filename)[0]
        filepath = os.path.join(scripts_dir, filename)
        with open(filepath, "r") as f:
            lua_script_content = f.read()
            sha1s[script_name] = hashlib.sha1(
                lua_script_content.encode("utf-8")
            ).hexdigest()
    return sha1s
