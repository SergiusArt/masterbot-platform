"""Bablo section keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_MAIN,
    MENU_BACK,
    MENU_BABLO_ANALYTICS,
    MENU_BABLO_SIGNALS,
    MENU_BABLO_SETTINGS,
    MENU_ACTIVITY,
    EMOJI_CHART,
    EMOJI_FIRE,
    EMOJI_HOME,
)


def get_bablo_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build Bablo section menu keyboard.

    Returns:
        Bablo menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_BABLO_ANALYTICS, style="primary", icon_custom_emoji_id=EMOJI_CHART),
                KeyboardButton(text=MENU_BABLO_SIGNALS, style="primary"),
            ],
            [
                KeyboardButton(text=MENU_ACTIVITY, icon_custom_emoji_id=EMOJI_FIRE),
                KeyboardButton(text=MENU_BABLO_SETTINGS),
            ],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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
                KeyboardButton(text="💰 За сегодня", style="primary"),
                KeyboardButton(text="💰 За вчера"),
            ],
            [
                KeyboardButton(text="💰 За неделю"),
                KeyboardButton(text="💰 За месяц"),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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
    if notifications_enabled:
        toggle_text = "🔕"
        toggle_style = "danger"
    else:
        toggle_text = "🔔"
        toggle_style = "success"

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
            [KeyboardButton(text=toggle_text, style=toggle_style), KeyboardButton(text=f"⭐ {min_quality}/10", style="primary")],
            [KeyboardButton(text=f"⏱ {tf_text}")],
            [KeyboardButton(text=f"📈 {dir_text}")],
            [KeyboardButton(text=MENU_BACK), KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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
                KeyboardButton(text="🟢 Long сигналы", style="success"),
                KeyboardButton(text="🔴 Short сигналы", style="danger"),
            ],
            [KeyboardButton(text="📋 Все сигналы", style="primary")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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

    def btn(tf: str) -> KeyboardButton:
        is_sel = tf in selected
        check = "✅" if is_sel else "⬜"
        return KeyboardButton(text=f"{check} {tf}", style="success" if is_sel else None)

    return ReplyKeyboardMarkup(
        keyboard=[
            [btn("1м"), btn("5м"), btn("15м")],
            [btn("30м"), btn("1ч")],
            [KeyboardButton(text="📋 Показать сигналы", style="primary")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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

    def btn(tf: str) -> KeyboardButton:
        is_sel = tf in selected
        check = "✅" if is_sel else "⬜"
        return KeyboardButton(text=f"{check} {tf}", style="success" if is_sel else None)

    return ReplyKeyboardMarkup(
        keyboard=[
            [btn("1м"), btn("5м"), btn("15м")],
            [btn("30м"), btn("1ч")],
            [KeyboardButton(text="✅ Сохранить", style="success")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
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
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{'✅' if long_enabled else '⬜'} Long", style="success" if long_enabled else None),
                KeyboardButton(text=f"{'✅' if short_enabled else '⬜'} Short", style="danger" if short_enabled else None),
            ],
            [KeyboardButton(text="✅ Сохранить", style="success")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_activity_menu_keyboard(
    window: int = 15,
    threshold: int = 10,
) -> ReplyKeyboardMarkup:
    """Build activity settings keyboard.

    Args:
        window: Activity window in minutes
        threshold: Activity threshold (number of signals)

    Returns:
        Activity menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"⏱ {window}м", style="primary"),
                KeyboardButton(text=f"📊 {threshold}", style="primary"),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
