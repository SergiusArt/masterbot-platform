"""Bablo analytics handlers."""

import logging

from aiogram import Router, F

logger = logging.getLogger(__name__)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import get_bablo_analytics_keyboard
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_ANALYTICS, EMOJI_CHART, EMOJI_MONEY, EMOJI_CHART_UP, EMOJI_STAR, EMOJI_TROPHY, animated
from states.navigation import MenuState

router = Router()


@router.message(MenuState.bablo, F.text == MENU_BABLO_ANALYTICS)
async def bablo_analytics_menu(message: Message, state: FSMContext) -> None:
    """Handle Bablo analytics menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_analytics)
    await message.answer(
        f"{animated(EMOJI_CHART, '📊')} <b>Статистика Bablo</b>\n\n"
        "Выберите период:",
        reply_markup=get_bablo_analytics_keyboard(),
    )


async def _show_analytics(message: Message, period: str) -> None:
    """Show analytics for specified period.

    Args:
        message: Incoming message
        period: Analytics period
    """
    period_labels = {
        "today": "за сегодня",
        "yesterday": "за вчера",
        "week": "за неделю",
        "month": "за месяц",
    }

    try:
        data = await bablo_client.get_analytics(period)

        total = data.get("total_signals", 0)
        long_count = data.get("long_count", 0)
        short_count = data.get("short_count", 0)
        avg_quality = data.get("average_quality")

        lines = [
            f"{animated(EMOJI_MONEY, '💰')} <b>Статистика Bablo {period_labels.get(period, period)}</b>",
            "",
            f"{animated(EMOJI_CHART, '📊')} Всего сигналов: <b>{total}</b>",
            f"🟢 Long: {long_count} | 🔴 Short: {short_count}",
        ]

        # Timeframe breakdown
        by_tf = data.get("by_timeframe", {})
        if by_tf:
            lines.append("")
            lines.append(f"{animated(EMOJI_CHART_UP, '📈')} <b>По таймфреймам:</b>")
            for tf, count in sorted(by_tf.items()):
                lines.append(f"  • {tf}: {count}")

        # Average quality
        if avg_quality:
            lines.append("")
            lines.append(f"{animated(EMOJI_STAR, '⭐')} Средний показатель качества: <b>{avg_quality}</b>")

        # Top symbols
        top_symbols = data.get("top_symbols", [])
        if top_symbols:
            lines.append("")
            lines.append(f"{animated(EMOJI_TROPHY, '🏆')} <b>Топ символы:</b>")
            for item in top_symbols[:5]:
                lines.append(f"  • {item['symbol']}: {item['count']}")

        await message.answer("\n".join(lines))

    except Exception as e:
        logger.error(f"Bablo analytics error for period {period}: {e}")
        await message.answer(
            "❌ Не удалось получить аналитику. Попробуйте позже."
        )


@router.message(F.text == "💰 За сегодня")
async def bablo_analytics_today(message: Message) -> None:
    """Show today's Bablo analytics."""
    await _show_analytics(message, "today")


@router.message(F.text == "💰 За вчера")
async def bablo_analytics_yesterday(message: Message) -> None:
    """Show yesterday's Bablo analytics."""
    await _show_analytics(message, "yesterday")


@router.message(F.text == "💰 За неделю")
async def bablo_analytics_week(message: Message) -> None:
    """Show week's Bablo analytics."""
    await _show_analytics(message, "week")


@router.message(F.text == "💰 За месяц")
async def bablo_analytics_month(message: Message) -> None:
    """Show month's Bablo analytics."""
    await _show_analytics(message, "month")
