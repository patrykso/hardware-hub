from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "prod"
    secret_key: str | None = None
    db_path: str = "hub.db"
    admin_username: str | None = None
    admin_password: str | None = None

    cors_origins: str = "http://localhost:5173"
    access_token_expire_hours: int = 8

    @model_validator(mode="after")
    def check_secrets(self) -> 'Settings':
        if self.env == "dev":
            self.secret_key = self.secret_key or "dev-secret-key-change-in-production"
            self.admin_username = self.admin_username or "admin"
            self.admin_password = self.admin_password or "admin"
        else:
            if not self.secret_key:
                raise ValueError("secret_key must be set in prod environment")
            if not self.admin_username or not self.admin_password:
                raise ValueError("admin credentials must be set in prod environment")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
