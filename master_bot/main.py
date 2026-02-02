"""Master Bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import settings
from bot.loader import setup_bot, setup_dispatcher
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from handlers import start, navigation
from handlers.impulse import menu as impulse_menu
from handlers.impulse import analytics as impulse_analytics
from handlers.impulse import reports as impulse_reports
from handlers.impulse import notifications as impulse_notifications
from handlers.impulse import activity as impulse_activity
from handlers.admin import menu as admin_menu
from handlers.admin import users as admin_users
from handlers.admin import services as admin_services
from handlers.settings import menu as settings_menu
from handlers.bablo import menu as bablo_menu
from handlers.bablo import analytics as bablo_analytics
from handlers.bablo import settings as bablo_settings
from handlers.bablo import signals as bablo_signals
from handlers.bablo import activity as bablo_activity
from handlers.reports import menu as reports_menu
from services.notification_listener import NotificationListener
from services.scheduler import init_scheduler
from shared.database.connection import init_db, close_db
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import setup_logger

logger = setup_logger("master_bot")


async def on_startup(bot: Bot) -> None:
    """Actions on bot startup."""
    logger.info("Initializing database...")
    await init_db()

    logger.info("Connecting to Redis...")
    await get_redis_client()

    # Notify admin about bot startup
    try:
        await bot.send_message(
            settings.ADMIN_ID,
            "🤖 <b>MasterBot запущен</b>\n\nВсе системы работают нормально.",
        )
    except Exception as e:
        logger.warning(f"Failed to notify admin: {e}")

    logger.info("Bot started successfully!")


async def on_shutdown(bot: Bot) -> None:
    """Actions on bot shutdown."""
    logger.info("Shutting down...")

    # Notify admin about bot shutdown
    try:
        await bot.send_message(
            settings.ADMIN_ID,
            "🤖 <b>MasterBot остановлен</b>",
        )
    except Exception:
        pass

    await close_db()
    logger.info("Bot stopped.")


def register_routers(dp: Dispatcher) -> None:
    """Register all routers."""
    # Main handlers
    dp.include_router(start.router)
    dp.include_router(navigation.router)

    # Reports handlers (unified reports menu)
    dp.include_router(reports_menu.router)

    # Bablo handlers (registered before Impulse for proper back button handling)
    dp.include_router(bablo_menu.router)
    dp.include_router(bablo_analytics.router)
    dp.include_router(bablo_settings.router)
    dp.include_router(bablo_signals.router)
    dp.include_router(bablo_activity.router)

    # Impulse handlers
    dp.include_router(impulse_menu.router)
    dp.include_router(impulse_analytics.router)
    dp.include_router(impulse_reports.router)
    dp.include_router(impulse_notifications.router)
    dp.include_router(impulse_activity.router)

    # Admin handlers
    dp.include_router(admin_menu.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_services.router)

    # Settings handlers
    dp.include_router(settings_menu.router)


async def main() -> None:
    """Main function."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create bot instance
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Create dispatcher
    dp = Dispatcher()

    # Setup middlewares
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register routers
    register_routers(dp)

    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start notification listener
    notification_listener = NotificationListener(bot)
    listener_task = asyncio.create_task(notification_listener.start())

    # Start report scheduler
    scheduler = init_scheduler(bot)
    scheduler.start()

    # Start polling
    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Stop scheduler and listener on shutdown
        scheduler.stop()
        await notification_listener.stop()
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
