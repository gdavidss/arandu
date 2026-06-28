from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from arandu.db import connect


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    return value


def export_dashboard_data(output_path: str | Path) -> dict[str, Any]:
    catalog_rows: dict[str, dict[str, Any]] = {}
    observations: dict[str, list[dict[str, Any]]] = defaultdict(list)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  series_id,
                  name,
                  source_series_code,
                  source_name,
                  institution,
                  unit,
                  frequency,
                  concept,
                  geography,
                  seasonal_adjustment,
                  transformation,
                  scope,
                  method,
                  start_date,
                  end_date,
                  latest_date,
                  latest_value,
                  last_successful_update_at,
                  source_url,
                  notes
                from analytics.series_latest
                order by source_name, name
                """
            )
            for row in cur.fetchall():
                columns = [desc.name for desc in cur.description]
                item = dict(zip(columns, row, strict=True))
                catalog_rows[item["series_id"]] = {
                    _camel(key): _json_value(value) for key, value in item.items()
                }

        with conn.cursor() as cur:
            cur.execute(
                """
                select
                  series_id,
                  date,
                  value
                from analytics.observations_enriched
                where date >= current_date - interval '12 years'
                order by series_id, date
                """
            )
            for series_id, obs_date, value in cur.fetchall():
                observations[series_id].append(
                    {"date": obs_date.isoformat(), "value": float(value)}
                )

    series = {}
    for series_id, metadata in catalog_rows.items():
        series[series_id] = {
            **metadata,
            "observations": observations.get(series_id, []),
        }

    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "series": series,
        "catalog": list(series.values()),
        "counts": {
            "configuredSeries": len(catalog_rows),
            "populatedSeries": sum(1 for item in series.values() if item["observations"]),
            "observations": sum(len(item["observations"]) for item in series.values()),
        },
    }

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also write a tidy long-format CSV of every observation (the "download all data" file).
    export_full_csv(target.parent / "arandu-data.csv")
    return payload["counts"]


def export_full_csv(output_path: str | Path) -> int:
    """Write every observation as a tidy long CSV with full metadata per row."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select
              series_id,
              name,
              source_name,
              source_series_code,
              unit,
              frequency,
              concept,
              seasonal_adjustment,
              scope,
              date,
              value
            from analytics.observations_enriched
            order by series_id, date
            """
        )
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "series_id",
                    "serie",
                    "fonte",
                    "codigo_fonte",
                    "unidade",
                    "frequencia",
                    "conceito",
                    "ajuste_sazonal",
                    "escopo",
                    "data",
                    "valor",
                ]
            )
            for row in cur:
                obs_date = row[9]
                writer.writerow([*row[:9], obs_date.isoformat() if obs_date else "", row[10]])
                rows += 1
    return rows


def _camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])
