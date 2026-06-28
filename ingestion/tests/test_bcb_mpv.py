from datetime import date
from decimal import Decimal
from typing import Any

import arandu.sources.bcb_mpv as mpv
from arandu.sources.bcb_mpv import fetch_bcb_mpv_cartoes, fetch_bcb_mpv_monthly


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


MONTHLY = {
    "value": [
        {"AnoMes": "202601", "valorPix": 2000.0, "quantidadePix": 5000.0},
        {"AnoMes": "202602", "valorPix": 3000.0, "quantidadePix": 6000.0},
        {"AnoMes": "202603", "valorPix": None, "quantidadePix": ""},  # skipped
    ]
}


def test_monthly_value_thousands_of_millions_to_billions(monkeypatch) -> None:
    monkeypatch.setattr(mpv.requests, "get", lambda *a, **k: FakeResponse(MONTHLY))
    series = {"series_id": "pix_v", "mpv_field": "valorPix", "mpv_divisor": 1000}
    obs = sorted(fetch_bcb_mpv_monthly(series), key=lambda o: o.date)
    # R$ milhões / 1000 -> R$ bilhões; first day of month; null/empty rows dropped.
    assert [o.date for o in obs] == [date(2026, 1, 1), date(2026, 2, 1)]
    assert obs[0].value == Decimal("2000.0") / Decimal("1000")
    assert obs[1].value == Decimal("3000.0") / Decimal("1000")


def test_monthly_count_thousands_to_millions(monkeypatch) -> None:
    monkeypatch.setattr(mpv.requests, "get", lambda *a, **k: FakeResponse(MONTHLY))
    series = {"series_id": "pix_q", "mpv_field": "quantidadePix", "mpv_divisor": 1000}
    obs = sorted(fetch_bcb_mpv_monthly(series), key=lambda o: o.date)
    assert obs[0].value == Decimal("5000.0") / Decimal("1000")


CARTOES = {
    "value": [
        # Two segments, same quarter and função -> summed.
        {"trimestre": "20231", "nomeFuncao": "Crédito", "valorTransacoesNacionais": 1.0e9},
        {"trimestre": "20231", "nomeFuncao": "Crédito", "valorTransacoesNacionais": 2.0e9},
        # Different função -> ignored for the Crédito series.
        {"trimestre": "20231", "nomeFuncao": "Débito", "valorTransacoesNacionais": 9.0e9},
        {"trimestre": "20232", "nomeFuncao": "Crédito", "valorTransacoesNacionais": 4.0e9},
    ]
}


def test_cartoes_sums_by_funcao_and_quarter(monkeypatch) -> None:
    monkeypatch.setattr(mpv.requests, "get", lambda *a, **k: FakeResponse(CARTOES))
    series = {
        "series_id": "cred_v",
        "mpv_funcao": "Crédito",
        "mpv_field": "valorTransacoesNacionais",
        "mpv_divisor": 1000000000,
    }
    obs = sorted(fetch_bcb_mpv_cartoes(series), key=lambda o: o.date)
    # 20231 -> first day of Q1 (Jan); 20232 -> first day of Q2 (Apr).
    assert [o.date for o in obs] == [date(2023, 1, 1), date(2023, 4, 1)]
    # (1e9 + 2e9) / 1e9 = 3 (Débito's 9e9 excluded); Q2 = 4.
    assert obs[0].value == Decimal("3")
    assert obs[1].value == Decimal("4")
