"""Master Bot configuration."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_ID: int

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://masterbot:masterbot@localhost:5432/masterbot_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Services
    IMPULSE_SERVICE_URL: str = "http://localhost:8001"
    BABLO_SERVICE_URL: str = "http://localhost:8002"

    # Timezone
    TIMEZONE: str = "Europe/Moscow"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings()
