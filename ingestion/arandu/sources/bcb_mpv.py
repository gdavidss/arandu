from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from urllib.parse import quote

import requests

from arandu.db import Observation
from arandu.parsing import parse_decimal

# Public BCB Olinda OData service "Estatísticas de Meios de Pagamentos" (MPV_DadosAbertos).
# Separate API from SGS and from the SPI service. Two resources are used here, both exposed
# as OData FunctionImports that REQUIRE a single mandatory parameter; passing the empty
# string returns the full history (the parameter is a ">= period" lower bound):
#
#   MeiosdePagamentosMensalDA(AnoMes='')        -> monthly rows from 2002-04, fields per
#       instrument: quantidade<Inst> (em milhares) and valor<Inst> (R$ milhões), for
#       Pix, TED, TEC, Cheque, Boleto, DOC.
#   Quantidadeetransacoesdecartoes(trimestre='') -> quarterly rows from 2011Q1, one row per
#       (bandeira, função, produto, modalidade); we aggregate by função (Crédito/Débito/
#       Pré-Pago) over national transactions: qtdTransacoesNacionais (count) and
#       valorTransacoesNacionais (R$).
#
# Units are normalised to the dashboard's conventions and count vs value are always kept as
# SEPARATE series (different units, never a dual axis).
MPV_BASE = "https://olinda.bcb.gov.br/olinda/servico/MPV_DadosAbertos/versao/v1/odata/"

# requests' default param encoding turns "%24" into "%2524" and "+" into a space the Olinda
# parser rejects, so we build the query string by hand with quote() (spaces -> %20), exactly
# like the existing Olinda connectors.
_SAFE = "',()"


def _odata_get(resource_call: str, params: dict[str, str]) -> list[dict[str, Any]]:
    query = "&".join(f"{key}={quote(value, safe=_SAFE)}" for key, value in params.items())
    url = f"{MPV_BASE}{resource_call}?{query}"
    headers = {"Accept": "application/json", "User-Agent": "arandu.aiBrasil/0.1"}
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json().get("value", [])


def _anomes_to_date(value: str) -> date:
    # AnoMes is "AAAAMM"; stamp on the first day of the month.
    text = str(value).strip()
    return date(int(text[:4]), int(text[4:6]), 1)


def _trimestre_to_date(value: str) -> date:
    # trimestre is "AAAAT" (e.g. "20231"); stamp on the first day of the quarter.
    text = str(value).strip()
    quarter = int(text[-1])
    return date(int(text[:4]), (quarter - 1) * 3 + 1, 1)


def fetch_bcb_mpv_monthly(series: dict[str, Any]) -> list[Observation]:
    """Monthly value or count for one payment instrument from MeiosdePagamentosMensalDA.

    Config keys:
      mpv_field   : exact source field, e.g. 'valorPix' (R$ milhões) or 'quantidadePix'
                    (em milhares).
      mpv_divisor : factor applied to the raw figure to reach the dashboard unit. Value
                    fields (R$ milhões) use 1000 -> R$ bilhões. Count fields (milhares)
                    use 1000 -> milhões de transações.
    """
    field = series["mpv_field"]
    divisor = Decimal(str(series.get("mpv_divisor", 1)))
    rows = _odata_get("MeiosdePagamentosMensalDA(AnoMes='')", {"$format": "json"})

    observations: list[Observation] = []
    for item in rows:
        raw_period = item.get("AnoMes")
        raw_value = item.get(field)
        if not raw_period or raw_value in (None, ""):
            continue
        value = parse_decimal(raw_value) / divisor
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=_anomes_to_date(raw_period),
                value=value,
                original_value=value,
                raw_payload={"AnoMes": raw_period, "field": field, "raw": str(raw_value)},
            )
        )
    return observations


def fetch_bcb_mpv_cartoes(series: dict[str, Any]) -> list[Observation]:
    """Quarterly card transactions for one função (Crédito/Débito/Pré-Pago).

    The source is disaggregated by bandeira/função/produto/modalidade; we sum the national
    transactions for the requested função within each quarter.

    Config keys:
      mpv_funcao  : função to keep, one of 'Crédito', 'Débito', 'Pré-Pago'.
      mpv_field   : 'valorTransacoesNacionais' (R$) or 'qtdTransacoesNacionais' (count).
      mpv_divisor : factor to the dashboard unit. Value (R$) uses 1e9 -> R$ bilhões;
                    count uses 1e6 -> milhões de transações.
    """
    funcao = series["mpv_funcao"]
    field = series["mpv_field"]
    divisor = Decimal(str(series.get("mpv_divisor", 1)))
    rows = _odata_get("Quantidadeetransacoesdecartoes(trimestre='')", {"$format": "json"})

    by_quarter: dict[date, Decimal] = {}
    for item in rows:
        if item.get("nomeFuncao") != funcao:
            continue
        raw_period = item.get("trimestre")
        raw_value = item.get(field)
        if not raw_period or raw_value in (None, ""):
            continue
        quarter = _trimestre_to_date(raw_period)
        by_quarter[quarter] = by_quarter.get(quarter, Decimal(0)) + parse_decimal(raw_value)

    observations: list[Observation] = []
    for quarter, raw_total in by_quarter.items():
        value = raw_total / divisor
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=quarter,
                value=value,
                original_value=value,
                raw_payload={"funcao": funcao, "field": field, "raw_sum": str(raw_total)},
            )
        )
    return observations
