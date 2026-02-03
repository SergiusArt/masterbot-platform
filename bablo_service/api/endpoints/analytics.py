"""Analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

VALID_PERIODS = ["today", "yesterday", "week", "month"]


@router.get("/timeseries/{period}")
async def get_time_series(
    period: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get signal counts as time series.

    Args:
        period: Time period (today, week, month)

    Returns:
        Time series data with labels and counts
    """
    if period not in ["today", "week", "month"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid period. Must be one of: today, week, month",
        )

    data = await analytics_service.get_time_series(session, period)
    return data


@router.get("/comparison/today")
async def get_comparison(
    session: AsyncSession = Depends(get_db_session),
):
    """Get comparison data for today vs historical."""
    comparison = await analytics_service.get_comparison(session)
    return comparison


@router.get("/{period}")
async def get_analytics(
    period: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get analytics for specified period."""
    if period not in VALID_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Must be one of: {VALID_PERIODS}",
        )

    analytics = await analytics_service.get_analytics(session, period)
    return analytics
