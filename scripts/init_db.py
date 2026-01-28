#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.connection import engine, Base
from shared.database.models import User, Service, UserServiceSubscription, ActionLog

# Import impulse models
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "impulse_service"))
from models.impulse import Impulse, UserNotificationSettings


async def init_database():
    """Initialize database tables."""
    print("Initializing database...")

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")


async def create_default_data():
    """Create default data."""
    from sqlalchemy import select
    from shared.database.connection import async_session_maker

    print("Creating default data...")

    async with async_session_maker() as session:
        # Check if Impulse Service is registered
        result = await session.execute(
            select(Service).where(Service.name == "impulse_service")
        )
        existing = result.scalar_one_or_none()

        if not existing:
            impulse_service = Service(
                name="impulse_service",
                display_name="📊 Импульсы",
                description="Сервис отслеживания криптовалютных импульсов",
                base_url="http://impulse_service:8001",
                is_active=True,
                health_endpoint="/health",
                menu_icon="📊",
                menu_order=10,
            )
            session.add(impulse_service)
            await session.commit()
            print("Impulse Service registered.")
        else:
            print("Impulse Service already registered.")

    print("Default data created successfully!")


async def main():
    """Main function."""
    await init_database()
    await create_default_data()
    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())
