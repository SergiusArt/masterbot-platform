#!/usr/bin/env python3
"""Script to import historical messages from Bablo Telegram channel."""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from core.parser import bablo_parser
from models.bablo import Base, BabloSignal


async def import_history(days: int = 30, limit: int = 1000) -> None:
    """Import historical messages from Bablo channel.

    Args:
        days: Number of days to import (from now backwards)
        limit: Maximum number of messages to import
    """
    print(f"Starting history import for last {days} days (max {limit} messages)...")

    # Setup database
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Setup Telegram client
    client = TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    await client.start()
    print("Connected to Telegram")

    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(f"Fetching messages from {start_date} to {end_date}...")

        # Get messages from channel
        messages = await client.get_messages(
            settings.BABLO_CHANNEL_ID,
            limit=limit,
            offset_date=end_date,
        )

        print(f"Retrieved {len(messages)} messages")

        imported = 0
        skipped = 0
        failed = 0

        async with async_session() as session:
            for msg in messages:
                if not msg.text:
                    skipped += 1
                    continue

                # Check if message is within date range
                if msg.date.replace(tzinfo=None) < start_date:
                    continue

                # Parse message
                parsed = bablo_parser.parse(msg.text)
                if not parsed:
                    skipped += 1
                    continue

                try:
                    # Create signal record
                    signal = BabloSignal(
                        symbol=parsed.symbol,
                        direction=parsed.direction,
                        strength=parsed.strength,
                        timeframe=parsed.timeframe,
                        time_horizon=parsed.time_horizon,
                        quality_total=parsed.quality_total,
                        quality_profit=parsed.quality_profit,
                        quality_drawdown=parsed.quality_drawdown,
                        quality_accuracy=parsed.quality_accuracy,
                        probabilities=parsed.probabilities,
                        max_drawdown=parsed.max_drawdown,
                        raw_message=parsed.raw_message,
                        received_at=msg.date.replace(tzinfo=None),
                    )

                    session.add(signal)
                    imported += 1

                    if imported % 50 == 0:
                        await session.commit()
                        print(f"Imported {imported} signals...")

                except Exception as e:
                    print(f"Error saving signal: {e}")
                    failed += 1

            # Final commit
            await session.commit()

        print("\n" + "=" * 50)
        print("Import completed!")
        print(f"  Imported: {imported}")
        print(f"  Skipped: {skipped}")
        print(f"  Failed: {failed}")
        print("=" * 50)

    finally:
        await client.disconnect()
        await engine.dispose()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Import Bablo history from Telegram")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to import (default: 30)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum messages to fetch (default: 1000)",
    )

    args = parser.parse_args()
    await import_history(days=args.days, limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
