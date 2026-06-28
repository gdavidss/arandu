from datetime import date
from decimal import Decimal

from arandu.db import Observation, dedupe_observations, upsert_observations


def test_dedupe_observations_keeps_latest_value_for_same_series_date() -> None:
    rows = dedupe_observations(
        [
            Observation("s1", date(2024, 1, 1), Decimal("1.0")),
            Observation("s1", date(2024, 1, 1), Decimal("2.0")),
            Observation("s1", date(2024, 2, 1), Decimal("3.0")),
        ]
    )

    assert rows == [
        Observation("s1", date(2024, 1, 1), Decimal("2.0")),
        Observation("s1", date(2024, 2, 1), Decimal("3.0")),
    ]


class FakeCursor:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...]) -> None:
        self.executed.append((sql, params))


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


def test_upsert_observations_writes_one_row_per_series_date() -> None:
    conn = FakeConnection()

    inserted = upsert_observations(
        conn,  # type: ignore[arg-type]
        [
            Observation("s1", date(2024, 1, 1), Decimal("1.0")),
            Observation("s1", date(2024, 1, 1), Decimal("2.0")),
        ],
    )

    assert inserted == 1
    assert len(conn.cursor_instance.executed) == 1
    _, params = conn.cursor_instance.executed[0]
    assert params[:3] == ("s1", date(2024, 1, 1), Decimal("2.0"))
