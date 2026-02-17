"""Strong Signal Service configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://masterbot:masterbot@localhost:5432/masterbot_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram Listener
    STRONG_CHANNEL_ID: int = -1001805899976
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION_STRING: str = ""

    # Timezone
    TIMEZONE: str = "Europe/Moscow"

    # Binance Futures API
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""

    # Service
    SERVICE_NAME: str = "strong_service"
    SERVICE_PORT: int = 8004

    class Config:
        env_file = ".env"


settings = Settings()
