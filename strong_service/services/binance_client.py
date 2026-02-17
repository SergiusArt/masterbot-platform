"""Binance Futures API client for kline data."""

import asyncio
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from config import settings
from shared.utils.logger import get_logger

logger = get_logger("binance_client")

# Binance Futures kline response indices
OPEN_TIME = 0
OPEN = 1
HIGH = 2
LOW = 3
CLOSE = 4

BINANCE_FUTURES_URL = "https://fapi.binance.com"


class BinanceClient:
    """Client for Binance Futures API (klines only)."""

    def __init__(self):
        self._api_key = settings.BINANCE_API_KEY
        self._min_interval = 0.15  # ~7 req/sec, well within 480/min limit

    async def get_klines(
        self,
        symbol: str,
        interval: str = "30m",
        start_time: Optional[datetime] = None,
        limit: int = 101,
    ) -> list[list]:
        """Fetch kline/candlestick data from Binance Futures.

        Args:
            symbol: Trading pair (e.g. "DOTUSDT")
            interval: Kline interval (e.g. "30m")
            start_time: Start time (UTC datetime)
            limit: Number of candles (max 1500)

        Returns:
            List of kline arrays [open_time, open, high, low, close, ...]
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)

        headers = {}
        if self._api_key:
            headers["X-MBX-APIKEY"] = self._api_key

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BINANCE_FUTURES_URL}/fapi/v1/klines",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"Binance API error {resp.status}: {text}")
                    raise ValueError(f"Binance API error {resp.status}: {text}")
                return await resp.json()

        # Rate limiter delay applied by caller between requests

    def get_entry_candle_start(self, received_at: datetime) -> datetime:
        """Round down signal time to the start of its 30-minute candle.

        Args:
            received_at: Signal timestamp (UTC)

        Returns:
            Candle open time (UTC)
        """
        ts = received_at.replace(second=0, microsecond=0)
        return ts.replace(minute=(ts.minute // 30) * 30)

    async def throttle(self):
        """Rate limiter pause between API calls."""
        await asyncio.sleep(self._min_interval)


# Global instance
binance_client = BinanceClient()
