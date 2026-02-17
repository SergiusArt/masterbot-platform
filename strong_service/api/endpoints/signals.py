"""Strong Signal endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from shared.database.connection import async_session_maker
from services.signal_service import signal_service

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
async def get_signals(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    direction: Optional[str] = Query(None, regex="^(long|short)$"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
):
    """Get list of signals with optional date range filtering."""
    async with async_session_maker() as session:
        signals = await signal_service.get_signals(
            session,
            limit=limit,
            offset=offset,
            direction=direction,
            from_date=from_date,
            to_date=to_date,
        )

        return {
            "signals": [
                {
                    "id": s.id,
                    "symbol": s.symbol,
                    "direction": s.direction,
                    "received_at": s.received_at.isoformat(),
                }
                for s in signals
            ],
            "count": len(signals),
        }
