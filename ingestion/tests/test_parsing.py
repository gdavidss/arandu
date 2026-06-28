from datetime import date
from decimal import Decimal

from arandu.parsing import (
    parse_brazilian_date,
    parse_decimal,
    parse_epoch_millis,
    sidra_period_to_date,
)


def test_parse_decimal_accepts_brazilian_and_api_formats() -> None:
    assert parse_decimal("1.234,56") == Decimal("1234.56")
    assert parse_decimal("1234.56") == Decimal("1234.56")
    assert parse_decimal(12.5) == Decimal("12.5")


def test_parse_brazilian_date() -> None:
    assert parse_brazilian_date("01/04/2026") == date(2026, 4, 1)


def test_parse_epoch_millis_as_utc_date() -> None:
    assert parse_epoch_millis(1775012400000) == date(2026, 4, 1)


def test_sidra_period_to_date() -> None:
    assert sidra_period_to_date("202405") == date(2024, 5, 1)
    assert sidra_period_to_date("20241") == date(2024, 1, 1)
    assert sidra_period_to_date("2024") == date(2024, 1, 1)
