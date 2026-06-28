from datetime import date
from decimal import Decimal
from typing import Any

import arandu.sources.bcb_spi as spi
from arandu.sources.bcb_spi import fetch_bcb_spi_pix


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


# Two full months plus a partial latest month. Daily rows must sum per calendar month,
# stamp on the first of the month, and the latest (incomplete) month must be dropped.
PAYLOAD = {
    "value": [
        {"Data": "2026-01-10", "Quantidade": 100, "Total": 2000.0},
        {"Data": "2026-01-20", "Quantidade": 300, "Total": 4000.0},
        {"Data": "2026-02-05", "Quantidade": 500, "Total": 6000.0},
        # March is the latest month -> treated as still running -> dropped.
        {"Data": "2026-03-01", "Quantidade": 999, "Total": 9999.0},
    ]
}


def _fetch(aggregate: str) -> list:
    series = {"series_id": f"pix_{aggregate}", "spi_aggregate": aggregate}
    return sorted(fetch_bcb_spi_pix(series), key=lambda o: o.date)


def test_pix_count_sums_to_monthly_millions_and_drops_partial_month(monkeypatch) -> None:
    monkeypatch.setattr(spi.requests, "get", lambda *a, **k: FakeResponse(PAYLOAD))
    obs = _fetch("pix_count")

    # Only the two complete months remain (March dropped).
    assert [o.date for o in obs] == [date(2026, 1, 1), date(2026, 2, 1)]
    # Jan: (100 + 300) / 1e6 transactions; Feb: 500 / 1e6.
    assert obs[0].value == Decimal("400") / Decimal("1000000")
    assert obs[1].value == Decimal("500") / Decimal("1000000")


def test_pix_value_converts_thousands_to_billions_and_drops_partial_month(monkeypatch) -> None:
    monkeypatch.setattr(spi.requests, "get", lambda *a, **k: FakeResponse(PAYLOAD))
    obs = _fetch("pix_value")

    assert [o.date for o in obs] == [date(2026, 1, 1), date(2026, 2, 1)]
    # Total is in R$ thousands; /1e6 -> R$ billions. Jan: (2000 + 4000) thousands.
    assert obs[0].value == Decimal("6000.0") / Decimal("1000000")
    assert obs[1].value == Decimal("6000.0") / Decimal("1000000")
