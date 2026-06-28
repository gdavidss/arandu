from datetime import date
from decimal import Decimal

import pytest

from arandu.sources.static_table import fetch_static_table


def test_static_table_emits_configured_points() -> None:
    series = {
        "series_id": "bets_bcb_pix_outros_ago2024",
        "static_observations": [
            {"date": "2024-08-01", "value": "20.8", "note": "outros CNAEs, R$ bi"},
        ],
    }
    obs = fetch_static_table(series)
    assert len(obs) == 1
    assert obs[0].date == date(2024, 8, 1)
    # Exact published figure preserved, no rounding/interpolation.
    assert obs[0].value == Decimal("20.8")
    assert obs[0].original_value == Decimal("20.8")
    assert obs[0].raw_payload == {"static": True, "source_note": "outros CNAEs, R$ bi"}


def test_static_table_requires_observations() -> None:
    with pytest.raises(ValueError):
        fetch_static_table({"series_id": "x"})
    with pytest.raises(ValueError):
        fetch_static_table({"series_id": "x", "static_observations": []})


def test_static_table_preserves_large_integer_counts() -> None:
    # SPA account/CPF counts are large integers; they must round-trip exactly (no float).
    series = {
        "series_id": "spa_contas_marcas_2025",
        "static_observations": [{"date": "2025-12-31", "value": "100775427"}],
    }
    obs = fetch_static_table(series)
    assert obs[0].value == Decimal("100775427")
    assert obs[0].date == date(2025, 12, 31)
