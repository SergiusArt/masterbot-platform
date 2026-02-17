"""Strong Signal business logic service."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.strong import StrongSignal
from core.parser import ParsedStrongSignal
from shared.utils.logger import get_logger

logger = get_logger("strong_signal_service")


class SignalService:
    """Service for managing Strong signals."""

    async def create_signal(
        self,
        session: AsyncSession,
        signal_data: ParsedStrongSignal,
        telegram_message_id: Optional[int] = None,
    ) -> StrongSignal:
        """Create a new signal record.

        Args:
            session: Database session
            signal_data: Parsed signal data
            telegram_message_id: Telegram message ID

        Returns:
            Created StrongSignal instance
        """
        signal = StrongSignal(
            symbol=signal_data.symbol,
            direction=signal_data.direction,
            raw_message=signal_data.raw_message,
            telegram_message_id=telegram_message_id,
        )
        session.add(signal)
        await session.commit()
        await session.refresh(signal)

        logger.info(f"Created signal: {signal.symbol} {signal.direction}")
        return signal

    async def get_signals(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        direction: Optional[str] = None,
    ) -> list[StrongSignal]:
        """Get signals with optional filtering.

        Args:
            session: Database session
            limit: Maximum number of signals
            offset: Number of signals to skip
            direction: Filter by direction (long/short)

        Returns:
            List of StrongSignal instances
        """
        query = select(StrongSignal).order_by(StrongSignal.received_at.desc())

        if direction:
            query = query.where(StrongSignal.direction == direction)

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_signals_count(
        self,
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> int:
        """Get count of signals in period.

        Args:
            session: Database session
            from_date: Start date filter
            to_date: End date filter

        Returns:
            Number of signals
        """
        query = select(func.count(StrongSignal.id))
        if from_date:
            query = query.where(StrongSignal.received_at >= from_date)
        if to_date:
            query = query.where(StrongSignal.received_at <= to_date)

        result = await session.execute(query)
        return result.scalar() or 0


# Global instance
signal_service = SignalService()
