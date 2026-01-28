"""Show sample messages from channel for format analysis."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import TelegramClient
from telethon.sessions import StringSession
from config import settings


async def show_messages(limit: int = 10):
    """Show sample messages from the channel."""
    client = TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    await client.start()

    channel_id = settings.SOURCE_CHANNEL_ID
    entity = await client.get_entity(channel_id)
    print(f"Channel: {getattr(entity, 'title', 'Unknown')}\n")
    print("=" * 60)

    async for message in client.iter_messages(entity, limit=limit):
        if message.text:
            print(f"[{message.date}]")
            print(message.text)
            print("-" * 60)

    await client.disconnect()


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(show_messages(limit))
