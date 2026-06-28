from datetime import date
from decimal import Decimal
from typing import Any

import arandu.sources.comexstat as comexstat
from arandu.sources.comexstat import fetch_comexstat


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def _payload() -> dict[str, Any]:
    # Whole-US$ FOB, two years, three countries. China is a named partner; Chile and
    # Uruguai fold into "Demais".
    return {
        "data": {
            "list": [
                {"year": "2024", "country": "China", "metricFOB": "94372036594"},
                {"year": "2025", "country": "China", "metricFOB": "99940244710"},
                {"year": "2024", "country": "Chile", "metricFOB": "7000000000"},
                {"year": "2025", "country": "Chile", "metricFOB": "7176227117"},
                {"year": "2025", "country": "Uruguai", "metricFOB": "3000000000"},
            ]
        }
    }


def test_comexstat_named_partner_converts_to_us_millions(monkeypatch) -> None:
    comexstat._FLOW_CACHE.clear()

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse(_payload())

    monkeypatch.setattr(comexstat.requests, "post", fake_post)

    series = {
        "series_id": "comexstat_export_china",
        "comexstat_flow": "export",
        "comexstat_partner": "China",
        "start_date": "2024-01-01",
        "end_date": "2025-12-31",
    }
    obs = sorted(fetch_comexstat(series), key=lambda o: o.date)

    assert [o.date for o in obs] == [date(2024, 1, 1), date(2025, 1, 1)]
    # 94,372,036,594 US$ -> 94,372.036594 US$ millions; stamped on first day of the year.
    assert obs[0].value == Decimal("94372.036594")


def test_comexstat_demais_sums_unnamed_partners(monkeypatch) -> None:
    comexstat._FLOW_CACHE.clear()

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse(_payload())

    monkeypatch.setattr(comexstat.requests, "post", fake_post)

    series = {
        "series_id": "comexstat_export_demais",
        "comexstat_flow": "export",
        "comexstat_partner": "Demais",
        "comexstat_named_partners": ["China"],
        "start_date": "2024-01-01",
        "end_date": "2025-12-31",
    }
    obs = {o.date: o.value for o in fetch_comexstat(series)}

    # 2024 Demais = Chile only = 7,000 M; 2025 Demais = Chile + Uruguai = 7,176.227117 + 3,000.
    assert obs[date(2024, 1, 1)] == Decimal("7000")
    assert obs[date(2025, 1, 1)] == Decimal("10176.227117")


def _chapter_payload() -> dict[str, Any]:
    # Whole-US$ FOB by SH2 chapter. Chapter codes arrive 0-padded as strings. Chapter 12
    # (soja) is a named product; 26 and 17 fold into "Demais produtos".
    return {
        "data": {
            "list": [
                {
                    "year": "2024",
                    "chapterCode": "12",
                    "chapter": "Soja",
                    "metricFOB": "43800000000",
                },
                {
                    "year": "2024",
                    "chapterCode": "26",
                    "chapter": "Minério",
                    "metricFOB": "35100000000",
                },
                {
                    "year": "2024",
                    "chapterCode": "17",
                    "chapter": "Açúcar",
                    "metricFOB": "18800000000",
                },
            ]
        }
    }


def test_comexstat_product_chapter_isolates_one_chapter(monkeypatch) -> None:
    comexstat._FLOW_CACHE.clear()

    def fake_post(url, json=None, headers=None, timeout=None):
        # Product mode must request the "chapter" breakout.
        assert json["details"] == ["chapter"]
        return FakeResponse(_chapter_payload())

    monkeypatch.setattr(comexstat.requests, "post", fake_post)

    series = {
        "series_id": "comexstat_export_prod_soja",
        "comexstat_flow": "export",
        "comexstat_product_chapter": "12",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    obs = {o.date: o.value for o in fetch_comexstat(series)}
    assert obs[date(2024, 1, 1)] == Decimal("43800")


def test_comexstat_product_demais_sums_unnamed_chapters(monkeypatch) -> None:
    comexstat._FLOW_CACHE.clear()

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResponse(_chapter_payload())

    monkeypatch.setattr(comexstat.requests, "post", fake_post)

    series = {
        "series_id": "comexstat_export_prod_demais",
        "comexstat_flow": "export",
        "comexstat_product_chapter": "Demais",
        "comexstat_named_chapters": ["12"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    obs = {o.date: o.value for o in fetch_comexstat(series)}
    # Demais = chapters 26 + 17 = 35,100 + 18,800 = 53,900 M.
    assert obs[date(2024, 1, 1)] == Decimal("53900")


def _block_payload() -> dict[str, Any]:
    # Whole-US$ FOB by economic block. Blocks overlap (a country sits in several), so
    # the connector isolates a single named bloc rather than summing or taking a residual.
    return {
        "data": {
            "list": [
                {
                    "year": "2024",
                    "economicBlock": "Mercado Comum do Sul - Mercosul",
                    "metricFOB": "20238378074",
                },
                {
                    "year": "2024",
                    "economicBlock": "União Europeia - UE",
                    "metricFOB": "48264000000",
                },
            ]
        }
    }


def test_comexstat_block_isolates_one_bloc(monkeypatch) -> None:
    comexstat._FLOW_CACHE.clear()

    def fake_post(url, json=None, headers=None, timeout=None):
        # Block mode must request the "economicBlock" breakout.
        assert json["details"] == ["economicBlock"]
        return FakeResponse(_block_payload())

    monkeypatch.setattr(comexstat.requests, "post", fake_post)

    series = {
        "series_id": "comexstat_export_mercosul",
        "comexstat_flow": "export",
        "comexstat_block": "Mercado Comum do Sul - Mercosul",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    obs = {o.date: o.value for o in fetch_comexstat(series)}
    # 20,238,378,074 US$ -> 20,238.378074 US$ millions, Mercosul only (UE excluded).
    assert obs[date(2024, 1, 1)] == Decimal("20238.378074")
