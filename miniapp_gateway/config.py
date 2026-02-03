"""Configuration for Mini App Gateway."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Gateway settings loaded from environment variables."""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG_MODE: bool = False  # Set to True only for local development

    # Telegram Bot
    BOT_TOKEN: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Backend services
    IMPULSE_SERVICE_URL: str = "http://localhost:8001"
    BABLO_SERVICE_URL: str = "http://localhost:8002"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 1000

    # Redis channels to subscribe
    REDIS_CHANNEL_IMPULSE: str = "impulse:notifications"
    REDIS_CHANNEL_BABLO: str = "bablo:notifications"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
