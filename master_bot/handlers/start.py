"""Start command and main menu handlers."""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards.reply.main_menu import get_main_menu_keyboard
from services.topic_manager import get_topic_manager
from shared.constants import EMOJI_HOME, EMOJI_CHART, EMOJI_TOOLBOX, EMOJI_CROWN, animated
from shared.utils.logger import get_logger

router = Router()
logger = get_logger("start_handler")


@router.message(CommandStart())
async def cmd_start(message: Message, is_admin: bool = False) -> None:
    """Handle /start command.

    Creates private chat topics on first interaction.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    user = message.from_user
    name = user.first_name or user.username or "пользователь"

    # Create forum topics in private chat (Bot API 9.4)
    tm = get_topic_manager()
    if tm:
        try:
            topics = await tm.ensure_topics(user.id)
            if topics:
                logger.info(f"Topics ready for user {user.id}: {list(topics.keys())}")
        except Exception as e:
            logger.error(f"Failed to create topics for user {user.id}: {e}")

    await message.answer(
        f"👋 <b>Добро пожаловать, {name}!</b>\n\n"
        f"Это <b>MasterBot</b> — единая платформа для управления сервисами.\n\n"
        f"Выберите раздел в меню ниже:",
        reply_markup=get_main_menu_keyboard(is_admin),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command.

    Args:
        message: Incoming message
    """
    await message.answer(
        "📚 <b>Справка по MasterBot</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start — Начать работу с ботом\n"
        "/help — Показать справку\n"
        "/menu — Вернуться в главное меню\n\n"
        "<b>Разделы:</b>\n"
        f"{animated(EMOJI_CHART, '📊')} <b>Импульсы</b> — Аналитика и уведомления по криптовалютам\n"
        f"{animated(EMOJI_TOOLBOX, '⚙️')} <b>Настройки</b> — Настройки профиля\n"
        f"{animated(EMOJI_CROWN, '👑')} <b>Админ-панель</b> — Управление пользователями (только для админов)\n\n"
        "По всем вопросам обращайтесь к администратору."
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, is_admin: bool = False) -> None:
    """Handle /menu command.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    await message.answer(
        f"{animated(EMOJI_HOME, '🏠')} <b>Главное меню</b>\n\nВыберите раздел:",
        reply_markup=get_main_menu_keyboard(is_admin),
    )
