"""Strong Signal signals handler — period-based filtering."""

from datetime import datetime, timezone, timedelta
from html import escape as html_escape

import pytz
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import (
    get_strong_signals_keyboard,
    BTN_STRONG_WEEK,
    BTN_STRONG_MONTH,
    BTN_STRONG_PREV_MONTH,
)
from services.impulse_client import impulse_client
from services.strong_client import strong_client
from shared.constants import MENU_STRONG_SIGNALS
from shared.utils.timezone import get_pytz_timezone
from states.navigation import MenuState

router = Router()

# Fallback timezone
_default_tz = pytz.timezone("Europe/Moscow")


async def _get_user_tz(user_id: int) -> str:
    """Get user timezone string from settings."""
    try:
        settings = await impulse_client.get_user_settings(user_id)
        return settings.get("timezone", "Europe/Moscow")
    except Exception:
        return "Europe/Moscow"


def _format_time(received_at: str, user_tz_str: str) -> str:
    """Format received_at in user's timezone."""
    try:
        dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        tz = get_pytz_timezone(user_tz_str) if user_tz_str else _default_tz
        dt_local = dt.astimezone(tz)
        return dt_local.strftime("%d.%m %H:%M")
    except Exception:
        return received_at[:16].replace("T", " ")


@router.message(MenuState.strong, F.text == MENU_STRONG_SIGNALS)
async def strong_signals_menu(message: Message, state: FSMContext) -> None:
    """Show Strong Signal period selection."""
    user_tz = await _get_user_tz(message.from_user.id)
    await state.set_state(MenuState.strong_signals)
    await state.update_data(user_timezone=user_tz)
    await message.answer(
        "💪 <b>Strong Signal — Сигналы</b>\n\n"
        "Выберите период:",
        reply_markup=get_strong_signals_keyboard(),
    )


@router.message(MenuState.strong_signals, F.text == BTN_STRONG_WEEK)
async def show_week_signals(message: Message, state: FSMContext) -> None:
    """Show signals for the last 7 days."""
    now = datetime.now(timezone.utc)
    from_date = now - timedelta(days=7)
    data = await state.get_data()
    await _show_signals(message, from_date, now, "за неделю", data.get("user_timezone"))


@router.message(MenuState.strong_signals, F.text == BTN_STRONG_MONTH)
async def show_month_signals(message: Message, state: FSMContext) -> None:
    """Show signals for the current month."""
    now = datetime.now(timezone.utc)
    from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    data = await state.get_data()
    await _show_signals(message, from_date, now, "за месяц", data.get("user_timezone"))


@router.message(MenuState.strong_signals, F.text == BTN_STRONG_PREV_MONTH)
async def show_prev_month_signals(message: Message, state: FSMContext) -> None:
    """Show signals for the previous month."""
    now = datetime.now(timezone.utc)
    first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev_month = first_this_month - timedelta(seconds=1)
    first_prev_month = last_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    data = await state.get_data()
    await _show_signals(message, first_prev_month, first_this_month, "за прошлый месяц", data.get("user_timezone"))


async def _show_signals(
    message: Message,
    from_date: datetime,
    to_date: datetime,
    period_label: str,
    user_tz: str | None = None,
) -> None:
    """Fetch and display signals for a date range."""
    try:
        result = await strong_client.get_signals(
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
            limit=200,
        )
        signals = result.get("signals", [])

        if not signals:
            await message.answer(f"📭 Нет сигналов {period_label}")
            return

        tz_str = user_tz or "Europe/Moscow"
        lines = [f"💪 <b>Strong Signal {period_label}</b> ({len(signals)} шт.)\n"]
        for s in signals:
            symbol = html_escape(s["symbol"])
            d = s["direction"]
            emoji = "🧤" if d == "long" else "🎒"
            dir_label = "Long" if d == "long" else "Short"
            ts = _format_time(s["received_at"], tz_str)
            lines.append(f"{emoji} <b>{symbol}</b> — {dir_label}  <i>{ts}</i>")

        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "\n..."

        await message.answer(text)

    except Exception:
        await message.answer("⚠️ Не удалось загрузить сигналы. Попробуйте позже.")
