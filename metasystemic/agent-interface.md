# Agent interface

Constitution: [section 12 — Agents](./CONSTITUTION.md). Layer: **metasystemic**. Label: `agent-interface`.

## Humans first, agents next

arandu.ai should be useful to humans first. But it should also be legible to machines.

The interface is built for a person reading a chart: calm, sparse, sourced. The same artifacts that make a card honest for a person — its source, its query, its last update, its caveats — are also the things an agent needs. So the agent interface is not a separate product. It is the same lens, exposed in a machine-readable shape.

Agent access happens through structured metadata, importable modules, and an MCP server; APIs and streams may follow. This document records what exists today.

## The six agent questions

The constitution says agents should be able to ask:

1. What a card is.
2. What source it uses.
3. What query produced it.
4. When it was updated.
5. What caveats it carries.
6. What changed since the last version.

These are the same questions a careful human asks. They map to the [data standard](./CONSTITUTION.md) (section 10) and to the per-card `Fonte / Unidade / Frequência / Conceito` description that every card already carries.

## The current agent-legible surface

There are four surfaces today. Two are static JSON files served by the frontend; one is an importable Python module pair; one is a live MCP server over the warehouse.

### 1. `frontend/public/dashboard-data.json` — the series catalog

A per-series catalog plus the observations behind every card. Top-level keys: `generatedAt`, `series`, `catalog`, `counts`.

Each catalog/series entry carries the metadata that answers the constitution's questions:

| Field | Meaning |
| --- | --- |
| `seriesId` | Stable identifier for the series. |
| `name` | Human-readable name of the series. |
| `sourceName` / `institution` | The source dataset and the institution that publishes it. |
| `sourceSeriesCode` / `sourceUrl` | The upstream series code and a link to the public source. |
| `unit` | Unit of measure (e.g. `BRL millions`). |
| `frequency` | Cadence of the series (e.g. `annual`, `monthly`). |
| `concept` | What the number means. |
| `seasonalAdjustment` | Whether the series is seasonally adjusted. |
| `transformation` / `method` | How the data was transformed from the source. |
| `scope` | What slice of the source this series covers. |
| `geography` | Geographic coverage. |
| `startDate` / `endDate` / `latestDate` / `latestValue` | Coverage range and most recent point. |
| `lastSuccessfulUpdateAt` | When the series was last refreshed by the worker. |
| `notes` | Free-text caveats, when present. |
| `observations` | The full `[ { date, value }, … ]` series behind the card. |

`counts` reports `configuredSeries`, `populatedSeries`, and total `observations`.

### 2. `frontend/public/metabase-dashboards.json` — the card index

Maps card names to their Metabase locations and sources. Top-level keys include `generated_at`, `status`, `metabase_base_url`, `links`, and:

- `question_by_name` — card name → public view URL.
- `question_edit_by_name` — card name → editable Metabase question URL (where the query lives).
- `card_sources` — card name → `{ label, url, domain }` for the upstream source.

### 3. `arandu.systemic` and `arandu.metasystemic` — the importable modules

Thin, importable surfaces over the code artifacts, so humans and agents can reach each layer without depending on internal module layout.

- `arandu.systemic` re-exports the content layer: `CHARTS` (the cards), `CHART_SOURCES`, `SERIES_LABELS`. See [systemic/](../systemic/).
- `arandu.metasystemic` re-exports the structure layer: `DASHBOARD_TABS` (the canonical tabs), `MANDATOS` (period presets), and the visual-grammar helpers (`line_settings`, `bar_settings`, `time_bar_settings`, `_grid`, `VIZ_PATCHES`, `DISPLAY_OVERRIDES`).

### 4. The MCP server — live, queryable access

A [Model Context Protocol](https://modelcontextprotocol.io) server (`ingestion/arandu/mcp_server.py`, compose service `mcp`) exposes the warehouse's analytics views over streamable HTTP at `http://localhost:8808/mcp`. Any MCP client — Claude Code, Claude Desktop, Cursor — can call four read-only tools:

- `list_series` — the catalog: `series_id`, `name`, `source_name`, `institution`, `unit`, `frequency`, `concept`, `latest_date`, `latest_value`, `source_url`.
- `search_series(query)` — the same shape, filtered by keyword across id, name, concept, and source.
- `get_series(series_id, start_date?, end_date?)` — full metadata plus the `[ { date, value }, … ]` observations behind a card (capped at 20 000 rows).
- `get_series_sources` — the distinct institutions and datasets behind the catalog, with their public URLs.

Connect with `claude mcp add --transport http arandu http://localhost:8808/mcp`, or in `mcp.json`: `{ "mcpServers": { "arandu": { "url": "http://localhost:8808/mcp" } } }`.

The MCP server reads the same `analytics.series_latest` / `analytics.observations_enriched` views the dashboard reads. It adds no new interpretation and grants no write access — it is the same lens, answered live.

### Mapping the surface to the six questions

| Agent question | Where it is answered |
| --- | --- |
| What a card is | `dashboard-data.json` (`name`, `concept`, `unit`); MCP `list_series` / `get_series`; `arandu.systemic.CHARTS`; `metabase-dashboards.json` (`question_by_name`). |
| What source it uses | `dashboard-data.json` (`sourceName`, `institution`, `sourceUrl`); MCP `get_series_sources`; `metabase-dashboards.json` (`card_sources`). |
| What query produced it | `metabase-dashboards.json` (`question_edit_by_name`); `arandu.systemic.CHARTS`. |
| When it was updated | `dashboard-data.json` (`lastSuccessfulUpdateAt`, `latestDate`); `generatedAt` / `generated_at`. |
| What caveats it carries | `dashboard-data.json` (`seasonalAdjustment`, `transformation`, `method`, `scope`, `notes`). |
| What changed since the last version | Git history of the cards and series, plus the `generatedAt` / `generated_at` timestamps on the JSON snapshots. |

## Future direction

The MCP server is the first live machine interface; the project may extend the surface further with APIs or streams. Any such surface must expose the same six questions and carry the same metadata. New machine-readable surfaces are agent-interface changes (see below).

## Rules

Machine access must preserve the same constitutional rules. An agent reading or writing through this interface is bound by the same grammar as a human contributor: the [data standard](./CONSTITUTION.md) (section 10), the [visual standard](./CONSTITUTION.md) (section 11), and the [two kinds of change](../CONTRIBUTING.md).

Agents may help maintain the lens. They may not quietly rewrite the lens.

- An agent may propose systemic changes — a new card, a new query, a new source, a better label, a correction — through the same review as a human.
- An agent may not add, remove, rename, or reorder a canonical tab, change the visual grammar, or change governance without a metasystemic proposal and a vote (see [GOVERNANCE.md](../GOVERNANCE.md)).
- Every change still passes through systemic or metasystemic review and carries the right [labels](./CONSTITUTION.md) (section 13). Low-quality automated pull requests may be refused under section 9.

**Changing this interface is metasystemic.** Adding, removing, or reshaping any of the surfaces above — the JSON schemas, the importable modules, or any future API, stream, or MCP interface — changes how the project is read by machines. Such changes require a written proposal, a bias-impact note, a migration plan, a rollback plan, a public discussion period, a vote, and the `agent-interface` label.

## See also

- [CONSTITUTION.md](./CONSTITUTION.md) — sections 12 (agents) and 13 (labels).
- [GOVERNANCE.md](../GOVERNANCE.md) — proposals and voting for metasystemic change.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — the two kinds of change.
- [systemic/](../systemic/) — the content layer documented here.
