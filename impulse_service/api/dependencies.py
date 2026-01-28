"""FastAPI dependencies for Impulse Service."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.connection import async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
