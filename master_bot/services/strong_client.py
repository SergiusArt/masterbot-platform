"""HTTP client for Strong Signal Service."""

from typing import Optional

from services.base import BaseServiceClient
from config import settings


class StrongServiceClient(BaseServiceClient):
    """Client for communicating with Strong Signal Service."""

    def __init__(self):
        super().__init__(settings.STRONG_SERVICE_URL)

    async def get_signals(
        self,
        limit: int = 100,
        offset: int = 0,
        direction: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> dict:
        """Get list of signals.

        Args:
            limit: Maximum number of signals
            offset: Number of signals to skip
            direction: Filter by direction (long/short)
            from_date: ISO datetime start filter
            to_date: ISO datetime end filter

        Returns:
            Signals list response
        """
        params = {"limit": limit, "offset": offset}
        if direction:
            params["direction"] = direction
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date

        return await self.get("/api/v1/signals", params=params)

    async def get_user_settings(self, user_id: int) -> dict:
        """Get user notification settings."""
        return await self.get(f"/api/v1/notifications/{user_id}")

    async def update_user_settings(self, user_id: int, settings: dict) -> dict:
        """Update user notification settings."""
        return await self.put(f"/api/v1/notifications/{user_id}", json=settings)

    async def calculate_performance(self, months: int = 2, recalculate: bool = False) -> dict:
        """Trigger performance calculation (long-running)."""
        return await self._request(
            "POST",
            "/api/v1/performance/calculate",
            params={"months": months, "recalculate": str(recalculate).lower()},
            timeout=300,
        )

    async def get_performance_stats(self, months: int = 2) -> dict:
        """Get performance statistics."""
        return await self.get("/api/v1/performance/stats", params={"months": months})

    async def get_performance_signals(self, months: int = 2, limit: int = 50) -> dict:
        """Get signals with performance data."""
        return await self.get("/api/v1/performance/signals", params={"months": months, "limit": limit})


# Global client instance
strong_client = StrongServiceClient()
