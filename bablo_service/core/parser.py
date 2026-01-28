"""Message parser for Bablo trading signals."""

import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from shared.utils.logger import get_logger

logger = get_logger("bablo_parser")


@dataclass
class ParsedBabloSignal:
    """Parsed Bablo signal data."""

    symbol: str
    direction: str  # 'long' or 'short'
    strength: int  # 1-5 (number of colored squares)
    timeframe: str  # '1m', '15m', '1h', '4h'
    time_horizon: Optional[str] = None  # '60 минут', '12 часов', '2 дня'

    # Quality metrics
    quality_total: int = 0
    quality_profit: Optional[int] = None
    quality_drawdown: Optional[int] = None
    quality_accuracy: Optional[int] = None

    # Probabilities: {"0.9": {"long": 82, "short": 73}, ...}
    probabilities: dict = field(default_factory=dict)

    max_drawdown: Optional[Decimal] = None
    raw_message: Optional[str] = None


class BabloParser:
    """Parser for Bablo trading signals from Telegram channel."""

    # Direction patterns (green = long, red = short)
    LONG_PATTERN = r"(🟩+)"
    SHORT_PATTERN = r"(🟥+)"

    # Symbol pattern - extract from markdown link [SYMBOL](url)
    # Example: [SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/)
    SYMBOL_PATTERN = r"\[([A-Z0-9]+(?:\.P)?)\]\(https?://[^)]+\)"

    # Timeframe pattern with backticks
    # Example: `| 1м ТФ |` or `| 30м ТФ |`
    TIMEFRAME_PATTERN = r"`?\|?\s*(\d+)([мч])\s*ТФ\s*\|?`?"

    # Quality pattern with bold markdown
    # Example: **Качество = 7 из 10:**
    QUALITY_PATTERN = r"\*?\*?Качество\s*=\s*(\d+)\s*из\s*10"

    # Quality breakdown patterns (with underscores)
    PROFIT_PATTERN = r"Профитность\s*_*(\d+)_*\s*из"
    DRAWDOWN_QUALITY_PATTERN = r"Просадка\s*_*(\d+)_*\s*из"
    ACCURACY_PATTERN = r"Точность\s*_*(\d+)_*\s*из"

    # Time horizon pattern
    # Example: **Вероятность (60 минут):**
    HORIZON_PATTERN = r"Вероятность\s*\(([^)]+)\)"

    # Probability pattern - new format with backticks
    # Example: `0.3%`: 📉 `86%`, 📈 `72%`
    PROB_PATTERN = r"`?([\d.]+)%`?:\s*📉\s*`?(\d+)%`?,\s*📈\s*`?(\d+)%`?"

    # Max drawdown pattern with underscores
    # Example: Максимальная просадка = __6%__
    MAX_DRAWDOWN_PATTERN = r"Максимальная просадка\s*=\s*_*(\d+)%?_*"

    # Timeframe mapping
    TIMEFRAME_MAP = {
        "м": "m",  # minutes
        "ч": "h",  # hours
    }

    def parse(self, message: str) -> Optional[ParsedBabloSignal]:
        """Parse message and extract signal data.

        Args:
            message: Raw message text from Telegram

        Returns:
            ParsedBabloSignal if parsing successful, None otherwise
        """
        if not message:
            return None

        try:
            # Extract direction and strength
            direction, strength = self._extract_direction_and_strength(message)
            if not direction:
                return None

            # Extract header info (symbol, timeframe, quality)
            header = self._extract_header(message)
            if not header:
                return None

            symbol, timeframe, quality_total = header

            # Extract quality breakdown
            quality_profit = self._extract_pattern_int(message, self.PROFIT_PATTERN)
            quality_drawdown = self._extract_pattern_int(message, self.DRAWDOWN_QUALITY_PATTERN)
            quality_accuracy = self._extract_pattern_int(message, self.ACCURACY_PATTERN)

            # Extract time horizon
            time_horizon = self._extract_time_horizon(message)

            # Extract probabilities
            probabilities = self._extract_probabilities(message)

            # Extract max drawdown
            max_drawdown = self._extract_max_drawdown(message)

            return ParsedBabloSignal(
                symbol=symbol,
                direction=direction,
                strength=strength,
                timeframe=timeframe,
                time_horizon=time_horizon,
                quality_total=quality_total,
                quality_profit=quality_profit,
                quality_drawdown=quality_drawdown,
                quality_accuracy=quality_accuracy,
                probabilities=probabilities,
                max_drawdown=max_drawdown,
                raw_message=message,
            )

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    def _extract_direction_and_strength(self, message: str) -> tuple[Optional[str], int]:
        """Extract signal direction and strength from emoji squares."""
        # Check for long (green squares)
        long_match = re.search(self.LONG_PATTERN, message)
        if long_match:
            strength = len(long_match.group(1))
            return "long", strength

        # Check for short (red squares)
        short_match = re.search(self.SHORT_PATTERN, message)
        if short_match:
            strength = len(short_match.group(1))
            return "short", strength

        return None, 0

    def _extract_header(self, message: str) -> Optional[tuple[str, str, int]]:
        """Extract symbol, timeframe, and quality from header."""
        # Extract symbol from markdown link
        symbol_match = re.search(self.SYMBOL_PATTERN, message)
        if not symbol_match:
            return None
        symbol = symbol_match.group(1)

        # Extract timeframe
        tf_match = re.search(self.TIMEFRAME_PATTERN, message)
        if not tf_match:
            return None
        tf_value = tf_match.group(1)
        tf_unit = tf_match.group(2)

        # Convert timeframe to standard format
        unit = self.TIMEFRAME_MAP.get(tf_unit, tf_unit)
        timeframe = f"{tf_value}{unit}"

        # Extract quality
        quality_match = re.search(self.QUALITY_PATTERN, message)
        if not quality_match:
            return None
        quality = int(quality_match.group(1))

        return symbol, timeframe, quality

    def _extract_pattern_int(self, message: str, pattern: str) -> Optional[int]:
        """Extract integer value from pattern match."""
        match = re.search(pattern, message)
        if match:
            return int(match.group(1))
        return None

    def _extract_time_horizon(self, message: str) -> Optional[str]:
        """Extract time horizon from probability section."""
        match = re.search(self.HORIZON_PATTERN, message)
        if match:
            return match.group(1)
        return None

    def _extract_probabilities(self, message: str) -> dict:
        """Extract probability values for different targets."""
        probabilities = {}
        matches = re.findall(self.PROB_PATTERN, message)

        for target, long_prob, short_prob in matches:
            probabilities[target] = {
                "long": int(long_prob),
                "short": int(short_prob),
            }

        return probabilities

    def _extract_max_drawdown(self, message: str) -> Optional[Decimal]:
        """Extract maximum drawdown percentage."""
        match = re.search(self.MAX_DRAWDOWN_PATTERN, message)
        if match:
            return Decimal(match.group(1))
        return None


# Global parser instance
bablo_parser = BabloParser()
