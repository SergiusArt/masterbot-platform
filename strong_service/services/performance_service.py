"""Performance calculation service for Strong Signals."""

from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.strong import StrongSignal
from services.binance_client import binance_client, HIGH, LOW, CLOSE
from shared.utils.logger import get_logger

logger = get_logger("performance_service")

# 100 bars × 30 min = 3000 min = 50 hours
MATURITY_HOURS = 50
BARS_COUNT = 100


class PerformanceService:
    """Service for calculating signal performance from Binance data."""

    async def calculate_signal_performance(
        self,
        session: AsyncSession,
        signal: StrongSignal,
    ) -> dict:
        """Calculate performance for a single signal.

        Args:
            session: DB session
            signal: Signal to calculate

        Returns:
            Dict with calculation results
        """
        candle_start = binance_client.get_entry_candle_start(signal.received_at)

        try:
            klines = await binance_client.get_klines(
                symbol=signal.symbol,
                interval="30m",
                start_time=candle_start,
                limit=BARS_COUNT + 1,  # entry candle + 100 bars
            )
        except Exception as e:
            logger.error(f"Binance API error for {signal.symbol}: {e}")
            return {"error": str(e)}

        if len(klines) < 2:
            logger.warning(f"Not enough klines for {signal.symbol} (got {len(klines)})")
            return {"error": "not_enough_data"}

        # Entry price = close of the candle containing the signal
        entry_price = float(klines[0][CLOSE])

        # Analyze subsequent candles for max profit
        analysis_candles = klines[1:]  # skip entry candle

        if signal.direction == "long":
            max_profit_price = entry_price
            bars_to_max = 0
            for i, candle in enumerate(analysis_candles):
                high = float(candle[HIGH])
                if high > max_profit_price:
                    max_profit_price = high
                    bars_to_max = i + 1
            max_profit_pct = (max_profit_price - entry_price) / entry_price * 100
        else:  # short
            max_profit_price = entry_price
            bars_to_max = 0
            for i, candle in enumerate(analysis_candles):
                low = float(candle[LOW])
                if low < max_profit_price:
                    max_profit_price = low
                    bars_to_max = i + 1
            max_profit_pct = (entry_price - max_profit_price) / entry_price * 100

        now = datetime.now(timezone.utc)
        await session.execute(
            update(StrongSignal)
            .where(StrongSignal.id == signal.id)
            .values(
                entry_price=entry_price,
                max_profit_pct=round(max_profit_pct, 4),
                max_profit_price=max_profit_price,
                bars_to_max=bars_to_max,
                performance_calculated_at=now,
            )
        )
        await session.commit()

        logger.info(
            f"Calculated {signal.symbol} {signal.direction}: "
            f"entry={entry_price}, max_profit={max_profit_pct:.2f}%, "
            f"bars_to_max={bars_to_max}"
        )

        return {
            "id": signal.id,
            "symbol": signal.symbol,
            "direction": signal.direction,
            "entry_price": entry_price,
            "max_profit_pct": round(max_profit_pct, 4),
            "max_profit_price": max_profit_price,
            "bars_to_max": bars_to_max,
        }

    async def calculate_pending(
        self,
        session: AsyncSession,
        months: int = 2,
    ) -> dict:
        """Calculate performance for all uncalculated signals in period.

        Args:
            session: DB session
            months: How many months back to process

        Returns:
            Summary dict with calculated/skipped/errors counts
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
        maturity = datetime.now(timezone.utc) - timedelta(hours=MATURITY_HOURS)

        query = (
            select(StrongSignal)
            .where(
                StrongSignal.performance_calculated_at.is_(None),
                StrongSignal.received_at >= cutoff,
                StrongSignal.received_at <= maturity,
            )
            .order_by(StrongSignal.received_at.asc())
        )

        result = await session.execute(query)
        signals = list(result.scalars().all())

        calculated = 0
        errors = 0

        for signal in signals:
            try:
                res = await self.calculate_signal_performance(session, signal)
                if "error" in res:
                    errors += 1
                else:
                    calculated += 1
            except Exception as e:
                logger.error(f"Error calculating {signal.symbol}: {e}")
                errors += 1

            await binance_client.throttle()

        return {
            "total": len(signals),
            "calculated": calculated,
            "errors": errors,
        }

    async def get_performance_stats(
        self,
        session: AsyncSession,
        months: int = 2,
    ) -> dict:
        """Get aggregate performance statistics.

        Args:
            session: DB session
            months: How many months back

        Returns:
            Stats dictionary
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)

        # Total signals in period
        total_q = select(func.count(StrongSignal.id)).where(
            StrongSignal.received_at >= cutoff
        )
        total = (await session.execute(total_q)).scalar() or 0

        # Calculated signals
        calc_q = select(func.count(StrongSignal.id)).where(
            StrongSignal.received_at >= cutoff,
            StrongSignal.performance_calculated_at.is_not(None),
        )
        calculated = (await session.execute(calc_q)).scalar() or 0

        # Aggregate stats (only calculated signals)
        stats_q = select(
            func.avg(StrongSignal.max_profit_pct),
            func.min(StrongSignal.max_profit_pct),
            func.max(StrongSignal.max_profit_pct),
            func.avg(StrongSignal.bars_to_max),
        ).where(
            StrongSignal.received_at >= cutoff,
            StrongSignal.performance_calculated_at.is_not(None),
        )
        row = (await session.execute(stats_q)).one_or_none()

        avg_profit = round(float(row[0]), 2) if row and row[0] else 0
        min_profit = round(float(row[1]), 2) if row and row[1] else 0
        max_profit = round(float(row[2]), 2) if row and row[2] else 0
        avg_bars = round(float(row[3]), 1) if row and row[3] else 0

        # By direction
        by_direction = {}
        for direction in ("long", "short"):
            dir_q = select(
                func.count(StrongSignal.id),
                func.avg(StrongSignal.max_profit_pct),
                func.min(StrongSignal.max_profit_pct),
                func.max(StrongSignal.max_profit_pct),
            ).where(
                StrongSignal.received_at >= cutoff,
                StrongSignal.performance_calculated_at.is_not(None),
                StrongSignal.direction == direction,
            )
            dr = (await session.execute(dir_q)).one_or_none()
            by_direction[direction] = {
                "count": int(dr[0]) if dr and dr[0] else 0,
                "avg_profit_pct": round(float(dr[1]), 2) if dr and dr[1] else 0,
                "min_profit_pct": round(float(dr[2]), 2) if dr and dr[2] else 0,
                "max_profit_pct": round(float(dr[3]), 2) if dr and dr[3] else 0,
            }

        return {
            "total": total,
            "calculated": calculated,
            "pending": total - calculated,
            "avg_profit_pct": avg_profit,
            "min_profit_pct": min_profit,
            "max_profit_pct": max_profit,
            "avg_bars_to_max": avg_bars,
            "by_direction": by_direction,
        }

    async def get_performance_signals(
        self,
        session: AsyncSession,
        months: int = 2,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Get signals with performance data.

        Args:
            session: DB session
            months: How many months back
            limit: Max results
            offset: Offset

        Returns:
            List of signal dicts with performance
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)

        query = (
            select(StrongSignal)
            .where(
                StrongSignal.received_at >= cutoff,
                StrongSignal.performance_calculated_at.is_not(None),
            )
            .order_by(StrongSignal.received_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(query)
        signals = list(result.scalars().all())

        return [
            {
                "id": s.id,
                "symbol": s.symbol,
                "direction": s.direction,
                "received_at": s.received_at.isoformat(),
                "entry_price": s.entry_price,
                "max_profit_pct": s.max_profit_pct,
                "max_profit_price": s.max_profit_price,
                "bars_to_max": s.bars_to_max,
            }
            for s in signals
        ]


# Global instance
performance_service = PerformanceService()
