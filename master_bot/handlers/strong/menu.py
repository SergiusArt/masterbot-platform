"""Strong Signal section menu handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import get_strong_menu_keyboard
from shared.constants import MENU_STRONG, MENU_BACK, EMOJI_LIGHTNING, EMOJI_MEMO, EMOJI_TOOLBOX, EMOJI_TROPHY, animated
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_STRONG)
async def strong_menu(message: Message, state: FSMContext) -> None:
    """Handle Strong Signal menu button."""
    await state.set_state(MenuState.strong)
    await message.answer(
        f"{animated(EMOJI_LIGHTNING, '⚡')} <b>Раздел: Strong Signal</b>\n\n"
        "Торговые сигналы Long/Short.\n\n"
        f"{animated(EMOJI_MEMO, '📋')} <b>Сигналы</b> — последние сигналы\n"
        f"{animated(EMOJI_TOOLBOX, '⚙️')} <b>Настройки</b> — фильтры уведомлений\n"
        f"{animated(EMOJI_TROPHY, '🏆')} <b>Отработка</b> — аналитика профита\n\n"
        "Выберите действие:",
        reply_markup=get_strong_menu_keyboard(),
    )


@router.message(MenuState.strong_signals, F.text == MENU_BACK)
@router.message(MenuState.strong_settings, F.text == MENU_BACK)
async def back_to_strong_menu(message: Message, state: FSMContext) -> None:
    """Handle back button from Strong sub-menus."""
    await state.set_state(MenuState.strong)
    await message.answer(
        f"{animated(EMOJI_LIGHTNING, '⚡')} <b>Раздел: Strong Signal</b>\n\nВыберите действие:",
        reply_markup=get_strong_menu_keyboard(),
    )
