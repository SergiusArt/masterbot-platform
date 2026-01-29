"""Bablo section keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import MENU_MAIN, MENU_BACK, MENU_BABLO_ANALYTICS, MENU_BABLO_SIGNALS, MENU_BABLO_SETTINGS


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
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_bablo_settings_keyboard(
    notifications_enabled: bool = True,
    min_quality: int = 7,
    timeframes: list[str] | None = None,
    directions: list[str] | None = None,
) -> ReplyKeyboardMarkup:
    """Build Bablo settings keyboard.

    Args:
        notifications_enabled: Whether notifications are enabled
        min_quality: Minimum quality threshold (1-10)
        timeframes: Selected timeframes for notifications
        directions: Selected directions (long, short)

    Returns:
        Settings menu keyboard
    """
    toggle_text = "🔕 Выключить Bablo" if notifications_enabled else "🔔 Включить Bablo"

    # Format timeframes display
    if timeframes:
        tf_text = ", ".join(timeframes)
    else:
        tf_text = "все"

    # Format directions display
    if directions:
        dir_text = ", ".join(d.capitalize() for d in directions)
    else:
        dir_text = "все"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=toggle_text)],
            [KeyboardButton(text=f"⭐ Качество: {min_quality}/10")],
            [KeyboardButton(text=f"⏱ Таймфреймы: {tf_text}")],
            [KeyboardButton(text=f"📈 Направления: {dir_text}")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_bablo_signals_keyboard() -> ReplyKeyboardMarkup:
    """Build Bablo signals direction selection keyboard.

    Returns:
        Signals menu keyboard with direction options
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🟢 Long сигналы"),
                KeyboardButton(text="🔴 Short сигналы"),
            ],
            [KeyboardButton(text="📋 Все сигналы")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_timeframe_selection_keyboard(selected: set[str] | None = None) -> ReplyKeyboardMarkup:
    """Build timeframe selection keyboard for signals.

    Args:
        selected: Currently selected timeframes

    Returns:
        Timeframe selection keyboard
    """
    if selected is None:
        selected = set()

    def btn(tf: str) -> str:
        check = "✅" if tf in selected else "⬜"
        return f"{check} {tf}"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=btn("1м")),
                KeyboardButton(text=btn("5м")),
                KeyboardButton(text=btn("15м")),
            ],
            [
                KeyboardButton(text=btn("30м")),
                KeyboardButton(text=btn("1ч")),
            ],
            [KeyboardButton(text="📋 Показать сигналы")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_settings_timeframe_keyboard(selected: set[str] | None = None) -> ReplyKeyboardMarkup:
    """Build timeframe selection keyboard for settings.

    Args:
        selected: Currently selected timeframes

    Returns:
        Timeframe selection keyboard for settings
    """
    if selected is None:
        selected = set()

    def btn(tf: str) -> str:
        check = "✅" if tf in selected else "⬜"
        return f"{check} {tf}"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=btn("1м")),
                KeyboardButton(text=btn("5м")),
                KeyboardButton(text=btn("15м")),
            ],
            [
                KeyboardButton(text=btn("30м")),
                KeyboardButton(text=btn("1ч")),
            ],
            [KeyboardButton(text="✅ Сохранить")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_settings_direction_keyboard(
    long_enabled: bool = True,
    short_enabled: bool = True,
) -> ReplyKeyboardMarkup:
    """Build direction selection keyboard for settings.

    Args:
        long_enabled: Whether long signals are enabled
        short_enabled: Whether short signals are enabled

    Returns:
        Direction selection keyboard for settings
    """
    long_check = "✅" if long_enabled else "⬜"
    short_check = "✅" if short_enabled else "⬜"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{long_check} Long"),
                KeyboardButton(text=f"{short_check} Short"),
            ],
            [KeyboardButton(text="✅ Сохранить")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
