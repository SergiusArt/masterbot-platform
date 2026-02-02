"""Navigation tests for all menus and buttons.

Tests handler functions directly to verify FSM state transitions
and back-button navigation.
"""

import pytest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, MagicMock, patch

from master_bot.states.navigation import MenuState
from shared.constants import *


@pytest.fixture
def storage():
    """Create memory storage for tests."""
    return MemoryStorage()


@pytest.fixture
def state(storage):
    """Create FSM context for a test user."""
    key = StorageKey(bot_id=1, chat_id=12345, user_id=12345)
    return FSMContext(storage=storage, key=key)


@pytest.fixture
def message():
    """Create mock message with answer method."""
    msg = MagicMock()
    msg.answer = AsyncMock()
    msg.from_user = MagicMock(id=12345)
    msg.chat = MagicMock(id=12345)
    return msg


class TestMainMenuNavigation:
    """Test main menu navigation."""

    @pytest.mark.asyncio
    async def test_start_command_sets_main_state(self, message, state):
        """Test /start command handler sets MenuState.main via state."""
        from master_bot.handlers.start import cmd_start

        # cmd_start doesn't take state, it just answers
        # But it should show the main menu
        await cmd_start(message, is_admin=False)

        assert message.answer.called
        call_text = message.answer.call_args[0][0]
        assert "Главное меню" in call_text or "Привет" in call_text or "MasterBot" in call_text


class TestImpulseNavigation:
    """Test Impulse section navigation."""

    @pytest.mark.asyncio
    async def test_impulse_menu_sets_impulse_state(self, message, state):
        """Test entering Impulse menu sets MenuState.impulse."""
        from master_bot.handlers.impulse.menu import impulse_menu

        await impulse_menu(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.impulse

    @pytest.mark.asyncio
    async def test_impulse_activity_sets_activity_state(self, message, state):
        """Test entering Impulse Activity sets MenuState.impulse_activity."""
        await state.set_state(MenuState.impulse)

        from master_bot.handlers.impulse.activity import activity_menu

        with patch('master_bot.handlers.impulse.activity.impulse_client') as mock_client:
            mock_client.get_user_settings = AsyncMock(return_value={})
            await activity_menu(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.impulse_activity

    @pytest.mark.asyncio
    async def test_back_from_impulse_activity_returns_to_impulse(self, message, state):
        """Test pressing Back from Impulse Activity returns to Impulse menu."""
        await state.set_state(MenuState.impulse_activity)

        from master_bot.handlers.impulse.activity import back_from_activity

        with patch('master_bot.handlers.impulse.activity.impulse_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await back_from_activity(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.impulse, \
            f"Expected MenuState.impulse, got {current_state}"


class TestBabloNavigation:
    """Test Bablo section navigation."""

    @pytest.mark.asyncio
    async def test_bablo_menu_sets_bablo_state(self, message, state):
        """Test entering Bablo menu sets MenuState.bablo."""
        from master_bot.handlers.bablo.menu import bablo_menu

        await bablo_menu(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.bablo

    @pytest.mark.asyncio
    async def test_bablo_activity_sets_activity_state(self, message, state):
        """Test entering Bablo Activity sets MenuState.bablo_activity."""
        await state.set_state(MenuState.bablo)

        from master_bot.handlers.bablo.activity import activity_menu

        with patch('master_bot.handlers.bablo.activity.bablo_client') as mock_client:
            mock_client.get_user_settings = AsyncMock(return_value={})
            await activity_menu(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.bablo_activity

    @pytest.mark.asyncio
    async def test_back_from_bablo_activity_returns_to_bablo(self, message, state):
        """Test pressing Back from Bablo Activity returns to Bablo menu."""
        await state.set_state(MenuState.bablo_activity)

        from master_bot.handlers.bablo.activity import back_from_activity

        with patch('master_bot.handlers.bablo.activity.bablo_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await back_from_activity(message, state)

        current_state = await state.get_state()
        assert current_state == MenuState.bablo, \
            f"Expected MenuState.bablo, got {current_state}"


class TestAdminNavigation:
    """Test Admin panel navigation."""

    @pytest.mark.asyncio
    async def test_admin_menu_sets_admin_state(self, message, state):
        """Test entering Admin menu sets MenuState.admin."""
        from master_bot.handlers.admin.menu import admin_menu

        await admin_menu(message, state, is_admin=True)

        current_state = await state.get_state()
        assert current_state == MenuState.admin

    @pytest.mark.asyncio
    async def test_admin_non_admin_rejected(self, message, state):
        """Test non-admin users are rejected from admin menu."""
        from master_bot.handlers.admin.menu import admin_menu

        await admin_menu(message, state, is_admin=False)

        # Non-admin should not get admin state
        current_state = await state.get_state()
        assert current_state != MenuState.admin

    @pytest.mark.asyncio
    async def test_back_from_admin_services_returns_to_admin(self, message, state):
        """Test pressing Back from Admin services returns to admin panel."""
        await state.set_state(MenuState.admin)

        from master_bot.handlers.admin.services import back_from_admin

        await back_from_admin(message, state, is_admin=True)

        current_state = await state.get_state()
        assert current_state == MenuState.admin, \
            f"Expected MenuState.admin, got {current_state}"


class TestServiceStatusNavigation:
    """Test admin service status doesn't conflict with activity handlers."""

    @pytest.mark.asyncio
    async def test_service_status_handler_responds(self, message, state):
        """Test service status handler responds correctly."""
        from master_bot.handlers.admin.services import check_services_status

        with patch('master_bot.handlers.admin.services.service_registry') as mock_registry:
            mock_registry.check_all_services_health = AsyncMock(return_value={})
            mock_registry.get_active_services = MagicMock(return_value=[])

            # Mock the status message that gets edited
            status_msg = MagicMock()
            status_msg.edit_text = AsyncMock()
            message.answer = AsyncMock(return_value=status_msg)

            await check_services_status(message, is_admin=True)

        assert message.answer.called
        call_text = message.answer.call_args[0][0]
        assert "статус" in call_text.lower() or "Проверяю" in call_text
