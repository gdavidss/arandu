from datetime import date
from decimal import Decimal
from typing import Any

import arandu.sources.pix_dict as pd
from arandu.sources.pix_dict import fetch_pix_dict_usuarios


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


PAYLOAD = {
    "value": [
        {
            "DataGraficosPix": "2021-07-31",
            "qtdUsuariosPessoaFisica": 96000000,
            "qtdUsuariosPessoaJuridica": 6000000,
            "qtdUsuariosCadastradosDICTTotal": 102000000,
        },
        {
            "DataGraficosPix": "2021-08-31",
            "qtdUsuariosPessoaFisica": 100000000,
            "qtdUsuariosPessoaJuridica": None,  # dropped for the PJ series
            "qtdUsuariosCadastradosDICTTotal": 107000000,
        },
    ]
}


def test_dict_users_to_millions_and_first_of_month(monkeypatch) -> None:
    monkeypatch.setattr(pd.requests, "get", lambda *a, **k: FakeResponse(PAYLOAD))
    series = {"series_id": "pix_pf", "dict_field": "qtdUsuariosPessoaFisica"}
    obs = sorted(fetch_pix_dict_usuarios(series), key=lambda o: o.date)
    # End-of-month snapshot stamped on the first of the month; /1e6 -> millions.
    assert [o.date for o in obs] == [date(2021, 7, 1), date(2021, 8, 1)]
    assert obs[0].value == Decimal("96000000") / Decimal("1000000")
    assert obs[1].value == Decimal("100000000") / Decimal("1000000")


def test_dict_users_drops_null_field(monkeypatch) -> None:
    monkeypatch.setattr(pd.requests, "get", lambda *a, **k: FakeResponse(PAYLOAD))
    series = {"series_id": "pix_pj", "dict_field": "qtdUsuariosPessoaJuridica"}
    obs = fetch_pix_dict_usuarios(series)
    # Only the July row has a PJ value; August is null and dropped.
    assert [o.date for o in obs] == [date(2021, 7, 1)]
    assert obs[0].value == Decimal("6000000") / Decimal("1000000")
