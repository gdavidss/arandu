# Systemic

The systemic layer is the content that appears inside the structure. It is the picture, not the lens.

The [metasystemic](../metasystemic/) layer decides how content is arranged and shown — the tabs, the visual grammar, the governance, the agent interface, the constitution. The systemic layer is what fills those rooms: the cards, the queries, the data sources, the series catalog, the labels, the corrections.

Two kinds of change run through arandu.ai. A systemic change adds, edits, or removes content inside the current structure. A metasystemic change changes the structure. This folder holds the first kind.

## What lives here

- [data-standard.md](data-standard.md) — the four questions every card must answer: where the data came from, how it was transformed, when it was last updated, what the viewer should be careful about.

## What in code belongs to this layer

The content is not only documented here; it is also defined in code.

- **The data sources** — the connectors in `ingestion/arandu/sources/`. One module per upstream API (BCB SGS, Tesouro, IBGE SIDRA, BCB Olinda/Focus/SPI/MPV, Comex Stat, ECB FX, RFB CNAE, and the static-table fallback), wired into the `CONNECTORS` registry in `ingestion/arandu/sources/__init__.py`. A new data source is a new connector here.
- **The series catalog** — `ingestion/config/series.yml`. Each `series` entry declares its `source_id`, `connector`, source code, name, unit, frequency, concept, geography, transformation, and `source_url`. The `sources` block above it records each upstream's institution, URL, and license. This is where a new indicator is registered.
- **The cards** — the `CHARTS` dict in `ingestion/arandu/metabase_setup.py`, re-exported as `arandu.systemic.CHARTS`. Each card carries its name, display type, SQL `query`, and a `description` that states `Fonte` (+ url) / `Unidade` / `Frequência` / `Conceito`. A new card, a new query, or a clearer label lives here. The same module also re-exports `CHART_SOURCES` and `SERIES_LABELS` through `arandu.systemic`.
- **`arandu.systemic`** — the importable module (`ingestion/arandu/systemic.py`), a thin surface over those content artifacts so humans and agents can reach the content layer without depending on internal module layout.

The structural counterpart is `arandu.metasystemic` (the `DASHBOARD_TABS`, the visual grammar, the period presets). Same file, different layer.

## The rule

Changing anything in this folder, or anything it documents in code, is a systemic change.

Systemic changes are the daily life of the project. They should be welcomed. A new card, a new query, a new data source, a better label, a correction — all of these add, edit, or remove content inside the current structure without touching the lens.

Two conditions hold.

First, a systemic change must meet the [data standard](data-standard.md). It must include source, method, reason, known limitations, and update cadence where relevant. A beautiful card with weak provenance is not accepted. A simple card with strong provenance is welcome.

Second, a systemic change must not smuggle in a political conclusion. It may show debt, inflation, revenue, spending, poverty, growth, or uncertainty. It must not tell the viewer what to believe. A chart may be uncomfortable. A number may be inconvenient. That is allowed. Bad method is not.

Adding a card inside a tab is systemic — welcome it. Adding, removing, renaming, or reordering a canonical tab is metasystemic — it needs a proposal and a vote. See [metasystemic/](../metasystemic/) and [GOVERNANCE.md](../GOVERNANCE.md).

Label such pull requests `systemic-change`. Use `correction` for a data or method fix, `data-source` for a new or changed source. The label tells the community what layer of the lens is being touched.

> The lens is part of the data.
