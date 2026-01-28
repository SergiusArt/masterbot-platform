"""Impulse Service configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://masterbot:masterbot@localhost:5432/masterbot_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram Listener
    SOURCE_CHANNEL_ID: int = 0
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION_STRING: str = ""

    # Timezone
    TIMEZONE: str = "Europe/Moscow"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings()
