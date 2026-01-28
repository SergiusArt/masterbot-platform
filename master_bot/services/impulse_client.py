"""HTTP client for Impulse Service."""

from typing import Optional

from services.base import BaseServiceClient
from config import settings


class ImpulseServiceClient(BaseServiceClient):
    """HTTP client for Impulse Service API."""

    def __init__(self):
        super().__init__(settings.IMPULSE_SERVICE_URL)

    async def get_analytics(self, period: str) -> dict:
        """Get analytics for period.

        Args:
            period: Analytics period (today, yesterday, week, month)

        Returns:
            Analytics data
        """
        return await self.get(f"/api/v1/analytics/{period}")

    async def generate_report(self, report_type: str, user_id: int) -> dict:
        """Request report generation.

        Args:
            report_type: Report type (morning, evening, weekly, monthly)
            user_id: User ID

        Returns:
            Report data
        """
        return await self.post(
            "/api/v1/reports/generate",
            json={"type": report_type, "user_id": user_id},
        )

    async def get_user_settings(self, user_id: int) -> dict:
        """Get user notification settings.

        Args:
            user_id: User ID

        Returns:
            User settings
        """
        return await self.get(f"/api/v1/notifications/{user_id}")

    async def update_user_settings(self, user_id: int, settings_data: dict) -> dict:
        """Update user notification settings.

        Args:
            user_id: User ID
            settings_data: New settings

        Returns:
            Updated settings
        """
        return await self.put(
            f"/api/v1/notifications/{user_id}",
            json=settings_data,
        )

    async def get_signals(
        self,
        limit: int = 100,
        offset: int = 0,
        from_date: Optional[str] = None,
    ) -> dict:
        """Get signals list.

        Args:
            limit: Maximum number of signals
            offset: Offset for pagination
            from_date: Filter by date (ISO format)

        Returns:
            Signals list
        """
        params = {"limit": limit, "offset": offset}
        if from_date:
            params["from_date"] = from_date
        return await self.get("/api/v1/signals", params=params)


# Global client instance
impulse_client = ImpulseServiceClient()
