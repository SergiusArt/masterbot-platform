"""Performance calculation and analytics endpoints."""

from fastapi import APIRouter, Query

from shared.database.connection import async_session_maker
from services.performance_service import performance_service

router = APIRouter(prefix="/performance", tags=["performance"])


@router.post("/calculate")
async def calculate_performance(
    months: int = Query(2, ge=1, le=24),
):
    """Trigger performance calculation for uncalculated signals."""
    async with async_session_maker() as session:
        result = await performance_service.calculate_pending(session, months=months)
        return result


@router.get("/stats")
async def get_performance_stats(
    months: int = Query(2, ge=1, le=24),
):
    """Get aggregate performance statistics."""
    async with async_session_maker() as session:
        return await performance_service.get_performance_stats(session, months=months)


@router.get("/signals")
async def get_performance_signals(
    months: int = Query(2, ge=1, le=24),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get signals with performance data."""
    async with async_session_maker() as session:
        signals = await performance_service.get_performance_signals(
            session, months=months, limit=limit, offset=offset,
        )
        return {"signals": signals, "count": len(signals)}
