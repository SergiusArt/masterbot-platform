"""Error publisher for microservices to report errors via Redis."""

import traceback
from datetime import datetime
from typing import Optional

from shared.constants import REDIS_CHANNEL_ERRORS, EVENT_SERVICE_ERROR
from shared.utils.logger import get_logger

logger = get_logger("error_publisher")


async def publish_error(
    redis_client,
    service_name: str,
    error: Exception,
    context: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """Publish error to Redis for master_bot to forward to admin.

    Args:
        redis_client: RedisClient instance
        service_name: Name of the service (e.g., "bablo_service", "impulse_service")
        error: The exception that occurred
        context: Additional context (e.g., function name, action)
        user_id: User ID if applicable
    """
    try:
        error_type = type(error).__name__
        error_message = str(error)[:500]
        stack_trace = "".join(traceback.format_tb(error.__traceback__))[-1000:]

        message = {
            "event": EVENT_SERVICE_ERROR,
            "service": service_name,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await redis_client.publish(REDIS_CHANNEL_ERRORS, message)
        logger.info(f"Published error to Redis: {service_name}/{error_type}")

    except Exception as e:
        logger.warning(f"Failed to publish error to Redis: {e}")
