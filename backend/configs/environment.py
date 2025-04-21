from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_PORT: int
    MINIO_WEBUI_PORT: int

    POSTGRESQL_ACCOUNTS_ROOT_USER: str
    POSTGRESQL_ACCOUNTS_ROOT_PASSWORD: str
    POSTGRESQL_ACCOUNTS_DB: str
    POSTGRESQL_ACCOUNTS_PORT: int

    POSTGRESQL_MUSIC_ROOT_USER: str
    POSTGRESQL_MUSIC_ROOT_PASSWORD: str
    POSTGRESQL_MUSIC_DB: str
    POSTGRESQL_MUSIC_PORT: int

    POSTGRESQL_USER_ACTIVITY_ROOT_USER: str
    POSTGRESQL_USER_ACTIVITY_ROOT_PASSWORD: str
    POSTGRESQL_USER_ACTIVITY_DB: str
    POSTGRESQL_USER_ACTIVITY_PORT: int

    BACKEND_PORT: int

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables():
    return Settings()  # type: ignore
