"""Bablo-related database models."""

from datetime import datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from shared.database.connection import Base


class BabloSignal(Base):
    """Bablo trading signals table."""

    __tablename__ = "bablo_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # 'long' | 'short'
    strength: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 (number of squares)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)  # '1m', '15m', '1h', '4h'
    time_horizon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # '60 минут', '12 часов'

    # Quality metrics
    quality_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_profit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_drawdown: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_accuracy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Probabilities as JSON: {"0.9": {"long": 82, "short": 73}, ...}
    probabilities: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    max_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    raw_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_bablo_signals_received_at", "received_at"),
        Index("idx_bablo_signals_symbol", "symbol"),
        Index("idx_bablo_signals_direction", "direction"),
        Index("idx_bablo_signals_timeframe", "timeframe"),
        Index("idx_bablo_signals_quality", "quality_total"),
    )

    def __repr__(self) -> str:
        return f"<BabloSignal(id={self.id}, symbol={self.symbol}, direction={self.direction})>"


class BabloUserSettings(Base):
    """User settings for Bablo notifications."""

    __tablename__ = "bablo_user_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Minimum quality threshold
    min_quality: Mapped[int] = mapped_column(Integer, default=7)

    # Minimum signal strength (squares)
    min_strength: Mapped[int] = mapped_column(Integer, default=3)

    # Timeframe filters
    timeframe_1m: Mapped[bool] = mapped_column(Boolean, default=False)
    timeframe_15m: Mapped[bool] = mapped_column(Boolean, default=True)
    timeframe_1h: Mapped[bool] = mapped_column(Boolean, default=True)
    timeframe_4h: Mapped[bool] = mapped_column(Boolean, default=True)

    # Direction filters
    long_signals: Mapped[bool] = mapped_column(Boolean, default=True)
    short_signals: Mapped[bool] = mapped_column(Boolean, default=True)

    # Report preferences
    morning_report: Mapped[bool] = mapped_column(Boolean, default=True)
    morning_report_time: Mapped[time] = mapped_column(Time, default=time(8, 0))
    evening_report: Mapped[bool] = mapped_column(Boolean, default=True)
    evening_report_time: Mapped[time] = mapped_column(Time, default=time(20, 0))
    weekly_report: Mapped[bool] = mapped_column(Boolean, default=True)
    monthly_report: Mapped[bool] = mapped_column(Boolean, default=True)

    # Activity alerts
    activity_window_minutes: Mapped[int] = mapped_column(Integer, default=15)
    activity_threshold: Mapped[int] = mapped_column(Integer, default=10)
    last_activity_alert_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<BabloUserSettings(user_id={self.user_id})>"
