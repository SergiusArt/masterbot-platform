"""Signals API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services.signal_service import signal_service
from shared.schemas.impulse import SignalListResponse, ImpulseCreate

router = APIRouter()


@router.get("", response_model=SignalListResponse)
async def get_signals(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    from_date: Optional[str] = Query(default=None),
):
    """Get list of signals.

    Args:
        limit: Maximum number of signals to return
        offset: Number of signals to skip
        from_date: Filter signals from this date (ISO format)

    Returns:
        List of signals with pagination info
    """
    try:
        result = await signal_service.get_signals(
            limit=limit,
            offset=offset,
            from_date=from_date,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_signal(impulse: ImpulseCreate):
    """Create new signal (internal use).

    Args:
        impulse: Impulse data

    Returns:
        Created impulse ID
    """
    try:
        impulse_id = await signal_service.create_signal(impulse)
        return {"id": impulse_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
