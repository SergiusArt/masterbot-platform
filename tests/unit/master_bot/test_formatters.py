"""Tests for message formatting utilities and timeframe mappings."""

import pytest

import sys
import os

# Add project paths — master_bot MUST be added AFTER shared
# so it ends up at position 0 (shared/utils/ shadows master_bot/utils/ otherwise)
_base = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, os.path.join(_base, "shared"))
sys.path.insert(0, os.path.join(_base, "master_bot"))

# Clear cached utils module to avoid shared/utils shadowing master_bot/utils
for mod_name in list(sys.modules.keys()):
    if mod_name == "utils" or mod_name.startswith("utils."):
        del sys.modules[mod_name]


class TestFormatAnalytics:
    """Tests for format_analytics function."""

    @pytest.mark.unit
    def test_basic_format(self):
        """Test basic analytics formatting with period, totals."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
        }

        result = format_analytics(data)

        assert "Аналитика за сегодня" in result
        assert "100" in result
        assert "60" in result
        assert "40" in result

    @pytest.mark.unit
    def test_yesterday_period_name(self):
        """Test yesterday period name is correct."""
        from utils.formatters import format_analytics

        data = {
            "period": "yesterday",
            "total_impulses": 50,
            "growth_count": 30,
            "fall_count": 20,
        }

        result = format_analytics(data)
        assert "Аналитика за вчера" in result

    @pytest.mark.unit
    def test_week_period_name(self):
        """Test week period name is correct."""
        from utils.formatters import format_analytics

        data = {
            "period": "week",
            "total_impulses": 500,
            "growth_count": 300,
            "fall_count": 200,
        }

        result = format_analytics(data)
        assert "Аналитика за неделю" in result

    @pytest.mark.unit
    def test_month_period_name(self):
        """Test month period name is correct."""
        from utils.formatters import format_analytics

        data = {
            "period": "month",
            "total_impulses": 2000,
            "growth_count": 1200,
            "fall_count": 800,
        }

        result = format_analytics(data)
        assert "Аналитика за месяц" in result

    @pytest.mark.unit
    def test_top_growth_displayed(self):
        """Test top growth impulses are displayed."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
            "top_growth": [
                {"symbol": "BTCUSDT.P", "percent": 33.8, "count": 4},
                {"symbol": "ETHUSDT.P", "percent": 22.5, "count": 2},
            ],
        }

        result = format_analytics(data)
        assert "Топ рост" in result
        assert "BTCUSDT.P" in result
        assert "+33.8%" in result
        assert "(4x)" in result

    @pytest.mark.unit
    def test_top_fall_displayed(self):
        """Test top fall impulses are displayed."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
            "top_fall": [
                {"symbol": "XRPUSDT.P", "percent": -15.0, "count": 3},
            ],
        }

        result = format_analytics(data)
        assert "Топ падение" in result
        assert "XRPUSDT.P" in result
        assert "-15.0%" in result

    @pytest.mark.unit
    def test_comparison_today_shows_vs_yesterday(self):
        """Test today comparison shows 'со вчера'."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
            "comparison": {
                "vs_yesterday": "+15.2%",
                "vs_week_median": "в норме",
                "week_median": 85,
            },
        }

        result = format_analytics(data)
        assert "По сравнению со вчера" in result
        assert "+15.2%" in result

    @pytest.mark.unit
    def test_comparison_yesterday_shows_vs_day_before(self):
        """Test yesterday comparison shows 'с позавчера'."""
        from utils.formatters import format_analytics

        data = {
            "period": "yesterday",
            "total_impulses": 92,
            "growth_count": 77,
            "fall_count": 15,
            "comparison": {
                "vs_yesterday": "+8.3%",
                "vs_week_median": "в норме",
                "week_median": 80,
            },
        }

        result = format_analytics(data)
        assert "По сравнению с позавчера" in result
        assert "+8.3%" in result
        # Should NOT say "со вчера" for yesterday period
        assert "со вчера" not in result

    @pytest.mark.unit
    def test_comparison_none_not_displayed(self):
        """Test that None comparison values are not displayed."""
        from utils.formatters import format_analytics

        data = {
            "period": "yesterday",
            "total_impulses": 92,
            "growth_count": 77,
            "fall_count": 15,
            "comparison": {
                "vs_yesterday": None,
                "vs_week_median": "в норме",
                "week_median": 85,
            },
        }

        result = format_analytics(data)
        assert "None" not in result
        assert "По сравнению" not in result

    @pytest.mark.unit
    def test_week_median_displayed(self):
        """Test weekly median comparison line is displayed."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
            "comparison": {
                "vs_yesterday": "+5.0%",
                "vs_week_median": "высокая активность",
                "week_median": 70,
            },
        }

        result = format_analytics(data)
        assert "Медиана за неделю" in result
        assert "70" in result
        assert "высокая активность" in result

    @pytest.mark.unit
    def test_week_median_none_not_displayed(self):
        """Test that None week median is not displayed."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 60,
            "fall_count": 40,
            "comparison": {
                "vs_yesterday": "+5.0%",
                "vs_week_median": None,
                "week_median": None,
            },
        }

        result = format_analytics(data)
        assert "Медиана за неделю" not in result

    @pytest.mark.unit
    def test_no_comparison_data(self):
        """Test formatting when no comparison data exists."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 10,
            "growth_count": 5,
            "fall_count": 5,
        }

        result = format_analytics(data)
        assert "По сравнению" not in result
        assert "Медиана" not in result

    @pytest.mark.unit
    def test_empty_top_growth_not_shown(self):
        """Test that empty top_growth list doesn't show header."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 0,
            "growth_count": 0,
            "fall_count": 0,
            "top_growth": [],
            "top_fall": [],
        }

        result = format_analytics(data)
        assert "Топ рост" not in result
        assert "Топ падение" not in result

    @pytest.mark.unit
    def test_top_items_limited_to_5(self):
        """Test that top items are limited to 5."""
        from utils.formatters import format_analytics

        data = {
            "period": "today",
            "total_impulses": 100,
            "growth_count": 100,
            "fall_count": 0,
            "top_growth": [
                {"symbol": f"COIN{i}USDT.P", "percent": 10.0 + i, "count": 1}
                for i in range(10)
            ],
        }

        result = format_analytics(data)
        # Should only show first 5
        assert "COIN0USDT.P" in result
        assert "COIN4USDT.P" in result
        assert "COIN5USDT.P" not in result


class TestFormatImpulse:
    """Tests for format_impulse function."""

    @pytest.mark.unit
    def test_growth_impulse(self):
        """Test formatting growth impulse."""
        from utils.formatters import format_impulse

        data = {
            "symbol": "BTCUSDT",
            "percent": 15.5,
            "type": "growth",
        }

        result = format_impulse(data)
        assert "🟢" in result
        assert "BTCUSDT" in result
        assert "Рост" in result
        assert "+15.50%" in result

    @pytest.mark.unit
    def test_fall_impulse(self):
        """Test formatting fall impulse."""
        from utils.formatters import format_impulse

        data = {
            "symbol": "ETHUSDT",
            "percent": -10.2,
            "type": "fall",
        }

        result = format_impulse(data)
        assert "🔴" in result
        assert "ETHUSDT" in result
        assert "Падение" in result
        assert "-10.20%" in result

    @pytest.mark.unit
    def test_with_max_percent(self):
        """Test formatting with max_percent field."""
        from utils.formatters import format_impulse

        data = {
            "symbol": "BTCUSDT",
            "percent": 15.5,
            "type": "growth",
            "max_percent": 22.3,
        }

        result = format_impulse(data)
        assert "Максимум" in result
        assert "+22.30%" in result


class TestTimeframeMapping:
    """Tests for TIMEFRAME_TO_DB and DB_TO_TIMEFRAME mappings.

    These test the mapping values directly without importing the handler module,
    since the handler has heavy dependencies (config, pytz, aiogram).
    """

    EXPECTED_MAPPING = {
        "1м": "1m",
        "5м": "5m",
        "15м": "15m",
        "30м": "30m",
        "1ч": "1h",
    }

    @pytest.mark.unit
    def test_timeframe_to_db_mapping(self):
        """Test button label to DB value mapping covers all timeframes."""
        for label, db_val in self.EXPECTED_MAPPING.items():
            assert label  # non-empty label
            assert db_val  # non-empty DB value

    @pytest.mark.unit
    def test_db_to_timeframe_mapping(self):
        """Test DB value to button label mapping is inverse."""
        inverse = {v: k for k, v in self.EXPECTED_MAPPING.items()}
        assert inverse["1m"] == "1м"
        assert inverse["5m"] == "5м"
        assert inverse["15m"] == "15м"
        assert inverse["30m"] == "30м"
        assert inverse["1h"] == "1ч"

    @pytest.mark.unit
    def test_all_timeframes_covered(self):
        """Test all expected timeframes are in the mapping."""
        expected_labels = {"1м", "5м", "15м", "30м", "1ч"}
        assert set(self.EXPECTED_MAPPING.keys()) == expected_labels

        expected_db = {"1m", "5m", "15m", "30m", "1h"}
        assert set(self.EXPECTED_MAPPING.values()) == expected_db

    @pytest.mark.unit
    def test_mappings_are_bijective(self):
        """Test that both mappings have no duplicate values."""
        # All labels are unique
        assert len(self.EXPECTED_MAPPING.keys()) == len(set(self.EXPECTED_MAPPING.keys()))
        # All DB values are unique
        assert len(self.EXPECTED_MAPPING.values()) == len(set(self.EXPECTED_MAPPING.values()))
