# Tabs

Tabs are constitutional.

Tabs are not decoration. Tabs define the public rooms of arandu.ai. The canonical tabs should remain stable unless changed by vote.

A pull request may add cards inside a tab. A pull request may improve a tab. A pull request may clarify a tab. But no pull request may add, remove, rename, or reorder a canonical tab without a metasystemic proposal.

## The two layers, applied to tabs

The grammar of this project draws one line, and tabs sit on one side of it.

- Adding, improving, or clarifying a **card** inside an existing tab is **systemic**. It changes what appears inside the current structure. It is the daily life of the project, and it is welcome.
- Touching the **tab set** — add, remove, rename, or reorder — is **metasystemic**. It changes the structure that organizes the project. It changes the lens, not only the picture.

A metasystemic tab change requires a written proposal, a reason, a bias impact note, a migration plan, a rollback plan, a public discussion period, and a vote. See [../GOVERNANCE.md](../GOVERNANCE.md).

## Initial canonical tabs (constitution, section 06)

These are the tabs named in the constitution at version v0.1.

1. Overview
2. Fiscal Pulse
3. Governo Central
4. Debt
5. Inflation and Monetary
6. Federal Budget
7. States and Municipalities
8. Data Catalog

## Current live tabs

The live dashboard has grown since v0.1. This is the de-facto canonical set today, in order.

1. Visão geral
2. Inflação e juros
3. Atividade e emprego
4. Bem-estar das famílias
5. Pulso fiscal
6. Dívida
7. Governo Central
8. Setores produtivos
9. Comércio exterior
10. Consumo digital

The live set has grown since the v0.1 list above. Any further add, remove, rename, or reorder is metasystemic and needs a vote, per [../GOVERNANCE.md](../GOVERNANCE.md).

## Where this lives in code

The canonical tabs are defined as `DASHBOARD_TABS` in [`../ingestion/arandu/metabase_setup.py`](../ingestion/arandu/metabase_setup.py), re-exported as `arandu.metasystemic.DASHBOARD_TABS`.

The cards inside each tab are the systemic layer — the `CHARTS` dict in the same file, re-exported as `arandu.systemic.CHARTS`. Editing a card stays inside a tab and is systemic. Editing the list of tabs is metasystemic.
