"""Unified reports menu keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import MENU_MAIN, MENU_BACK, EMOJI_HOME


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
        return "☑️" if enabled else "⬜"

    def toggle(enabled: bool) -> str:
        return "ВКЛ" if enabled else "ВЫКЛ"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"{checkbox(impulse_enabled)} Импульсы",
                    style="success" if impulse_enabled else None,
                ),
                KeyboardButton(
                    text=f"{checkbox(bablo_enabled)} Bablo",
                    style="success" if bablo_enabled else None,
                ),
            ],
            [
                KeyboardButton(
                    text=f"🌅 Утренний: {toggle(morning)}",
                    style="success" if morning else "danger",
                ),
                KeyboardButton(
                    text=f"🌆 Вечерний: {toggle(evening)}",
                    style="success" if evening else "danger",
                ),
            ],
            [
                KeyboardButton(
                    text=f"📊 Недельный: {toggle(weekly)}",
                    style="success" if weekly else "danger",
                ),
                KeyboardButton(
                    text=f"📊 Месячный: {toggle(monthly)}",
                    style="success" if monthly else "danger",
                ),
            ],
            [
                KeyboardButton(text=MENU_BACK),
                KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
