"""One-time script: backfill strong_signals from channel history."""

import asyncio
import os
import re
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon.sessions import StringSession

# DB
import asyncpg

# Config from env
API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ["TELEGRAM_SESSION_STRING"]
CHANNEL_ID = int(os.environ["STRONG_CHANNEL_ID"])

DB_USER = os.environ.get("DB_USER", "masterbot")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "masterbot_secure_2024")
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "masterbot_db")

# Parser patterns (same as core/parser.py)
LONG_RE = re.compile(r"🧤\*{0,2}([A-Z0-9]+(?:\.P)?)\*{0,2}\s*_{0,2}Long_{0,2}🧤", re.IGNORECASE)
SHORT_RE = re.compile(r"🎒\*{0,2}([A-Z0-9]+(?:\.P)?)\*{0,2}\s*_{0,2}Short_{0,2}🎒", re.IGNORECASE)


def parse(text: str):
    if not text:
        return None
    m = LONG_RE.search(text)
    if m:
        symbol = m.group(1)
        if symbol.endswith(".P"):
            symbol = symbol[:-2]
        return symbol, "long"
    m = SHORT_RE.search(text)
    if m:
        symbol = m.group(1)
        if symbol.endswith(".P"):
            symbol = symbol[:-2]
        return symbol, "short"
    return None


async def main():
    # Connect to Telegram
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    print(f"Connected to Telegram. Fetching messages from {CHANNEL_ID}...")

    # Fetch all messages from channel
    messages = []
    async for msg in client.iter_messages(CHANNEL_ID, limit=None):
        if msg.text:
            result = parse(msg.text)
            if result:
                symbol, direction = result
                messages.append({
                    "symbol": symbol,
                    "direction": direction,
                    "raw_message": msg.text,
                    "telegram_message_id": msg.id,
                    "received_at": msg.date.astimezone(timezone.utc),
                })

    await client.disconnect()
    print(f"Found {len(messages)} signals in channel history.")

    if not messages:
        print("Nothing to insert.")
        return

    # Connect to DB
    dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    conn = await asyncpg.connect(dsn)

    # Check existing telegram_message_ids to avoid duplicates
    existing = set()
    rows = await conn.fetch("SELECT telegram_message_id FROM strong_signals")
    for row in rows:
        existing.add(row["telegram_message_id"])

    inserted = 0
    for sig in messages:
        if sig["telegram_message_id"] in existing:
            continue
        await conn.execute(
            """INSERT INTO strong_signals (symbol, direction, raw_message, telegram_message_id, received_at)
               VALUES ($1, $2, $3, $4, $5)""",
            sig["symbol"],
            sig["direction"],
            sig["raw_message"],
            sig["telegram_message_id"],
            sig["received_at"],
        )
        inserted += 1

    await conn.close()
    print(f"Inserted {inserted} signals (skipped {len(messages) - inserted} duplicates).")


if __name__ == "__main__":
    asyncio.run(main())
