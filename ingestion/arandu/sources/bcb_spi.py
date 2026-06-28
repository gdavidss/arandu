from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import requests

from arandu.db import Observation
from arandu.parsing import parse_decimal

# Public BCB Olinda OData service for the SPI (Sistema de Pagamentos Instantâneos), the
# settlement system behind Pix. PixLiquidadosAtual is a DAILY series of Pix transactions
# settled in the SPI, starting at Pix launch (2020-11). It is a separate API from SGS
# (api.bcb.gov.br) and from the Focus Expectativas service. Pix is not published in SGS,
# so this dedicated connector is the official source for monthly Pix volume and value.
#
# Source fields (per day):
#   Quantidade : count of Pix settled in the SPI (transactions).
#   Total      : value settled, in R$ thousands.
# We aggregate the daily series to calendar months and convert to dashboard-friendly
# units: millions of transactions (count) and R$ billions (value). Count and value are
# DIFFERENT units and are exposed as two separate series — never a misleading dual axis.
SPI_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/odata/"
    "PixLiquidadosAtual?$format=json&$select=Data,Quantidade,Total&$orderby=Data%20asc"
)

# What each series reads off the daily payload, and the factor that turns the daily-summed
# raw figure into the published unit.
SPI_AGGREGATES: dict[str, tuple[str, Decimal]] = {
    # Quantidade is a transaction count; /1e6 -> millions of transactions.
    "pix_count": ("Quantidade", Decimal("1000000")),
    # Total is in R$ thousands; thousands -> R$ billions is /1e6 (1e3 * 1e6 = 1e9).
    "pix_value": ("Total", Decimal("1000000")),
}


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value.strip()[:10])


def fetch_bcb_spi_pix(series: dict[str, Any]) -> list[Observation]:
    """Fetch monthly Pix volume or value from the BCB SPI daily series.

    Config keys (under the series entry):
      spi_aggregate : which monthly aggregate to build, one of SPI_AGGREGATES keys
                      ('pix_count' or 'pix_value').

    The source is daily; we sum each calendar month and stamp the total on the first day
    of that month so it lines up with the rest of the monthly dashboard. The latest
    (still-running) month is dropped: a partial month would understate the total and
    break comparability, so we only emit months that are fully elapsed.
    """
    aggregate = series["spi_aggregate"]
    field, divisor = SPI_AGGREGATES[aggregate]

    headers = {"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"}
    response = requests.get(SPI_URL, headers=headers, timeout=120)
    response.raise_for_status()
    rows = response.json().get("value", [])

    monthly_raw: dict[date, Decimal] = {}
    monthly_days: dict[date, set[date]] = {}
    for item in rows:
        raw_date = item.get("Data")
        raw_value = item.get(field)
        if not raw_date or raw_value in (None, ""):
            continue
        day = _parse_iso_date(raw_date)
        month_key = day.replace(day=1)
        monthly_raw[month_key] = monthly_raw.get(month_key, Decimal(0)) + parse_decimal(raw_value)
        monthly_days.setdefault(month_key, set()).add(day)

    if not monthly_raw:
        return []

    # Drop the most recent month: it is the current, still-incomplete month.
    latest_month = max(monthly_raw)

    observations: list[Observation] = []
    for month_key, raw_total in monthly_raw.items():
        if month_key == latest_month:
            continue
        value = raw_total / divisor
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=month_key,
                value=value,
                original_value=value,
                raw_payload={
                    "field": field,
                    "raw_sum": str(raw_total),
                    "days": len(monthly_days[month_key]),
                },
            )
        )
    return observations
