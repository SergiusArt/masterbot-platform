"""Signals API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from services.signal_service import signal_service

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
async def list_signals(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    from_date: Optional[str] = None,
    direction: Optional[str] = None,
    timeframe: Optional[str] = None,
    min_quality: Optional[int] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """List signals with optional filters."""
    from_dt = None
    if from_date:
        from_dt = datetime.fromisoformat(from_date)

    signals = await signal_service.get_signals(
        session,
        limit=limit,
        offset=offset,
        from_date=from_dt,
        direction=direction,
        timeframe=timeframe,
        min_quality=min_quality,
    )

    total = await signal_service.get_signals_count(session, from_dt)

    return {
        "signals": [
            {
                "id": s.id,
                "symbol": s.symbol,
                "direction": s.direction,
                "strength": s.strength,
                "timeframe": s.timeframe,
                "time_horizon": s.time_horizon,
                "quality_total": s.quality_total,
                "quality_profit": s.quality_profit,
                "quality_drawdown": s.quality_drawdown,
                "quality_accuracy": s.quality_accuracy,
                "probabilities": s.probabilities,
                "max_drawdown": float(s.max_drawdown) if s.max_drawdown else None,
                "received_at": s.received_at.isoformat(),
            }
            for s in signals
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
