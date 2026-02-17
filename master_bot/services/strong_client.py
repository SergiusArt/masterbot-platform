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
    ) -> dict:
        """Get list of signals.

        Args:
            limit: Maximum number of signals
            offset: Number of signals to skip
            direction: Filter by direction (long/short)

        Returns:
            Signals list response
        """
        params = {"limit": limit, "offset": offset}
        if direction:
            params["direction"] = direction

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


# Global client instance
strong_client = StrongServiceClient()
