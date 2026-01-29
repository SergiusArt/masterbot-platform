"""Integration tests for database operations."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "impulse_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "bablo_service"))


class TestDatabaseConnection:
    """Tests for database connection and session management."""

    @pytest.fixture
    async def async_engine(self):
        """Create async in-memory SQLite engine."""
        from sqlalchemy import StaticPool

        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        from shared.database.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await engine.dispose()

    @pytest.fixture
    async def session(self, async_engine) -> AsyncSession:
        """Create async session."""
        async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_local() as session:
            yield session

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_creation(self, session):
        """Test database session is created successfully."""
        assert session is not None
        assert isinstance(session, AsyncSession)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_commit(self, session):
        """Test session commit works."""
        await session.commit()  # Should not raise

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_rollback(self, session):
        """Test session rollback works."""
        await session.rollback()  # Should not raise


class TestImpulseModel:
    """Integration tests for Impulse model."""

    @pytest.fixture
    async def async_engine(self):
        """Create async engine with Impulse model."""
        from sqlalchemy import StaticPool

        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # Import and create tables
        from shared.database.models import Base
        from models.impulse import Impulse  # This adds Impulse to Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await engine.dispose()

    @pytest.fixture
    async def session(self, async_engine) -> AsyncSession:
        """Create async session."""
        async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_local() as session:
            yield session

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_impulse(self, session):
        """Test creating an impulse record."""
        from models.impulse import Impulse

        impulse = Impulse(
            symbol="BTCUSDT",
            percent=Decimal("15.5"),
            max_percent=Decimal("20.0"),
            type="growth",
            growth_ratio=Decimal("65"),
            fall_ratio=Decimal("35"),
        )

        session.add(impulse)
        await session.commit()
        await session.refresh(impulse)

        assert impulse.id is not None
        assert impulse.symbol == "BTCUSDT"
        assert impulse.percent == Decimal("15.5")
        assert impulse.type == "growth"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_query_impulses(self, session):
        """Test querying impulse records."""
        from models.impulse import Impulse

        # Create test data
        impulses = [
            Impulse(symbol="BTCUSDT", percent=Decimal("10"), type="growth"),
            Impulse(symbol="ETHUSDT", percent=Decimal("-15"), type="fall"),
            Impulse(symbol="BTCUSDT", percent=Decimal("20"), type="growth"),
        ]

        for imp in impulses:
            session.add(imp)
        await session.commit()

        # Query all
        result = await session.execute(select(Impulse))
        all_impulses = result.scalars().all()
        assert len(all_impulses) == 3

        # Query by symbol
        result = await session.execute(
            select(Impulse).where(Impulse.symbol == "BTCUSDT")
        )
        btc_impulses = result.scalars().all()
        assert len(btc_impulses) == 2

        # Query by type
        result = await session.execute(
            select(Impulse).where(Impulse.type == "growth")
        )
        growth_impulses = result.scalars().all()
        assert len(growth_impulses) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_impulse_ordering(self, session):
        """Test impulse ordering by received_at."""
        from models.impulse import Impulse
        from datetime import timedelta

        now = datetime.now(timezone.utc)

        impulses = [
            Impulse(symbol="BTC1", percent=Decimal("10"), type="growth"),
            Impulse(symbol="BTC2", percent=Decimal("20"), type="growth"),
            Impulse(symbol="BTC3", percent=Decimal("30"), type="growth"),
        ]

        for i, imp in enumerate(impulses):
            imp.received_at = now - timedelta(hours=i)
            session.add(imp)
        await session.commit()

        # Query ordered by received_at desc (most recent first)
        result = await session.execute(
            select(Impulse).order_by(Impulse.received_at.desc())
        )
        ordered = result.scalars().all()

        assert ordered[0].symbol == "BTC1"  # Most recent
        assert ordered[2].symbol == "BTC3"  # Oldest

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_impulse_aggregations(self, session):
        """Test aggregate queries on impulses."""
        from models.impulse import Impulse

        impulses = [
            Impulse(symbol="BTC", percent=Decimal("10"), type="growth"),
            Impulse(symbol="BTC", percent=Decimal("20"), type="growth"),
            Impulse(symbol="ETH", percent=Decimal("-15"), type="fall"),
        ]

        for imp in impulses:
            session.add(imp)
        await session.commit()

        # Count total
        result = await session.execute(select(func.count(Impulse.id)))
        total = result.scalar()
        assert total == 3

        # Count by type
        result = await session.execute(
            select(func.count(Impulse.id)).where(Impulse.type == "growth")
        )
        growth_count = result.scalar()
        assert growth_count == 2

        # Max percent
        result = await session.execute(select(func.max(Impulse.percent)))
        max_percent = result.scalar()
        assert max_percent == Decimal("20")


class TestBabloSignalModel:
    """Integration tests for BabloSignal model."""

    @pytest.fixture
    async def async_engine(self):
        """Create async engine with BabloSignal model."""
        from sqlalchemy import StaticPool

        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        from shared.database.models import Base
        from models.bablo import BabloSignal

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await engine.dispose()

    @pytest.fixture
    async def session(self, async_engine) -> AsyncSession:
        """Create async session."""
        async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_local() as session:
            yield session

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_bablo_signal(self, session):
        """Test creating a Bablo signal record."""
        from models.bablo import BabloSignal

        signal = BabloSignal(
            symbol="BTCUSDT.P",
            direction="long",
            strength=4,
            timeframe="1m",
            time_horizon="60 минут",
            quality_total=7,
            quality_profit=8,
            quality_drawdown=6,
            quality_accuracy=7,
            probabilities={"0.3": {"long": 72, "short": 86}},
            max_drawdown=Decimal("6"),
        )

        session.add(signal)
        await session.commit()
        await session.refresh(signal)

        assert signal.id is not None
        assert signal.symbol == "BTCUSDT.P"
        assert signal.direction == "long"
        assert signal.strength == 4
        assert signal.quality_total == 7

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_query_signals_by_direction(self, session):
        """Test querying signals by direction."""
        from models.bablo import BabloSignal

        signals = [
            BabloSignal(symbol="BTC1", direction="long", strength=3, timeframe="1m", quality_total=5),
            BabloSignal(symbol="BTC2", direction="short", strength=2, timeframe="15m", quality_total=6),
            BabloSignal(symbol="BTC3", direction="long", strength=4, timeframe="1h", quality_total=7),
        ]

        for sig in signals:
            session.add(sig)
        await session.commit()

        # Query long signals
        result = await session.execute(
            select(BabloSignal).where(BabloSignal.direction == "long")
        )
        long_signals = result.scalars().all()
        assert len(long_signals) == 2

        # Query short signals
        result = await session.execute(
            select(BabloSignal).where(BabloSignal.direction == "short")
        )
        short_signals = result.scalars().all()
        assert len(short_signals) == 1

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_query_signals_by_quality(self, session):
        """Test querying signals by minimum quality."""
        from models.bablo import BabloSignal

        signals = [
            BabloSignal(symbol="BTC1", direction="long", strength=1, timeframe="1m", quality_total=3),
            BabloSignal(symbol="BTC2", direction="long", strength=3, timeframe="1m", quality_total=6),
            BabloSignal(symbol="BTC3", direction="long", strength=5, timeframe="1m", quality_total=9),
        ]

        for sig in signals:
            session.add(sig)
        await session.commit()

        # Query signals with quality >= 6
        result = await session.execute(
            select(BabloSignal).where(BabloSignal.quality_total >= 6)
        )
        quality_signals = result.scalars().all()
        assert len(quality_signals) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_signal_json_field(self, session):
        """Test JSON field (probabilities) storage and retrieval."""
        from models.bablo import BabloSignal

        probs = {
            "0.3": {"long": 85, "short": 90},
            "0.6": {"long": 75, "short": 82},
            "0.9": {"long": 65, "short": 72},
        }

        signal = BabloSignal(
            symbol="ETHUSDT.P",
            direction="long",
            strength=5,
            timeframe="15m",
            quality_total=8,
            probabilities=probs,
        )

        session.add(signal)
        await session.commit()
        await session.refresh(signal)

        # Verify JSON is stored and retrieved correctly
        assert signal.probabilities == probs
        assert signal.probabilities["0.3"]["long"] == 85
        assert signal.probabilities["0.9"]["short"] == 72


class TestUserModel:
    """Integration tests for User model."""

    @pytest.fixture
    async def async_engine(self):
        """Create async engine with User model."""
        from sqlalchemy import StaticPool

        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        from shared.database.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await engine.dispose()

    @pytest.fixture
    async def session(self, async_engine) -> AsyncSession:
        """Create async session."""
        async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_local() as session:
            yield session

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user(self, session):
        """Test creating a user record."""
        from shared.database.models import User

        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_admin=False,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.is_active is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_query_user_by_telegram_id(self, session):
        """Test querying user by Telegram ID."""
        from shared.database.models import User

        user = User(
            telegram_id=987654321,
            username="queryuser",
        )

        session.add(user)
        await session.commit()

        result = await session.execute(
            select(User).where(User.telegram_id == 987654321)
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.username == "queryuser"
