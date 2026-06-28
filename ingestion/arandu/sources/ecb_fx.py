from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import requests

from arandu.db import Observation

# ECB reference exchange rates via the Frankfurter service (no key, ECB-sourced, daily
# business days). Used for currencies BCB does not publish a BRL rate for — notably the
# Chinese yuan (CNY): BCB PTAX covers only ~10 currencies and BCB SGS has no clean
# BRL/CNY series. We read the cross directly (e.g. base=CNY, symbol=BRL = R$ per CNY).
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/{start}..{end}"


def fetch_ecb_fx(series: dict[str, Any]) -> list[Observation]:
    """Fetch a daily FX cross-rate from ECB reference rates (Frankfurter).

    Config keys:
      ecb_base  : base currency code (e.g. "CNY").
      ecb_quote : quote currency code (e.g. "BRL"). Value = ecb_quote per 1 ecb_base.
      start_date: ISO date to start from (default 2010-01-01).
    """
    base = series["ecb_base"]
    quote = series["ecb_quote"]
    start = series.get("start_date", "2010-01-01")
    end = date.today().isoformat()

    url = FRANKFURTER_URL.format(start=start, end=end)
    response = requests.get(url, params={"base": base, "symbols": quote}, timeout=60)
    response.raise_for_status()
    rates = response.json().get("rates", {})

    observations: list[Observation] = []
    for day, values in sorted(rates.items()):
        value = values.get(quote)
        if value is None:
            continue
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=date.fromisoformat(day),
                value=Decimal(str(value)),
                original_value=Decimal(str(value)),
                raw_payload={"date": day, **values},
            )
        )
    return observations
