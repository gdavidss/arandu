from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import requests

from arandu.db import Observation

# Official MDIC/SECEX foreign-trade statistics API (Comex Stat). This is a POST/JSON
# service, distinct from BCB SGS and IBGE SIDRA, so it gets its own connector.
# We request yearly totals (monthDetail=false) broken out by partner country, in FOB
# US$, for both flows. One request per flow covers every country and every year, which
# we then fold into a small set of named partners plus a "Demais países" remainder.
COMEXSTAT_URL = "https://api-comexstat.mdic.gov.br/general"

# Comex Stat returns FOB values in whole US$. The rest of the trade tab (BCB SGS
# 22707/22708/22709) is in US$ millions, so we divide to keep units consistent.
_USD_TO_MILLIONS = Decimal("1000000")

# Cache the (heavy) per-flow responses for the duration of one ingestion process so the
# many partner / product series share just one HTTP call per (flow, detail) instead of
# one each. Keyed by (flow, detail, period_from, period_to).
_FLOW_CACHE: dict[tuple[str, str, str, str], dict[str, dict[int, Decimal]]] = {}

# Comex Stat detail key -> the per-row JSON field used to identify each group. We group
# trade either by partner country ("country", folded by country name) or by product
# chapter (SH2, "chapter", folded by the 2-digit chapter code so short config codes like
# "27" select "Combustíveis minerais..." without repeating its long official name).
_DETAIL_KEY_FIELD = {
    "country": "country",
    "chapter": "chapterCode",
    "economicBlock": "economicBlock",
}


def _fetch_flow(
    flow: str, period_from: str, period_to: str, detail: str = "country"
) -> dict[str, dict[int, Decimal]]:
    """Return {group_name: {year: fob_us$_millions}} for one flow/detail over a period.

    ``detail`` selects the Comex Stat breakout: "country" (partner), "chapter" (SH2
    product), or "economicBlock" (trade bloc, e.g. Mercosul). One request covers every
    group and every year in the period.
    """
    cache_key = (flow, detail, period_from, period_to)
    cached = _FLOW_CACHE.get(cache_key)
    if cached is not None:
        return cached

    key_field = _DETAIL_KEY_FIELD[detail]
    payload = {
        "flow": flow,
        "monthDetail": False,
        "period": {"from": period_from, "to": period_to},
        "filters": [],
        "details": [detail],
        "metrics": ["metricFOB"],
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "arandu.aiBrasil/0.1",
    }
    response = requests.post(COMEXSTAT_URL, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    rows = response.json().get("data", {}).get("list", [])

    by_group: dict[str, dict[int, Decimal]] = {}
    for item in rows:
        group = item.get(key_field)
        raw_year = item.get("year")
        raw_fob = item.get("metricFOB")
        if group in (None, "") or raw_year in (None, "") or raw_fob in (None, ""):
            continue
        # Chapter codes arrive 0-padded as strings ("02"); normalize to a plain string.
        group = str(group).strip()
        year = int(raw_year)
        fob_millions = Decimal(str(raw_fob)) / _USD_TO_MILLIONS
        by_group.setdefault(group, {})[year] = (
            by_group.get(group, {}).get(year, Decimal(0)) + fob_millions
        )

    _FLOW_CACHE[cache_key] = by_group
    return by_group


def fetch_comexstat(series: dict[str, Any]) -> list[Observation]:
    """Fetch yearly FOB trade for one group (or the residual remainder) and flow.

    Two modes, selected by which config key is present:

    Partner mode (default; ``comexstat_partner`` set):
      comexstat_flow    : 'export' or 'import'.
      comexstat_partner : exact Comex Stat country name to isolate (e.g. 'China'),
                          or 'Demais' to sum every country NOT listed in
                          comexstat_named_partners.
      comexstat_named_partners : list of partner names used to define the 'Demais'
                          remainder (only read when comexstat_partner == 'Demais').

    Product mode (``comexstat_product_chapter`` set):
      comexstat_flow    : 'export' or 'import'.
      comexstat_product_chapter : 2-digit SH2 chapter code to isolate (e.g. '12' for
                          soybeans/oilseeds), or 'Demais' to sum every chapter NOT in
                          comexstat_named_chapters.
      comexstat_named_chapters : list of SH2 codes used to define the 'Demais' remainder.

    Economic-block mode (``comexstat_block`` set):
      comexstat_flow    : 'export' or 'import'.
      comexstat_block   : exact Comex Stat economic-block name to isolate (e.g.
                          'Mercado Comum do Sul - Mercosul'). The bloc breakout already
                          reflects each bloc's membership over time, so no member list is
                          needed and there is no 'Demais' remainder here (blocs overlap:
                          a country can sit in several blocs, so blocs do not sum to the
                          total — only single-bloc isolation is meaningful).

    start_date / end_date bound the request period (years used) in all modes.
    """
    flow = series["comexstat_flow"]
    start = series.get("start_date", "2010-01-01")
    end = series.get("end_date") or f"{date.today().year}-12-31"
    period_from = f"{str(start)[:4]}-01"
    period_to = f"{str(end)[:4]}-12"

    if "comexstat_product_chapter" in series:
        detail = "chapter"
        target = str(series["comexstat_product_chapter"])
        named = {str(c) for c in series.get("comexstat_named_chapters", [])}
        raw_kind = "chapter"
    elif "comexstat_block" in series:
        detail = "economicBlock"
        target = series["comexstat_block"]
        named = set()
        raw_kind = "block"
    else:
        detail = "country"
        target = series["comexstat_partner"]
        named = set(series.get("comexstat_named_partners", []))
        raw_kind = "partner"

    by_group = _fetch_flow(flow, period_from, period_to, detail=detail)

    if target == "Demais":
        totals: dict[int, Decimal] = {}
        for group, year_values in by_group.items():
            if group in named:
                continue
            for year, value in year_values.items():
                totals[year] = totals.get(year, Decimal(0)) + value
        year_values = totals
    else:
        year_values = by_group.get(target, {})

    observations: list[Observation] = []
    for year, value in year_values.items():
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=date(year, 1, 1),
                value=value,
                original_value=value,
                raw_payload={"flow": flow, raw_kind: target, "year": year},
            )
        )
    return observations
