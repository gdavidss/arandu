from __future__ import annotations

import csv
import io
from datetime import date, timedelta
from typing import Any

import requests

from arandu.db import Observation
from arandu.parsing import parse_brazilian_date, parse_decimal

BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
# BCB SGS rejects daily-series requests spanning more than ~10 years, so chunk them.
DAILY_WINDOW_YEARS = 10


def _format_bcb_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def _as_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _plus_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:  # Feb 29
        return value.replace(year=value.year + years, day=28)


def _windows(start: date, end: date, max_years: int) -> list[tuple[date, date]]:
    """Split [start, end] into consecutive <= max_years windows (BCB daily-series limit)."""
    windows: list[tuple[date, date]] = []
    cur = start
    while cur <= end:
        window_end = min(end, _plus_years(cur, max_years) - timedelta(days=1))
        windows.append((cur, window_end))
        cur = window_end + timedelta(days=1)
    return windows


def _obs(series_id: str, raw: dict[str, Any], raw_date: str, value: str) -> Observation:
    return Observation(
        series_id=series_id,
        date=parse_brazilian_date(raw_date),
        value=parse_decimal(value),
        original_value=parse_decimal(value),
        raw_payload=raw,
    )


def _fetch_range(
    series_id: str, code: str, start: date | None, end: date | None
) -> list[Observation]:
    params: dict[str, str] = {"formato": "json"}
    if start:
        params["dataInicial"] = _format_bcb_date(start)
    if end:
        params["dataFinal"] = _format_bcb_date(end)
    url = BCB_BASE_URL.format(code=code)
    headers = {"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"}
    response = requests.get(url, params=params, headers=headers, timeout=45)
    if response.ok and response.headers.get("content-type", "").startswith("application/json"):
        return [
            _obs(series_id, item, item["data"], item["valor"])
            for item in response.json()
            if item.get("valor") not in {None, ""}
        ]

    # BCB occasionally serves CSV more reliably through the same resource. Keep this
    # official fallback, and let HTTP errors surface if it also fails.
    csv_params = dict(params)
    csv_params["formato"] = "csv"
    csv_response = requests.get(
        url, params=csv_params, headers={"User-Agent": headers["User-Agent"]}, timeout=45
    )
    csv_response.raise_for_status()
    reader = csv.DictReader(io.StringIO(csv_response.text), delimiter=";")
    return [
        _obs(series_id, item, item["data"], item["valor"])
        for item in reader
        if item.get("data") and item.get("valor")
    ]


def fetch_bcb_sgs(series: dict[str, Any]) -> list[Observation]:
    code = str(series["source_series_code"])
    series_id = series["series_id"]
    start = _as_date(series.get("start_date"))
    end = _as_date(series.get("end_date")) or date.today()

    is_daily = str(series.get("frequency", "")).lower() == "daily"
    if is_daily and start is not None:
        ranges = _windows(start, end, DAILY_WINDOW_YEARS)
    else:
        ranges = [(start, end if series.get("end_date") else None)]

    observations: list[Observation] = []
    for window_start, window_end in ranges:
        observations.extend(_fetch_range(series_id, code, window_start, window_end))
    return observations
