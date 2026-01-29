#!/usr/bin/env python3
"""Backfill missed impulses from Telegram channel."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from core.parser import impulse_parser
from services.signal_service import signal_service
from shared.schemas.impulse import ImpulseCreate
from shared.database.connection import init_db, close_db
from shared.utils.logger import setup_logger

logger = setup_logger("backfill")


async def get_last_impulse_date():
    """Get the date of the last impulse in database."""
    from shared.database.connection import async_session_maker
    from models import Impulse
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Impulse.received_at)
            .order_by(Impulse.received_at.desc())
            .limit(1)
        )
        last_date = result.scalar_one_or_none()
        return last_date


async def backfill_impulses():
    """Backfill missed impulses from Telegram channel."""
    logger.info("=" * 60)
    logger.info("Starting impulse backfill process")
    logger.info("=" * 60)

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Get last impulse date
    last_date = await get_last_impulse_date()
    if last_date:
        logger.info(f"Last impulse in database: {last_date}")
    else:
        logger.info("No impulses in database, will fetch all available history")

    # Check credentials
    if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
        logger.error("Telegram API credentials not configured")
        return

    if not settings.TELEGRAM_SESSION_STRING:
        logger.error("Telegram session string not configured")
        return

    if not settings.SOURCE_CHANNEL_ID:
        logger.error("Source channel ID not configured")
        return

    logger.info(f"Connecting to Telegram channel {settings.SOURCE_CHANNEL_ID}...")

    # Create Telegram client
    client = TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    try:
        await client.start()
        logger.info("Connected to Telegram successfully!")

        # Get channel entity
        channel = await client.get_entity(settings.SOURCE_CHANNEL_ID)
        logger.info(f"Channel: {getattr(channel, 'title', 'Unknown')}")

        # Determine how many messages to fetch
        # If we have last_date, fetch from that point
        # Otherwise, fetch last 100 messages
        if last_date:
            # Make last_date timezone-aware if it isn't
            if last_date.tzinfo is None:
                last_date = last_date.replace(tzinfo=timezone.utc)

            logger.info(f"Fetching messages since {last_date}...")
            # Get all messages since last_date
            messages = await client.get_messages(
                settings.SOURCE_CHANNEL_ID,
                limit=None,  # Get all
                offset_date=last_date,
            )
        else:
            logger.info("Fetching last 100 messages...")
            messages = await client.get_messages(
                settings.SOURCE_CHANNEL_ID,
                limit=100,
            )

        logger.info(f"Retrieved {len(messages)} messages from channel")

        # Process messages
        parsed_count = 0
        saved_count = 0
        skipped_count = 0
        error_count = 0

        for message in reversed(messages):  # Process in chronological order
            if not message.text:
                continue

            try:
                # Parse the message
                parsed = impulse_parser.parse(message.text)
                if not parsed:
                    skipped_count += 1
                    continue

                parsed_count += 1

                # Check if this impulse is newer than last_date
                message_date = message.date
                if message_date.tzinfo is None:
                    message_date = message_date.replace(tzinfo=timezone.utc)

                if last_date and message_date <= last_date:
                    logger.debug(f"Skipping {parsed.symbol} - already in database")
                    skipped_count += 1
                    continue

                # Create impulse in database
                impulse_create = ImpulseCreate(
                    symbol=parsed.symbol,
                    percent=parsed.percent,
                    max_percent=parsed.max_percent,
                    type=parsed.type,
                    growth_ratio=parsed.growth_ratio,
                    fall_ratio=parsed.fall_ratio,
                    raw_message=message.text,
                )

                await signal_service.create_signal(impulse_create)
                saved_count += 1

                logger.info(
                    f"✅ Saved: {parsed.symbol} {parsed.percent:+.2f}% "
                    f"({parsed.type}) at {message_date}"
                )

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing message: {e}")
                logger.debug(f"Message text: {message.text[:100]}...")

        logger.info("=" * 60)
        logger.info("Backfill complete!")
        logger.info(f"Total messages retrieved: {len(messages)}")
        logger.info(f"Successfully parsed: {parsed_count}")
        logger.info(f"Saved to database: {saved_count}")
        logger.info(f"Skipped (not impulse or duplicate): {skipped_count}")
        logger.info(f"Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error during backfill: {e}", exc_info=True)
    finally:
        await client.disconnect()
        await close_db()
        logger.info("Disconnected from Telegram")


if __name__ == "__main__":
    asyncio.run(backfill_impulses())
