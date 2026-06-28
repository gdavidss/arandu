from __future__ import annotations

import io
import re
import zipfile
from datetime import date
from decimal import Decimal
from typing import Any
from xml.etree import ElementTree as ET

import requests

from arandu.db import Observation

# Official Receita Federal open-data workbook: federal tax revenue (receita administrada
# pela RFB) by CNAE economic division, one sheet per year. This is a plain XLSX download,
# distinct from BCB SGS / IBGE SIDRA / Tesouro, so it gets its own connector. We parse the
# workbook with the standard library only (an XLSX is a zip of XML), to avoid pulling in a
# heavy Excel dependency (openpyxl/pandas) for a single annual file.
#
# Layout of each yearly sheet (verified against the published file):
#   row 1: "UNIDADE: R$ 1,00"
#   row 2: ANO            | <year> repeated across the division columns
#   row 3: DIVISÃO ECONÔMICA | the 2-digit CNAE division code per column (e.g. "92")
#   rows 4+: one row per receita (tax line); column A is the tax-line label, each later
#            column is that tax line's value for the division above it.
# Division 92 = "Atividades de exploração de jogos de azar e apostas" (gambling and betting),
# which captures the regulated fixed-odds betting market from 2025 (when the betting tax
# took effect): the total jumps from a few million R$/year (legacy) to ~R$10 bi in 2025.
#
# The download URL carries the covered year range (…2011-2025.xlsx). RFB rolls this forward
# once a year, so we probe the most recent few ranges and use the first that exists.
RFB_CNAE_BASE = (
    "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/"
    "receitadata/arrecadacao/arrecadacao-por-divisao-economica-da-cnae/"
    "arrecadacao-por-divisao-economica-cnae-2011-{year}.xlsx"
)

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Top-level tax lines to sum into a division's total receita administrada. The IPI and IRRF
# sub-lines (IPI - Fumo/Bebidas/…, IRRF - Rendimentos do Trabalho/Capital/…) are detail of
# "IPI TOTAL" / "IRRF - Imposto de Renda Retido na Fonte" and must be excluded to avoid
# double counting.
_TOPLEVEL_TAX_LINES = frozenset(
    {
        "Imposto sobre a Importação - II",
        "Imposto sobre a Exportação - IE",
        "IPI TOTAL",
        "Imposto s/ a Renda - Pessoas Jurídicas - IRPJ",
        "IRRF - Imposto de Renda Retido na Fonte",
        "Imposto s/ Operações Financeiras - IOF",
        "Contribuição p/ Financiamento da Seguridade Social - Cofins",
        "Contribuição para o Pis/Pasep",
        "Contribuição Social sobre o Lucro Líquido - CSLL",
        "CPSSS - Contrib. p/ o Plano de Segurid. Social Serv. Público",
        "Outras Receitas Administradas",
        "Contribuição Previdenciária - em DARF (substitutiva)",
        "Contribuição Previdenciária em GPS",
    }
)

# Cache the (heavy) workbook download for the duration of one ingestion process so several
# division series (if added) share a single HTTP fetch + parse.
_WORKBOOK_CACHE: dict[str, dict[int, dict[str, dict[str, Decimal]]]] = {}

_REAL_TO_MILLIONS = Decimal("1000000")


def _column_letter(cell_ref: str) -> str:
    return re.match(r"[A-Z]+", cell_ref).group(0)


def _cell_text(cell: ET.Element, shared_strings: list[str]) -> str | None:
    value = cell.find(f"{_NS}v")
    if value is None or value.text is None:
        return None
    if cell.get("t") == "s":
        return shared_strings[int(value.text)]
    return value.text


def _download_workbook_bytes() -> tuple[bytes, str]:
    """Return the workbook bytes and the URL it came from, trying recent year ranges."""
    today = date.today()
    errors: list[str] = []
    # The file is named after the last full year it covers; try this year and the two
    # previous ones (the current-year file may not be published until well into the year).
    for year in (today.year, today.year - 1, today.year - 2):
        url = RFB_CNAE_BASE.format(year=year)
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "arandu.aiBrasil/0.1"},
                timeout=120,
            )
        except requests.RequestException as exc:  # network error: try the next range
            errors.append(f"{url}: {exc}")
            continue
        if response.status_code == 200 and response.content:
            return response.content, url
        errors.append(f"{url}: HTTP {response.status_code}")
    raise RuntimeError("RFB CNAE workbook not found in any recent year range: " + "; ".join(errors))


def _parse_workbook(content: bytes) -> dict[int, dict[str, dict[str, Decimal]]]:
    """Parse the workbook into {year: {division_code: {tax_line: value}}}.

    Values are kept in whole reais (the file's unit) as Decimals.
    """
    archive = zipfile.ZipFile(io.BytesIO(content))

    shared_strings: list[str] = []
    sst_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    for si in sst_root.findall(f"{_NS}si"):
        shared_strings.append("".join(t.text or "" for t in si.iter(f"{_NS}t")))

    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    sheet_names = [s.get("name") for s in workbook.iter(f"{_NS}sheet")]

    result: dict[int, dict[str, dict[str, Decimal]]] = {}
    for index, sheet_name in enumerate(sheet_names, start=1):
        if not (sheet_name and sheet_name.isdigit()):
            continue  # only the per-year sheets are named like "2025"
        year = int(sheet_name)
        sheet_root = ET.fromstring(archive.read(f"xl/worksheets/sheet{index}.xml"))
        sheet_data = sheet_root.find(f"{_NS}sheetData")
        if sheet_data is None:
            continue
        rows = sheet_data.findall(f"{_NS}row")
        if len(rows) < 4:
            continue

        # Row 3 maps each column letter -> CNAE division code.
        division_by_col: dict[str, str] = {}
        for cell in rows[2].findall(f"{_NS}c"):
            col = _column_letter(cell.get("r"))
            text = _cell_text(cell, shared_strings)
            if col == "A" or text in (None, ""):
                continue
            division_by_col[col] = str(text).strip()

        year_divisions: dict[str, dict[str, Decimal]] = {}
        for row in rows[3:]:
            label: str | None = None
            values_by_col: dict[str, str] = {}
            for cell in row.findall(f"{_NS}c"):
                col = _column_letter(cell.get("r"))
                text = _cell_text(cell, shared_strings)
                if col == "A":
                    label = text
                elif text not in (None, ""):
                    values_by_col[col] = text
            if not label:
                continue
            for col, raw_value in values_by_col.items():
                division = division_by_col.get(col)
                if division is None:
                    continue
                try:
                    value = Decimal(str(raw_value))
                except (ValueError, ArithmeticError):
                    continue
                year_divisions.setdefault(division, {})[label.strip()] = value
        result[year] = year_divisions
    return result


def fetch_rfb_cnae(series: dict[str, Any]) -> list[Observation]:
    """Annual federal tax revenue (receita administrada pela RFB) for one CNAE division.

    Config keys (under the series entry):
      rfb_cnae_division : 2-digit CNAE division code to isolate (e.g. "92" for jogos de
                          azar e apostas). source_series_code mirrors this for provenance.
      unit              : "BRL millions" emits values in R$ millions; anything else keeps
                          whole reais. Defaults to whole reais.

    One observation per year, stamped on 1 January of that year, valued as the sum of the
    division's top-level tax lines (sub-lines excluded to avoid double counting).
    """
    division = str(series.get("rfb_cnae_division", series.get("source_series_code", ""))).strip()
    if not division:
        raise ValueError("rfb_cnae connector requires rfb_cnae_division")

    in_millions = str(series.get("unit", "")).lower().startswith("brl million")

    cache_key = "default"
    parsed = _WORKBOOK_CACHE.get(cache_key)
    if parsed is None:
        content, _url = _download_workbook_bytes()
        parsed = _parse_workbook(content)
        _WORKBOOK_CACHE[cache_key] = parsed

    observations: list[Observation] = []
    for year, divisions in sorted(parsed.items()):
        tax_lines = divisions.get(division)
        if not tax_lines:
            continue
        total = sum(
            (value for label, value in tax_lines.items() if label in _TOPLEVEL_TAX_LINES),
            Decimal(0),
        )
        emitted = total / _REAL_TO_MILLIONS if in_millions else total
        observations.append(
            Observation(
                series_id=series["series_id"],
                date=date(year, 1, 1),
                value=emitted,
                original_value=emitted,
                raw_payload={"cnae_division": division, "year": year, "reais": str(total)},
            )
        )
    return observations
