#!/usr/bin/env python3
"""Script to register a new service in the platform."""

import asyncio
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


async def register_service(
    name: str,
    display_name: str,
    base_url: str,
    description: str = None,
    menu_icon: str = "📦",
    menu_order: int = 100,
):
    """Register a new service in the database."""
    from shared.database.connection import async_session_maker
    from shared.database.models import Service
    from sqlalchemy import select

    async with async_session_maker() as session:
        # Check if service already exists
        result = await session.execute(
            select(Service).where(Service.name == name)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"⚠️ Service '{name}' already exists.")
            print(f"   Display name: {existing.display_name}")
            print(f"   URL: {existing.base_url}")
            print(f"   Active: {existing.is_active}")
            return

        # Create new service
        service = Service(
            name=name,
            display_name=display_name,
            description=description,
            base_url=base_url,
            is_active=True,
            menu_icon=menu_icon,
            menu_order=menu_order,
        )
        session.add(service)
        await session.commit()

        print(f"✅ Service registered successfully!")
        print(f"   Name: {name}")
        print(f"   Display name: {display_name}")
        print(f"   URL: {base_url}")
        print(f"   Icon: {menu_icon}")
        print(f"   Order: {menu_order}")


async def list_services():
    """List all registered services."""
    from shared.database.connection import async_session_maker
    from shared.database.models import Service
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Service).order_by(Service.menu_order)
        )
        services = result.scalars().all()

        if not services:
            print("No services registered.")
            return

        print("📋 Registered services:\n")
        for service in services:
            status = "🟢" if service.is_active else "🔴"
            print(f"{status} {service.menu_icon} {service.display_name}")
            print(f"   Name: {service.name}")
            print(f"   URL: {service.base_url}")
            print(f"   Order: {service.menu_order}")
            print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Register services in MasterBot Platform")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new service")
    register_parser.add_argument("--name", required=True, help="Service unique name")
    register_parser.add_argument("--display-name", required=True, help="Display name")
    register_parser.add_argument("--url", required=True, help="Service base URL")
    register_parser.add_argument("--description", help="Service description")
    register_parser.add_argument("--icon", default="📦", help="Menu icon emoji")
    register_parser.add_argument("--order", type=int, default=100, help="Menu order")

    # List command
    subparsers.add_parser("list", help="List all services")

    args = parser.parse_args()

    if args.command == "register":
        asyncio.run(register_service(
            name=args.name,
            display_name=args.display_name,
            base_url=args.url,
            description=args.description,
            menu_icon=args.icon,
            menu_order=args.order,
        ))
    elif args.command == "list":
        asyncio.run(list_services())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
