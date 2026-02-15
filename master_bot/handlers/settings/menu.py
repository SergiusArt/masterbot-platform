"""General settings handlers."""

import logging

from aiogram import Router, F

logger = logging.getLogger(__name__)
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards.reply.main_menu import get_main_menu_keyboard
from keyboards.inline.timezone import get_timezone_keyboard, get_timezone_display
from services.impulse_client import impulse_client
from services.error_reporter import report_error
from shared.constants import MENU_SETTINGS, MENU_BACK, MENU_MAIN, EMOJI_HOME, EMOJI_GLOBE, EMOJI_TOOLBOX, animated
from shared.utils.timezone import validate_timezone_input, get_utc_offset_display
from states.navigation import MenuState

router = Router()


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """Build settings menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Часовой пояс", style="primary", icon_custom_emoji_id=EMOJI_GLOBE)],
            # [KeyboardButton(text="🌐 Язык")],  # TODO: Enable when i18n is ready
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_language_keyboard(current_lang: str = "ru") -> InlineKeyboardMarkup:
    """Build language selection keyboard."""
    buttons = [
        [InlineKeyboardButton(
            text="✓ 🇷🇺 Русский" if current_lang == "ru" else "🇷🇺 Русский",
            callback_data="lang:set:ru"
        )],
        [InlineKeyboardButton(
            text="✓ 🇬🇧 English" if current_lang == "en" else "🇬🇧 English",
            callback_data="lang:set:en"
        )],
        [InlineKeyboardButton(
            text="❌ Отмена" if current_lang == "ru" else "❌ Cancel",
            callback_data="lang:cancel"
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == MENU_SETTINGS)
async def settings_menu(message: Message, state: FSMContext) -> None:
    """Handle settings menu button."""
    await state.set_state(MenuState.settings)
    await message.answer(
        f"{animated(EMOJI_TOOLBOX, '⚙️')} <b>Настройки</b>\n\nВыберите раздел:",
        reply_markup=get_settings_keyboard(),
    )


@router.message(MenuState.settings, F.text == "Часовой пояс")
async def timezone_settings(message: Message, state: FSMContext) -> None:
    """Handle timezone settings."""
    user_id = message.from_user.id

    # Get current timezone from impulse service
    try:
        settings_data = await impulse_client.get_user_settings(user_id)
        current_tz = settings_data.get("timezone", "Europe/Moscow")
    except Exception:
        current_tz = "Europe/Moscow"

    tz_display = get_timezone_display(current_tz, include_offset=False)
    utc_offset = get_utc_offset_display(current_tz)

    await state.set_state(MenuState.settings_timezone)
    await message.answer(
        f"{animated(EMOJI_GLOBE, '🌍')} <b>Часовой пояс</b>\n\n"
        f"Текущий часовой пояс: <b>{tz_display}</b> ({utc_offset})\n\n"
        "Выберите новый часовой пояс или введите вручную:",
        reply_markup=get_timezone_keyboard(current_tz),
    )


@router.callback_query(F.data.startswith("tz:set:"))
async def set_timezone(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle timezone selection from predefined list."""
    user_id = callback.from_user.id
    new_tz = callback.data.split(":", 2)[2]  # e.g., "Europe/Moscow"

    # Update timezone in impulse service
    try:
        await impulse_client.update_user_settings(user_id, {"timezone": new_tz})
        tz_display = get_timezone_display(new_tz, include_offset=False)
        utc_offset = get_utc_offset_display(new_tz)

        await callback.message.edit_text(
            f"✅ Часовой пояс изменён на <b>{tz_display}</b> ({utc_offset})\n\n"
            "Теперь все отчёты и время сигналов будут отображаться "
            "в вашем часовом поясе."
        )
    except Exception as e:
        logger.error(f"Timezone save error for user {user_id}: {e}")
        await report_error(e, user_id=user_id, context="timezone_save")
        await callback.message.edit_text(
            "❌ Не удалось сохранить часовой пояс. Попробуйте позже."
        )

    await state.set_state(MenuState.settings)
    await callback.answer()


@router.callback_query(F.data == "tz:custom")
async def request_custom_timezone(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle custom timezone input request."""
    await state.set_state(MenuState.settings_timezone_custom)
    await callback.message.edit_text(
        "⌨️ <b>Ввод часового пояса вручную</b>\n\n"
        "Введите ваш часовой пояс относительно UTC.\n\n"
        "<b>Формат:</b> число от -12 до +14\n\n"
        "<b>Примеры:</b>\n"
        "• <code>+3</code> — Москва (UTC+3)\n"
        "• <code>-5</code> — Нью-Йорк (UTC-5)\n"
        "• <code>0</code> — Лондон (UTC+0)\n"
        "• <code>+5</code> — Екатеринбург (UTC+5)\n\n"
        "Отправьте число со знаком + или - (или без знака для положительных):"
    )
    await callback.answer()


@router.message(MenuState.settings_timezone_custom)
async def process_custom_timezone(message: Message, state: FSMContext) -> None:
    """Process custom timezone input."""
    user_id = message.from_user.id
    user_input = message.text.strip()

    # Handle back/cancel
    if user_input == MENU_BACK:
        await state.set_state(MenuState.settings)
        await message.answer(
            f"{animated(EMOJI_TOOLBOX, '⚙️')} <b>Настройки</b>\n\nВыберите раздел:",
            reply_markup=get_settings_keyboard(),
        )
        return

    # Validate input
    is_valid, normalized_tz, error_msg = validate_timezone_input(user_input)

    if not is_valid:
        await message.answer(
            f"❌ {error_msg}\n\n"
            "Попробуйте ещё раз или нажмите «Назад» для отмены."
        )
        return

    # Update timezone in impulse service
    try:
        await impulse_client.update_user_settings(user_id, {"timezone": normalized_tz})

        await message.answer(
            f"✅ Часовой пояс изменён на <b>{normalized_tz}</b>\n\n"
            "Теперь все отчёты и время сигналов будут отображаться "
            "в вашем часовом поясе.",
            reply_markup=get_settings_keyboard(),
        )
    except Exception as e:
        logger.error(f"Custom timezone save error for user {user_id}: {e}")
        await report_error(e, user_id=user_id, context="custom_timezone_save")
        await message.answer(
            "❌ Не удалось сохранить часовой пояс. Попробуйте позже.",
            reply_markup=get_settings_keyboard(),
        )

    await state.set_state(MenuState.settings)


@router.callback_query(F.data == "tz:cancel")
async def cancel_timezone_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle timezone selection cancellation."""
    await callback.message.edit_text(
        "🌍 Выбор часового пояса отменён."
    )
    await state.set_state(MenuState.settings)
    await callback.answer()


@router.message(MenuState.settings, F.text == "🌐 Язык")
async def language_settings(message: Message, state: FSMContext) -> None:
    """Handle language settings."""
    user_id = message.from_user.id

    # Get current language from impulse service
    try:
        settings_data = await impulse_client.get_user_settings(user_id)
        current_lang = settings_data.get("language", "ru")
    except Exception:
        current_lang = "ru"

    await state.set_state(MenuState.settings_language)

    if current_lang == "en":
        await message.answer(
            "🌐 <b>Language</b>\n\n"
            "Current language: <b>English</b>\n\n"
            "Select language:",
            reply_markup=get_language_keyboard(current_lang),
        )
    else:
        await message.answer(
            "🌐 <b>Язык</b>\n\n"
            "Текущий язык: <b>Русский</b>\n\n"
            "Выберите язык:",
            reply_markup=get_language_keyboard(current_lang),
        )


@router.callback_query(F.data.startswith("lang:set:"))
async def set_language(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection."""
    user_id = callback.from_user.id
    new_lang = callback.data.split(":")[-1]  # "ru" or "en"

    # Update language in impulse service
    try:
        await impulse_client.update_user_settings(user_id, {"language": new_lang})

        if new_lang == "en":
            await callback.message.edit_text(
                "✅ Language changed to <b>English</b>\n\n"
                "All messages will now be displayed in English."
            )
        else:
            await callback.message.edit_text(
                "✅ Язык изменён на <b>Русский</b>\n\n"
                "Все сообщения теперь будут отображаться на русском языке."
            )
    except Exception as e:
        logger.error(f"Language save error for user {user_id}: {e}")
        await report_error(e, user_id=user_id, context="language_save")
        await callback.message.edit_text(
            "❌ Failed to save. Try again later." if new_lang == "en"
            else "❌ Не удалось сохранить. Попробуйте позже."
        )

    await state.set_state(MenuState.settings)
    await callback.answer()


@router.callback_query(F.data == "lang:cancel")
async def cancel_language_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection cancellation."""
    await callback.message.edit_text(
        "🌐 Выбор языка отменён."
    )
    await state.set_state(MenuState.settings)
    await callback.answer()


# Back button handlers for all settings states
@router.message(MenuState.settings, F.text == MENU_BACK)
@router.message(MenuState.settings_timezone, F.text == MENU_BACK)
@router.message(MenuState.settings_language, F.text == MENU_BACK)
async def back_from_settings(message: Message, state: FSMContext) -> None:
    """Handle back button from settings menu."""
    await state.set_state(MenuState.main)
    await message.answer(
        "📱 <b>Главное меню</b>",
        reply_markup=get_main_menu_keyboard(),
    )
