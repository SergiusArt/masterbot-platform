"""Bablo inline keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_signals_pagination_keyboard(
    current_page: int,
    has_prev: bool,
    has_next: bool,
) -> InlineKeyboardMarkup:
    """Build pagination keyboard for signals list."""
    buttons = []
    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"bablo:signals:page:{current_page - 1}",
                style="primary",
            )
        )
    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}",
            callback_data="noop",
        )
    )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text="Вперёд →",
                callback_data=f"bablo:signals:page:{current_page + 1}",
                style="primary",
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_quality_keyboard(current: int = 7) -> InlineKeyboardMarkup:
    """Build quality threshold selection keyboard.

    Args:
        current: Current quality threshold

    Returns:
        Quality selection inline keyboard
    """
    buttons = []
    for value in [7, 8, 9]:
        label = f"✓ {value}/10" if value == current else f"{value}/10"
        buttons.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"bablo:quality:{value}",
                style="success" if value == current else None,
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,  # All 3 buttons in one row
        ]
    )
