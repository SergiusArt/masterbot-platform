"""End-to-end navigation tests for all menus and buttons."""

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, MagicMock, patch

from master_bot.states.navigation import MenuState
from master_bot.handlers import start, navigation
from master_bot.handlers.impulse import menu as impulse_menu, activity as impulse_activity
from master_bot.handlers.bablo import menu as bablo_menu, activity as bablo_activity
from master_bot.handlers.admin import menu as admin_menu, services as admin_services
from shared.constants import *


@pytest.fixture
def storage():
    """Create memory storage for tests."""
    return MemoryStorage()


@pytest.fixture
async def dp(storage):
    """Create dispatcher with all handlers."""
    dispatcher = Dispatcher(storage=storage)

    # Register all handlers in correct order
    dispatcher.include_router(start.router)
    dispatcher.include_router(navigation.router)
    dispatcher.include_router(bablo_menu.router)
    dispatcher.include_router(bablo_activity.router)
    dispatcher.include_router(impulse_menu.router)
    dispatcher.include_router(impulse_activity.router)
    dispatcher.include_router(admin_menu.router)
    dispatcher.include_router(admin_services.router)

    return dispatcher


@pytest.fixture
def user():
    """Create test user."""
    return User(id=12345, is_bot=False, first_name="Test")


@pytest.fixture
def admin_user():
    """Create admin test user."""
    return User(id=99999, is_bot=False, first_name="Admin")


@pytest.fixture
def chat():
    """Create test chat."""
    return Chat(id=12345, type="private")


def create_message(text: str, user: User, chat: Chat) -> Message:
    """Helper to create message."""
    return Message(
        message_id=1,
        date=1234567890,
        chat=chat,
        from_user=user,
        text=text
    )


class TestMainMenuNavigation:
    """Test main menu navigation."""

    @pytest.mark.asyncio
    async def test_start_command_sets_main_state(self, dp, user, chat, storage):
        """Test /start command sets MenuState.main."""
        message = create_message("/start", user, chat)
        message.answer = AsyncMock()

        await dp.feed_update(MagicMock(message=message, update_id=1))

        # Check state was set
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        current_state = await state.get_state()
        assert current_state == MenuState.main


class TestImpulseNavigation:
    """Test Impulse section navigation."""

    @pytest.mark.asyncio
    async def test_impulse_menu_sets_impulse_state(self, dp, user, chat, storage):
        """Test entering Impulse menu sets MenuState.impulse."""
        message = create_message(MENU_IMPULSE, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.impulse.menu.impulse_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        current_state = await state.get_state()
        assert current_state == MenuState.impulse

    @pytest.mark.asyncio
    async def test_impulse_activity_sets_activity_state(self, dp, user, chat, storage):
        """Test entering Impulse Activity sets MenuState.impulse_activity."""
        # First set to impulse state
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.impulse)

        message = create_message(MENU_ACTIVITY, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.impulse.activity.impulse_client') as mock_client:
            mock_client.get_user_settings = AsyncMock(return_value={})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        current_state = await state.get_state()
        assert current_state == MenuState.impulse_activity

    @pytest.mark.asyncio
    async def test_impulse_activity_emoji_buttons_only_in_activity_state(self, dp, user, chat, storage):
        """Test emoji buttons ⏱ and 📊 only work in impulse_activity state."""
        # Set state to admin (NOT impulse_activity)
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.admin)

        # Try to trigger emoji handler with ⏱ emoji
        message = create_message("⏱ 15м", user, chat)
        message.answer = AsyncMock()

        await dp.feed_update(MagicMock(message=message, update_id=1))

        # State should still be admin (handler should not have triggered)
        current_state = await state.get_state()
        assert current_state == MenuState.admin
        # Message should not be about activity window
        if message.answer.called:
            call_args = message.answer.call_args[0][0] if message.answer.call_args else ""
            assert "Окно активности" not in call_args


class TestBabloNavigation:
    """Test Bablo section navigation."""

    @pytest.mark.asyncio
    async def test_bablo_menu_sets_bablo_state(self, dp, user, chat, storage):
        """Test entering Bablo menu sets MenuState.bablo."""
        message = create_message(MENU_BABLO, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.bablo.menu.bablo_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        current_state = await state.get_state()
        assert current_state == MenuState.bablo

    @pytest.mark.asyncio
    async def test_bablo_activity_sets_activity_state(self, dp, user, chat, storage):
        """Test entering Bablo Activity sets MenuState.bablo_activity."""
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.bablo)

        message = create_message(MENU_ACTIVITY, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.bablo.activity.bablo_client') as mock_client:
            mock_client.get_user_settings = AsyncMock(return_value={})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        current_state = await state.get_state()
        assert current_state == MenuState.bablo_activity

    @pytest.mark.asyncio
    async def test_bablo_activity_emoji_buttons_only_in_activity_state(self, dp, user, chat, storage):
        """Test emoji buttons ⏱ and 📊 only work in bablo_activity state."""
        # Set state to admin (NOT bablo_activity)
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.admin)

        # Try to trigger emoji handler with 📊 emoji (like "📊 Статус сервисов")
        message = create_message("📊 Статус сервисов", user, chat)
        message.answer = AsyncMock()
        message.edit_text = AsyncMock()

        with patch('master_bot.services.service_registry.service_registry') as mock_registry:
            mock_registry.check_all_services_health = AsyncMock(return_value={})
            mock_registry.get_active_services = AsyncMock(return_value=[])

            # Provide is_admin=True middleware value
            await dp.feed_update(
                MagicMock(message=message, update_id=1),
                is_admin=True
            )

        # State should still be admin (bablo handler should not have triggered)
        current_state = await state.get_state()
        assert current_state == MenuState.admin

        # Message should be about service status, NOT about activity threshold
        if message.answer.called:
            call_args = message.answer.call_args[0][0] if message.answer.call_args else ""
            assert "Порог активности" not in call_args, \
                f"Bablo activity handler incorrectly triggered in admin state: {call_args}"


class TestAdminNavigation:
    """Test Admin panel navigation."""

    @pytest.mark.asyncio
    async def test_admin_menu_sets_admin_state(self, dp, admin_user, chat, storage):
        """Test entering Admin menu sets MenuState.admin."""
        message = create_message(MENU_ADMIN, admin_user, chat)
        message.answer = AsyncMock()

        await dp.feed_update(
            MagicMock(message=message, update_id=1),
            is_admin=True
        )

        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, admin_user.id))
        current_state = await state.get_state()
        assert current_state == MenuState.admin

    @pytest.mark.asyncio
    async def test_admin_service_status_button_works_in_admin_state(self, dp, admin_user, chat, storage):
        """Test 📊 Статус сервисов button works correctly in admin state."""
        # Set admin state
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, admin_user.id))
        await state.set_state(MenuState.admin)

        message = create_message(MENU_SERVICE_STATUS, admin_user, chat)
        message.answer = AsyncMock(return_value=MagicMock(edit_text=AsyncMock()))
        message.edit_text = AsyncMock()

        with patch('master_bot.services.service_registry.service_registry') as mock_registry:
            mock_registry.check_all_services_health = AsyncMock(return_value={})
            mock_registry.get_active_services = AsyncMock(return_value=[])

            await dp.feed_update(
                MagicMock(message=message, update_id=1),
                is_admin=True
            )

        # Should have shown service status, not activity threshold
        assert message.answer.called
        call_text = message.answer.call_args[0][0] if message.answer.call_args else ""
        assert "Проверяю статус" in call_text or "статус" in call_text.lower()
        assert "Порог активности" not in call_text, \
            f"Activity handler incorrectly triggered: {call_text}"


class TestBackButtonNavigation:
    """Test back button navigation from all menus."""

    @pytest.mark.asyncio
    async def test_back_from_bablo_activity_returns_to_bablo(self, dp, user, chat, storage):
        """Test pressing Back from Bablo Activity returns to Bablo menu."""
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.bablo_activity)

        message = create_message(MENU_BACK, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.bablo.activity.bablo_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        current_state = await state.get_state()
        assert current_state == MenuState.bablo, \
            f"Expected MenuState.bablo, got {current_state}"

    @pytest.mark.asyncio
    async def test_back_from_impulse_activity_returns_to_impulse(self, dp, user, chat, storage):
        """Test pressing Back from Impulse Activity returns to Impulse menu."""
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, user.id))
        await state.set_state(MenuState.impulse_activity)

        message = create_message(MENU_BACK, user, chat)
        message.answer = AsyncMock()

        with patch('master_bot.handlers.impulse.activity.impulse_client') as mock_client:
            mock_client.get_analytics = AsyncMock(return_value={"total": 0})
            await dp.feed_update(MagicMock(message=message, update_id=1))

        current_state = await state.get_state()
        assert current_state == MenuState.impulse, \
            f"Expected MenuState.impulse, got {current_state}"

    @pytest.mark.asyncio
    async def test_back_from_admin_services_returns_to_admin(self, dp, admin_user, chat, storage):
        """Test pressing Back from Admin Services returns to Admin menu."""
        state = FSMContext(storage, key=dp.storage.key_builder.build(chat.id, admin_user.id))
        await state.set_state(MenuState.admin)

        message = create_message(MENU_BACK, admin_user, chat)
        message.answer = AsyncMock()

        await dp.feed_update(
            MagicMock(message=message, update_id=1),
            is_admin=True
        )

        current_state = await state.get_state()
        assert current_state == MenuState.admin, \
            f"Expected MenuState.admin, got {current_state}"
