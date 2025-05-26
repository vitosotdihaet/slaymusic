from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DWH_ROOT_USER: str
    DWH_ROOT_PASSWORD: str
    DWH_DB: str
    DWH_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
