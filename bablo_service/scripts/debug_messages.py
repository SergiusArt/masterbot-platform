#!/usr/bin/env python3
"""Debug script to view Bablo channel messages."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from core.parser import bablo_parser


async def main():
    print("Connecting to Telegram...")

    client = TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    await client.start()
    print(f"Connected! Fetching messages from channel {settings.BABLO_CHANNEL_ID}...\n")

    messages = await client.get_messages(settings.BABLO_CHANNEL_ID, limit=10)

    for i, msg in enumerate(messages, 1):
        print(f"{'='*60}")
        print(f"Message {i} (ID: {msg.id}, Date: {msg.date})")
        print(f"{'='*60}")
        if msg.text:
            print(msg.text[:500])
            print()

            # Try to parse
            parsed = bablo_parser.parse(msg.text)
            if parsed:
                print(f"✅ PARSED: {parsed.symbol} {parsed.direction} {parsed.timeframe} Q:{parsed.quality_total}")
            else:
                print("❌ NOT PARSED")
        else:
            print("[No text content]")
        print()

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
