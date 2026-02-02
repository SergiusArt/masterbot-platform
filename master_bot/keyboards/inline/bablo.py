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
        style = "✓ " if value == current else ""
        buttons.append(
            InlineKeyboardButton(
                text=f"{style}{value}/10",
                callback_data=f"bablo:quality:{value}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,  # All 3 buttons in one row
        ]
    )
