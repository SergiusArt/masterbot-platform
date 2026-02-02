"""WebSocket message schemas for Mini App communication."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WSMessageType(str, Enum):
    """WebSocket message types."""

    # Server -> Client
    IMPULSE_NEW = "impulse:new"
    IMPULSE_STATS = "impulse:stats"
    BABLO_NEW = "bablo:new"
    BABLO_STATS = "bablo:stats"
    ACTIVITY_ZONE = "activity:zone"
    CONNECTED = "connected"
    ERROR = "error"
    PONG = "pong"

    # Client -> Server
    PING = "ping"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class WSMessage(BaseModel):
    """WebSocket message structure."""

    type: WSMessageType
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        use_enum_values = True


class ImpulseWSPayload(BaseModel):
    """Payload for impulse WebSocket messages."""

    id: int
    symbol: str
    percent: float
    max_percent: Optional[float] = None
    type: str  # 'growth' or 'fall'
    received_at: datetime


class BabloWSPayload(BaseModel):
    """Payload for Bablo signal WebSocket messages."""

    id: int
    symbol: str
    direction: str  # 'long' or 'short'
    strength: int
    timeframe: str
    quality_total: int
    received_at: datetime


class StatsUpdatePayload(BaseModel):
    """Payload for stats update messages."""

    service: str  # 'impulse' or 'bablo'
    today_count: int
    activity_zone: str  # 'low', 'medium', 'high'


class ActivityZonePayload(BaseModel):
    """Payload for activity zone change notifications."""

    service: str
    zone: str  # 'low', 'medium', 'high'
    previous_zone: str
