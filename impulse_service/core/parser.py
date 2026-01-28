"""Message parser for impulse signals."""

import re
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from shared.utils.logger import get_logger

logger = get_logger("parser")


@dataclass
class ParsedImpulse:
    """Parsed impulse data."""

    symbol: str
    percent: Decimal
    max_percent: Optional[Decimal] = None
    type: str = "growth"  # 'growth' or 'fall'
    growth_ratio: Optional[Decimal] = None
    fall_ratio: Optional[Decimal] = None


class ImpulseParser:
    """Parser for impulse messages from Telegram channel."""

    # Common patterns for impulse messages
    PATTERNS = [
        # Pattern: 🟢[SYNUSDT.P](link) **10%** or 🔴[AXSUSDT.P](link) **-15%**
        r"\[([A-Z0-9]+(?:USDT|BUSD)?\.?P?)\]\([^)]+\)\s*\*\*([+-]?\d+\.?\d*)%\*\*",
        # Pattern: BTCUSDT +15.5%
        r"([A-Z0-9]+(?:USDT|BUSD|USDC|BTC|ETH))\s*([+-]?\d+\.?\d*)%",
        # Pattern: BTC/USDT: 15.5%
        r"([A-Z0-9]+)/([A-Z]+):\s*([+-]?\d+\.?\d*)%",
        # Pattern: $BTC +15.5%
        r"\$([A-Z0-9]+)\s*([+-]?\d+\.?\d*)%",
    ]

    def parse(self, message: str) -> Optional[ParsedImpulse]:
        """Parse message and extract impulse data.

        Args:
            message: Raw message text

        Returns:
            Parsed impulse data or None if not matched
        """
        if not message:
            return None

        # Try each pattern
        for pattern in self.PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return self._process_match(match, message)

        return None

    def _process_match(self, match: re.Match, raw_message: str) -> Optional[ParsedImpulse]:
        """Process regex match and create ParsedImpulse.

        Args:
            match: Regex match object
            raw_message: Original message

        Returns:
            ParsedImpulse or None
        """
        try:
            groups = match.groups()

            if len(groups) == 2:
                # Pattern: SYMBOL PERCENT%
                symbol = groups[0].upper()
                percent_str = groups[1]
            elif len(groups) == 3:
                # Pattern: BASE/QUOTE: PERCENT%
                symbol = f"{groups[0]}{groups[1]}".upper()
                percent_str = groups[2]
            else:
                return None

            percent = Decimal(percent_str)
            impulse_type = "growth" if percent >= 0 else "fall"

            # Extract max percent if present
            max_percent = self._extract_max_percent(raw_message)

            # Extract ratios if present
            growth_ratio, fall_ratio = self._extract_ratios(raw_message)

            return ParsedImpulse(
                symbol=symbol,
                percent=percent,
                max_percent=max_percent,
                type=impulse_type,
                growth_ratio=growth_ratio,
                fall_ratio=fall_ratio,
            )

        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse impulse: {e}")
            return None

    def _extract_max_percent(self, message: str) -> Optional[Decimal]:
        """Extract max percent from message if present.

        Args:
            message: Raw message

        Returns:
            Max percent or None
        """
        # Pattern: Максимальный импульс: 91% or max: 25.5%
        patterns = [
            r"Максимальный импульс[:\s]+([+-]?\d+\.?\d*)%",
            r"max[:\s]+([+-]?\d+\.?\d*)%",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    return Decimal(match.group(1))
                except ValueError:
                    pass
        return None

    def _extract_ratios(self, message: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
        """Extract growth/fall ratios from message.

        Args:
            message: Raw message

        Returns:
            Tuple of (growth_ratio, fall_ratio)
        """
        growth_ratio = None
        fall_ratio = None

        # Pattern: 📈|29%|---|71%|📉 or G/F: 3.5/2.1
        patterns = [
            r"📈\|(\d+\.?\d*)%\|---\|(\d+\.?\d*)%\|📉",
            r"G/F[:\s]+(\d+\.?\d*)/(\d+\.?\d*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    growth_ratio = Decimal(match.group(1))
                    fall_ratio = Decimal(match.group(2))
                    break
                except ValueError:
                    pass

        return growth_ratio, fall_ratio


# Global parser instance
impulse_parser = ImpulseParser()
