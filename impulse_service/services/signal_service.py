"""Signal service for managing impulses."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.impulse import Impulse
from shared.database.connection import async_session_maker
from shared.schemas.impulse import ImpulseCreate, ImpulseSchema, SignalListResponse
from shared.utils.logger import get_logger

logger = get_logger("signal_service")


class SignalService:
    """Service for managing signal/impulse data."""

    async def create_signal(self, impulse: ImpulseCreate) -> int:
        """Create new impulse signal.

        Args:
            impulse: Impulse data

        Returns:
            Created impulse ID
        """
        async with async_session_maker() as session:
            db_impulse = Impulse(
                symbol=impulse.symbol,
                percent=impulse.percent,
                max_percent=impulse.max_percent,
                type=impulse.type,
                growth_ratio=impulse.growth_ratio,
                fall_ratio=impulse.fall_ratio,
                raw_message=impulse.raw_message,
            )
            session.add(db_impulse)
            await session.commit()
            await session.refresh(db_impulse)

            logger.info(f"Created impulse: {db_impulse.symbol} {db_impulse.percent}%")
            return db_impulse.id

    async def get_signals(
        self,
        limit: int = 100,
        offset: int = 0,
        from_date: Optional[str] = None,
    ) -> SignalListResponse:
        """Get list of signals with pagination.

        Args:
            limit: Maximum number of signals
            offset: Number of signals to skip
            from_date: Filter by date (ISO format)

        Returns:
            Signals list with pagination info
        """
        async with async_session_maker() as session:
            query = select(Impulse).order_by(Impulse.received_at.desc())

            if from_date:
                try:
                    date_filter = datetime.fromisoformat(from_date)
                    query = query.where(Impulse.received_at >= date_filter)
                except ValueError:
                    pass

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total = await session.scalar(count_query) or 0

            # Get paginated results
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            signals = result.scalars().all()

            return SignalListResponse(
                signals=[
                    ImpulseSchema(
                        id=s.id,
                        symbol=s.symbol,
                        percent=s.percent,
                        max_percent=s.max_percent,
                        type=s.type,
                        growth_ratio=s.growth_ratio,
                        fall_ratio=s.fall_ratio,
                        raw_message=s.raw_message,
                        received_at=s.received_at,
                    )
                    for s in signals
                ],
                total=total,
                limit=limit,
                offset=offset,
            )

    async def get_recent_signals(self, minutes: int = 15) -> list[Impulse]:
        """Get signals from recent time window.

        Args:
            minutes: Time window in minutes

        Returns:
            List of recent impulses
        """
        from datetime import timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        async with async_session_maker() as session:
            query = (
                select(Impulse)
                .where(Impulse.received_at >= cutoff)
                .order_by(Impulse.received_at.desc())
            )
            result = await session.execute(query)
            return list(result.scalars().all())


# Global service instance
signal_service = SignalService()
