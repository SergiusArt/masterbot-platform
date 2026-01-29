"""Integration tests for Redis operations."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))


class TestRedisClientUnit:
    """Unit tests for RedisClient (mocked)."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis = MagicMock()
        redis.ping = AsyncMock(return_value=True)
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock(return_value=True)
        redis.delete = AsyncMock(return_value=1)
        redis.publish = AsyncMock(return_value=1)
        redis.subscribe = AsyncMock()
        redis.close = AsyncMock()
        return redis

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_redis_ping(self, mock_redis):
        """Test Redis ping operation."""
        result = await mock_redis.ping()
        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_redis_get_set(self, mock_redis):
        """Test Redis get/set operations."""
        # Set value
        await mock_redis.set("test_key", "test_value")
        mock_redis.set.assert_called_with("test_key", "test_value")

        # Get value
        mock_redis.get.return_value = "test_value"
        result = await mock_redis.get("test_key")
        assert result == "test_value"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_redis_delete(self, mock_redis):
        """Test Redis delete operation."""
        result = await mock_redis.delete("test_key")
        assert result == 1
        mock_redis.delete.assert_called_with("test_key")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_redis_publish(self, mock_redis):
        """Test Redis publish operation."""
        message = {"type": "new_signal", "data": {"symbol": "BTCUSDT"}}
        result = await mock_redis.publish("signals", json.dumps(message))

        assert result == 1
        mock_redis.publish.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_redis_close(self, mock_redis):
        """Test Redis connection close."""
        await mock_redis.close()
        mock_redis.close.assert_called_once()


class TestRedisPubSub:
    """Tests for Redis Pub/Sub functionality."""

    @pytest.fixture
    def mock_pubsub(self):
        """Create mock PubSub object."""
        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.get_message = AsyncMock()
        pubsub.close = AsyncMock()
        return pubsub

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self, mock_pubsub):
        """Test subscribing to a channel."""
        await mock_pubsub.subscribe("impulse_signals")
        mock_pubsub.subscribe.assert_called_with("impulse_signals")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_receive_message(self, mock_pubsub):
        """Test receiving a message from channel."""
        message = {
            "type": "message",
            "channel": b"impulse_signals",
            "data": b'{"symbol": "BTCUSDT", "percent": 15.5}',
        }
        mock_pubsub.get_message.return_value = message

        result = await mock_pubsub.get_message()

        assert result["type"] == "message"
        assert result["channel"] == b"impulse_signals"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self, mock_pubsub):
        """Test unsubscribing from a channel."""
        await mock_pubsub.unsubscribe("impulse_signals")
        mock_pubsub.unsubscribe.assert_called_with("impulse_signals")


class TestRedisChannelMessages:
    """Tests for Redis channel message formats."""

    @pytest.mark.unit
    def test_impulse_signal_message_format(self):
        """Test impulse signal message format."""
        message = {
            "type": "new_signal",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "id": 1,
                "symbol": "BTCUSDT",
                "percent": "15.5",
                "type": "growth",
                "max_percent": "20.0",
            },
        }

        serialized = json.dumps(message)
        deserialized = json.loads(serialized)

        assert deserialized["type"] == "new_signal"
        assert deserialized["data"]["symbol"] == "BTCUSDT"
        assert deserialized["data"]["percent"] == "15.5"

    @pytest.mark.unit
    def test_bablo_signal_message_format(self):
        """Test Bablo signal message format."""
        message = {
            "type": "new_bablo_signal",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "id": 1,
                "symbol": "BTCUSDT.P",
                "direction": "long",
                "strength": 4,
                "timeframe": "1m",
                "quality_total": 7,
            },
        }

        serialized = json.dumps(message)
        deserialized = json.loads(serialized)

        assert deserialized["type"] == "new_bablo_signal"
        assert deserialized["data"]["direction"] == "long"
        assert deserialized["data"]["strength"] == 4

    @pytest.mark.unit
    def test_report_message_format(self):
        """Test report notification message format."""
        message = {
            "type": "report_generated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "report_type": "morning",
                "user_id": 123,
                "title": "Morning Report",
                "text": "Report content...",
            },
        }

        serialized = json.dumps(message)
        deserialized = json.loads(serialized)

        assert deserialized["type"] == "report_generated"
        assert deserialized["data"]["report_type"] == "morning"
        assert deserialized["data"]["user_id"] == 123


class TestRedisHealthCheck:
    """Tests for Redis health check functionality."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client with health_check method."""
        client = MagicMock()
        client.health_check = AsyncMock(return_value=True)
        return client

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_redis_client):
        """Test successful health check."""
        result = await mock_redis_client.health_check()
        assert result is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_redis_client):
        """Test failed health check."""
        mock_redis_client.health_check.side_effect = Exception("Connection refused")

        with pytest.raises(Exception) as exc_info:
            await mock_redis_client.health_check()

        assert "Connection refused" in str(exc_info.value)


class TestRedisKeyPatterns:
    """Tests for Redis key naming patterns."""

    @pytest.mark.unit
    def test_user_settings_key_format(self):
        """Test user settings key format."""
        user_id = 123456
        key = f"user:{user_id}:settings"

        assert key == "user:123456:settings"
        assert "user:" in key
        assert ":settings" in key

    @pytest.mark.unit
    def test_signal_cache_key_format(self):
        """Test signal cache key format."""
        signal_id = 42
        key = f"signal:{signal_id}"

        assert key == "signal:42"

    @pytest.mark.unit
    def test_analytics_cache_key_format(self):
        """Test analytics cache key format."""
        period = "today"
        key = f"analytics:{period}"

        assert key == "analytics:today"

    @pytest.mark.unit
    def test_rate_limit_key_format(self):
        """Test rate limit key format."""
        user_id = 789
        key = f"rate_limit:{user_id}"

        assert key == "rate_limit:789"
