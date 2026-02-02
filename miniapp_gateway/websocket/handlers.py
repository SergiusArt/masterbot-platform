"""WebSocket message handlers."""

import json
import logging
from typing import Optional

from .manager import (
    ConnectionManager,
    WebSocketMessage,
    WSMessageType,
    connection_manager,
)

logger = logging.getLogger(__name__)


async def handle_client_message(
    user_id: int,
    raw_message: str,
    manager: ConnectionManager = connection_manager,
) -> Optional[WebSocketMessage]:
    """Handle incoming message from client.

    Args:
        user_id: Telegram user ID
        raw_message: Raw message string from client
        manager: Connection manager instance

    Returns:
        Response message to send back (if any)
    """
    try:
        # Try to parse as JSON
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type", "")
        except json.JSONDecodeError:
            # Handle simple string messages
            msg_type = raw_message.strip().lower()
            data = {}

        # Handle ping
        if msg_type == "ping" or msg_type == WSMessageType.PING.value:
            manager.update_ping(user_id)
            return WebSocketMessage(type=WSMessageType.PONG, data={"user_id": user_id})

        # Handle subscribe
        if msg_type == "subscribe" or msg_type == WSMessageType.SUBSCRIBE.value:
            channel = data.get("channel")
            if channel:
                manager.subscribe(user_id, channel)
                logger.info(f"User {user_id} subscribed to {channel}")
                return WebSocketMessage(
                    type=WSMessageType.CONNECTED,
                    data={"subscribed": channel},
                )

        # Handle unsubscribe
        if msg_type == "unsubscribe" or msg_type == WSMessageType.UNSUBSCRIBE.value:
            channel = data.get("channel")
            if channel:
                manager.unsubscribe(user_id, channel)
                logger.info(f"User {user_id} unsubscribed from {channel}")
                return WebSocketMessage(
                    type=WSMessageType.CONNECTED,
                    data={"unsubscribed": channel},
                )

        # Unknown message type
        logger.debug(f"Unknown message from user {user_id}: {msg_type}")
        return None

    except Exception as e:
        logger.error(f"Error handling message from user {user_id}: {e}")
        return WebSocketMessage(
            type=WSMessageType.ERROR,
            data={"error": str(e)},
        )
