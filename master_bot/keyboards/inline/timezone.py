"""Timezone selection keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Popular timezones with their UTC offsets
POPULAR_TIMEZONES = [
    ("🇷🇺 Москва (UTC+3)", "Europe/Moscow"),
    ("🇷🇺 Калининград (UTC+2)", "Europe/Kaliningrad"),
    ("🇷🇺 Самара (UTC+4)", "Europe/Samara"),
    ("🇷🇺 Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
    ("🇷🇺 Новосибирск (UTC+7)", "Asia/Novosibirsk"),
    ("🇷🇺 Владивосток (UTC+10)", "Asia/Vladivostok"),
    ("🇺🇦 Киев (UTC+2)", "Europe/Kiev"),
    ("🇰🇿 Алматы (UTC+5)", "Asia/Almaty"),
    ("🇧🇾 Минск (UTC+3)", "Europe/Minsk"),
    ("🇺🇿 Ташкент (UTC+5)", "Asia/Tashkent"),
]


def get_timezone_keyboard(current_tz: str | None = None) -> InlineKeyboardMarkup:
    """Build timezone selection keyboard.

    Args:
        current_tz: Current user timezone for highlighting

    Returns:
        InlineKeyboardMarkup with timezone options
    """
    buttons = []

    for label, tz_value in POPULAR_TIMEZONES:
        # Add checkmark if this is current timezone
        is_current = tz_value == current_tz
        display_label = f"✓ {label}" if is_current else label
        buttons.append([
            InlineKeyboardButton(
                text=display_label,
                callback_data=f"tz:set:{tz_value}",
                style="success" if is_current else None,
            )
        ])

    # Add custom input option
    buttons.append([
        InlineKeyboardButton(
            text="⌨️ Ввести вручную (UTC±N)",
            callback_data="tz:custom",
            style="primary",
        )
    ])

    # Add cancel button
    buttons.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="tz:cancel",
            style="danger",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_timezone_display(timezone: str, include_offset: bool = True) -> str:
    """Get human-readable timezone display.

    Args:
        timezone: Timezone string (e.g., "Europe/Moscow" or "UTC+3")
        include_offset: Whether to include UTC offset in display

    Returns:
        Human-readable string (without UTC offset if include_offset=False)
    """
    # Check if it's a named timezone
    for label, tz_value in POPULAR_TIMEZONES:
        if tz_value == timezone:
            if include_offset:
                return label
            else:
                # Remove UTC offset from label: "🇷🇺 Москва (UTC+3)" -> "🇷🇺 Москва"
                if " (UTC" in label:
                    return label.split(" (UTC")[0]
                return label

    # Handle UTC offset format
    if timezone.startswith("UTC"):
        return f"🌍 {timezone}"

    # Fallback
    return f"🌍 {timezone}"
