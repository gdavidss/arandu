import io
import zipfile
from datetime import date
from decimal import Decimal

import arandu.sources.rfb_cnae as rfb_cnae
from arandu.sources.rfb_cnae import fetch_rfb_cnae

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _build_workbook() -> bytes:
    """A minimal two-year XLSX mirroring the real RFB layout.

    Columns B/C hold divisions 49 and 92. Rows are: ANO, DIVISÃO ECONÔMICA, then tax lines.
    For division 92 we include two top-level lines (IRPJ, Cofins) plus an IPI sub-line that
    must be excluded from the total.
    """
    shared = [
        "UNIDADE: R$ 1,00",  # 0
        "ANO",  # 1
        "DIVISÃO ECONÔMICA",  # 2
        "49",  # 3
        "92",  # 4
        "Imposto s/ a Renda - Pessoas Jurídicas - IRPJ",  # 5
        "Contribuição p/ Financiamento da Seguridade Social - Cofins",  # 6
        "IPI - Bebidas",  # 7 (sub-line; must NOT be summed)
        "2024",  # 8
        "2025",  # 9
    ]
    sst = (
        f'<sst xmlns="{NS}" count="{len(shared)}" uniqueCount="{len(shared)}">'
        + "".join(f"<si><t>{s}</t></si>" for s in shared)
        + "</sst>"
    )

    def s(idx: int) -> str:
        return f'<c t="s"><v>{idx}</v></c>'

    def num(v: str) -> str:
        return f"<c><v>{v}</v></c>"

    # Year sheet: row1 title, row2 ANO, row3 division codes, rows 4+ tax lines.
    def sheet(year_idx: int, irpj92: str, cofins92: str, ipi92: str) -> str:
        return (
            f'<worksheet xmlns="{NS}"><sheetData>'
            f'<row r="1"><c r="A1" t="s"><v>0</v></c></row>'
            f'<row r="2"><c r="A2" t="s"><v>1</v></c>'
            f'<c r="B2" t="s"><v>{year_idx}</v></c><c r="C2" t="s"><v>{year_idx}</v></c></row>'
            f'<row r="3"><c r="A3" t="s"><v>2</v></c>'
            f'<c r="B3" t="s"><v>3</v></c><c r="C3" t="s"><v>4</v></c></row>'
            # IRPJ line: A=label(5), C=value for division 92
            f'<row r="4"><c r="A4" t="s"><v>5</v></c><c r="C4"><v>{irpj92}</v></c></row>'
            # Cofins line
            f'<row r="5"><c r="A5" t="s"><v>6</v></c><c r="C5"><v>{cofins92}</v></c></row>'
            # IPI sub-line (excluded)
            f'<row r="6"><c r="A6" t="s"><v>7</v></c><c r="C6"><v>{ipi92}</v></c></row>'
            "</sheetData></worksheet>"
        )

    workbook = (
        f'<workbook xmlns="{NS}" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="2024" sheetId="1" r:id="rId1"/>'
        '<sheet name="2025" sheetId="2" r:id="rId2"/></sheets></workbook>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/sharedStrings.xml", sst)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/worksheets/sheet1.xml", sheet(8, "100", "50", "9"))
        z.writestr("xl/worksheets/sheet2.xml", sheet(9, "1000000", "500000", "123"))
    return buf.getvalue()


def test_rfb_cnae_sums_toplevel_lines_in_millions(monkeypatch) -> None:
    rfb_cnae._WORKBOOK_CACHE.clear()
    workbook = _build_workbook()

    def fake_download() -> tuple[bytes, str]:
        return workbook, "test://rfb_cnae.xlsx"

    monkeypatch.setattr(rfb_cnae, "_download_workbook_bytes", fake_download)

    series = {
        "series_id": "rfb_cnae_apostas_arrecadacao",
        "rfb_cnae_division": "92",
        "unit": "BRL millions",
    }
    obs = {o.date: o.value for o in fetch_rfb_cnae(series)}

    # 2024: (100 + 50) reais = 150 -> 0.00015 millions; IPI sub-line (9) excluded.
    assert obs[date(2024, 1, 1)] == Decimal("150") / Decimal("1000000")
    # 2025: (1,000,000 + 500,000) = 1,500,000 reais = 1.5 millions; IPI sub-line excluded.
    assert obs[date(2025, 1, 1)] == Decimal("1.5")


def test_rfb_cnae_keeps_reais_when_not_millions(monkeypatch) -> None:
    rfb_cnae._WORKBOOK_CACHE.clear()
    workbook = _build_workbook()
    monkeypatch.setattr(
        rfb_cnae, "_download_workbook_bytes", lambda: (workbook, "test://rfb_cnae.xlsx")
    )

    series = {
        "series_id": "rfb_cnae_apostas_arrecadacao",
        "rfb_cnae_division": "92",
        "unit": "BRL",
    }
    obs = {o.date: o.value for o in fetch_rfb_cnae(series)}
    assert obs[date(2025, 1, 1)] == Decimal("1500000")
