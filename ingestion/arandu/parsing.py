from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from dateutil import parser as date_parser


def parse_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    if value is None:
        raise ValueError("Cannot parse None as Decimal")
    text = str(value).strip()
    if text in {"", "-", "null", "None"}:
        raise ValueError(f"Cannot parse empty numeric value {value!r}")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Cannot parse decimal value {value!r}") from exc


def parse_brazilian_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%d/%m/%Y").date()


def parse_any_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date_parser.parse(str(value), dayfirst=True).date()


def parse_epoch_millis(value: int | str) -> date:
    millis = int(value)
    return datetime.fromtimestamp(millis / 1000, tz=UTC).date()


def sidra_period_to_date(period: str) -> date:
    text = str(period).strip()
    if len(text) == 6 and text.isdigit():
        return date(int(text[:4]), int(text[4:6]), 1)
    if len(text) == 5 and text[:4].isdigit() and text[-1].isdigit():
        quarter = int(text[-1])
        month = (quarter - 1) * 3 + 1
        return date(int(text[:4]), month, 1)
    if len(text) == 4 and text.isdigit():
        return date(int(text), 1, 1)
    return parse_any_date(text)
