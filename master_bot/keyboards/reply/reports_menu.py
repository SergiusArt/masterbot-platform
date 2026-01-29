"""Unified reports menu keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import MENU_MAIN, MENU_BACK


def get_reports_menu_keyboard(
    impulse_enabled: bool = True,
    bablo_enabled: bool = True,
    morning: bool = True,
    evening: bool = True,
    weekly: bool = True,
    monthly: bool = True,
) -> ReplyKeyboardMarkup:
    """Build unified reports settings keyboard.

    Args:
        impulse_enabled: Whether impulse reports are enabled
        bablo_enabled: Whether bablo reports are enabled
        morning: Morning report enabled
        evening: Evening report enabled
        weekly: Weekly report enabled
        monthly: Monthly report enabled

    Returns:
        Reports menu keyboard
    """

    def checkbox(enabled: bool) -> str:
        """Get checkbox symbol.

        Args:
            enabled: Whether checkbox is checked

        Returns:
            Checkbox symbol
        """
        return "☑️" if enabled else "⬜"

    def toggle(enabled: bool) -> str:
        """Get toggle status.

        Args:
            enabled: Whether toggle is on

        Returns:
            Toggle status
        """
        return "ВКЛ" if enabled else "ВЫКЛ"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{checkbox(impulse_enabled)} Импульсы"),
                KeyboardButton(text=f"{checkbox(bablo_enabled)} Bablo"),
            ],
            [
                KeyboardButton(text=f"🌅 Утренний: {toggle(morning)}"),
                KeyboardButton(text=f"🌆 Вечерний: {toggle(evening)}"),
            ],
            [
                KeyboardButton(text=f"📊 Недельный: {toggle(weekly)}"),
                KeyboardButton(text=f"📊 Месячный: {toggle(monthly)}"),
            ],
            [
                KeyboardButton(text=MENU_BACK),
                KeyboardButton(text=MENU_MAIN),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
