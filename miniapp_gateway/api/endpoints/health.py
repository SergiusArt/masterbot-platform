"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

from websocket.manager import connection_manager
from services.redis_subscriber import redis_subscriber

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "websocket_connections": connection_manager.connection_count,
        "redis_subscriber_running": redis_subscriber.is_running,
    }
