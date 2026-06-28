# The Data Standard — The Four Questions

> This is the data acceptance standard. It implements section 10 of the [constitution](../metasystemic/CONSTITUTION.md).
>
> The standard itself is metasystemic: changing it requires a metasystemic proposal and a vote. See [`../GOVERNANCE.md`](../GOVERNANCE.md). Living inside the standard — adding a card, citing a source, writing a caveat — is systemic, and is the daily life of the project. See [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## The four questions

Every card answers four questions.

1. **Where did this data come from?**
2. **How was it transformed?**
3. **When was it last updated?**
4. **What should the viewer be careful about?**

A card that cannot answer all four is not ready. The questions are not optional, and they are not for the maintainers alone. They are written into the card itself, where the viewer can read them.

## What the standard requires

Preferred sources are public, stable, documented, and reproducible. A source another person can fetch, on their own, and get the same numbers.

When using secondary sources, the card must explain why the original source was not used. A secondary source is not forbidden. An unexplained one is.

When data is incomplete, the incompleteness must be visible. A gap that is hidden reads as a zero, or as nothing, and that is a lie of omission. Show the gap.

When a category is constructed, the construction must be explained. If a number is a sum, a ratio, a reclassification, or a basket someone assembled, say who assembled it and how.

> A beautiful dashboard with weak provenance is not accepted. A simple chart with strong provenance is welcome.

This is the line. Polish does not buy a pass on provenance. Plainness does not lose one.

## How arandu implements it

The four questions are not a separate document the viewer has to find. They travel with the card.

### 1. Every card description carries four fields

Every card in `CHARTS` (in [`../ingestion/arandu/metabase_setup.py`](../ingestion/arandu/metabase_setup.py), re-exported as `arandu.systemic.CHARTS`) has a description that carries four fields:

| Field | Constitutional question | What it states |
| --- | --- | --- |
| **Fonte** (+ url) | Where did this data come from? | The institution, the series, and a link a viewer can follow. |
| **Conceito** | How was it transformed? / What should I be careful about? | What the number measures, how it was built, and what not to confuse it with. |
| **Unidade** | What should the viewer be careful about? | The unit, so the axis is never read wrong (% a.a., R$ milhões, % do PIB). |
| **Frequência** | When was it last updated? | The cadence the source publishes on (diária, mensal, trimestral). |

`Fonte`, `Unidade`, `Frequência`, and `Conceito` map directly onto the four questions: source, transformation, last updated, and caveats. The mapping is deliberate. The fields are the questions, in Portuguese, on the card.

`Conceito` carries most of the care. It is where a card warns that NFSP (below-the-line) must not be mixed with RTN (above-the-line), that SPI-only Pix is narrower than MPV Pix, that a count and a value are different units, or that expectations are forward-looking and must not be read as realized prints.

### 2. Series metadata lives in `series.yml`

Behind every card is a series, and every series is declared once in [`../ingestion/config/series.yml`](../ingestion/config/series.yml). Each entry carries its own provenance — independent of any card that draws it.

Each `sources:` block records the publishing institution, the canonical `url`, the `license_or_terms`, and `notes` about how the source must and must not be read. Each `series:` entry records `source_id`, `connector`, `source_series_code`, `unit`, `frequency`, `concept`, `geography`, `seasonal_adjustment`, `transformation`, `source_url`, and `start_date`.

This is where reproducibility lives. The `connector` and `source_series_code` say exactly which connector in [`../ingestion/arandu/sources/`](../ingestion/arandu/sources/) fetched which series from which endpoint, so anyone can re-run the fetch and get the same numbers. The `transformation` field records what was done to the raw values — a monthly flow, an accumulation over 12 months, a conversion to US$ millions — answering the second question at the level of the series, not just the card.

### 3. A daily worker refreshes the cadence

The third question — when was it last updated? — has two answers, and the project keeps both.

The ingestion worker (`python -m arandu worker`, in [`../ingestion/arandu/__main__.py`](../ingestion/arandu/__main__.py)) runs in the `ingestion` service and refreshes on a 24-hour interval (`REFRESH_INTERVAL_HOURS`). Each run re-fetches the series, upserts the warehouse, and re-exports the agent surface. The export in [`../ingestion/arandu/export_dashboard_data.py`](../ingestion/arandu/export_dashboard_data.py) records, per series:

- `latest_date` — the date of the most recent observation the **source** has published.
- `last_successful_update_at` — the last time **arandu** successfully fetched it.

These are different facts and the project does not conflate them. A source can stop publishing while the worker keeps succeeding; the gap between the two is itself information, and it is visible. Both land in [`../frontend/public/dashboard-data.json`](../frontend/public/dashboard-data.json), so humans and agents read the same freshness.

## A compliant card description

A card that meets the standard. From `overview_selic` in `CHARTS`:

```python
"overview_selic": {
    "name": "Selic meta",
    "display": "line",
    "description": (
        "Selic meta definida pelo Copom. Fonte: BCB SGS 432. "
        "Unidade: % ao ano. Frequência: diária."
    ),
    ...
}
```

Read against the four questions:

- **Where did this come from?** — *Fonte: BCB SGS 432.* Banco Central, series 432, a public series anyone can fetch. The full URL and license live in `series.yml` under `bcb_sgs`.
- **How was it transformed?** — Nothing dramatized: it is the target rate set by the Copom, carried through as published (`transformation: stock / target rate` in `series.yml`).
- **When was it last updated?** — *Frequência: diária*, and the worker records the source's `latest_date` and arandu's own `last_successful_update_at` in the agent surface.
- **What should I be careful about?** — *Unidade: % ao ano.* The unit is stated, so the axis is not misread. Where a series carries a sharper trap, the `Conceito` line names it.

This card is plain. One line, one series, no decoration. Under this standard, plain with strong provenance is exactly what the project wants.

## Related

- [`../metasystemic/CONSTITUTION.md`](../metasystemic/CONSTITUTION.md) — section 10 is the source of this standard; section 11 is the visual standard a card must also meet.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — what a systemic pull request must include, and the pull request checklist.
- [`../GOVERNANCE.md`](../GOVERNANCE.md) — how the standard itself is changed.
