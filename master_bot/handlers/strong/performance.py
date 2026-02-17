"""Strong Signal performance analytics handler."""

from datetime import datetime, timezone, timedelta
from html import escape as html_escape

import pytz
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import (
    get_strong_menu_keyboard,
    get_strong_performance_keyboard,
    BTN_PERF_CURRENT_MONTH,
    BTN_PERF_PREV_MONTH,
)
from services.impulse_client import impulse_client
from services.strong_client import strong_client
from shared.constants import (
    MENU_STRONG_PERFORMANCE,
    MENU_BACK,
    EMOJI_TROPHY,
    EMOJI_LIGHTNING,
    animated,
)
from shared.utils.timezone import get_pytz_timezone
from states.navigation import MenuState

router = Router()

_default_tz = pytz.timezone("Europe/Moscow")

# Month names in Russian
_MONTH_NAMES = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}


async def _get_user_tz(user_id: int) -> str:
    """Get user timezone string from settings."""
    try:
        settings = await impulse_client.get_user_settings(user_id)
        return settings.get("timezone", "Europe/Moscow")
    except Exception:
        return "Europe/Moscow"


def _format_time(received_at: str, user_tz_str: str) -> str:
    """Format received_at in user's timezone (DD.MM.YY HH:MM)."""
    try:
        dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        tz = get_pytz_timezone(user_tz_str) if user_tz_str else _default_tz
        return dt.astimezone(tz).strftime("%d.%m.%y %H:%M")
    except Exception:
        return received_at[:16].replace("T", " ")


@router.message(MenuState.strong, F.text == MENU_STRONG_PERFORMANCE)
async def strong_performance_menu(message: Message, state: FSMContext) -> None:
    """Show Strong Signal performance period selection."""
    user_tz = await _get_user_tz(message.from_user.id)
    await state.set_state(MenuState.strong_performance)
    await state.update_data(user_timezone=user_tz)
    await message.answer(
        f"{animated(EMOJI_TROPHY, '🏆')} <b>Отработка Strong Signal</b>\n\n"
        "Максимальное отклонение цены в сторону профита\n"
        "за 100 баров (30-мин TF) от момента сигнала.\n\n"
        "Выберите период:",
        reply_markup=get_strong_performance_keyboard(),
    )


@router.message(MenuState.strong_performance, F.text == BTN_PERF_CURRENT_MONTH)
async def show_current_month(message: Message, state: FSMContext) -> None:
    """Show performance for the current month."""
    now = datetime.now(timezone.utc)
    from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_name = _MONTH_NAMES[now.month]
    label = f"{month_name} {now.year}"
    data = await state.get_data()
    await _show_performance(message, from_date, now, label, data.get("user_timezone"))


@router.message(MenuState.strong_performance, F.text == BTN_PERF_PREV_MONTH)
async def show_prev_month(message: Message, state: FSMContext) -> None:
    """Show performance for the previous month."""
    now = datetime.now(timezone.utc)
    first_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev = first_this - timedelta(seconds=1)
    first_prev = last_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_name = _MONTH_NAMES[last_prev.month]
    label = f"{month_name} {last_prev.year}"
    data = await state.get_data()
    await _show_performance(message, first_prev, first_this, label, data.get("user_timezone"))


@router.message(MenuState.strong_performance, F.text == MENU_BACK)
async def back_to_strong(message: Message, state: FSMContext) -> None:
    """Back to Strong Signal menu."""
    await state.set_state(MenuState.strong)
    await message.answer(
        f"{animated(EMOJI_LIGHTNING, '⚡')} <b>Раздел: Strong Signal</b>\n\nВыберите действие:",
        reply_markup=get_strong_menu_keyboard(),
    )


async def _show_performance(
    message: Message,
    from_date: datetime,
    to_date: datetime,
    period_label: str,
    user_tz: str | None = None,
) -> None:
    """Fetch and display performance report for a date range."""
    loading = await message.answer("⏳ Загружаю данные...")

    try:
        from_iso = from_date.isoformat()
        to_iso = to_date.isoformat()

        stats = await strong_client.get_performance_stats(
            from_date=from_iso, to_date=to_iso,
        )
        result = await strong_client.get_performance_signals(
            from_date=from_iso, to_date=to_iso, limit=50,
        )
        signals = result.get("signals", [])

        long = stats.get("by_direction", {}).get("long", {})
        short = stats.get("by_direction", {}).get("short", {})
        tz_str = user_tz or "Europe/Moscow"

        lines = [
            f"{animated(EMOJI_TROPHY, '🏆')} <b>Отработка Strong Signal — {period_label}</b>\n",
            f"📌 Всего сигналов: <b>{stats['total']}</b>",
            f"✅ Рассчитано: <b>{stats['calculated']}</b>",
            f"⏳ Ожидают (&lt; 50 ч): <b>{stats['pending']}</b>\n",
        ]

        if stats["calculated"] > 0:
            lines.extend([
                f"📈 Средний макс. профит: <b>{stats['avg_profit_pct']}%</b>",
                f"🟢 Лучший: <b>+{stats['max_profit_pct']}%</b>",
                f"🔴 Худший: <b>+{stats['min_profit_pct']}%</b>\n",
            ])

        if long.get("count", 0) > 0:
            lines.append(
                f"🧤 <b>Long</b> ({long['count']} шт.) — средн. {long['avg_profit_pct']}%"
            )

        if short.get("count", 0) > 0:
            lines.append(
                f"🎒 <b>Short</b> ({short['count']} шт.) — средн. {short['avg_profit_pct']}%"
            )

        if signals:
            lines.append("")
            for s in signals:
                emoji = "🧤" if s["direction"] == "long" else "🎒"
                pct = s["max_profit_pct"]
                pct_str = f"+{pct:.2f}%" if pct >= 0 else f"{pct:.2f}%"
                ts = _format_time(s["received_at"], tz_str)
                lines.append(f"{emoji} <b>{html_escape(s['symbol'])}</b> | {pct_str} | {ts}")

        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "\n..."

        await loading.edit_text(text)

    except Exception as e:
        await loading.edit_text(f"❌ Ошибка: {html_escape(str(e))}")
