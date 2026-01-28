"""Admin services management handlers."""

from aiogram import Router, F
from aiogram.types import Message

from keyboards.reply.admin_menu import (
    get_admin_menu_keyboard,
    get_admin_services_keyboard,
)
from services.service_registry import service_registry
from shared.constants import (
    MENU_SERVICES,
    MENU_SERVICE_STATUS,
    MENU_RESTART_SERVICE,
    MENU_BACK,
)

router = Router()


@router.message(F.text == MENU_SERVICES)
async def services_menu(message: Message, is_admin: bool = False) -> None:
    """Handle services menu button.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await message.answer(
        "🔧 <b>Управление сервисами</b>\n\nВыберите действие:",
        reply_markup=get_admin_services_keyboard(),
    )


@router.message(F.text == MENU_SERVICE_STATUS)
async def check_services_status(message: Message, is_admin: bool = False) -> None:
    """Check status of all services.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    loading_msg = await message.answer("⏳ Проверяю статус сервисов...")

    try:
        health_results = await service_registry.check_all_services_health()
        services = await service_registry.get_active_services()

        lines = ["📊 <b>Статус сервисов</b>\n"]

        for service in services:
            status = health_results.get(service.name, False)
            emoji = "🟢" if status else "🔴"
            lines.append(
                f"{emoji} <b>{service.display_name}</b>\n"
                f"   URL: {service.base_url}"
            )

        if not services:
            lines.append("Нет зарегистрированных сервисов.")

        await loading_msg.edit_text("\n".join(lines))

    except Exception as e:
        await loading_msg.edit_text(f"❌ Ошибка проверки: {str(e)}")


@router.message(F.text == MENU_RESTART_SERVICE)
async def restart_service(message: Message, is_admin: bool = False) -> None:
    """Restart service info.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await message.answer(
        "🔄 <b>Перезапуск сервисов</b>\n\n"
        "Для перезапуска сервиса используйте команду:\n"
        "<code>docker-compose restart [service_name]</code>\n\n"
        "Доступные сервисы:\n"
        "• master_bot\n"
        "• impulse_service\n"
        "• postgres\n"
        "• redis"
    )


@router.message(F.text == MENU_BACK)
async def back_from_admin(message: Message, is_admin: bool = False) -> None:
    """Handle back from admin sections.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await message.answer(
        "👑 <b>Админ-панель</b>",
        reply_markup=get_admin_menu_keyboard(),
    )
