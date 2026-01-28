"""Impulse Service Pydantic schemas."""

from datetime import datetime, time
from typing import Optional, Literal
from decimal import Decimal

from pydantic import Field

from shared.schemas.base import BaseSchema


class ImpulseSchema(BaseSchema):
    """Impulse data schema."""

    id: int
    symbol: str
    percent: Decimal
    max_percent: Optional[Decimal] = None
    type: Literal["growth", "fall"]
    growth_ratio: Optional[Decimal] = None
    fall_ratio: Optional[Decimal] = None
    raw_message: Optional[str] = None
    received_at: datetime


class ImpulseCreate(BaseSchema):
    """Schema for creating an impulse."""

    symbol: str
    percent: Decimal
    max_percent: Optional[Decimal] = None
    type: Literal["growth", "fall"]
    growth_ratio: Optional[Decimal] = None
    fall_ratio: Optional[Decimal] = None
    raw_message: Optional[str] = None


class TopImpulse(BaseSchema):
    """Top impulse item schema."""

    symbol: str
    percent: Decimal
    count: int


class ComparisonData(BaseSchema):
    """Analytics comparison data."""

    vs_yesterday: str
    vs_week_median: str
    vs_month_median: str


class AnalyticsResponse(BaseSchema):
    """Analytics response schema."""

    period: str
    start_date: datetime
    end_date: datetime
    total_impulses: int
    growth_count: int
    fall_count: int
    top_growth: list[TopImpulse]
    top_fall: list[TopImpulse]
    comparison: Optional[ComparisonData] = None


class ReportRequest(BaseSchema):
    """Report generation request schema."""

    type: Literal["morning", "evening", "weekly", "monthly"]
    user_id: int


class ReportData(BaseSchema):
    """Report data schema."""

    title: str
    text: str
    generated_at: datetime


class ReportResponse(BaseSchema):
    """Report generation response schema."""

    status: str
    report: ReportData


class NotificationSettingsSchema(BaseSchema):
    """User notification settings schema."""

    user_id: int
    growth_threshold: int = Field(default=20, ge=1, le=100)
    fall_threshold: int = Field(default=-15, ge=-100, le=-1)
    morning_report: bool = True
    morning_report_time: time = Field(default=time(8, 0))
    evening_report: bool = True
    evening_report_time: time = Field(default=time(20, 0))
    weekly_report: bool = True
    monthly_report: bool = True
    activity_window_minutes: int = Field(default=15, ge=5, le=60)
    activity_threshold: int = Field(default=10, ge=1, le=100)


class NotificationSettingsUpdate(BaseSchema):
    """Update notification settings schema."""

    growth_threshold: Optional[int] = Field(default=None, ge=1, le=100)
    fall_threshold: Optional[int] = Field(default=None, ge=-100, le=-1)
    morning_report: Optional[bool] = None
    morning_report_time: Optional[time] = None
    evening_report: Optional[bool] = None
    evening_report_time: Optional[time] = None
    weekly_report: Optional[bool] = None
    monthly_report: Optional[bool] = None
    activity_window_minutes: Optional[int] = Field(default=None, ge=5, le=60)
    activity_threshold: Optional[int] = Field(default=None, ge=1, le=100)


class SignalListResponse(BaseSchema):
    """Signal list response schema."""

    signals: list[ImpulseSchema]
    total: int
    limit: int
    offset: int
