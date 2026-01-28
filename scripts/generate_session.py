#!/usr/bin/env python3
"""Generate a new Telegram session string."""

import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        print("Error: Set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables")
        print("\nExample:")
        print("  export TELEGRAM_API_ID=12345678")
        print("  export TELEGRAM_API_HASH=abcdef123456...")
        sys.exit(1)

    print("Creating new Telegram session...")
    print("You will need to enter your phone number and verification code.\n")

    client = TelegramClient(StringSession(), int(api_id), api_hash)

    await client.start()

    session_string = client.session.save()

    print("\n" + "=" * 60)
    print("NEW SESSION STRING (save this!):")
    print("=" * 60)
    print(session_string)
    print("=" * 60)

    print("\nAdd this to your .env file:")
    print(f"TELEGRAM_SESSION_STRING={session_string}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
