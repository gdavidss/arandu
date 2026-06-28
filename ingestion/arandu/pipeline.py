from __future__ import annotations

import logging
from typing import Any

from arandu.db import (
    connect,
    create_run,
    finish_run,
    mark_series_checked,
    record_error,
    update_series_window,
    upsert_observations,
    upsert_series,
    upsert_sources,
)
from arandu.sources import CONNECTORS

logger = logging.getLogger(__name__)


def run_ingestion(config: dict[str, Any]) -> dict[str, int | str]:
    attempted = 0
    succeeded = 0
    upserted_total = 0

    with connect() as conn:
        run_id = create_run(conn)
        upsert_sources(conn, config["sources"])
        conn.commit()

        for series in config["series"]:
            if series.get("enabled", True) is False:
                continue
            attempted += 1
            connector_name = series.get("connector")
            connector = CONNECTORS.get(connector_name)
            try:
                if connector is None:
                    raise ValueError(f"Unknown connector {connector_name!r}")
                upsert_series(conn, series)
                observations = connector(series)
                inserted = upsert_observations(conn, observations)
                update_series_window(conn, series["series_id"])
                conn.commit()
                succeeded += 1
                upserted_total += inserted
                logger.info(
                    "ingested %s observations for %s",
                    inserted,
                    series["series_id"],
                )
            except Exception as exc:  # noqa: BLE001 - per-series isolation is deliberate.
                conn.rollback()
                with connect() as error_conn:
                    upsert_sources(error_conn, config["sources"])
                    try:
                        upsert_series(error_conn, series)
                        mark_series_checked(error_conn, series["series_id"])
                    except Exception:
                        logger.exception("failed to mark %s checked", series.get("series_id"))
                    record_error(
                        error_conn,
                        run_id,
                        source_id=series.get("source_id"),
                        series_id=series.get("series_id"),
                        message=str(exc),
                        details={"connector": connector_name},
                    )
                    error_conn.commit()
                logger.exception("failed to ingest %s", series.get("series_id"))

        status = "success" if succeeded == attempted else "partial" if succeeded else "failed"
        finish_run(
            conn,
            run_id,
            status=status,
            series_attempted=attempted,
            series_succeeded=succeeded,
            observations_upserted=upserted_total,
        )
        conn.commit()

    return {
        "status": status,
        "series_attempted": attempted,
        "series_succeeded": succeeded,
        "observations_upserted": upserted_total,
    }
