
from decimal import Decimal, InvalidOperation


def values_equal(actual: str, expected: str) -> bool:
    """Compare numeric values precisely, otherwise compare text."""

    actual = actual.strip()
    expected = expected.strip()

    try:
        actual_number = Decimal(actual)
        expected_number = Decimal(expected)

        if not actual_number.is_finite() or not expected_number.is_finite():
            return False

        return actual_number == expected_number

    except InvalidOperation:
        return actual == expected
