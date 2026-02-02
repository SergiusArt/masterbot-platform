"""Impulse analytics handlers."""

import logging

from aiogram import Router, F

logger = logging.getLogger(__name__)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.impulse_menu import (
    get_analytics_menu_keyboard,
    get_impulse_menu_keyboard,
)
from services.impulse_client import impulse_client
from shared.constants import (
    MENU_ANALYTICS,
    MENU_BACK,
    MENU_TODAY,
    MENU_YESTERDAY,
    MENU_WEEK,
    MENU_MONTH,
)
from states.navigation import MenuState
from utils.formatters import format_analytics

router = Router()


@router.message(MenuState.impulse, F.text == MENU_ANALYTICS)
async def analytics_menu(message: Message, state: FSMContext) -> None:
    """Handle analytics menu button.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.impulse_analytics)
    await message.answer(
        "📈 <b>Аналитика</b>\n\nВыберите период:",
        reply_markup=get_analytics_menu_keyboard(),
    )


@router.message(F.text == MENU_TODAY)
async def analytics_today(message: Message) -> None:
    """Handle today analytics request.

    Args:
        message: Incoming message
    """
    await _send_analytics(message, "today", "сегодня")


@router.message(F.text == MENU_YESTERDAY)
async def analytics_yesterday(message: Message) -> None:
    """Handle yesterday analytics request.

    Args:
        message: Incoming message
    """
    await _send_analytics(message, "yesterday", "вчера")


@router.message(F.text == MENU_WEEK)
async def analytics_week(message: Message) -> None:
    """Handle week analytics request.

    Args:
        message: Incoming message
    """
    await _send_analytics(message, "week", "неделю")


@router.message(F.text == MENU_MONTH)
async def analytics_month(message: Message) -> None:
    """Handle month analytics request.

    Args:
        message: Incoming message
    """
    await _send_analytics(message, "month", "месяц")


async def _send_analytics(message: Message, period: str, period_name: str) -> None:
    """Fetch and send analytics.

    Args:
        message: Incoming message
        period: Period identifier
        period_name: Human-readable period name
    """
    try:
        # Show loading message
        loading_msg = await message.answer(f"⏳ Загружаю аналитику за {period_name}...")

        # Fetch analytics
        data = await impulse_client.get_analytics(period)

        # Format and send
        text = format_analytics(data)
        await loading_msg.edit_text(text)

    except Exception as e:
        logger.error(f"Impulse analytics error for period {period}: {e}")
        await message.answer(
            "❌ Не удалось получить аналитику. Попробуйте позже."
        )


@router.message(MenuState.impulse_analytics, F.text == MENU_BACK)
async def back_from_analytics(message: Message, state: FSMContext) -> None:
    """Handle back from impulse analytics menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.impulse)
    await message.answer(
        "📊 <b>Раздел: Импульсы</b>\n\nВыберите действие:",
        reply_markup=get_impulse_menu_keyboard(),
    )
