"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def detailed_health():
    """Detailed health check.

    Returns:
        Detailed health status
    """
    return {
        "status": "ok",
        "service": "service_template",
        "version": "1.0.0",
    }
