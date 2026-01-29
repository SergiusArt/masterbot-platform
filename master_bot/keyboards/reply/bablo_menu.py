"""Bablo section keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_MAIN,
    MENU_BACK,
    MENU_BABLO_ANALYTICS,
    MENU_BABLO_SIGNALS,
    MENU_BABLO_SETTINGS,
)


def get_bablo_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build Bablo section menu keyboard.

    Returns:
        Bablo menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_BABLO_ANALYTICS),
                KeyboardButton(text=MENU_BABLO_SIGNALS),
            ],
            [KeyboardButton(text=MENU_BABLO_SETTINGS)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_bablo_analytics_keyboard() -> ReplyKeyboardMarkup:
    """Build Bablo analytics period selection keyboard.

    Returns:
        Analytics menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💰 За сегодня"),
                KeyboardButton(text="💰 За вчера"),
            ],
            [
                KeyboardButton(text="💰 За неделю"),
                KeyboardButton(text="💰 За месяц"),
            ],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_bablo_settings_keyboard(
    notifications_enabled: bool = True,
    min_quality: int = 7,
    min_strength: int = 3,
) -> ReplyKeyboardMarkup:
    """Build Bablo settings keyboard.

    Args:
        notifications_enabled: Whether notifications are enabled
        min_quality: Minimum quality threshold (1-10)
        min_strength: Minimum strength threshold (1-5)

    Returns:
        Settings menu keyboard
    """
    toggle_text = "🔕 Выключить Bablo" if notifications_enabled else "🔔 Включить Bablo"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=toggle_text)],
            [KeyboardButton(text=f"⭐ Качество: {min_quality}/10")],
            [KeyboardButton(text=f"📊 Сила: {min_strength}/5")],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_bablo_signals_keyboard() -> ReplyKeyboardMarkup:
    """Build Bablo signals list keyboard.

    Returns:
        Signals menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🟢 Long сигналы"),
                KeyboardButton(text="🔴 Short сигналы"),
            ],
            [KeyboardButton(text="📋 Все сигналы")],
            [
                KeyboardButton(text="⏱ 15м"),
                KeyboardButton(text="⏱ 1ч"),
                KeyboardButton(text="⏱ 4ч"),
            ],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
