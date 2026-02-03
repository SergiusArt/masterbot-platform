"""Unified reports menu handlers."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.reports_menu import get_reports_menu_keyboard
from keyboards.reply.main_menu import get_main_menu_keyboard
from services.impulse_client import impulse_client
from services.bablo_client import bablo_client
from shared.constants import MENU_REPORTS, MENU_BACK, MENU_MAIN
from states.navigation import MenuState

router = Router()


REPORTS_HELP = """📋 <b>Отчёты</b>

Управление отчётами от всех сервисов в одном месте.

<b>Выберите сервисы:</b>
- Нажмите на кнопку сервиса для включения/выключения

<b>Настройте типы отчётов:</b>
🌅 <b>Утренний</b> — 08:00 (итоги за прошлый день)
🌆 <b>Вечерний</b> — 20:00 (итоги за текущий день)
📊 <b>Недельный</b> — понедельник 09:00 (пн-вс прошлой недели)
📊 <b>Месячный</b> — 1-е число месяца 09:00 (прошлый месяц)

<i>Изменения применяются ко всем включённым сервисам</i>"""


@router.message(F.text == MENU_REPORTS)
async def reports_menu(message: Message, state: FSMContext) -> None:
    """Handle reports menu button.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.reports)
    user_id = message.from_user.id

    # Get settings from both services
    impulse_enabled = True
    bablo_enabled = True
    morning = True
    evening = True
    weekly = True
    monthly = True

    try:
        impulse_settings = await impulse_client.get_user_settings(user_id)
        morning = impulse_settings.get("morning_report", True)
        evening = impulse_settings.get("evening_report", True)
        weekly = impulse_settings.get("weekly_report", True)
        monthly = impulse_settings.get("monthly_report", True)
    except Exception:
        pass

    # Store current state
    await state.update_data(
        impulse_enabled=impulse_enabled,
        bablo_enabled=bablo_enabled,
        morning=morning,
        evening=evening,
        weekly=weekly,
        monthly=monthly,
    )

    await message.answer(
        REPORTS_HELP,
        reply_markup=get_reports_menu_keyboard(
            impulse_enabled=impulse_enabled,
            bablo_enabled=bablo_enabled,
            morning=morning,
            evening=evening,
            weekly=weekly,
            monthly=monthly,
        ),
    )


@router.message(MenuState.reports, F.text.endswith(" Импульсы"))
async def toggle_impulse_service(message: Message, state: FSMContext) -> None:
    """Toggle impulse service for reports.

    Args:
        message: Incoming message
        state: FSM context
    """
    data = await state.get_data()
    impulse_enabled = not data.get("impulse_enabled", True)
    await state.update_data(impulse_enabled=impulse_enabled)

    status = "включены ✅" if impulse_enabled else "выключены ❌"
    await message.answer(f"📊 Отчёты от Импульсов {status}")

    # Refresh menu
    data = await state.get_data()
    await message.answer(
        "Настройка отчётов:",
        reply_markup=get_reports_menu_keyboard(
            impulse_enabled=data.get("impulse_enabled", True),
            bablo_enabled=data.get("bablo_enabled", True),
            morning=data.get("morning", True),
            evening=data.get("evening", True),
            weekly=data.get("weekly", True),
            monthly=data.get("monthly", True),
        ),
    )


@router.message(MenuState.reports, F.text.endswith(" Bablo"))
async def toggle_bablo_service(message: Message, state: FSMContext) -> None:
    """Toggle bablo service for reports.

    Args:
        message: Incoming message
        state: FSM context
    """
    data = await state.get_data()
    bablo_enabled = not data.get("bablo_enabled", True)
    await state.update_data(bablo_enabled=bablo_enabled)

    status = "включены ✅" if bablo_enabled else "выключены ❌"
    await message.answer(f"💰 Отчёты от Bablo {status}")

    # Refresh menu
    data = await state.get_data()
    await message.answer(
        "Настройка отчётов:",
        reply_markup=get_reports_menu_keyboard(
            impulse_enabled=data.get("impulse_enabled", True),
            bablo_enabled=data.get("bablo_enabled", True),
            morning=data.get("morning", True),
            evening=data.get("evening", True),
            weekly=data.get("weekly", True),
            monthly=data.get("monthly", True),
        ),
    )


@router.message(MenuState.reports, F.text.contains("Утренний:"))
async def toggle_morning_report(message: Message, state: FSMContext) -> None:
    """Toggle morning report for all enabled services.

    Args:
        message: Incoming message
        state: FSM context
    """
    await _toggle_report_type(message, state, "morning", "Утренний отчёт", "morning_report")


@router.message(MenuState.reports, F.text.contains("Вечерний:"))
async def toggle_evening_report(message: Message, state: FSMContext) -> None:
    """Toggle evening report for all enabled services.

    Args:
        message: Incoming message
        state: FSM context
    """
    await _toggle_report_type(message, state, "evening", "Вечерний отчёт", "evening_report")


@router.message(MenuState.reports, F.text.contains("Недельный:"))
async def toggle_weekly_report(message: Message, state: FSMContext) -> None:
    """Toggle weekly report for all enabled services.

    Args:
        message: Incoming message
        state: FSM context
    """
    await _toggle_report_type(message, state, "weekly", "Недельный отчёт", "weekly_report")


@router.message(MenuState.reports, F.text.contains("Месячный:"))
async def toggle_monthly_report(message: Message, state: FSMContext) -> None:
    """Toggle monthly report for all enabled services.

    Args:
        message: Incoming message
        state: FSM context
    """
    await _toggle_report_type(message, state, "monthly", "Месячный отчёт", "monthly_report")


async def _toggle_report_type(
    message: Message,
    state: FSMContext,
    state_key: str,
    name: str,
    api_key: str,
) -> None:
    """Toggle report type for all enabled services.

    Args:
        message: Incoming message
        state: FSM context
        state_key: State data key
        name: Human-readable name
        api_key: API setting key
    """
    user_id = message.from_user.id
    data = await state.get_data()

    # Toggle value
    current_value = data.get(state_key, True)
    new_value = not current_value
    await state.update_data(**{state_key: new_value})

    impulse_enabled = data.get("impulse_enabled", True)
    bablo_enabled = data.get("bablo_enabled", True)

    # Update settings in enabled services
    errors = []

    if impulse_enabled:
        try:
            await impulse_client.update_user_settings(user_id, {api_key: new_value})
        except Exception as e:
            errors.append(f"Импульсы: {str(e)}")

    if bablo_enabled:
        try:
            await bablo_client.update_user_settings(user_id, {api_key: new_value})
        except Exception as e:
            errors.append(f"Bablo: {str(e)}")

    # Show result
    if errors:
        await message.answer(f"⚠️ Ошибки при обновлении:\n" + "\n".join(errors))
    else:
        status = "включён ✅" if new_value else "выключен ❌"
        services = []
        if impulse_enabled:
            services.append("Импульсы")
        if bablo_enabled:
            services.append("Bablo")
        services_text = ", ".join(services) if services else "нет включённых сервисов"
        await message.answer(f"📋 {name} {status}\nСервисы: {services_text}")

    # Refresh menu
    data = await state.get_data()
    await message.answer(
        "Настройка отчётов:",
        reply_markup=get_reports_menu_keyboard(
            impulse_enabled=data.get("impulse_enabled", True),
            bablo_enabled=data.get("bablo_enabled", True),
            morning=data.get("morning", True),
            evening=data.get("evening", True),
            weekly=data.get("weekly", True),
            monthly=data.get("monthly", True),
        ),
    )


@router.message(MenuState.reports, F.text == MENU_BACK)
async def back_from_reports(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Handle back button from reports menu.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin (injected by middleware)
    """
    await state.set_state(MenuState.main)

    await message.answer(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin),
    )


@router.message(MenuState.reports, F.text == MENU_MAIN)
async def main_from_reports(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Handle main menu button from reports menu.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin (injected by middleware)
    """
    await state.set_state(MenuState.main)

    await message.answer(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_menu_keyboard(is_admin=is_admin),
    )
