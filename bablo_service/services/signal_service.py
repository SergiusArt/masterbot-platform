"""Signal service for Bablo signals."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.bablo import BabloSignal
from core.parser import ParsedBabloSignal
from shared.utils.logger import get_logger

logger = get_logger("bablo_signal_service")


class SignalService:
    """Service for managing Bablo signals."""

    async def create_signal(
        self,
        session: AsyncSession,
        signal_data: ParsedBabloSignal,
        telegram_message_id: Optional[int] = None,
    ) -> BabloSignal:
        """Create a new signal in database.

        Args:
            session: Database session
            signal_data: Parsed signal data
            telegram_message_id: Optional Telegram message ID

        Returns:
            Created BabloSignal instance
        """
        signal = BabloSignal(
            symbol=signal_data.symbol,
            direction=signal_data.direction,
            strength=signal_data.strength,
            timeframe=signal_data.timeframe,
            time_horizon=signal_data.time_horizon,
            quality_total=signal_data.quality_total,
            quality_profit=signal_data.quality_profit,
            quality_drawdown=signal_data.quality_drawdown,
            quality_accuracy=signal_data.quality_accuracy,
            probabilities=signal_data.probabilities,
            max_drawdown=signal_data.max_drawdown,
            raw_message=signal_data.raw_message,
            telegram_message_id=telegram_message_id,
        )

        session.add(signal)
        await session.commit()
        await session.refresh(signal)

        logger.info(f"Created signal: {signal.symbol} {signal.direction} {signal.timeframe}")
        return signal

    async def get_signals(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        from_date: Optional[datetime] = None,
        direction: Optional[str] = None,
        timeframe: Optional[str] = None,
        min_quality: Optional[int] = None,
    ) -> list[BabloSignal]:
        """Get signals with optional filters.

        Args:
            session: Database session
            limit: Maximum number of signals
            offset: Number of signals to skip
            from_date: Filter signals from this date
            direction: Filter by direction ('long' or 'short')
            timeframe: Filter by timeframe
            min_quality: Minimum quality threshold

        Returns:
            List of BabloSignal instances
        """
        query = select(BabloSignal).order_by(desc(BabloSignal.received_at))

        if from_date:
            query = query.where(BabloSignal.received_at >= from_date)

        if direction:
            query = query.where(BabloSignal.direction == direction)

        if timeframe:
            query = query.where(BabloSignal.timeframe == timeframe)

        if min_quality:
            query = query.where(BabloSignal.quality_total >= min_quality)

        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_signals_count(
        self,
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> int:
        """Get total count of signals."""
        query = select(func.count(BabloSignal.id))

        if from_date:
            query = query.where(BabloSignal.received_at >= from_date)
        if to_date:
            query = query.where(BabloSignal.received_at < to_date)

        result = await session.execute(query)
        return result.scalar() or 0

    async def get_signals_by_direction(
        self,
        session: AsyncSession,
        from_date: datetime,
        to_date: datetime,
    ) -> dict[str, int]:
        """Get signal counts grouped by direction."""
        query = (
            select(BabloSignal.direction, func.count(BabloSignal.id))
            .where(BabloSignal.received_at >= from_date)
            .where(BabloSignal.received_at < to_date)
            .group_by(BabloSignal.direction)
        )

        result = await session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def get_signals_by_timeframe(
        self,
        session: AsyncSession,
        from_date: datetime,
        to_date: datetime,
    ) -> dict[str, int]:
        """Get signal counts grouped by timeframe."""
        query = (
            select(BabloSignal.timeframe, func.count(BabloSignal.id))
            .where(BabloSignal.received_at >= from_date)
            .where(BabloSignal.received_at < to_date)
            .group_by(BabloSignal.timeframe)
        )

        result = await session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def get_top_symbols(
        self,
        session: AsyncSession,
        from_date: datetime,
        to_date: datetime,
        limit: int = 5,
    ) -> list[tuple[str, int]]:
        """Get most frequent symbols."""
        query = (
            select(BabloSignal.symbol, func.count(BabloSignal.id).label("count"))
            .where(BabloSignal.received_at >= from_date)
            .where(BabloSignal.received_at < to_date)
            .group_by(BabloSignal.symbol)
            .order_by(desc("count"))
            .limit(limit)
        )

        result = await session.execute(query)
        return [(row[0], row[1]) for row in result.all()]

    async def get_average_quality(
        self,
        session: AsyncSession,
        from_date: datetime,
        to_date: datetime,
    ) -> Optional[float]:
        """Get average quality score."""
        query = (
            select(func.avg(BabloSignal.quality_total))
            .where(BabloSignal.received_at >= from_date)
            .where(BabloSignal.received_at < to_date)
        )

        result = await session.execute(query)
        value = result.scalar()
        return float(value) if value else None


# Global service instance
signal_service = SignalService()
