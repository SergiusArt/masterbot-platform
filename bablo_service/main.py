"""Bablo Service main application."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router
from config import settings
from telegram_listener.listener import bablo_listener
from shared.database.connection import init_db, close_db
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger

logger = get_logger("bablo_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Bablo Service...")

    logger.info("Initializing database...")
    await init_db()

    logger.info("Connecting to Redis...")
    await get_redis_client()

    logger.info("Starting Telegram listener...")
    asyncio.create_task(bablo_listener.start())

    logger.info("Bablo Service started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Bablo Service...")
    await bablo_listener.stop()
    await close_db()
    logger.info("Bablo Service stopped")


app = FastAPI(
    title="Bablo Service",
    description="Trading signals service for MasterBot Platform",
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
    # Check database
    try:
        from sqlalchemy import text
        from shared.database.connection import async_session_maker
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    # Check Redis
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
