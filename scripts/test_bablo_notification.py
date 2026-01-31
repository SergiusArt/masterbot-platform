#!/usr/bin/env python3
"""Test Bablo notification system by publishing a test signal notification."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from shared.utils.redis_client import get_redis_client
from shared.constants import REDIS_CHANNEL_BABLO, EVENT_BABLO_SIGNAL


async def test_bablo_notification():
    """Publish test Bablo signal notification to Redis."""
    print("📡 Connecting to Redis...")
    redis = await get_redis_client()

    user_id = 1380438067  # Your user ID

    # Test Bablo signal data
    test_data = {
        "event": EVENT_BABLO_SIGNAL,
        "user_id": user_id,
        "data": {
            "symbol": "TESTBTC.P",
            "direction": "long",
            "strength": 4,
            "timeframe": "15m",
            "quality": 8,
            "message": "🟩🟩🟩🟩 <b>TESTBTC.P</b>\n🟢 Long | 15m ТФ\n⭐ Качество: 8/10\n",
        },
    }

    print(f"\n📨 Publishing test Bablo notification to {REDIS_CHANNEL_BABLO}...")
    print(f"User ID: {test_data['user_id']}")
    print(f"Symbol: {test_data['data']['symbol']}")
    print(f"Direction: {test_data['data']['direction']}")
    print(f"Strength: {test_data['data']['strength']} squares")
    print(f"Timeframe: {test_data['data']['timeframe']}")
    print(f"Quality: {test_data['data']['quality']}/10")

    await redis.publish(REDIS_CHANNEL_BABLO, test_data)

    print("\n✅ Test Bablo notification published!")
    print("Check your Telegram bot for the notification.")

    await redis.close()


if __name__ == "__main__":
    asyncio.run(test_bablo_notification())
