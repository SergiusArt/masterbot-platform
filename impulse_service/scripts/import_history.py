"""Import historical messages from Telegram channel."""

import asyncio
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from core.parser import ImpulseParser
from shared.database.connection import init_db, async_session_maker
from models.impulse import Impulse


async def import_history(limit: int = 500):
    """Import historical messages from the channel.

    Args:
        limit: Maximum number of messages to fetch
    """
    print(f"Connecting to Telegram...")

    client = TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    await client.start()
    print("Connected to Telegram!")

    # Initialize database
    print("Initializing database...")
    await init_db()

    # Get channel entity
    channel_id = settings.SOURCE_CHANNEL_ID
    print(f"Fetching messages from channel {channel_id}...")

    try:
        entity = await client.get_entity(channel_id)
        print(f"Channel: {getattr(entity, 'title', 'Unknown')}")
    except Exception as e:
        print(f"Error getting channel: {e}")
        await client.disconnect()
        return

    parser = ImpulseParser()
    imported = 0
    skipped = 0
    failed = 0

    async with async_session_maker() as session:
        async for message in client.iter_messages(entity, limit=limit):
            if not message.text:
                continue

            try:
                # Parse the message
                parsed = parser.parse(message.text)

                if parsed is None:
                    skipped += 1
                    continue

                # Check if already exists (by raw_message and received_at)
                # Create impulse record
                impulse = Impulse(
                    symbol=parsed.symbol,
                    percent=parsed.percent,
                    max_percent=parsed.max_percent,
                    type=parsed.type,
                    growth_ratio=parsed.growth_ratio,
                    fall_ratio=parsed.fall_ratio,
                    raw_message=message.text,
                    received_at=message.date.replace(tzinfo=timezone.utc),
                )

                session.add(impulse)
                imported += 1

                if imported % 50 == 0:
                    await session.commit()
                    print(f"  Imported {imported} impulses...")

            except Exception as e:
                failed += 1
                print(f"  Error parsing message: {e}")
                continue

        # Final commit
        await session.commit()

    await client.disconnect()

    print("\n" + "=" * 50)
    print(f"Import complete!")
    print(f"  Imported: {imported}")
    print(f"  Skipped (not impulse): {skipped}")
    print(f"  Failed: {failed}")
    print("=" * 50)


if __name__ == "__main__":
    # Get limit from command line argument
    limit = 500
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}, using default 500")

    print(f"Importing up to {limit} messages from channel history...")
    asyncio.run(import_history(limit))
