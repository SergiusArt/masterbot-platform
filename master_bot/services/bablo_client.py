"""HTTP client for Bablo Service."""

from typing import Optional

from services.base import BaseServiceClient
from config import settings


class BabloServiceClient(BaseServiceClient):
    """Client for communicating with Bablo Service."""

    def __init__(self):
        super().__init__(settings.BABLO_SERVICE_URL)

    async def get_analytics(self, period: str) -> dict:
        """Get analytics for specified period.

        Args:
            period: Period name (today, yesterday, week, month)

        Returns:
            Analytics data dictionary
        """
        return await self.get(f"/api/v1/analytics/{period}")

    async def get_signals(
        self,
        limit: int = 100,
        offset: int = 0,
        direction: Optional[str] = None,
        timeframe: Optional[str] = None,
        min_quality: Optional[int] = None,
        min_strength: Optional[int] = None,
        max_strength: Optional[int] = None,
    ) -> dict:
        """Get list of signals.

        Args:
            limit: Maximum number of signals
            offset: Number of signals to skip
            direction: Filter by direction
            timeframe: Filter by timeframe
            min_quality: Filter by minimum quality
            min_strength: Filter by minimum strength (1-5)
            max_strength: Filter by maximum strength (1-5)

        Returns:
            Signals list response
        """
        params = {"limit": limit, "offset": offset}
        if direction:
            params["direction"] = direction
        if timeframe:
            params["timeframe"] = timeframe
        if min_quality:
            params["min_quality"] = min_quality
        if min_strength:
            params["min_strength"] = min_strength
        if max_strength:
            params["max_strength"] = max_strength

        return await self.get("/api/v1/signals", params=params)

    async def get_user_settings(self, user_id: int) -> dict:
        """Get user notification settings.

        Args:
            user_id: User ID

        Returns:
            User settings dictionary
        """
        return await self.get(f"/api/v1/notifications/{user_id}")

    async def update_user_settings(self, user_id: int, settings: dict) -> dict:
        """Update user notification settings.

        Args:
            user_id: User ID
            settings: Settings to update

        Returns:
            Update response
        """
        return await self.put(f"/api/v1/notifications/{user_id}", json=settings)

    async def generate_report(self, report_type: str) -> dict:
        """Generate report on demand.

        Args:
            report_type: Report type (morning, evening, weekly, monthly)

        Returns:
            Report data
        """
        return await self.post(
            "/api/v1/reports/generate",
            params={"report_type": report_type},
        )

    async def get_report_data(self, report_type: str) -> dict:
        """Get raw report data for aggregation.

        Args:
            report_type: Report type

        Returns:
            Raw report data
        """
        return await self.get(f"/api/v1/reports/data/{report_type}")


    async def get_users_for_report(self, report_type: str) -> list[int]:
        """Get users subscribed to specific report type.

        Args:
            report_type: Report type (morning, evening, weekly, monthly)

        Returns:
            List of user IDs
        """
        result = await self.get(f"/api/v1/notifications/reports/{report_type}/users")
        return result.get("users", [])


# Global client instance
bablo_client = BabloServiceClient()
