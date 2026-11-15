"""Tests for parse_number(): what users type -> numbers (or a friendly error)."""
import pytest

from utils.helpers import parse_number


@pytest.mark.parametrize("typed, expected", [
    ("250000", 250000),
    ("$250,000.00", 250000),
    ("  $ 1,234.56 ", 1234.56),
    ("1e6", 1_000_000),
])
def test_accepts_friendly_formats(typed, expected):
    assert parse_number(typed) == expected


def test_percent_becomes_decimal():
    assert parse_number("2.99", is_percent=True) == pytest.approx(0.0299)
    assert parse_number("2.99%", is_percent=True) == pytest.approx(0.0299)


def test_whole_number_returns_int():
    result = parse_number("30", whole_number=True)
    assert result == 30 and isinstance(result, int)


@pytest.mark.parametrize("typed, message", [
    ("", "Please enter a value."),
    (None, "Please enter a value."),
    ("abc", "valid number"),
    ("inf", "real number"),
    ("nan", "real number"),
])
def test_rejects_bad_input(typed, message):
    # pytest.raises checks that the code raises ValueError and that the message matches
    with pytest.raises(ValueError, match=message):
        parse_number(typed)


def test_whole_number_rejects_decimals():
    with pytest.raises(ValueError, match="whole number"):
        parse_number("30.5", whole_number=True)


def test_limits():
    with pytest.raises(ValueError, match="at least 1"):
        parse_number("0", min_value=1)
    with pytest.raises(ValueError, match="at most 100"):
        parse_number("299", max_value=100)
