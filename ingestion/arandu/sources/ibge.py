from __future__ import annotations

from typing import Any

import requests

from arandu.db import Observation
from arandu.parsing import parse_decimal, sidra_period_to_date


def fetch_ibge_sidra(series: dict[str, Any]) -> list[Observation]:
    url = series.get("sidra_url")
    if not url:
        raise ValueError(f"IBGE SIDRA series {series['series_id']} needs sidra_url")
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        return []

    period_key = series.get("sidra_period_key", "D2C")
    value_key = series.get("sidra_value_key", "V")
    observations: list[Observation] = []
    for item in payload[1:]:
        raw_value = item.get(value_key)
        raw_period = item.get(period_key)
        if raw_value in {None, "-", "..."} or raw_period is None:
            continue
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=sidra_period_to_date(str(raw_period)),
                value=parse_decimal(raw_value),
                original_value=parse_decimal(raw_value),
                raw_payload=item,
            )
        )
    return observations
