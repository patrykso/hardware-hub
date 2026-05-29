from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-key-change-in-production"
    db_path: str = "hub.db"
    admin_username: str = "admin"
    admin_password: str = "admin"

    cors_origins: str = "http://localhost:5173"
    access_token_expire_hours: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
