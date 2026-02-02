"""Base HTTP client for service communication."""

from typing import Any, Optional

import aiohttp
from aiohttp import ClientTimeout


class BaseServiceClient:
    """Base HTTP client for microservice communication."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize client.

        Args:
            base_url: Service base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request to service.

        Args:
            method: HTTP method
            endpoint: API endpoint
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            aiohttp.ClientError: On request failure
        """
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.request(
                method=method,
                url=url,
                json=json,
                params=params,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        """Make GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make POST request."""
        return await self._request("POST", endpoint, json=json, params=params)

    async def put(
        self,
        endpoint: str,
        json: Optional[dict] = None,
    ) -> dict:
        """Make PUT request."""
        return await self._request("PUT", endpoint, json=json)

    async def delete(
        self,
        endpoint: str,
    ) -> dict:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint)

    async def health_check(self) -> bool:
        """Check service health.

        Returns:
            True if service is healthy
        """
        try:
            response = await self.get("/health")
            return response.get("status") == "healthy"
        except Exception:
            return False
