"""Analytics API endpoints."""

from fastapi import APIRouter, HTTPException

from services.analytics_service import analytics_service
from shared.schemas.impulse import AnalyticsResponse
from shared.constants import AnalyticsPeriod

router = APIRouter()


@router.get("/{period}", response_model=AnalyticsResponse)
async def get_analytics(period: str):
    """Get analytics for specified period.

    Args:
        period: Analytics period (today, yesterday, week, month)

    Returns:
        Analytics data
    """
    # Validate period
    try:
        AnalyticsPeriod(period)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Must be one of: {[p.value for p in AnalyticsPeriod]}",
        )

    try:
        data = await analytics_service.get_analytics(period)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
