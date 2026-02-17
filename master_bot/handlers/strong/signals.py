"""Strong Signal signals handler — period-based filtering."""

from datetime import datetime, timezone, timedelta
from html import escape as html_escape

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import (
    get_strong_signals_keyboard,
    BTN_STRONG_WEEK,
    BTN_STRONG_MONTH,
    BTN_STRONG_PREV_MONTH,
)
from services.strong_client import strong_client
from shared.constants import MENU_STRONG_SIGNALS, EMOJI_HOME
from states.navigation import MenuState

router = Router()


@router.message(MenuState.strong, F.text == MENU_STRONG_SIGNALS)
async def strong_signals_menu(message: Message, state: FSMContext) -> None:
    """Show Strong Signal period selection."""
    await state.set_state(MenuState.strong_signals)
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
    await _show_signals(message, from_date, now, "за неделю")


@router.message(MenuState.strong_signals, F.text == BTN_STRONG_MONTH)
async def show_month_signals(message: Message, state: FSMContext) -> None:
    """Show signals for the current month."""
    now = datetime.now(timezone.utc)
    from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_signals(message, from_date, now, "за месяц")


@router.message(MenuState.strong_signals, F.text == BTN_STRONG_PREV_MONTH)
async def show_prev_month_signals(message: Message, state: FSMContext) -> None:
    """Show signals for the previous month."""
    now = datetime.now(timezone.utc)
    first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev_month = first_this_month - timedelta(seconds=1)
    first_prev_month = last_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_signals(message, first_prev_month, first_this_month, "за прошлый месяц")


async def _show_signals(
    message: Message,
    from_date: datetime,
    to_date: datetime,
    period_label: str,
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

        lines = [f"💪 <b>Strong Signal {period_label}</b> ({len(signals)} шт.)\n"]
        for s in signals:
            symbol = html_escape(s["symbol"])
            d = s["direction"]
            emoji = "🧤" if d == "long" else "🎒"
            dir_label = "Long" if d == "long" else "Short"
            ts = s["received_at"][:16].replace("T", " ")
            lines.append(f"{emoji} <b>{symbol}</b> — {dir_label}  <i>{ts} UTC</i>")

        text = "\n".join(lines)
        # Telegram message limit is 4096 chars
        if len(text) > 4000:
            text = text[:4000] + "\n..."

        await message.answer(text)

    except Exception:
        await message.answer("⚠️ Не удалось загрузить сигналы. Попробуйте позже.")
