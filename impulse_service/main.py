"""Impulse Service entry point."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.scheduler import start_scheduler, stop_scheduler
from telegram_listener.listener import TelegramListener
from shared.database.connection import init_db, close_db
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import setup_logger

# Import models to register them with Base.metadata before init_db
from models import Impulse, UserNotificationSettings  # noqa: F401

logger = setup_logger("impulse_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Impulse Service...")

    logger.info("Initializing database...")
    await init_db()

    logger.info("Connecting to Redis...")
    await get_redis_client()

    logger.info("Starting scheduler...")
    start_scheduler()

    logger.info("Starting Telegram listener...")
    listener = TelegramListener()
    asyncio.create_task(listener.start())

    logger.info("Impulse Service started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Impulse Service...")
    stop_scheduler()
    await listener.stop()
    await close_db()
    logger.info("Impulse Service stopped.")


app = FastAPI(
    title="Impulse Service",
    description="Microservice for crypto impulse tracking and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from shared.database.connection import async_session_maker
    from shared.utils.redis_client import get_redis_client

    db_status = "connected"
    redis_status = "connected"

    try:
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
    except Exception:
        db_status = "disconnected"

    try:
        redis = await get_redis_client()
        await redis.health_check()
    except Exception:
        redis_status = "disconnected"

    status = "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy"

    return {
        "status": status,
        "database": db_status,
        "redis": redis_status,
    }
