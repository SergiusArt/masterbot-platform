"""Conftest for e2e tests - handles config mocking for test environment."""

import sys
from types import ModuleType
from unittest.mock import MagicMock

# Create a fake config module with test settings before any master_bot imports.
# This prevents Pydantic ValidationError when .env contains fields from other services.
_config = ModuleType("config")
_config.settings = MagicMock(
    BOT_TOKEN="test_token_e2e",
    ADMIN_ID=99999,
    DATABASE_URL="sqlite+aiosqlite:///:memory:",
    REDIS_URL="redis://localhost:6379/0",
    IMPULSE_SERVICE_URL="http://localhost:8001",
    BABLO_SERVICE_URL="http://localhost:8002",
    TIMEZONE="Europe/Moscow",
)
_config.get_settings = lambda: _config.settings

# Insert before master_bot handlers are collected (they import from config)
sys.modules.setdefault("config", _config)
sys.modules.setdefault("master_bot.config", _config)
