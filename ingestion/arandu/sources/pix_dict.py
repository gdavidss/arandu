from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote

import requests

from arandu.db import Observation
from arandu.parsing import parse_decimal

# Public BCB Olinda OData service "Estatísticas do Pix" (Pix_DadosAbertos). The
# PixUsuariosCadastradosDICT resource is a monthly series of the stock of users registered
# in the DICT (Diretório de Identificadores de Contas Transacionais — the Pix key
# directory), split into pessoa física, pessoa jurídica and total. Each end-of-month
# snapshot is stamped on the first day of that month so it lines up with the rest of the
# monthly dashboard. This resource takes no parameters and returns the full history.
PIX_DICT_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
    "PixUsuariosCadastradosDICT?$format=json"
)
_SAFE = "',()"


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value.strip()[:10])


def fetch_pix_dict_usuarios(series: dict[str, Any]) -> list[Observation]:
    """Monthly stock of Pix DICT-registered users for one segment.

    Config keys:
      dict_field  : source field to read, one of qtdUsuariosPessoaFisica,
                    qtdUsuariosPessoaJuridica, qtdUsuariosCadastradosDICTTotal.
      dict_divisor: factor to the dashboard unit (default 1e6 -> millions of users).
    """
    field = series["dict_field"]
    divisor = parse_decimal(series.get("dict_divisor", 1000000))
    # Build the query by hand so the literal '$' survives (requests would re-encode it).
    base, _, query = PIX_DICT_URL.partition("?")
    safe_query = "&".join(
        f"{k}={quote(v, safe=_SAFE)}" for k, v in (p.split("=", 1) for p in query.split("&"))
    )
    url = f"{base}?{safe_query}"
    headers = {"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"}
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    rows = response.json().get("value", [])

    observations: list[Observation] = []
    for item in rows:
        raw_date = item.get("DataGraficosPix")
        raw_value = item.get(field)
        if not raw_date or raw_value in (None, ""):
            continue
        month_key = _parse_iso_date(raw_date).replace(day=1)
        value = parse_decimal(raw_value) / divisor
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=month_key,
                value=value,
                original_value=value,
                raw_payload={"field": field, "raw": str(raw_value), "snapshot": raw_date},
            )
        )
    return observations
