"""Base Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HealthResponse(BaseSchema):
    """Health check response schema."""

    status: str
    database: str
    redis: str
    details: Optional[dict] = None
