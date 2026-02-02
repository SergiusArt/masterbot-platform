"""Dashboard API endpoints - proxies to backend services."""

from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ServiceStats(BaseModel):
    """Statistics for a service."""

    today_count: int
    activity_zone: Literal["low", "medium", "high"]


class ImpulseStats(ServiceStats):
    """Impulse-specific statistics."""

    growth_count: int
    fall_count: int


class BabloStats(ServiceStats):
    """Bablo-specific statistics."""

    long_count: int
    short_count: int
    avg_quality: float


class DashboardSummary(BaseModel):
    """Combined dashboard summary."""

    impulses: ImpulseStats
    bablo: BabloStats
    market_pulse: Literal["calm", "normal", "active", "very_active"]
    timestamp: datetime


class HourlyActivity(BaseModel):
    """Hourly activity data point."""

    hour: str
    count: int


class ActivityChartData(BaseModel):
    """Activity chart data for both services."""

    impulses: list[HourlyActivity]
    bablo: list[HourlyActivity]
    medians: dict


def calculate_activity_zone(current: int, median: float) -> Literal["low", "medium", "high"]:
    """Calculate activity zone based on current count vs median."""
    if median == 0:
        return "medium"
    ratio = current / median
    if ratio < 0.5:
        return "low"
    if ratio > 1.5:
        return "high"
    return "medium"


def calculate_market_pulse(
    impulse_zone: str, bablo_zone: str
) -> Literal["calm", "normal", "active", "very_active"]:
    """Calculate overall market pulse from service zones."""
    zones = [impulse_zone, bablo_zone]
    high_count = zones.count("high")
    low_count = zones.count("low")

    if high_count == 2:
        return "very_active"
    if high_count == 1:
        return "active"
    if low_count == 2:
        return "calm"
    return "normal"


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary() -> DashboardSummary:
    """Get combined dashboard summary from both services."""
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
                impulse_median = 0.0
            else:
                impulse_data = impulse_resp.json()
                # Get median from comparison if available
                comparison = impulse_data.get("comparison", {})
                median_value = comparison.get("vs_week_median", 0)
                # Handle non-numeric values (e.g., "в норме", "high", etc.)
                try:
                    impulse_median = float(median_value) if median_value else 0.0
                except (ValueError, TypeError):
                    impulse_median = 0.0

            # Process bablo data
            if isinstance(bablo_resp, Exception):
                bablo_data = {"total_signals": 0, "long_count": 0, "short_count": 0, "average_quality": 0}
                bablo_median = 0
            else:
                bablo_data = bablo_resp.json()
                # Estimate median (would need separate endpoint ideally)
                bablo_median = bablo_data.get("total_signals", 0) * 0.8  # Rough estimate

            # Calculate activity zones
            impulse_zone = calculate_activity_zone(
                impulse_data.get("total_impulses", 0), impulse_median
            )
            bablo_zone = calculate_activity_zone(
                bablo_data.get("total_signals", 0), bablo_median
            )

            return DashboardSummary(
                impulses=ImpulseStats(
                    today_count=impulse_data.get("total_impulses", 0),
                    growth_count=impulse_data.get("growth_count", 0),
                    fall_count=impulse_data.get("fall_count", 0),
                    activity_zone=impulse_zone,
                ),
                bablo=BabloStats(
                    today_count=bablo_data.get("total_signals", 0) or 0,
                    long_count=bablo_data.get("long_count", 0) or 0,
                    short_count=bablo_data.get("short_count", 0) or 0,
                    avg_quality=bablo_data.get("average_quality", 0) or 0.0,
                    activity_zone=bablo_zone,
                ),
                market_pulse=calculate_market_pulse(impulse_zone, bablo_zone),
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")


@router.get("/impulses")
async def get_impulses(
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
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Impulse service error: {e}")


@router.get("/bablo")
async def get_bablo_signals(
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


@router.get("/analytics/{service}/{period}")
async def get_analytics(
    service: Literal["impulse", "bablo"],
    period: Literal["today", "yesterday", "week", "month"],
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


# Import asyncio for gather
import asyncio
