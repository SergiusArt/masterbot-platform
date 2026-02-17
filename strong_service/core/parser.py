"""Message parser for Strong Signal trading signals."""

import re
from dataclasses import dataclass
from typing import Optional

from shared.utils.logger import get_logger

logger = get_logger("strong_parser")


@dataclass
class ParsedStrongSignal:
    """Parsed Strong Signal data."""

    symbol: str
    direction: str  # 'long' or 'short'
    raw_message: Optional[str] = None


class StrongParser:
    """Parser for Strong Signal messages from Telegram channel.

    Message formats:
        Plain:    🧤DOTUSDT.P Long🧤 / 🎒SOLUSDT.P Short🎒
        Markdown: 🧤**DOTUSDT.P** __Long__🧤 / 🎒**SOLUSDT.P** __Short__🎒
        (also single * / _ variants)
    """

    # Long pattern: 🧤 ... Long ... 🧤
    LONG_PATTERN = re.compile(
        r"🧤\*{0,2}([A-Z0-9]+(?:\.P)?)\*{0,2}\s*_{0,2}Long_{0,2}🧤",
        re.IGNORECASE,
    )

    # Short pattern: 🎒 ... Short ... 🎒
    SHORT_PATTERN = re.compile(
        r"🎒\*{0,2}([A-Z0-9]+(?:\.P)?)\*{0,2}\s*_{0,2}Short_{0,2}🎒",
        re.IGNORECASE,
    )

    def parse(self, message: str) -> Optional[ParsedStrongSignal]:
        """Parse message and extract signal data.

        Args:
            message: Raw message text from Telegram

        Returns:
            ParsedStrongSignal if parsing successful, None otherwise
        """
        if not message:
            return None

        try:
            # Try long pattern
            match = self.LONG_PATTERN.search(message)
            if match:
                symbol = self._clean_symbol(match.group(1))
                return ParsedStrongSignal(
                    symbol=symbol,
                    direction="long",
                    raw_message=message,
                )

            # Try short pattern
            match = self.SHORT_PATTERN.search(message)
            if match:
                symbol = self._clean_symbol(match.group(1))
                return ParsedStrongSignal(
                    symbol=symbol,
                    direction="short",
                    raw_message=message,
                )

            return None

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    @staticmethod
    def _clean_symbol(symbol: str) -> str:
        """Remove .P suffix from perpetual futures symbol.

        Args:
            symbol: Raw symbol (e.g., 'DOTUSDT.P')

        Returns:
            Cleaned symbol (e.g., 'DOTUSDT')
        """
        if symbol.endswith(".P"):
            return symbol[:-2]
        return symbol


# Global parser instance
strong_parser = StrongParser()
