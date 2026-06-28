from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time

from arandu.config import load_config
from arandu.db import apply_sql_file, connect, default_dsn
from arandu.export_dashboard_data import export_dashboard_data
from arandu.pipeline import run_ingestion

logger = logging.getLogger(__name__)

DEFAULT_DASHBOARD_DATA_PATH = "/frontend-public/dashboard-data.json"
SLEEP_CHUNK_SECONDS = 60


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"false", "0", "no", "off"}


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("invalid %s=%r; using default %s", name, raw, default)
        return default


def run_refresh_cycle(dashboard_data_path: str) -> None:
    """Run one warehouse refresh and re-export the dashboard JSON.

    Ingestion is the critical step; the export is best-effort so a missing
    output path never aborts the cycle. Callers wrap this so a failure here
    is logged and the scheduler loop survives to the next run.
    """
    summary = run_ingestion(load_config())
    logger.info("ingestion summary: %s", summary)
    try:
        counts = export_dashboard_data(dashboard_data_path)
        logger.info("exported dashboard data to %s: %s", dashboard_data_path, counts)
    except Exception:  # noqa: BLE001 - export is secondary; ingestion already succeeded.
        logger.warning(
            "dashboard data export to %s failed; warehouse refresh kept",
            dashboard_data_path,
            exc_info=True,
        )


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(prog="arandu")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("worker", help="keep the ingestion container alive as a job runner")
    sub.add_parser("ingest", help="fetch configured public series into the warehouse")
    sub.add_parser("migrate", help="apply warehouse schema and analytical views")
    export_parser = sub.add_parser(
        "export-dashboard-data",
        help="export warehouse observations to frontend dashboard JSON",
    )
    export_parser.add_argument(
        "--output",
        default="/frontend-public/dashboard-data.json",
        help="output JSON path",
    )

    args = parser.parse_args(argv)

    if args.command == "worker":
        stop = False

        def handle_stop(_sig: int, _frame: object) -> None:
            nonlocal stop
            stop = True

        signal.signal(signal.SIGTERM, handle_stop)
        signal.signal(signal.SIGINT, handle_stop)

        dashboard_data_path = os.environ.get("DASHBOARD_DATA_PATH", DEFAULT_DASHBOARD_DATA_PATH)
        interval_hours = _env_float("REFRESH_INTERVAL_HOURS", 24.0)
        interval_seconds = max(interval_hours * 3600.0, 0.0)
        logger.info(
            "ingestion worker started; refreshing every %s h, export -> %s",
            interval_hours,
            dashboard_data_path,
        )

        next_run = 0.0 if _env_bool("REFRESH_ON_START", True) else interval_seconds
        while not stop:
            if next_run <= 0.0:
                try:
                    run_refresh_cycle(dashboard_data_path)
                except Exception:  # noqa: BLE001 - one bad cycle must not kill the loop.
                    logger.exception("refresh cycle failed; scheduler still alive")
                next_run = interval_seconds
                logger.info("next refresh in %s h", interval_hours)
            # Sleep in short chunks so SIGTERM/SIGINT stops the loop promptly.
            chunk = min(SLEEP_CHUNK_SECONDS, next_run) if next_run > 0 else SLEEP_CHUNK_SECONDS
            time.sleep(chunk)
            next_run -= chunk
        logger.info("ingestion worker stopping")
        return 0

    if args.command == "migrate":
        with connect(default_dsn()) as conn:
            apply_sql_file(conn, "/warehouse-init/01_schema.sql")
            apply_sql_file(conn, "/warehouse-init/02_views.sql")
        logging.info("warehouse schema and views applied")
        return 0

    if args.command == "ingest":
        config = load_config()
        summary = run_ingestion(config)
        logging.info("ingestion summary: %s", summary)
        return 0 if summary["series_succeeded"] > 0 else 2

    if args.command == "export-dashboard-data":
        counts = export_dashboard_data(args.output)
        logging.info("exported dashboard data: %s", counts)
        return 0

    return 1


def _self_check() -> None:
    """Sanity-check the env parsing helpers used by the scheduler loop."""
    os.environ.pop("FL_SELFCHECK", None)
    assert _env_bool("FL_SELFCHECK", True) is True
    assert _env_bool("FL_SELFCHECK", False) is False
    for value, expected in (("true", True), ("1", True), ("false", False), ("off", False)):
        os.environ["FL_SELFCHECK"] = value
        assert _env_bool("FL_SELFCHECK", True) is expected, value
    os.environ.pop("FL_SELFCHECK", None)
    assert _env_float("FL_SELFCHECK", 24.0) == 24.0
    os.environ["FL_SELFCHECK"] = "0.5"
    assert _env_float("FL_SELFCHECK", 24.0) == 0.5
    os.environ["FL_SELFCHECK"] = "not-a-number"
    assert _env_float("FL_SELFCHECK", 24.0) == 24.0
    os.environ.pop("FL_SELFCHECK", None)
    print("self-check ok")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        _self_check()
        sys.exit(0)
    sys.exit(main())
