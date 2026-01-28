"""Service Template entry point.

This is a template for creating new microservices.
Replace 'service_template' with your service name.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from shared.database.connection import init_db, close_db
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import setup_logger

logger = setup_logger("service_template")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Service Template...")

    logger.info("Initializing database...")
    await init_db()

    logger.info("Connecting to Redis...")
    await get_redis_client()

    logger.info("Service Template started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Service Template...")
    await close_db()
    logger.info("Service Template stopped.")


app = FastAPI(
    title="Service Template",
    description="Template for creating new microservices",
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
