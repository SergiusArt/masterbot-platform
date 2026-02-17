"""Strong Signal database models."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from shared.database.connection import Base


class StrongSignal(Base):
    """Strong trading signals table."""

    __tablename__ = "strong_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # 'long' | 'short'
    raw_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_strong_signals_received_at", "received_at"),
        Index("idx_strong_signals_symbol", "symbol"),
        Index("idx_strong_signals_direction", "direction"),
    )

    def __repr__(self) -> str:
        return f"<StrongSignal(id={self.id}, symbol={self.symbol}, direction={self.direction})>"


class StrongUserSettings(Base):
    """User settings for Strong Signal notifications."""

    __tablename__ = "strong_user_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    long_signals: Mapped[bool] = mapped_column(Boolean, default=True)
    short_signals: Mapped[bool] = mapped_column(Boolean, default=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<StrongUserSettings(user_id={self.user_id})>"
