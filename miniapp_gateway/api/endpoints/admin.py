"""Admin API endpoints for Mini App."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.telegram import TelegramUser
from config import settings
from database import get_db, async_session_maker
from shared.constants import REDIS_CHANNEL_BROADCAST

router = APIRouter(prefix="/admin", tags=["admin"])


# ============== Pydantic Models ==============

class AddUserRequest(BaseModel):
    """Request to add a new user."""
    user_id: int
    days: int = 30  # 0 = unlimited
    username: Optional[str] = None
    first_name: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Request to update user."""
    is_active: Optional[bool] = None
    extend_days: Optional[int] = None
    is_admin: Optional[bool] = None


class BroadcastRequest(BaseModel):
    """Request to send broadcast message."""
    message: str
    user_ids: Optional[list[int]] = None  # None = all active users


class AdminUser(BaseModel):
    """Admin user response model."""
    id: int
    username: Optional[str]
    first_name: Optional[str]
    is_active: bool
    is_admin: bool
    access_expires_at: Optional[datetime]
    created_at: datetime
    last_activity: Optional[datetime]


class UserStats(BaseModel):
    """User statistics."""
    total_users: int
    active_users: int
    expiring_soon: int  # in 7 days
    blocked_users: int
    admins: int


class DailyActivity(BaseModel):
    """Daily activity data point."""
    date: str
    count: int


class UserActivityItem(BaseModel):
    """User activity log item."""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    action: str
    created_at: datetime


class ServiceStatus(BaseModel):
    """Service health status."""
    name: str
    display_name: str
    status: str  # 'healthy' or 'unhealthy'
    latency_ms: Optional[int]
    error: Optional[str] = None


class BroadcastHistoryItem(BaseModel):
    """Broadcast history item."""
    id: str
    message: str
    sent_to: int
    created_at: datetime
    created_by: Optional[int]


# ============== Dependencies ==============

async def check_is_admin(user_id: int, db: AsyncSession) -> bool:
    """Check if user is admin."""
    # Check ADMIN_ID first
    if user_id == settings.ADMIN_ID:
        return True

    # Check users table
    result = await db.execute(
        text("SELECT is_admin FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    row = result.fetchone()
    return row is not None and row[0] is True


async def get_admin_user(
    user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TelegramUser:
    """Dependency to ensure user is admin."""
    is_admin = await check_is_admin(user.id, db)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ============== User Management ==============

@router.get("/users", response_model=list[AdminUser])
async def list_users(
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Get list of all users with pagination and search."""
    # Build query
    query = """
        SELECT
            u.id,
            u.username,
            u.first_name,
            u.is_active,
            u.is_admin,
            u.access_expires_at,
            u.created_at,
            (
                SELECT MAX(al.created_at)
                FROM action_logs al
                WHERE al.user_id = u.id
            ) as last_activity
        FROM users u
        WHERE 1=1
    """
    params = {"limit": limit, "offset": offset}

    if search:
        query += """ AND (
            u.username ILIKE :search
            OR u.first_name ILIKE :search
            OR CAST(u.id AS TEXT) LIKE :search
        )"""
        params["search"] = f"%{search}%"

    query += " ORDER BY u.created_at DESC LIMIT :limit OFFSET :offset"

    result = await db.execute(text(query), params)
    rows = result.fetchall()

    return [
        AdminUser(
            id=row[0],
            username=row[1],
            first_name=row[2],
            is_active=row[3],
            is_admin=row[4],
            access_expires_at=row[5],
            created_at=row[6],
            last_activity=row[7],
        )
        for row in rows
    ]


@router.post("/users")
async def add_user(
    request: AddUserRequest,
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new user or reactivate existing."""
    # Check if user already exists
    result = await db.execute(
        text("SELECT id, is_active FROM users WHERE id = :user_id"),
        {"user_id": request.user_id}
    )
    existing = result.fetchone()

    # Calculate expiration date
    expires_at = None
    if request.days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.days)

    if existing:
        # Reactivate or extend existing user
        await db.execute(
            text("""
                UPDATE users
                SET is_active = true,
                    access_expires_at = :expires_at,
                    username = COALESCE(:username, username),
                    first_name = COALESCE(:first_name, first_name),
                    updated_at = NOW()
                WHERE id = :user_id
            """),
            {
                "user_id": request.user_id,
                "expires_at": expires_at,
                "username": request.username,
                "first_name": request.first_name,
            }
        )
        action = "reactivated"
    else:
        # Create new user
        await db.execute(
            text("""
                INSERT INTO users (id, username, first_name, is_active, access_expires_at, created_at, updated_at)
                VALUES (:user_id, :username, :first_name, true, :expires_at, NOW(), NOW())
            """),
            {
                "user_id": request.user_id,
                "username": request.username,
                "first_name": request.first_name,
                "expires_at": expires_at,
            }
        )
        action = "created"

    # Log action
    await db.execute(
        text("""
            INSERT INTO action_logs (user_id, service_name, action, details, created_at)
            VALUES (:admin_id, 'miniapp_admin', :action, :details::jsonb, NOW())
        """),
        {
            "admin_id": user.id,
            "action": f"user_{action}",
            "details": json.dumps({
                "target_user_id": request.user_id,
                "days": request.days,
            }),
        }
    )

    await db.commit()

    return {
        "status": "ok",
        "action": action,
        "user_id": request.user_id,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user (extend access, activate/deactivate, set admin)."""
    # Check if user exists
    result = await db.execute(
        text("SELECT id, access_expires_at FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    existing = result.fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    updates = []
    params = {"user_id": user_id}

    if request.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = request.is_active

    if request.is_admin is not None:
        updates.append("is_admin = :is_admin")
        params["is_admin"] = request.is_admin

    if request.extend_days is not None:
        current_expires = existing[1]
        base_date = current_expires if current_expires and current_expires > datetime.now(timezone.utc) else datetime.now(timezone.utc)

        if request.extend_days == 0:
            # Unlimited access
            new_expires = None
        else:
            new_expires = base_date + timedelta(days=request.extend_days)

        updates.append("access_expires_at = :expires_at")
        params["expires_at"] = new_expires

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    updates.append("updated_at = NOW()")
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = :user_id"

    await db.execute(text(query), params)

    # Log action
    await db.execute(
        text("""
            INSERT INTO action_logs (user_id, service_name, action, details, created_at)
            VALUES (:admin_id, 'miniapp_admin', 'user_updated', :details::jsonb, NOW())
        """),
        {
            "admin_id": user.id,
            "details": json.dumps({
                "target_user_id": user_id,
                "updates": {k: v for k, v in request.model_dump().items() if v is not None},
            }),
        }
    )

    await db.commit()

    return {"status": "ok", "user_id": user_id}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate user (soft delete)."""
    # Don't allow deleting yourself
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    # Check if user exists
    result = await db.execute(
        text("SELECT id FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(
        text("UPDATE users SET is_active = false, updated_at = NOW() WHERE id = :user_id"),
        {"user_id": user_id}
    )

    # Log action
    await db.execute(
        text("""
            INSERT INTO action_logs (user_id, service_name, action, details, created_at)
            VALUES (:admin_id, 'miniapp_admin', 'user_deactivated', :details::jsonb, NOW())
        """),
        {
            "admin_id": user.id,
            "details": json.dumps({"target_user_id": user_id}),
        }
    )

    await db.commit()

    return {"status": "ok", "user_id": user_id}


# ============== Statistics ==============

@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user statistics."""
    result = await db.execute(text("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE is_active = true) as active,
            COUNT(*) FILTER (WHERE is_active = true AND access_expires_at IS NOT NULL
                AND access_expires_at <= NOW() + INTERVAL '7 days'
                AND access_expires_at > NOW()) as expiring_soon,
            COUNT(*) FILTER (WHERE is_active = false) as blocked,
            COUNT(*) FILTER (WHERE is_admin = true) as admins
        FROM users
    """))
    row = result.fetchone()

    return UserStats(
        total_users=row[0] or 0,
        active_users=row[1] or 0,
        expiring_soon=row[2] or 0,
        blocked_users=row[3] or 0,
        admins=row[4] or 0,
    )


# ============== Activity Analytics ==============

@router.get("/activity")
async def get_user_activity(
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=30, le=90),
):
    """Get user activity analytics."""
    # Daily active users (users with action_logs per day)
    daily_result = await db.execute(text("""
        SELECT
            DATE(created_at) as date,
            COUNT(DISTINCT user_id) as count
        FROM action_logs
        WHERE created_at >= NOW() - INTERVAL ':days days'
            AND user_id IS NOT NULL
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """.replace(":days", str(days))))

    daily_active_users = [
        DailyActivity(date=row[0].isoformat(), count=row[1])
        for row in daily_result.fetchall()
    ]

    # Recent logins (last 50)
    recent_result = await db.execute(text("""
        SELECT
            al.user_id,
            u.username,
            u.first_name,
            al.action,
            al.created_at
        FROM action_logs al
        LEFT JOIN users u ON u.id = al.user_id
        WHERE al.action = 'miniapp_login'
        ORDER BY al.created_at DESC
        LIMIT 50
    """))

    recent_logins = [
        UserActivityItem(
            user_id=row[0],
            username=row[1],
            first_name=row[2],
            action=row[3],
            created_at=row[4],
        )
        for row in recent_result.fetchall()
    ]

    # User activity frequency (how often each user visits)
    frequency_result = await db.execute(text("""
        SELECT
            al.user_id,
            u.username,
            u.first_name,
            COUNT(*) as visit_count,
            MAX(al.created_at) as last_visit
        FROM action_logs al
        LEFT JOIN users u ON u.id = al.user_id
        WHERE al.action = 'miniapp_login'
            AND al.created_at >= NOW() - INTERVAL ':days days'
            AND al.user_id IS NOT NULL
        GROUP BY al.user_id, u.username, u.first_name
        ORDER BY visit_count DESC
        LIMIT 50
    """.replace(":days", str(days))))

    user_frequency = [
        {
            "user_id": row[0],
            "username": row[1],
            "first_name": row[2],
            "visit_count": row[3],
            "last_visit": row[4].isoformat() if row[4] else None,
        }
        for row in frequency_result.fetchall()
    ]

    return {
        "daily_active_users": daily_active_users,
        "recent_logins": recent_logins,
        "user_frequency": user_frequency,
    }


# ============== Services Health ==============

@router.get("/services", response_model=list[ServiceStatus])
async def get_services_health(
    user: TelegramUser = Depends(get_admin_user),
):
    """Get health status of all services."""
    services = [
        ("impulse_service", "Impulse Service", settings.IMPULSE_SERVICE_URL),
        ("bablo_service", "Bablo Service", settings.BABLO_SERVICE_URL),
    ]

    results = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, display_name, url in services:
            try:
                start = datetime.now()
                resp = await client.get(f"{url}/health")
                latency = int((datetime.now() - start).total_seconds() * 1000)

                if resp.status_code == 200:
                    results.append(ServiceStatus(
                        name=name,
                        display_name=display_name,
                        status="healthy",
                        latency_ms=latency,
                    ))
                else:
                    results.append(ServiceStatus(
                        name=name,
                        display_name=display_name,
                        status="unhealthy",
                        latency_ms=latency,
                        error=f"Status code: {resp.status_code}",
                    ))
            except Exception as e:
                results.append(ServiceStatus(
                    name=name,
                    display_name=display_name,
                    status="unhealthy",
                    latency_ms=None,
                    error=str(e),
                ))

    return results


# ============== Broadcast ==============

@router.post("/broadcast")
async def send_broadcast(
    request: BroadcastRequest,
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Send broadcast message to users via Redis pub/sub."""
    from shared.utils.redis_client import get_redis_client

    # Get target users
    if request.user_ids:
        user_ids = request.user_ids
    else:
        # Get all active users
        result = await db.execute(text("""
            SELECT id FROM users
            WHERE is_active = true
            AND (access_expires_at IS NULL OR access_expires_at > NOW())
        """))
        user_ids = [row[0] for row in result.fetchall()]

    if not user_ids:
        raise HTTPException(status_code=400, detail="No users to send to")

    # Generate broadcast ID
    broadcast_id = str(uuid4())[:8]

    # Publish to Redis for master_bot to pick up
    redis = await get_redis_client()
    await redis.publish(REDIS_CHANNEL_BROADCAST, {
        "broadcast_id": broadcast_id,
        "message": request.message,
        "user_ids": user_ids,
        "sent_by": user.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Log the broadcast
    await db.execute(
        text("""
            INSERT INTO action_logs (user_id, service_name, action, details, created_at)
            VALUES (:admin_id, 'miniapp_admin', 'broadcast', :details::jsonb, NOW())
        """),
        {
            "admin_id": user.id,
            "details": json.dumps({
                "broadcast_id": broadcast_id,
                "message": request.message[:100],  # Truncate for log
                "sent_to_count": len(user_ids),
            }),
        }
    )

    await db.commit()

    return {
        "status": "ok",
        "broadcast_id": broadcast_id,
        "sent_to": len(user_ids),
    }


@router.get("/broadcasts")
async def get_broadcast_history(
    user: TelegramUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
):
    """Get broadcast history."""
    result = await db.execute(text("""
        SELECT
            details->>'broadcast_id' as id,
            details->>'message' as message,
            (details->>'sent_to_count')::int as sent_to,
            created_at,
            user_id as created_by
        FROM action_logs
        WHERE action = 'broadcast'
        ORDER BY created_at DESC
        LIMIT :limit
    """), {"limit": limit})

    return [
        BroadcastHistoryItem(
            id=row[0] or "unknown",
            message=row[1] or "",
            sent_to=row[2] or 0,
            created_at=row[3],
            created_by=row[4],
        )
        for row in result.fetchall()
    ]
