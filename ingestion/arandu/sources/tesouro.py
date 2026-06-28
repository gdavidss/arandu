from __future__ import annotations

from typing import Any

import requests

from arandu.db import Observation
from arandu.parsing import parse_brazilian_date, parse_decimal

TESOURO_BASE_URL = (
    "https://series-temporais.tesouro.gov.br/backend-series-temporais/rest/Public/SerieGrafico"
)


def fetch_tesouro_series(series: dict[str, Any]) -> list[Observation]:
    series_code = str(series["source_series_code"])
    url = f"{TESOURO_BASE_URL}/ValorSerie/{series_code}"
    response = requests.get(
        url,
        headers={"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    observations: list[Observation] = []
    for item in payload:
        raw_value = item.get("valor")
        raw_date = item.get("dataString")
        if raw_value is None or not raw_date:
            continue
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=parse_brazilian_date(raw_date),
                value=parse_decimal(raw_value),
                original_value=parse_decimal(raw_value),
                raw_payload=item,
            )
        )
    return observations
