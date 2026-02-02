"""WebSocket connection manager."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


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


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""

    type: WSMessageType
    data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(
            {
                "type": self.type.value,
                "data": self.data,
                "timestamp": self.timestamp.isoformat(),
            }
        )

    @classmethod
    def from_json(cls, data: str) -> "WebSocketMessage":
        """Deserialize from JSON string."""
        parsed = json.loads(data)
        return cls(
            type=WSMessageType(parsed.get("type", "error")),
            data=parsed.get("data", {}),
            timestamp=datetime.fromisoformat(parsed["timestamp"])
            if "timestamp" in parsed
            else datetime.now(timezone.utc),
        )


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client."""

    websocket: WebSocket
    user_id: int
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    subscriptions: Set[str] = field(default_factory=set)
    last_ping: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections
        # user_id -> ClientConnection
        self._connections: Dict[int, ClientConnection] = {}
        # For broadcast - all websockets
        self._active_websockets: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    @property
    def connection_count(self) -> int:
        """Number of active connections."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket, user_id: int) -> bool:
        """Accept a new WebSocket connection.

        Returns:
            True if connected successfully, False if limit reached
        """
        async with self._lock:
            # Check connection limit
            if len(self._connections) >= self.max_connections:
                logger.warning(
                    f"Connection limit reached ({self.max_connections}), rejecting user {user_id}"
                )
                return False

            # Disconnect existing connection for this user (if any)
            if user_id in self._connections:
                old_conn = self._connections[user_id]
                try:
                    await old_conn.websocket.close(code=1000, reason="New connection")
                    self._active_websockets.discard(old_conn.websocket)
                except Exception:
                    pass
                logger.info(f"Replaced existing connection for user {user_id}")

            # Accept new connection
            await websocket.accept()

            connection = ClientConnection(websocket=websocket, user_id=user_id)
            self._connections[user_id] = connection
            self._active_websockets.add(websocket)

            logger.info(
                f"User {user_id} connected. Total connections: {len(self._connections)}"
            )
            return True

    async def disconnect(self, user_id: int) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            if user_id in self._connections:
                conn = self._connections.pop(user_id)
                self._active_websockets.discard(conn.websocket)
                logger.info(
                    f"User {user_id} disconnected. Total connections: {len(self._connections)}"
                )

    async def disconnect_websocket(self, websocket: WebSocket) -> None:
        """Remove connection by WebSocket object."""
        async with self._lock:
            for user_id, conn in list(self._connections.items()):
                if conn.websocket == websocket:
                    self._connections.pop(user_id)
                    self._active_websockets.discard(websocket)
                    logger.info(
                        f"User {user_id} disconnected. Total: {len(self._connections)}"
                    )
                    break

    async def send_to_user(self, user_id: int, message: WebSocketMessage) -> bool:
        """Send message to specific user.

        Returns:
            True if sent successfully, False if user not connected
        """
        conn = self._connections.get(user_id)
        if not conn:
            return False

        try:
            await conn.websocket.send_text(message.to_json())
            return True
        except Exception as e:
            logger.error(f"Failed to send to user {user_id}: {e}")
            await self.disconnect(user_id)
            return False

    async def broadcast(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connected clients.

        Returns:
            Number of clients that received the message
        """
        if not self._active_websockets:
            return 0

        json_message = message.to_json()
        sent_count = 0
        failed_websockets = []

        for websocket in self._active_websockets:
            try:
                await websocket.send_text(json_message)
                sent_count += 1
            except Exception:
                failed_websockets.append(websocket)

        # Clean up failed connections
        for ws in failed_websockets:
            await self.disconnect_websocket(ws)

        return sent_count

    async def send_to_subscribed(
        self, channel: str, message: WebSocketMessage
    ) -> int:
        """Send message to users subscribed to a channel.

        Returns:
            Number of clients that received the message
        """
        sent_count = 0

        for user_id, conn in list(self._connections.items()):
            if channel in conn.subscriptions:
                success = await self.send_to_user(user_id, message)
                if success:
                    sent_count += 1

        return sent_count

    def subscribe(self, user_id: int, channel: str) -> bool:
        """Subscribe user to a channel."""
        conn = self._connections.get(user_id)
        if conn:
            conn.subscriptions.add(channel)
            return True
        return False

    def unsubscribe(self, user_id: int, channel: str) -> bool:
        """Unsubscribe user from a channel."""
        conn = self._connections.get(user_id)
        if conn:
            conn.subscriptions.discard(channel)
            return True
        return False

    def update_ping(self, user_id: int) -> None:
        """Update last ping time for user."""
        conn = self._connections.get(user_id)
        if conn:
            conn.last_ping = datetime.now(timezone.utc)

    def get_connection(self, user_id: int) -> Optional[ClientConnection]:
        """Get connection info for user."""
        return self._connections.get(user_id)

    def get_all_user_ids(self) -> Set[int]:
        """Get all connected user IDs."""
        return set(self._connections.keys())


# Global connection manager instance
connection_manager = ConnectionManager()
