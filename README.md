# arandu.ai

A public lens for Brazil.

arandu.ai is a public, open-source interface for Brazilian fiscal and economic
data. It is built on open-source tools, maintained in public, and made so that
citizens, researchers, journalists, builders, students, and agents can look at
the same numbers and ask better questions.

## What it is, and what it is not

arandu.ai is not a party. It is not a campaign. It is not a ministry. It is not
a newspaper.

It is a civic instrument.

The goal is not to remove interpretation. Every dataset, category, label, and
chart carries choices, and pretending otherwise would be its own kind of bias.
The goal is to make interpretation auditable: every number should trace back to
a source, a method, and a date, so that anyone can check the work.

## The two layers

The project is organized around a single distinction. Every change touches one
of two layers, and knowing which one keeps the work honest.

- **Systemic** — content inside the current structure: a card, a query, a data
  source, a better label, a correction. See
  [systemic/README.md](systemic/README.md).
- **Metasystemic** — the structure that organizes the content: tabs, visual
  grammar, governance, the agent interface, the constitution itself. See
  [metasystemic/README.md](metasystemic/README.md).

Systemic changes are the daily life of the project. Metasystemic changes are
slower and require more care, because they change the lens rather than the
picture.

## Tech stack

- **Dashboards** — [Metabase](https://www.metabase.com/), embedded in the app
  through a small Node proxy.
- **Warehouse** — Postgres.
- **Ingestion** — a Python package named `arandu` (`ingestion/arandu/`), with
  connectors in `arandu/sources/` and the series catalog in
  `ingestion/config/series.yml`.
- **Frontend** — React plus a small Node server (`frontend/`).
- **Orchestration** — Docker Compose. A daily worker refreshes the data on its
  own.

## Quickstart

You will need Docker. Copy `.env.example` to `.env`, then:

```sh
make up
```

This builds and runs everything. When it is ready:

- The app is at **http://localhost:5173**
- Metabase is at **http://localhost:3000**

To build the dashboard inside Metabase:

```sh
make seed-metabase
```

## How the data standard works

Every card answers four questions:

1. **Where did this data come from?**
2. **How was it transformed?**
3. **When was it last updated?**
4. **What should the viewer be careful about?**

In practice each card already carries *Fonte* (with a URL), *Unidade*,
*Frequência*, and *Conceito*, which map directly to those four questions.

Preferred sources are public, stable, documented, and reproducible. When data is
incomplete, the incompleteness is made visible; when a category is constructed,
the construction is explained. A beautiful dashboard with weak provenance is not
accepted. A simple chart with strong provenance is.

## The visual standard

The interface should feel like a public library — readable, sparse, and
respectful of attention: no alarmism, no chartjunk, no manipulation by color,
no hidden uncertainty, no false precision.

## Contributing

Contributions are welcome, especially systemic ones. Read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request — it explains
how to label your change, what a card must include, and the pledge every
contributor affirms.

## Governance

The project is governed in public. The rules for tabs, voting, moderation, and
maintainership live in [GOVERNANCE.md](GOVERNANCE.md), and the document they all
rest on is the constitution at
[metasystemic/CONSTITUTION.md](metasystemic/CONSTITUTION.md).

## For agents

arandu.ai is meant to be useful to humans first and legible to machines next. An
agent should be able to ask what a card is, what source it uses, what query
produced it, when it was updated, and what caveats it carries — all under the
same constitutional rules that bind people. Start at
[metasystemic/agent-interface.md](metasystemic/agent-interface.md).

## Color

The project color is arandu green, `#0B5E3A`. It is used for the wordmark and
structural chrome only, never to encode or dramatize data.

---

The lens is part of the data. arandu.ai exists to keep the lens in view.
