from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote

import requests

from arandu.db import Observation
from arandu.parsing import parse_decimal

# Public BCB Olinda OData service that exposes the Focus survey (Expectativas de Mercado).
# This is a separate API from SGS (api.bcb.gov.br). We use the dedicated 12-months-ahead
# inflation-expectation resource so the horizon is a true forward-looking 12m window,
# directly comparable to realized IPCA accumulated in 12 months (SGS 13522).
OLINDA_BASE_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/{resource}"
)


def _parse_iso_date(value: str) -> date:
    # Olinda returns survey dates as ISO strings, e.g. "2026-06-19".
    return date.fromisoformat(value.strip()[:10])


def fetch_bcb_olinda_expectativas(series: dict[str, Any]) -> list[Observation]:
    """Fetch a Focus expectation series from the BCB Olinda OData service.

    Config keys (under the series entry):
      olinda_resource : OData entity set (e.g. ExpectativasMercadoInflacao12Meses).
      olinda_indicador: filtered Indicador value (e.g. IPCA).
      olinda_field    : numeric field to read (Media or Mediana; default Mediana).
      olinda_filters  : optional dict of extra equality filters, e.g.
                        {Suavizada: 'S', baseCalculo: 0}.

    The survey runs daily, but the rest of the dashboard is monthly. We keep the last
    survey reading of each calendar month and stamp it on the first day of that month,
    so the expectation overlays cleanly on the monthly realized-inflation series.
    """
    resource = series["olinda_resource"]
    indicador = series["olinda_indicador"]
    field = series.get("olinda_field", "Mediana")
    extra_filters: dict[str, Any] = series.get("olinda_filters", {}) or {}

    filters = [f"Indicador eq '{indicador}'"]
    for key, value in extra_filters.items():
        if isinstance(value, str):
            filters.append(f"{key} eq '{value}'")
        else:
            filters.append(f"{key} eq {value}")

    # Build the query string by hand: the Olinda OData parser rejects '+'-encoded spaces
    # (HTTP 400) and requires percent (%20) encoding, which requests' default param
    # encoding (urlencode / quote_plus) does not produce. quote() keeps spaces as %20.
    params = {
        "$format": "json",
        "$filter": " and ".join(filters),
        "$orderby": "Data asc",
        "$select": f"Data,{field}",
    }
    safe_chars = "',()"
    query = "&".join(f"{key}={quote(value, safe=safe_chars)}" for key, value in params.items())
    url = f"{OLINDA_BASE_URL.format(resource=resource)}?{query}"
    headers = {"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    rows = response.json().get("value", [])

    # Collapse the daily survey to one (last) reading per calendar month.
    by_month: dict[date, tuple[date, dict[str, Any]]] = {}
    for item in rows:
        raw_date = item.get("Data")
        raw_value = item.get(field)
        if not raw_date or raw_value in (None, ""):
            continue
        survey_date = _parse_iso_date(raw_date)
        month_key = survey_date.replace(day=1)
        existing = by_month.get(month_key)
        if existing is None or survey_date > existing[0]:
            by_month[month_key] = (survey_date, item)

    observations: list[Observation] = []
    for month_key, (_survey_date, item) in by_month.items():
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=month_key,
                value=parse_decimal(item[field]),
                original_value=parse_decimal(item[field]),
                raw_payload=item,
            )
        )
    return observations
