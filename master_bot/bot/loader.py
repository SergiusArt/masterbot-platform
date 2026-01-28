"""Bot and dispatcher initialization."""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings


def setup_bot() -> Bot:
    """Create and configure bot instance."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def setup_dispatcher() -> Dispatcher:
    """Create and configure dispatcher instance."""
    storage = MemoryStorage()
    return Dispatcher(storage=storage)
