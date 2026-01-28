"""Unified logging configuration for MasterBot Platform."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """Setup and configure a logger.

    Args:
        name: Logger name
        level: Logging level
        log_format: Custom log format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set format
    if log_format is None:
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(filename)s:%(lineno)d | %(message)s"
        )

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Pre-configured loggers
bot_logger = setup_logger("master_bot")
impulse_logger = setup_logger("impulse_service")
bablo_logger = setup_logger("bablo_service")
bablo_listener_logger = setup_logger("bablo_listener")
db_logger = setup_logger("database")
