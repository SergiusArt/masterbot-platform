"""Shared test fixtures and configuration."""

import asyncio
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "shared"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "impulse_service"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "bablo_service"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "master_bot"))

# Optional imports - only load if available
try:
    from sqlalchemy import StaticPool
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


# ============================================================================
# Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures (In-Memory SQLite for Testing)
# ============================================================================


if HAS_SQLALCHEMY:
    @pytest.fixture(scope="function")
    async def async_engine():
        """Create async in-memory SQLite engine for testing."""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # Import all models to create tables
        from shared.database.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()


    @pytest.fixture(scope="function")
    async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
        """Create async session for testing."""
        async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        async with async_session_local() as session:
            yield session
            await session.rollback()


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock()
    redis.health_check = AsyncMock(return_value=True)
    redis.publish = AsyncMock()
    redis.subscribe = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def mock_telegram_client():
    """Create a mock Telegram client."""
    client = MagicMock()
    client.start = AsyncMock()
    client.disconnect = AsyncMock()
    client.get_messages = AsyncMock(return_value=[])
    return client


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_impulse_messages() -> dict[str, str]:
    """Sample impulse messages for parser testing."""
    return {
        "growth_standard": """
🟢[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/) **10%**
📈|29%|---|71%|📉
Максимальный импульс: 15%
""",
        "fall_standard": """
🔴[AXSUSDT.P](https://ru.tradingview.com/symbols/AXSUSDT.P/) **-15%**
📈|35%|---|65%|📉
Максимальный импульс: 25%
""",
        "simple_growth": "BTCUSDT +25.5%",
        "simple_fall": "ETHUSDT -12.3%",
        "ratio_format": "BTC/USDT: 15.5%",
        "dollar_format": "$BTC +8.7%",
        "no_match": "This is not an impulse message",
        "empty": "",
        "malformed": "BTCUSDT without percent",
    }


@pytest.fixture
def sample_bablo_messages() -> dict[str, str]:
    """Sample Bablo messages for parser testing."""
    return {
        "long_signal": """
[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/)
🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 7 из 10:**
  ° Профитность _8_ из 10
  ° Просадка _6_ из 10
  ° Точность _7_ из 10

**Вероятность (60 минут):**
`0.3%`: 📉 `86%`, 📈 `72%`
`0.6%`: 📉 `75%`, 📈 `60%`

Максимальная просадка = __6%__
""",
        "short_signal": """
[BTCUSDT.P](https://ru.tradingview.com/symbols/BTCUSDT.P/)
🟥🟥🟥
`| 15м ТФ |`
**Качество = 8 из 10:**
  ° Профитность _10_ из 10
  ° Просадка _4_ из 10
  ° Точность _10_ из 10

**Вероятность (12 часов):**
`0.9%`: 📉 `82%`, 📈 `73%`
`1.5%`: 📉 `75%`, 📈 `66%`
`2.7%`: 📉 `55%`, 📈 `45%`

Максимальная просадка = __17%__
""",
        "minimal_long": """
[XRPUSDT.P](https://example.com)
🟩🟩
`| 1ч ТФ |`
**Качество = 5 из 10:**

**Вероятность (2 дня):**
`1.0%`: 📉 `70%`, 📈 `65%`

Максимальная просадка = __10%__
""",
        "no_match": "This is not a Bablo signal",
        "empty": "",
        "missing_direction": """
[ETHUSDT.P](https://example.com)
`| 4ч ТФ |`
**Качество = 6 из 10:**
""",
        "missing_quality": """
[DOTUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`
**Вероятность (60 минут):**
`0.3%`: 📉 `80%`, 📈 `70%`
""",
    }


@pytest.fixture
def sample_impulse_data() -> dict:
    """Sample impulse data for service testing."""
    return {
        "symbol": "BTCUSDT",
        "percent": Decimal("15.5"),
        "max_percent": Decimal("20.0"),
        "type": "growth",
        "growth_ratio": Decimal("65"),
        "fall_ratio": Decimal("35"),
        "raw_message": "Test message",
    }


@pytest.fixture
def sample_bablo_signal_data() -> dict:
    """Sample Bablo signal data for service testing."""
    return {
        "symbol": "SYNUSDT.P",
        "direction": "long",
        "strength": 5,
        "timeframe": "1m",
        "time_horizon": "60 минут",
        "quality_total": 7,
        "quality_profit": 8,
        "quality_drawdown": 6,
        "quality_accuracy": 7,
        "probabilities": {
            "0.3": {"long": 72, "short": 86},
            "0.6": {"long": 60, "short": 75},
        },
        "max_drawdown": Decimal("6"),
        "raw_message": "Test signal",
    }


# ============================================================================
# DateTime Fixtures
# ============================================================================


@pytest.fixture
def now_utc() -> datetime:
    """Current UTC datetime."""
    return datetime.now(timezone.utc)


@pytest.fixture
def today_start(now_utc) -> datetime:
    """Start of today in UTC."""
    return now_utc.replace(hour=0, minute=0, second=0, microsecond=0)


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def mock_session_maker(async_session):
    """Mock async_session_maker for service testing."""

    async def _mock_session_maker():
        return async_session

    # Create a context manager mock
    class MockContextManager:
        async def __aenter__(self):
            return async_session

        async def __aexit__(self, *args):
            pass

    return MockContextManager
