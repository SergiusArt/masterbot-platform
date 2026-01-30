#!/usr/bin/env python3
"""Test notification system by publishing a test impulse notification."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from shared.utils.redis_client import get_redis_client
from shared.constants import REDIS_CHANNEL_NOTIFICATIONS, EVENT_IMPULSE_ALERT


async def test_notification():
    """Publish test impulse notification to Redis."""
    print("📡 Connecting to Redis...")
    redis = await get_redis_client()

    # Test notification data
    test_data = {
        "event": EVENT_IMPULSE_ALERT,
        "user_id": int(input("Enter your Telegram user ID: ")),
        "data": {
            "symbol": "TESTBTC",
            "percent": 5.25,
            "type": "growth",
        },
    }

    print(f"\n📨 Publishing test notification to {REDIS_CHANNEL_NOTIFICATIONS}...")
    print(f"User ID: {test_data['user_id']}")
    print(f"Symbol: {test_data['data']['symbol']}")
    print(f"Percent: +{test_data['data']['percent']}%")
    print(f"Type: {test_data['data']['type']}")

    await redis.publish(REDIS_CHANNEL_NOTIFICATIONS, test_data)

    print("\n✅ Test notification published!")
    print("Check your Telegram bot for the notification.")

    await redis.close()


if __name__ == "__main__":
    asyncio.run(test_notification())
