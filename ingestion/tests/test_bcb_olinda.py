from datetime import date
from decimal import Decimal
from typing import Any

import arandu.sources.bcb_olinda as olinda
from arandu.sources.bcb_olinda import fetch_bcb_olinda_expectativas


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_olinda_resamples_to_last_survey_of_each_month(monkeypatch) -> None:
    # Two surveys in May (keep the later one), one in June. Daily -> monthly collapse.
    payload = {
        "value": [
            {"Data": "2026-05-04", "Mediana": 4.10},
            {"Data": "2026-05-29", "Mediana": 4.25},
            {"Data": "2026-06-19", "Mediana": "4,29"},
        ]
    }
    captured: dict[str, Any] = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return FakeResponse(payload)

    monkeypatch.setattr(olinda.requests, "get", fake_get)

    series = {
        "series_id": "bcb_focus_ipca_12m_ahead",
        "olinda_resource": "ExpectativasMercadoInflacao12Meses",
        "olinda_indicador": "IPCA",
        "olinda_field": "Mediana",
        "olinda_filters": {"Suavizada": "S", "baseCalculo": 0},
    }
    obs = sorted(fetch_bcb_olinda_expectativas(series), key=lambda o: o.date)

    # One observation per month, stamped on the first day of the month.
    assert [o.date for o in obs] == [date(2026, 5, 1), date(2026, 6, 1)]
    # May keeps the 29th reading (last of month), not the 4th.
    assert obs[0].value == Decimal("4.25")
    # Brazilian-format decimal string is parsed too.
    assert obs[1].value == Decimal("4.29")

    # The OData filter is in the URL, percent-encoded (spaces as %20, never '+').
    url = captured["url"]
    assert "+" not in url
    assert "Indicador%20eq%20'IPCA'" in url
    assert "Suavizada%20eq%20'S'" in url
    assert "baseCalculo%20eq%200" in url
