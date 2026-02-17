"""Strong Signal Service main application."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router
from config import settings
from telegram_listener.listener import strong_listener
from services.performance_scheduler import performance_scheduler
from shared.database.connection import init_db, close_db
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger

# Import models to register them with Base.metadata before init_db
from models import StrongSignal, StrongUserSettings  # noqa: F401

logger = get_logger("strong_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Strong Signal Service...")

    logger.info("Initializing database...")
    await init_db()

    logger.info("Connecting to Redis...")
    await get_redis_client()

    logger.info("Starting Telegram listener...")

    async def run_listener():
        try:
            await strong_listener.start()
        except Exception as e:
            logger.error(f"Fatal error in Telegram listener: {e}", exc_info=True)

    listener_task = asyncio.create_task(run_listener())

    def task_done_callback(task):
        try:
            task.result()
        except Exception as e:
            logger.error(f"Telegram listener task failed: {e}", exc_info=True)

    listener_task.add_done_callback(task_done_callback)

    logger.info("Starting performance scheduler...")
    scheduler_task = asyncio.create_task(performance_scheduler.start())

    logger.info("Strong Signal Service started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Strong Signal Service...")
    await performance_scheduler.stop()
    await strong_listener.stop()
    await close_db()
    logger.info("Strong Signal Service stopped")


app = FastAPI(
    title="Strong Signal Service",
    description="Strong trading signals service for MasterBot Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        from sqlalchemy import text
        from shared.database.connection import async_session_maker
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    try:
        redis = await get_redis_client()
        await redis.health_check()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {e}"

    status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"

    return {
        "status": status,
        "service": settings.SERVICE_NAME,
        "database": db_status,
        "redis": redis_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
    )
