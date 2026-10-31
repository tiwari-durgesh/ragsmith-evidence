
import pytest

from ragsmith.sufficiency.numeric import values_equal


@pytest.mark.parametrize(
    "actual,expected",
    [
        ("145", "145.0"),
        ("145.00", "145"),
        ("00145", "145"),
        ("-25", "-25.0"),
        ("0.50", "0.5"),
        ("1e3", "1000"),
    ],
)
def test_equivalent_numeric_values(actual, expected):
    assert values_equal(actual, expected) is True


@pytest.mark.parametrize(
    "actual,expected",
    [
        ("145", "150"),
        ("-25", "25"),
        ("0.5", "0.6"),
    ],
)
def test_different_numeric_values(actual, expected):
    assert values_equal(actual, expected) is False


def test_equal_text_values():
    assert values_equal("Approved", "Approved") is True


def test_different_text_values():
    assert values_equal("Approved", "Rejected") is False


def test_whitespace_is_ignored():
    assert values_equal(" 145 ", "145.0 ") is True


@pytest.mark.parametrize(
    "actual,expected",
    [
        ("NaN", "NaN"),
        ("Infinity", "Infinity"),
        ("-Infinity", "-Infinity"),
    ],
)
def test_non_finite_numbers_rejected(actual, expected):
    assert values_equal(actual, expected) is False


def test_numeric_precision():
    assert values_equal(
        "0.123456789123456789",
        "0.1234567891234567890",
    ) is True
