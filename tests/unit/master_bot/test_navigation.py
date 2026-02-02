"""Tests for navigation state management and back button handling."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "master_bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))


class TestMenuState:
    """Test MenuState FSM states."""

    @pytest.mark.unit
    def test_menu_state_exists(self):
        """Test MenuState class exists with expected states."""
        from states.navigation import MenuState

        # Main sections
        assert hasattr(MenuState, "main")
        assert hasattr(MenuState, "impulse")
        assert hasattr(MenuState, "bablo")
        assert hasattr(MenuState, "settings")

        # Impulse sub-menus
        assert hasattr(MenuState, "impulse_analytics")
        assert hasattr(MenuState, "impulse_notifications")
        assert hasattr(MenuState, "impulse_reports")
        assert hasattr(MenuState, "impulse_activity")

        # Bablo sub-menus
        assert hasattr(MenuState, "bablo_analytics")
        assert hasattr(MenuState, "bablo_signals")
        assert hasattr(MenuState, "bablo_settings")


class TestMainMenuKeyboard:
    """Test main menu keyboard layout."""

    @pytest.mark.unit
    def test_main_menu_layout(self):
        """Test main menu layout with Reports button."""
        from keyboards.reply.main_menu import get_main_menu_keyboard
        from shared.constants import MENU_IMPULSES, MENU_BABLO, MENU_REPORTS, MENU_SETTINGS

        keyboard = get_main_menu_keyboard(is_admin=False)

        # First row should have both Impulses and Bablo
        first_row = keyboard.keyboard[0]
        assert len(first_row) == 2
        assert first_row[0].text == MENU_IMPULSES
        assert first_row[1].text == MENU_BABLO

        # Second row should have Reports
        second_row = keyboard.keyboard[1]
        assert len(second_row) == 1
        assert second_row[0].text == MENU_REPORTS

        # Third row should have Settings
        third_row = keyboard.keyboard[2]
        assert len(third_row) == 1
        assert third_row[0].text == MENU_SETTINGS

    @pytest.mark.unit
    def test_main_menu_with_admin(self):
        """Test main menu has admin button when user is admin."""
        from keyboards.reply.main_menu import get_main_menu_keyboard
        from shared.constants import MENU_ADMIN

        keyboard = get_main_menu_keyboard(is_admin=True)

        # Should have 4 rows: [Impulses, Bablo], [Reports], [Settings], [Admin]
        assert len(keyboard.keyboard) == 4
        admin_row = keyboard.keyboard[3]
        assert admin_row[0].text == MENU_ADMIN


class TestBabloSignalsKeyboard:
    """Test Bablo signals keyboard."""

    @pytest.mark.unit
    def test_signals_keyboard_has_direction_buttons(self):
        """Test signals keyboard includes direction selection buttons."""
        from keyboards.reply.bablo_menu import get_bablo_signals_keyboard
        from shared.constants import MENU_MAIN

        keyboard = get_bablo_signals_keyboard()

        # Flatten all button texts
        all_buttons = [btn.text for row in keyboard.keyboard for btn in row]

        # Check direction buttons exist
        assert "🟢 Long сигналы" in all_buttons
        assert "🔴 Short сигналы" in all_buttons
        assert "📋 Все сигналы" in all_buttons

        # Check main menu button exists
        assert MENU_MAIN in all_buttons

    @pytest.mark.unit
    def test_timeframe_selection_keyboard(self):
        """Test timeframe selection keyboard."""
        from keyboards.reply.bablo_menu import get_timeframe_selection_keyboard
        from shared.constants import MENU_MAIN

        keyboard = get_timeframe_selection_keyboard()

        # Flatten all button texts
        all_buttons = [btn.text for row in keyboard.keyboard for btn in row]

        # Check timeframe buttons exist
        assert "⬜ 1м" in all_buttons
        assert "⬜ 5м" in all_buttons
        assert "⬜ 15м" in all_buttons
        assert "⬜ 30м" in all_buttons
        assert "⬜ 1ч" in all_buttons

        # Check show button exists
        assert "📋 Показать сигналы" in all_buttons

        # Check main menu button exists
        assert MENU_MAIN in all_buttons

    @pytest.mark.unit
    def test_timeframe_selection_with_selected(self):
        """Test timeframe selection keyboard with pre-selected items."""
        from keyboards.reply.bablo_menu import get_timeframe_selection_keyboard

        keyboard = get_timeframe_selection_keyboard(selected={"1м", "15м"})

        # Flatten all button texts
        all_buttons = [btn.text for row in keyboard.keyboard for btn in row]

        # Check selected timeframes have checkmark
        assert "✅ 1м" in all_buttons
        assert "✅ 15м" in all_buttons

        # Check unselected timeframes have empty box
        assert "⬜ 5м" in all_buttons
        assert "⬜ 30м" in all_buttons
        assert "⬜ 1ч" in all_buttons


class TestSignalFormatting:
    """Test signal formatting functions."""

    @pytest.mark.unit
    def test_format_time_today(self):
        """Test time formatting for today's signals."""
        from datetime import datetime, timezone
        from handlers.bablo.signals import _format_time

        now = datetime.now(timezone.utc)
        iso_time = now.isoformat()

        result = _format_time(iso_time)

        # Should return HH:MM format for today
        assert ":" in result
        assert len(result) == 5  # HH:MM

    @pytest.mark.unit
    def test_format_time_invalid(self):
        """Test time formatting handles invalid input."""
        from handlers.bablo.signals import _format_time

        result = _format_time("invalid")
        assert result == ""

        result = _format_time("")
        assert result == ""

    @pytest.mark.unit
    def test_format_signal_long(self):
        """Test formatting long signal."""
        from handlers.bablo.signals import _format_signal

        signal = {
            "symbol": "BTCUSDT.P",
            "direction": "long",
            "strength": 4,
            "timeframe": "1h",
            "quality_total": 8,
            "max_drawdown": 5.5,
            "received_at": "2024-01-15T10:30:00+00:00",
        }

        result = _format_signal(signal)

        assert "🟢" in result
        assert "BTCUSDT.P" in result
        assert "Long" in result
        assert "🟩🟩🟩🟩⬜" in result
        assert "8/10" in result
        assert "5.5%" in result

    @pytest.mark.unit
    def test_format_signal_short(self):
        """Test formatting short signal."""
        from handlers.bablo.signals import _format_signal

        signal = {
            "symbol": "ETHUSDT.P",
            "direction": "short",
            "strength": 3,
            "timeframe": "15m",
            "quality_total": 6,
            "received_at": "2024-01-15T14:00:00+00:00",
        }

        result = _format_signal(signal)

        assert "🔴" in result
        assert "ETHUSDT.P" in result
        assert "Short" in result
        assert "🟩🟩🟩⬜⬜" in result
        assert "6/10" in result
