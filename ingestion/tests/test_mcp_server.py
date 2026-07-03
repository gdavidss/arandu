from datetime import date
from decimal import Decimal
from typing import Any

import arandu.mcp_server as mcp_server
from arandu.mcp_server import get_series, get_series_sources, list_series, search_series


class FakeCursor:
    """Returns one canned result set per execute(), recording each call."""

    def __init__(self, result_sets: list[list[tuple]]) -> None:
        self._result_sets = result_sets
        self._current: list[tuple] = []
        self.executed: list[tuple[str, Any]] = []

    def execute(self, sql: str, params: Any = None) -> None:
        self.executed.append((sql, params))
        self._current = self._result_sets.pop(0)

    def fetchall(self) -> list[tuple]:
        return self._current

    def fetchone(self) -> tuple | None:
        return self._current[0] if self._current else None

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class FakeConnection:
    def __init__(self, result_sets: list[list[tuple]]) -> None:
        self.cursor_obj = FakeCursor(result_sets)

    def cursor(self) -> FakeCursor:
        return self.cursor_obj

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


def _install(monkeypatch, result_sets: list[list[tuple]]) -> FakeConnection:
    conn = FakeConnection(result_sets)
    monkeypatch.setattr(mcp_server, "connect", lambda: conn)
    return conn


def _catalog_row() -> tuple:
    return (
        "bcb_sgs_selic_target",
        "Selic target set by Copom",
        "SGS",
        "Banco Central do Brasil",
        "% a.a.",
        "daily",
        "Policy interest rate target",
        date(2026, 7, 2),
        Decimal("14.25"),
        "https://www3.bcb.gov.br/sgspub",
    )


def test_list_series_returns_catalog_dicts(monkeypatch) -> None:
    _install(monkeypatch, [[_catalog_row()]])

    result = list_series()

    assert len(result) == 1
    entry = result[0]
    assert entry["series_id"] == "bcb_sgs_selic_target"
    assert entry["institution"] == "Banco Central do Brasil"
    # DB scalars are converted to JSON-friendly types.
    assert entry["latest_date"] == "2026-07-02"
    assert entry["latest_value"] == 14.25
    assert set(entry) == {
        "series_id",
        "name",
        "source_name",
        "institution",
        "unit",
        "frequency",
        "concept",
        "latest_date",
        "latest_value",
        "source_url",
    }


def test_search_series_matches_with_ilike_on_four_fields(monkeypatch) -> None:
    conn = _install(monkeypatch, [[_catalog_row()]])

    result = search_series("selic")

    sql, params = conn.cursor_obj.executed[0]
    assert sql.lower().count("ilike") == 4
    assert params == ("%selic%",) * 4
    assert result[0]["series_id"] == "bcb_sgs_selic_target"


def test_get_series_returns_metadata_and_observations(monkeypatch) -> None:
    meta_row = _catalog_row() + (
        "Brazil",
        "not seasonally adjusted",
        None,
        None,
        date(1999, 3, 5),
        date(2026, 7, 2),
        None,
    )
    obs_rows = [
        (date(2026, 6, 30), Decimal("14.25")),
        (date(2026, 7, 1), Decimal("14.25")),
    ]
    _install(monkeypatch, [[meta_row], obs_rows])

    result = get_series("bcb_sgs_selic_target")

    assert result["series"]["series_id"] == "bcb_sgs_selic_target"
    assert result["series"]["geography"] == "Brazil"
    assert result["observations"] == [
        {"date": "2026-06-30", "value": 14.25},
        {"date": "2026-07-01", "value": 14.25},
    ]
    assert result["observation_count"] == 2
    assert result["truncated"] is False


def test_get_series_applies_date_window(monkeypatch) -> None:
    meta_row = _catalog_row() + (None,) * 7
    conn = _install(monkeypatch, [[meta_row], []])

    get_series("bcb_sgs_selic_target", start_date="2024-01-01", end_date="2024-12-31")

    obs_sql, obs_params = conn.cursor_obj.executed[1]
    assert "date >= %s" in obs_sql
    assert "date <= %s" in obs_sql
    assert obs_params == [
        "bcb_sgs_selic_target",
        "2024-01-01",
        "2024-12-31",
        mcp_server.MAX_OBSERVATIONS,
    ]


def test_get_series_unknown_id_returns_clear_error(monkeypatch) -> None:
    _install(monkeypatch, [[]])

    result = get_series("nope_not_a_series")

    assert set(result) == {"error"}
    assert "nope_not_a_series" in result["error"]
    assert "search_series" in result["error"]


def test_get_series_sources_lists_institutions(monkeypatch) -> None:
    _install(
        monkeypatch,
        [
            [
                ("Banco Central do Brasil", "SGS", "https://www3.bcb.gov.br/sgspub"),
                ("IBGE", "SIDRA", "https://sidra.ibge.gov.br"),
            ]
        ],
    )

    result = get_series_sources()

    assert result == [
        {
            "institution": "Banco Central do Brasil",
            "source_name": "SGS",
            "source_url": "https://www3.bcb.gov.br/sgspub",
        },
        {
            "institution": "IBGE",
            "source_name": "SIDRA",
            "source_url": "https://sidra.ibge.gov.br",
        },
    ]
