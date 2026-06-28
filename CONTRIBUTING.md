# Contributing to arandu.ai

arandu.ai is a public interface for Brazilian fiscal and economic data. It is a civic instrument, not a party, a campaign, a ministry, or a newspaper. The goal is not to remove interpretation. The goal is to make interpretation auditable.

Contributions are welcome. This document explains how to contribute, what every contribution must carry, and which layer of the system each change touches. It is practical, and it is firm on method.

If you are new, read this file once, end to end, before opening a pull request. Then read [`systemic/data-standard.md`](systemic/data-standard.md) and [`metasystemic/visual-grammar.md`](metasystemic/visual-grammar.md).

---

## 1. Contributor terms

By contributing to arandu.ai, you accept these terms.

You can be a source of data bias. So can other contributors. So can institutions, datasets, categories, charts, colors, labels, tabs, filters, and missing data.

Data is not neutral. We will not pretend it is. We will try to make the work more inspectable, more reproducible, and more honest.

Every change touches a layer of the system. Some changes add content. Some changes change the lens itself. Knowing which layer you are touching is the first responsibility of a contributor.

---

## 2. Two kinds of change

Every pull request should know what layer it is touching. There are two.

### Systemic — content inside the current structure

A systemic change adds, edits, or removes content inside the structure that already exists.

Constitution examples: a new card, a new query, a new data source, a better label, a correction.

In this repo, a systemic change touches:

- `CHARTS` in [`ingestion/arandu/metabase_setup.py`](ingestion/arandu/metabase_setup.py) (re-exported as `arandu.systemic.CHARTS`) — the cards.
- the SQL queries behind those cards.
- the series catalog in [`ingestion/config/series.yml`](ingestion/config/series.yml).
- the data sources in [`arandu/sources/*`](ingestion/arandu/sources/).

Systemic changes are documented in [`systemic/`](systemic/). They are the daily life of the project, and they should be welcomed.

### Metasystemic — the structure that organizes content

A metasystemic change changes how the system itself is organized. It changes the lens, not only the picture.

Constitution examples: a new tab, a tab removal, a governance rule, a change to the visual grammar, a change to the agent interface.

In this repo, a metasystemic change touches:

- `DASHBOARD_TABS` in [`ingestion/arandu/metabase_setup.py`](ingestion/arandu/metabase_setup.py) (re-exported as `arandu.metasystemic.DASHBOARD_TABS`) — the canonical tabs.
- the visual grammar: the `*_settings` helpers, `_grid`, the period presets `MANDATOS`, and the palette.
- governance and the agent interface.
- the constitution.

Metasystemic changes are documented in [`metasystemic/`](metasystemic/). They are slower. They require more care.

> Tabs are constitutional. A pull request may add cards inside a tab, improve a tab, or clarify a tab. No pull request may add, remove, rename, or reorder a canonical tab without a metasystemic proposal and a vote. See [`GOVERNANCE.md`](GOVERNANCE.md).

---

## 3. What a systemic PR must include

A systemic change must include, when relevant:

- **Source** — where the data came from.
- **Method** — how it was transformed.
- **Reason** — why this card, query, source, or label.
- **Known limitations** — what the viewer should be careful about.
- **Update cadence** — how often it refreshes.

A systemic change must not smuggle in a political conclusion. It may show debt, inflation, revenue, spending, poverty, growth, or uncertainty. It must not tell the user what to believe.

In practice, every card carries `Fonte` (+ url) / `Unidade` / `Frequência` / `Conceito` in its description. That maps directly to the four questions of the [data standard](systemic/data-standard.md): source, transformation, last updated, caveats.

---

## 4. What a metasystemic PR must include

A metasystemic change must include:

- a **written proposal**.
- a **reason**.
- a **bias-impact note** — how this change affects what the public can and cannot see.
- a **migration plan**.
- a **rollback plan**.
- a **public discussion period**.
- a **vote**, when the change affects tabs, governance, or public structure.

The discussion period and the voting rules — proposal open at least 14 days, the eligibility and majority thresholds, and how voting power comes from contribution — live in [`GOVERNANCE.md`](GOVERNANCE.md). Read it before opening a metasystemic proposal.

---

## 5. The data standard — the four questions

Every card answers four questions.

1. Where did this data come from?
2. How was it transformed?
3. When was it last updated?
4. What should the viewer be careful about?

Preferred sources are public, stable, documented, and reproducible. When using secondary sources, the card must explain why the original source was not used. When data is incomplete, the incompleteness must be visible. When a category is constructed, the construction must be explained.

A beautiful dashboard with weak provenance is not accepted. A simple chart with strong provenance is welcome.

Full standard: [`systemic/data-standard.md`](systemic/data-standard.md).

---

## 6. The visual standard, in brief

The interface should be calm. Readable. Sparse. Respectful of attention.

No alarmism. No decorative noise. No manipulation by color. No chartjunk. No hiding uncertainty. No false precision.

The arandu green `#0B5E3A` is structural chrome only — the wordmark and the frame. It is never used to encode or dramatize data.

The interface should feel like a public library. Not a casino. Not a campaign room. Not a trading desk.

Full grammar: [`metasystemic/visual-grammar.md`](metasystemic/visual-grammar.md).

---

## 7. GitHub labels

Labels are public grammar. The label tells the community what layer of the lens is being touched. It is not bureaucracy.

| Label | Meaning |
| --- | --- |
| `systemic-change` | Cards, data, queries, labels, sources, and dashboard content. |
| `metasystemic-change` | Tabs, governance, architecture, moderation rules, visual grammar, and constitutional structure. |
| `correction` | A factual, methodological, or data fix. |
| `data-source` | A new or changed data source. |
| `governance` | Voting, moderation, maintainership, and constitutional changes. |
| `agent-interface` | MCP, API, stream, or machine-readable context changes. |
| `tab-change` | A change to a canonical tab (always metasystemic, always a vote). |
| `needs-methodology` | The change lacks a clear method note. |
| `needs-source` | The change lacks a cited source. |
| `needs-bias-note` | The change lacks a bias-impact note. |
| `good-first-card` | A small, well-scoped systemic change for newcomers. |

---

## 8. Pull request checklist

Copy this into your pull request description and check what applies.

```markdown
### Layer
- [ ] This PR is **systemic** (content inside the current structure)
- [ ] This PR is **metasystemic** (changes the structure / the lens)

### If systemic
- [ ] Source cited (Fonte + url)
- [ ] Method described (how the data was transformed)
- [ ] Reason given (why this card / query / source / label)
- [ ] Known limitations stated (Conceito / caveats)
- [ ] Update cadence noted (Frequência), when relevant
- [ ] No political conclusion is smuggled in — data is separated from interpretation
- [ ] The card answers the four questions (source, transformation, last updated, caveats)

### If metasystemic
- [ ] Written proposal included
- [ ] Reason given
- [ ] Bias-impact note included
- [ ] Migration plan included
- [ ] Rollback plan included
- [ ] Public discussion period opened (see GOVERNANCE.md)
- [ ] Vote opened if it touches tabs, governance, or public structure

### Always
- [ ] Correct label applied
- [ ] Visual standard respected (calm, no chartjunk, no color manipulation, no false precision)
- [ ] `make lint` passes
- [ ] `make test` passes
```

---

## 9. Contributor pledge

Before contributing, I affirm:

> I am contributing to a public civic instrument. I will make my work reproducible. I will cite sources. I will separate data from interpretation. I will disclose uncertainty. I will welcome correction. I will not use arandu.ai to hide bias behind charts. I will not change the structure of the project without the project consent.
>
> I understand that the lens is part of the data.

---

## Local development

The project is orchestrated by docker-compose. The common loop:

```sh
make up             # build and run everything (app at http://localhost:5173, Metabase at http://localhost:3000)
make lint           # lint the codebase
make test           # run the tests
make seed-metabase  # build the dashboard in Metabase
```

A daily worker refreshes the data. `make up` is enough to see the app, the dashboards, and your change in context before you open a pull request.
