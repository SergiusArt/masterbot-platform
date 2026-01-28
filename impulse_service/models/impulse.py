"""Impulse-related database models."""

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
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from shared.database.connection import Base


class Impulse(Base):
    """Impulse signals table."""

    __tablename__ = "impulses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    percent: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'growth' | 'fall'
    growth_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    fall_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    raw_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_impulses_received_at", "received_at"),
        Index("idx_impulses_symbol", "symbol"),
        Index("idx_impulses_type", "type"),
    )

    def __repr__(self) -> str:
        return f"<Impulse(id={self.id}, symbol={self.symbol}, percent={self.percent})>"


class UserNotificationSettings(Base):
    """User notification settings table."""

    __tablename__ = "user_notification_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    growth_threshold: Mapped[int] = mapped_column(Integer, default=20)
    fall_threshold: Mapped[int] = mapped_column(Integer, default=-15)
    morning_report: Mapped[bool] = mapped_column(Boolean, default=True)
    morning_report_time: Mapped[time] = mapped_column(Time, default=time(8, 0))
    evening_report: Mapped[bool] = mapped_column(Boolean, default=True)
    evening_report_time: Mapped[time] = mapped_column(Time, default=time(20, 0))
    weekly_report: Mapped[bool] = mapped_column(Boolean, default=True)
    monthly_report: Mapped[bool] = mapped_column(Boolean, default=True)
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
        return f"<UserNotificationSettings(user_id={self.user_id})>"
