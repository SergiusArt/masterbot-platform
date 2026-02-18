"""Dashboard API endpoints - proxies to backend services."""

import asyncio
from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, check_is_admin
from auth.telegram import TelegramUser
from config import settings
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Activity zone type
ActivityZoneType = Literal["very_low", "low", "normal", "high", "extreme"]


class ServiceStats(BaseModel):
    """Statistics for a service."""

    today_count: int
    median: float
    activity_zone: ActivityZoneType
    activity_ratio: float  # current / median ratio


class ImpulseStats(ServiceStats):
    """Impulse-specific statistics."""

    growth_count: int
    fall_count: int


class BabloStats(ServiceStats):
    """Bablo-specific statistics."""

    long_count: int
    short_count: int
    avg_quality: float


class UserInfo(BaseModel):
    """Current user information."""

    id: int
    username: Optional[str]
    first_name: Optional[str]
    is_admin: bool


class DashboardSummary(BaseModel):
    """Combined dashboard summary."""

    impulses: ImpulseStats
    bablo: BabloStats
    market_pulse: Literal["calm", "normal", "active", "very_active"]
    timestamp: datetime
    user: UserInfo


class HourlyActivity(BaseModel):
    """Hourly activity data point."""

    hour: str
    count: int


class ActivityChartData(BaseModel):
    """Activity chart data for both services."""

    impulses: list[HourlyActivity]
    bablo: list[HourlyActivity]
    medians: dict


def calculate_activity_zone(current: int, median: float) -> tuple[ActivityZoneType, float]:
    """
    Calculate activity zone based on current count vs median.

    Zones:
    - very_low: < 25% of median
    - low: 25-75% of median
    - normal: 75-125% of median
    - high: 125-200% of median
    - extreme: > 200% of median

    Returns (zone, ratio)
    """
    if median == 0:
        return "normal", 1.0

    ratio = current / median

    if ratio < 0.25:
        zone = "very_low"
    elif ratio < 0.75:
        zone = "low"
    elif ratio <= 1.25:
        zone = "normal"
    elif ratio <= 2.0:
        zone = "high"
    else:
        zone = "extreme"

    return zone, round(ratio, 2)


def calculate_market_pulse(
    impulse_zone: str, bablo_zone: str
) -> Literal["calm", "normal", "active", "very_active"]:
    """Calculate overall market pulse from service zones."""
    zone_scores = {
        "very_low": 0,
        "low": 1,
        "normal": 2,
        "high": 3,
        "extreme": 4,
    }

    total_score = zone_scores.get(impulse_zone, 2) + zone_scores.get(bablo_zone, 2)

    if total_score <= 2:
        return "calm"
    elif total_score <= 4:
        return "normal"
    elif total_score <= 6:
        return "active"
    else:
        return "very_active"


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """Get combined dashboard summary from both services."""
    # Check if user is admin
    is_admin = await check_is_admin(user.id, db)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Fetch analytics from both services in parallel
            impulse_resp, bablo_resp = await asyncio.gather(
                client.get(f"{settings.IMPULSE_SERVICE_URL}/api/v1/analytics/today"),
                client.get(f"{settings.BABLO_SERVICE_URL}/api/v1/analytics/today"),
                return_exceptions=True,
            )

            # Process impulse data
            if isinstance(impulse_resp, Exception):
                impulse_data = {"total_impulses": 0, "growth_count": 0, "fall_count": 0}
                impulse_median = 50.0  # Default median
            else:
                impulse_data = impulse_resp.json()
                # Get actual median from comparison.week_median
                comparison = impulse_data.get("comparison", {})
                impulse_median = float(comparison.get("week_median", 50) or 50)

            # Process bablo data
            if isinstance(bablo_resp, Exception):
                bablo_data = {"total_signals": 0, "long_count": 0, "short_count": 0, "average_quality": 0}
                bablo_median = 30.0  # Default median
            else:
                bablo_data = bablo_resp.json()
                bablo_median = float(bablo_data.get("week_median", 30) or 30)

            # Calculate activity zones
            impulse_zone, impulse_ratio = calculate_activity_zone(
                impulse_data.get("total_impulses", 0), impulse_median
            )
            bablo_zone, bablo_ratio = calculate_activity_zone(
                bablo_data.get("total_signals", 0), bablo_median
            )

            return DashboardSummary(
                impulses=ImpulseStats(
                    today_count=impulse_data.get("total_impulses", 0),
                    growth_count=impulse_data.get("growth_count", 0),
                    fall_count=impulse_data.get("fall_count", 0),
                    median=impulse_median,
                    activity_zone=impulse_zone,
                    activity_ratio=impulse_ratio,
                ),
                bablo=BabloStats(
                    today_count=bablo_data.get("total_signals", 0) or 0,
                    long_count=bablo_data.get("long_count", 0) or 0,
                    short_count=bablo_data.get("short_count", 0) or 0,
                    avg_quality=bablo_data.get("average_quality", 0) or 0.0,
                    median=bablo_median,
                    activity_zone=bablo_zone,
                    activity_ratio=bablo_ratio,
                ),
                market_pulse=calculate_market_pulse(impulse_zone, bablo_zone),
                timestamp=datetime.now(timezone.utc),
                user=UserInfo(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    is_admin=is_admin,
                ),
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")


@router.get("/impulses")
async def get_impulses(
    user: TelegramUser = Depends(get_current_user),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """Get recent impulses from impulse service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{settings.IMPULSE_SERVICE_URL}/api/v1/signals",
                params={"limit": limit, "offset": offset},
            )
            resp.raise_for_status()
            data = resp.json()
            # Transform response: rename 'signals' to 'impulses' for frontend consistency
            return {
                "impulses": data.get("signals", []),
                "total": data.get("total", len(data.get("signals", []))),
            }
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Impulse service error: {e}")


@router.get("/bablo")
async def get_bablo_signals(
    user: TelegramUser = Depends(get_current_user),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    direction: Optional[str] = None,
    timeframe: Optional[str] = None,
    min_quality: Optional[int] = None,
) -> dict:
    """Get recent Bablo signals from bablo service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {"limit": limit, "offset": offset}
            if direction:
                params["direction"] = direction
            if timeframe:
                params["timeframe"] = timeframe
            if min_quality is not None:
                params["min_quality"] = min_quality

            resp = await client.get(
                f"{settings.BABLO_SERVICE_URL}/api/v1/signals",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Bablo service error: {e}")


@router.get("/strong/stats")
async def get_strong_stats(
    user: TelegramUser = Depends(get_current_user),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
) -> dict:
    """Get Strong Signal performance statistics."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {}
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date

            resp = await client.get(
                f"{settings.STRONG_SERVICE_URL}/api/v1/performance/stats",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Strong service error: {e}")


@router.get("/strong/signals")
async def get_strong_signals(
    user: TelegramUser = Depends(get_current_user),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """Get Strong Signal signals with performance data."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {"limit": limit, "offset": offset}
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date

            resp = await client.get(
                f"{settings.STRONG_SERVICE_URL}/api/v1/performance/signals",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Strong service error: {e}")


@router.get("/strong/recent")
async def get_strong_recent(
    user: TelegramUser = Depends(get_current_user),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    direction: Optional[str] = None,
) -> dict:
    """Get recent Strong Signal signals (raw, without performance data)."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {"limit": limit, "offset": offset}
            if direction:
                params["direction"] = direction

            resp = await client.get(
                f"{settings.STRONG_SERVICE_URL}/api/v1/signals",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Strong service error: {e}")


@router.get("/analytics/{service}/{period}")
async def get_analytics(
    service: Literal["impulse", "bablo"],
    period: Literal["today", "yesterday", "week", "month"],
    user: TelegramUser = Depends(get_current_user),
) -> dict:
    """Get analytics for a specific service and period."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if service == "impulse":
                url = f"{settings.IMPULSE_SERVICE_URL}/api/v1/analytics/{period}"
            else:
                url = f"{settings.BABLO_SERVICE_URL}/api/v1/analytics/{period}"

            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Service error: {e}")


@router.get("/timeseries/{service}/{period}")
async def get_time_series(
    service: Literal["impulse", "bablo"],
    period: Literal["today", "week", "month"],
    user: TelegramUser = Depends(get_current_user),
) -> dict:
    """Get signal counts as time series.

    Args:
        service: Service name (impulse or bablo)
        period: Time period (today, week, month)

    Returns:
        Time series data with labels, counts, and median
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if service == "impulse":
                url = f"{settings.IMPULSE_SERVICE_URL}/api/v1/analytics/timeseries/{period}"
            else:
                url = f"{settings.BABLO_SERVICE_URL}/api/v1/analytics/timeseries/{period}"

            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Service error: {e}")
