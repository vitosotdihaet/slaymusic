from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANALYTICS_ROOT_USER: str
    ANALYTICS_ROOT_PASSWORD: str
    ANALYTICS_DB: str
    ANALYTICS_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
