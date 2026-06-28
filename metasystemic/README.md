# Metasystemic

The metasystemic layer is the structure that organizes the project. It is the lens, not the picture.

The [systemic](../systemic/) layer is the content inside the structure: cards, queries, data sources, labels, corrections. The metasystemic layer is everything that decides how that content is arranged and shown — the tabs, the visual grammar, the governance, the agent interface, the constitution itself.

Two kinds of change run through arandu.ai. A systemic change adds or edits content inside the current structure. A metasystemic change changes the structure. This folder holds the second kind.

## What lives here

- [CONSTITUTION.md](CONSTITUTION.md) — the source of truth. What the project is, the two-layer grammar, the data and visual standards, the contributor terms and pledge.
- [GOVERNANCE.md](../GOVERNANCE.md) — voting, voter eligibility, moderation, maintainer powers. (At the repository root.)
- [tabs.md](tabs.md) — the canonical tabs, the public rooms of arandu.ai. Tabs are constitutional; they do not change without a vote.
- [visual-grammar.md](visual-grammar.md) — the calm visual standard in practice: the palette, period presets, grid, and chart-settings conventions.
- [agent-interface.md](agent-interface.md) — how machines read the lens. Structured metadata, the exported context files, and the importable modules.

## What in code belongs to this layer

The structure is not only documented here; it is also defined in code.

- **`DASHBOARD_TABS`** in `ingestion/arandu/metabase_setup.py` — the canonical tabs and the cards each one holds. Re-exported as `arandu.metasystemic.DASHBOARD_TABS`.
- **The visual grammar**, also in `ingestion/arandu/metabase_setup.py`:
  - `line_settings`, `bar_settings`, `time_bar_settings` — the chart-settings helpers.
  - `_grid` — the layout.
  - `MANDATOS` — the period presets.
  - the palette and the structural color `#0B5E3A` (arandu green), used for the wordmark and structural chrome only — never to encode or dramatize data.
- **`arandu.metasystemic`** — the importable module (`ingestion/arandu/metasystemic.py`), a thin surface over those structural artifacts so humans and agents can reach the lens without depending on internal module layout.

The content counterpart is `arandu.systemic` (the `CHARTS` dict and the queries, data sources, and series catalog behind it). Same file, different layer.

## The rule

Changing anything in this folder, or anything it documents in code, is a metasystemic change.

Metasystemic changes are slower. They require more care. They change the lens, not only the picture.

A metasystemic change must include a written proposal, a reason, a bias-impact note, a migration plan, a rollback plan, and a public discussion period. It needs a vote when it affects tabs, governance, or public structure. The proposal stays open at least 14 days before the vote. See [GOVERNANCE.md](../GOVERNANCE.md) for the voting rules and thresholds.

Adding a card inside a tab is systemic — welcome it. Adding, removing, renaming, or reordering a canonical tab is metasystemic — it needs a proposal and a vote.

Label such pull requests `metasystemic-change`. The label tells the community what layer of the lens is being touched.

> The lens is part of the data.
