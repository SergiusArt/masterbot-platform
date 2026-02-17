"""Conftest for strong_service tests - handles module isolation."""

import sys
import os

import pytest

STRONG_SERVICE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "strong_service")
)
SHARED_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared")
)

# Conflicting service directories that have their own services/core/models packages
_CONFLICTING = ("impulse_service", "master_bot", "bablo_service")


def _setup_strong_paths():
    """Set up sys.path for strong_service imports."""
    sys.path = [p for p in sys.path if not any(c in p for c in _CONFLICTING)]
    if STRONG_SERVICE_PATH not in sys.path:
        sys.path.insert(0, STRONG_SERVICE_PATH)
    if SHARED_PATH not in sys.path:
        sys.path.insert(0, SHARED_PATH)


def _clear_service_modules():
    """Clear cached service/core/models modules."""
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(("services", "core", "models", "config")) and not mod_name.startswith("shared"):
            del sys.modules[mod_name]


# Module-level setup for collection time (needed for top-level imports in test files)
_setup_strong_paths()
_clear_service_modules()


@pytest.fixture(autouse=True)
def _ensure_strong_paths():
    """Ensure strong_service paths are correct (lightweight, no module clearing)."""
    _setup_strong_paths()
    yield
