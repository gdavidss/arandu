from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb


@dataclass(frozen=True)
class Observation:
    series_id: str
    date: date
    value: Decimal
    original_value: Decimal | None = None
    raw_payload: dict[str, Any] | None = None


def default_dsn() -> str:
    return os.environ.get(
        "WAREHOUSE_DSN",
        "postgresql://fiscallens:fiscallens@localhost:5433/fiscallens",
    )


def connect(dsn: str | None = None) -> psycopg.Connection:
    return psycopg.connect(dsn or default_dsn(), autocommit=False)


def apply_sql_file(conn: psycopg.Connection, path: str | Path) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def upsert_sources(conn: psycopg.Connection, sources: dict[str, dict[str, Any]]) -> None:
    with conn.cursor() as cur:
        for source_id, source in sources.items():
            cur.execute(
                """
                insert into raw.sources
                  (source_id, name, institution, url, license_or_terms, notes)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (source_id) do update set
                  name = excluded.name,
                  institution = excluded.institution,
                  url = excluded.url,
                  license_or_terms = excluded.license_or_terms,
                  notes = excluded.notes
                """,
                (
                    source_id,
                    source["name"],
                    source["institution"],
                    source["url"],
                    source.get("license_or_terms"),
                    source.get("notes"),
                ),
            )


def upsert_series(conn: psycopg.Connection, series: dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.series (
              series_id, source_id, source_series_code, name, description, unit,
              frequency, concept, geography, seasonal_adjustment, transformation,
              scope, method, source_url, notes
            )
            values (
              %(series_id)s, %(source_id)s, %(source_series_code)s, %(name)s,
              %(description)s, %(unit)s, %(frequency)s, %(concept)s,
              %(geography)s, %(seasonal_adjustment)s, %(transformation)s,
              %(scope)s, %(method)s, %(source_url)s, %(notes)s
            )
            on conflict (series_id) do update set
              source_id = excluded.source_id,
              source_series_code = excluded.source_series_code,
              name = excluded.name,
              description = excluded.description,
              unit = excluded.unit,
              frequency = excluded.frequency,
              concept = excluded.concept,
              geography = excluded.geography,
              seasonal_adjustment = excluded.seasonal_adjustment,
              transformation = excluded.transformation,
              scope = excluded.scope,
              method = excluded.method,
              source_url = excluded.source_url,
              notes = excluded.notes,
              last_checked_at = now()
            """,
            {
                "series_id": series["series_id"],
                "source_id": series["source_id"],
                "source_series_code": str(series["source_series_code"]),
                "name": series["name"],
                "description": series.get("description"),
                "unit": series["unit"],
                "frequency": series["frequency"],
                "concept": series["concept"],
                "geography": series.get("geography", "Brazil"),
                "seasonal_adjustment": series.get("seasonal_adjustment", "not seasonally adjusted"),
                "transformation": series["transformation"],
                "scope": series.get("scope"),
                "method": series.get("method"),
                "source_url": series.get("source_url"),
                "notes": series.get("notes"),
            },
        )


def dedupe_observations(observations: Iterable[Observation]) -> list[Observation]:
    by_key: dict[tuple[str, date], Observation] = {}
    for obs in observations:
        by_key[(obs.series_id, obs.date)] = obs
    return sorted(by_key.values(), key=lambda item: (item.series_id, item.date))


def upsert_observations(conn: psycopg.Connection, observations: Iterable[Observation]) -> int:
    rows = dedupe_observations(observations)
    if not rows:
        return 0

    with conn.cursor() as cur:
        for obs in rows:
            cur.execute(
                """
                insert into raw.observations
                  (series_id, date, value, original_value, raw_payload)
                values (%s, %s, %s, %s, %s)
                on conflict (series_id, date) do update set
                  value = excluded.value,
                  original_value = excluded.original_value,
                  raw_payload = excluded.raw_payload,
                  revised_at = case
                    when raw.observations.value is distinct from excluded.value
                      or raw.observations.original_value is distinct from excluded.original_value
                    then now()
                    else raw.observations.revised_at
                  end
                """,
                (
                    obs.series_id,
                    obs.date,
                    obs.value,
                    obs.original_value,
                    Jsonb(obs.raw_payload) if obs.raw_payload is not None else None,
                ),
            )

    return len(rows)


def update_series_window(conn: psycopg.Connection, series_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update raw.series s
            set
              start_date = stats.start_date,
              end_date = stats.end_date,
              last_successful_update_at = now(),
              last_checked_at = now()
            from (
              select series_id, min(date) as start_date, max(date) as end_date
              from raw.observations
              where series_id = %s
              group by series_id
            ) stats
            where s.series_id = stats.series_id
            """,
            (series_id,),
        )


def mark_series_checked(conn: psycopg.Connection, series_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "update raw.series set last_checked_at = now() where series_id = %s",
            (series_id,),
        )


def create_run(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("insert into raw.ingestion_runs default values returning run_id")
        run_id = cur.fetchone()[0]
    return int(run_id)


def finish_run(
    conn: psycopg.Connection,
    run_id: int,
    *,
    status: str,
    series_attempted: int,
    series_succeeded: int,
    observations_upserted: int,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update raw.ingestion_runs
            set finished_at = now(),
                status = %s,
                series_attempted = %s,
                series_succeeded = %s,
                observations_upserted = %s
            where run_id = %s
            """,
            (status, series_attempted, series_succeeded, observations_upserted, run_id),
        )


def record_error(
    conn: psycopg.Connection,
    run_id: int,
    *,
    source_id: str | None,
    series_id: str | None,
    message: str,
    details: dict[str, Any] | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.ingestion_errors
              (run_id, source_id, series_id, message, details)
            values (%s, %s, %s, %s, %s)
            """,
            (
                run_id,
                source_id,
                series_id,
                message,
                Jsonb(json.loads(json.dumps(details or {}, ensure_ascii=False))),
            ),
        )
