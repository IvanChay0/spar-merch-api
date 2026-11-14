from functools import lru_cache
from os.path import abspath

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """Настройки приложения, загружаются из .env файла."""
    DATABASE_URL: str
    DB_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=abspath(".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()