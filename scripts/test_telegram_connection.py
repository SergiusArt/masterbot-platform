#!/usr/bin/env python3
"""Test Telegram connection and session validity."""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv


async def test_connection():
    """Test Telegram connection."""
    # Load environment variables
    load_dotenv()

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_string = os.getenv("TELEGRAM_SESSION_STRING")
    channel_id = os.getenv("SOURCE_CHANNEL_ID")

    print("=" * 50)
    print("Telegram Connection Test")
    print("=" * 50)
    print()

    # Check credentials
    print("1. Checking credentials...")
    if not api_id:
        print("❌ TELEGRAM_API_ID not found in .env")
        return
    if not api_hash:
        print("❌ TELEGRAM_API_HASH not found in .env")
        return
    if not session_string:
        print("❌ TELEGRAM_SESSION_STRING not found in .env")
        return
    if not channel_id:
        print("❌ SOURCE_CHANNEL_ID not found in .env")
        return

    print(f"✅ TELEGRAM_API_ID: {api_id}")
    print(f"✅ TELEGRAM_API_HASH: {api_hash[:10]}...")
    print(f"✅ TELEGRAM_SESSION_STRING length: {len(session_string)}")
    print(f"✅ SOURCE_CHANNEL_ID: {channel_id}")
    print()

    # Test connection
    print("2. Creating Telegram client...")
    try:
        client = TelegramClient(
            StringSession(session_string),
            int(api_id),
            api_hash,
        )
        print("✅ Client created")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return

    print()
    print("3. Connecting to Telegram...")
    try:
        await asyncio.wait_for(client.start(), timeout=30.0)
        print("✅ Connected successfully!")
    except asyncio.TimeoutError:
        print("❌ Connection timeout (30 seconds)")
        return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print()
    print("4. Getting account info...")
    try:
        me = await client.get_me()
        print(f"✅ Logged in as: {me.first_name} (ID: {me.id})")
    except Exception as e:
        print(f"❌ Failed to get account info: {e}")
        await client.disconnect()
        return

    print()
    print("5. Checking channel access...")
    try:
        channel = await client.get_entity(int(channel_id))
        print(f"✅ Channel found: {getattr(channel, 'title', 'Unknown')}")
        print(f"   Channel ID: {channel_id}")
    except ValueError as e:
        print(f"❌ Invalid channel ID format: {e}")
        await client.disconnect()
        return
    except Exception as e:
        print(f"❌ Failed to access channel: {e}")
        print("   This could mean:")
        print("   - You don't have access to the channel")
        print("   - The channel ID is incorrect")
        print("   - The session has been revoked")
        await client.disconnect()
        return

    print()
    print("6. Testing message retrieval...")
    try:
        messages = await client.get_messages(int(channel_id), limit=1)
        if messages:
            print(f"✅ Successfully retrieved last message")
            print(f"   Date: {messages[0].date}")
            print(f"   Text preview: {messages[0].text[:100] if messages[0].text else 'No text'}...")
        else:
            print("⚠️  No messages in channel")
    except Exception as e:
        print(f"❌ Failed to retrieve messages: {e}")

    await client.disconnect()

    print()
    print("=" * 50)
    print("Test completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_connection())
