from functools import lru_cache
from os.path import abspath

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """Настройки приложения, загружаются из .env файла."""
    DATABASE_URL: str
    DB_ECHO: bool = False

    # JWT Настройки
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 30
    REFRESH_TOKEN_LIFETIME_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=abspath(".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()