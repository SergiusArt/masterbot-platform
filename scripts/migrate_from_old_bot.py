#!/usr/bin/env python3
"""
Migration script from old ImpulseBot (SQLite) to MasterBot Platform (PostgreSQL).

Usage:
    python scripts/migrate_from_old_bot.py /path/to/old/bot.db

Before running, ensure:
1. PostgreSQL database is created and migrations applied
2. Old bot is stopped (to prevent data changes during migration)
"""

import asyncio
import argparse
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")


async def migrate_impulses(sqlite_conn: sqlite3.Connection, pg_conn: asyncpg.Connection):
    """Migrate impulse history."""
    print("📊 Migrating impulses...")

    cursor = sqlite_conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='impulses'
    """)
    if not cursor.fetchone():
        print("   Table 'impulses' not found, skipping")
        return

    cursor.execute("""
        SELECT symbol, percent, max_percent, type,
               growth_ratio, fall_ratio, raw_message, created_at
        FROM impulses
        ORDER BY created_at
    """)

    impulses = cursor.fetchall()
    print(f"   Found {len(impulses)} impulses")

    if not impulses:
        return

    # Batch insert
    batch_size = 1000
    inserted = 0

    for i in range(0, len(impulses), batch_size):
        batch = impulses[i:i + batch_size]

        await pg_conn.executemany("""
            INSERT INTO impulses
                (symbol, percent, max_percent, type, growth_ratio, fall_ratio, raw_message, received_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT DO NOTHING
        """, [
            (
                row[0],  # symbol
                row[1],  # percent
                row[2],  # max_percent
                row[3],  # type
                row[4],  # growth_ratio
                row[5],  # fall_ratio
                row[6],  # raw_message
                datetime.fromisoformat(row[7]) if row[7] else datetime.now()
            )
            for row in batch
        ])

        inserted += len(batch)
        print(f"   Processed: {inserted}/{len(impulses)}")

    print(f"✅ Impulses migrated: {inserted}")


async def migrate_users(sqlite_conn: sqlite3.Connection, pg_conn: asyncpg.Connection):
    """Migrate users."""
    print("👥 Migrating users...")

    cursor = sqlite_conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='users'
    """)
    if not cursor.fetchone():
        print("   Table 'users' not found, skipping")
        return

    cursor.execute("""
        SELECT id, username, access_until, is_admin, created_at
        FROM users
    """)

    users = cursor.fetchall()
    print(f"   Found {len(users)} users")

    for row in users:
        user_id, username, access_until, is_admin, created_at = row

        # Parse date
        expires_at = None
        if access_until:
            try:
                expires_at = datetime.fromisoformat(access_until)
            except:
                try:
                    expires_at = datetime.strptime(access_until, "%d.%m.%Y")
                except:
                    pass

        created = datetime.now()
        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
            except:
                pass

        await pg_conn.execute("""
            INSERT INTO users (id, username, is_admin, is_active, access_expires_at, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                is_admin = EXCLUDED.is_admin,
                access_expires_at = EXCLUDED.access_expires_at
        """, user_id, username, bool(is_admin), True, expires_at, created)

        # Create subscription to Impulse Service
        await pg_conn.execute("""
            INSERT INTO user_service_subscriptions (user_id, service_name, is_active, expires_at)
            VALUES ($1, 'impulse_service', TRUE, $2)
            ON CONFLICT (user_id, service_name) DO UPDATE SET
                expires_at = EXCLUDED.expires_at
        """, user_id, expires_at)

    print(f"✅ Users migrated: {len(users)}")


async def migrate_user_settings(sqlite_conn: sqlite3.Connection, pg_conn: asyncpg.Connection):
    """Migrate user notification settings."""
    print("⚙️ Migrating user settings...")

    cursor = sqlite_conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='user_settings'
    """)
    if not cursor.fetchone():
        print("   Table 'user_settings' not found, skipping")
        return

    cursor.execute("SELECT * FROM user_settings")
    settings = cursor.fetchall()
    print(f"   Found {len(settings)} settings")

    if not settings:
        return

    # Get column names
    columns = [description[0] for description in cursor.description]

    for row in settings:
        data = dict(zip(columns, row))
        user_id = data.get('user_id')

        if not user_id:
            continue

        await pg_conn.execute("""
            INSERT INTO user_notification_settings (
                user_id,
                growth_threshold,
                fall_threshold,
                morning_report,
                evening_report,
                weekly_report,
                monthly_report,
                activity_window_minutes,
                activity_threshold
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (user_id) DO UPDATE SET
                growth_threshold = EXCLUDED.growth_threshold,
                fall_threshold = EXCLUDED.fall_threshold,
                morning_report = EXCLUDED.morning_report,
                evening_report = EXCLUDED.evening_report,
                weekly_report = EXCLUDED.weekly_report,
                monthly_report = EXCLUDED.monthly_report,
                activity_window_minutes = EXCLUDED.activity_window_minutes,
                activity_threshold = EXCLUDED.activity_threshold
        """,
            user_id,
            data.get('growth_threshold', 20),
            data.get('fall_threshold', -15),
            bool(data.get('morning_report', 1)),
            bool(data.get('evening_report', 1)),
            bool(data.get('weekly_report', 1)),
            bool(data.get('monthly_report', 1)),
            data.get('activity_window', 15),
            data.get('activity_threshold', 10)
        )

    print(f"✅ Settings migrated: {len(settings)}")


async def verify_migration(sqlite_conn: sqlite3.Connection, pg_conn: asyncpg.Connection):
    """Verify migration."""
    print("\n🔍 Verifying migration...")

    cursor = sqlite_conn.cursor()

    # Check impulses
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='impulses'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM impulses")
        sqlite_impulses = cursor.fetchone()[0]
        pg_impulses = await pg_conn.fetchval("SELECT COUNT(*) FROM impulses")
        print(f"   Impulses: SQLite={sqlite_impulses}, PostgreSQL={pg_impulses}")

    # Check users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM users")
        sqlite_users = cursor.fetchone()[0]
        pg_users = await pg_conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"   Users: SQLite={sqlite_users}, PostgreSQL={pg_users}")

    print("\n✅ Migration verification complete!")


async def main(sqlite_path: str):
    """Main migration function."""
    print("=" * 60)
    print("📦 MIGRATION: ImpulseBot → MasterBot Platform")
    print("=" * 60)

    # Check SQLite file
    if not Path(sqlite_path).exists():
        print(f"❌ File not found: {sqlite_path}")
        return

    print(f"\n📁 Source: {sqlite_path}")
    print(f"🎯 Target: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

    # Connect
    sqlite_conn = sqlite3.connect(sqlite_path)
    pg_conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Run in transaction
        async with pg_conn.transaction():
            await migrate_impulses(sqlite_conn, pg_conn)
            await migrate_users(sqlite_conn, pg_conn)
            await migrate_user_settings(sqlite_conn, pg_conn)
            await verify_migration(sqlite_conn, pg_conn)

    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        raise
    finally:
        sqlite_conn.close()
        await pg_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate data from old ImpulseBot")
    parser.add_argument("sqlite_path", help="Path to old bot.db file")
    parser.add_argument("--dry-run", action="store_true", help="Check only, no write")

    args = parser.parse_args()
    asyncio.run(main(args.sqlite_path))
