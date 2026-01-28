"""User Pydantic schemas."""

from datetime import datetime
from typing import Optional

from shared.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base user schema."""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    id: int  # Telegram ID
    is_admin: bool = False
    is_active: bool = True
    access_expires_at: Optional[datetime] = None


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    access_expires_at: Optional[datetime] = None


class UserSchema(UserBase, TimestampSchema):
    """Full user schema."""

    id: int
    is_admin: bool
    is_active: bool
    access_expires_at: Optional[datetime] = None


class UserServiceSubscriptionSchema(BaseSchema):
    """User service subscription schema."""

    id: int
    user_id: int
    service_name: str
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
