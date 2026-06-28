from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from arandu.db import Observation

# A connector for one-off, hand-curated reference figures published by an official source as a
# static study/table rather than as an updatable time series (e.g. a BCB special-study
# snapshot). The exact figures live in series.yml under `static_observations`, so every value
# is auditable next to its source citation and nothing is fetched or interpolated. There is no
# network call: by construction this connector cannot drift or fabricate — it re-emits exactly
# the published numbers recorded in the config.
#
# `static_observations` is a list of {date, value} entries (usually one entry: a single date).
# Because raw.observations is keyed on (series_id, date), a multi-category published table is
# modelled as one static series per category, each with its own single observation — mirroring
# how the categorical Comex Stat partner charts use one series per partner.
#
# This is deliberately NOT a way to fake a time series from a single estimate: it is meant for
# genuinely static, single-point reference data, and the chart that uses it is labelled as a
# one-off estimate that the daily cron does not update.


def fetch_static_table(series: dict[str, Any]) -> list[Observation]:
    rows = series.get("static_observations")
    if not rows:
        raise ValueError("static_table connector requires a non-empty static_observations list")

    observations: list[Observation] = []
    for row in rows:
        raw_date = row["date"]
        obs_date = raw_date if isinstance(raw_date, date) else date.fromisoformat(str(raw_date))
        value = Decimal(str(row["value"]))
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=obs_date,
                value=value,
                original_value=value,
                raw_payload={"static": True, "source_note": row.get("note")},
            )
        )
    return observations
