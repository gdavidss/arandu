"""MCP server for arandu — the same data behind the charts, for agents.

Exposes the warehouse's analytics views (`analytics.series_latest`,
`analytics.observations_enriched`) over the Model Context Protocol
(streamable HTTP), so any MCP client — Claude Code, Claude Desktop,
Cursor — can read the same sourced series the dashboard renders.

Machine access preserves the constitutional rules (metasystemic/
agent-interface.md): the surface is read-only and carries the same
provenance metadata every card carries.

Run: python -m arandu.mcp_server  →  http://0.0.0.0:8808/mcp
"""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from typing import Any

from mcp.server.fastmcp import FastMCP

from arandu.db import connect

MAX_OBSERVATIONS = 20_000

_CATALOG_COLUMNS = (
    "series_id",
    "name",
    "source_name",
    "institution",
    "unit",
    "frequency",
    "concept",
    "latest_date",
    "latest_value",
    "source_url",
)

_CATALOG_SQL = """
    select series_id, name, source_name, institution, unit, frequency,
           concept, latest_date, latest_value, source_url
    from analytics.series_latest
"""

_METADATA_COLUMNS = _CATALOG_COLUMNS + (
    "geography",
    "seasonal_adjustment",
    "scope",
    "method",
    "start_date",
    "end_date",
    "notes",
)

_METADATA_SQL = """
    select series_id, name, source_name, institution, unit, frequency,
           concept, latest_date, latest_value, source_url,
           geography, seasonal_adjustment, scope, method,
           start_date, end_date, notes
    from analytics.series_latest
    where series_id = %s
"""

mcp = FastMCP(
    "arandu",
    host=os.environ.get("MCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("MCP_PORT", "8808")),
    streamable_http_path="/mcp",
)


def _plain(value: Any) -> Any:
    """Convert DB scalars to JSON-friendly types."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def _rows_to_dicts(columns: tuple[str, ...], rows: list[tuple]) -> list[dict[str, Any]]:
    return [dict(zip(columns, (_plain(v) for v in row), strict=True)) for row in rows]


@mcp.tool()
def list_series() -> list[dict[str, Any]]:
    """List the full series catalog: id, name, source, institution, unit,
    frequency, concept, latest date/value, and source URL for every series."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(_CATALOG_SQL + " order by series_id")
        rows = cur.fetchall()
    return _rows_to_dicts(_CATALOG_COLUMNS, rows)


@mcp.tool()
def search_series(query: str) -> list[dict[str, Any]]:
    """Search the catalog by keyword (case-insensitive) across series_id,
    name, concept, and source_name. Returns matching catalog entries."""
    pattern = f"%{query}%"
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            _CATALOG_SQL
            + """
            where series_id ilike %s or name ilike %s
               or concept ilike %s or source_name ilike %s
            order by series_id
            """,
            (pattern, pattern, pattern, pattern),
        )
        rows = cur.fetchall()
    return _rows_to_dicts(_CATALOG_COLUMNS, rows)


@mcp.tool()
def get_series(series_id: str, start_date: str = "", end_date: str = "") -> dict[str, Any]:
    """Get one series: full metadata plus observations as [{date, value}].
    Optional start_date/end_date (YYYY-MM-DD) restrict the window.
    Observations are capped at 20000 rows (oldest first)."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(_METADATA_SQL, (series_id,))
        meta_row = cur.fetchone()
        if meta_row is None:
            return {
                "error": (
                    f"Unknown series_id: {series_id!r}. "
                    "Use list_series or search_series to find valid ids."
                )
            }

        obs_sql = """
            select date, value
            from analytics.observations_enriched
            where series_id = %s
        """
        params: list[Any] = [series_id]
        if start_date:
            obs_sql += " and date >= %s"
            params.append(start_date)
        if end_date:
            obs_sql += " and date <= %s"
            params.append(end_date)
        obs_sql += " order by date limit %s"
        params.append(MAX_OBSERVATIONS)
        cur.execute(obs_sql, params)
        obs_rows = cur.fetchall()

    metadata = _rows_to_dicts(_METADATA_COLUMNS, [meta_row])[0]
    observations = [{"date": _plain(d), "value": _plain(v)} for d, v in obs_rows]
    return {
        "series": metadata,
        "observations": observations,
        "observation_count": len(observations),
        "truncated": len(observations) >= MAX_OBSERVATIONS,
    }


@mcp.tool()
def get_series_sources() -> list[dict[str, Any]]:
    """List where the data comes from: the distinct institutions and source
    datasets behind the catalog, each with its public source URL."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select distinct institution, source_name, source_url
            from analytics.series_latest
            order by institution, source_name
            """
        )
        rows = cur.fetchall()
    return _rows_to_dicts(("institution", "source_name", "source_url"), rows)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
