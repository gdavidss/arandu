# Arandu

**A public lens for Brazil** — live at **[arandu.cc](https://arandu.cc)**.

Arandu is an open-source, public interface for Brazil's fiscal and economic data.
It gathers the numbers — debt, inflation, interest, revenue, spending, jobs,
trade, and more — into one calm place, each one traceable to its source, so that
citizens, researchers, journalists, builders, students, and agents can look at
the same figures and ask better questions.

Arandu is not a party, a campaign, a ministry, or a newspaper. It is a civic
instrument. The goal is not to remove interpretation — every dataset, category,
label, and chart carries choices, and pretending otherwise would be its own kind
of bias. The goal is to make interpretation **auditable**: every number traces
back to a source, a method, and a date, so anyone can check the work.

> The lens is part of the data. Arandu exists to keep the lens in view.

## What's inside

The dashboard is organized into public rooms (tabs): *Visão geral, Inflação e
juros, Atividade e emprego, Bem-estar das famílias, Pulso fiscal, Dívida, Governo
Central, Setores produtivos, Comércio exterior, Consumo digital.*

Click any card to open it full-screen and explore it with Metabase's own
visualization tools — switch to a table, a pie, a bar, a line, tweak the
settings. Your view is saved in your browser, not on the server. Every series is
downloadable as CSV, and each card states where its data comes from.

## The two layers

The project is organized around a single distinction. Every change touches one of
two layers, and naming which one keeps the work honest.

- **Systemic** — content inside the current structure: a card, a query, a data
  source, a better label, a correction. The daily life of the project. See
  [systemic/README.md](systemic/README.md).
- **Metasystemic** — the structure that organizes the content: tabs, visual
  grammar, governance, the agent interface, the constitution itself. Slower, and
  it requires a proposal — it changes the lens, not just the picture. See
  [metasystemic/README.md](metasystemic/README.md).

## Tech stack

- **Dashboards** — [Metabase](https://www.metabase.com/), embedded through a small
  Node proxy.
- **Warehouse** — Postgres.
- **Ingestion** — a Python package, `arandu` (`ingestion/arandu/`), with connectors
  in `arandu/sources/` and the series catalog in `ingestion/config/series.yml`.
- **Frontend** — React plus a small Node server (`frontend/`).
- **Orchestration** — Docker Compose; a daily worker refreshes the data on its own.

Sources include the Banco Central do Brasil (SGS, Olinda), IBGE/SIDRA, Tesouro
Nacional, MDIC/ComexStat, Receita Federal, and the ECB reference rates.

## Quickstart

You need Docker. Then:

```sh
cp .env.example .env   # adjust if needed
make up                # build + run everything
make seed-metabase     # build the dashboard inside Metabase
```

When it's up:

- App — **http://localhost:5173**
- Metabase — **http://localhost:3000**

Useful targets: `make lint`, `make test`, `make ingest`, `make down`.

## The data standard

Every card answers four questions:

1. **Where did this data come from?**
2. **How was it transformed?**
3. **When was it last updated?**
4. **What should the viewer be careful about?**

In practice each card carries *Fonte* (with a URL), *Unidade*, *Frequência*, and
*Conceito* — the same four questions. Preferred sources are public, stable,
documented, and reproducible. Incomplete data shows its incompleteness;
constructed categories explain their construction. A beautiful dashboard with weak
provenance is not accepted; a simple chart with strong provenance is. See
[systemic/data-standard.md](systemic/data-standard.md).

## The visual standard

The interface should feel like a public library — readable, sparse, respectful of
attention. No alarmism, no chartjunk, no manipulation by color, no hidden
uncertainty, no false precision. The project color, **arandu green `#0B5E3A`**, is
used for the wordmark and structural chrome only, never to encode or dramatize
data. See [metasystemic/visual-grammar.md](metasystemic/visual-grammar.md).

## Contributing

Contributions are welcome, especially systemic ones. Read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request — it explains how
to label your change, what a card must include, and the pledge every contributor
affirms.

## Governance

Arandu is governed in public. The rules for tabs, voting, moderation, and
maintainership live in [GOVERNANCE.md](GOVERNANCE.md), and the document they all
rest on is the constitution at
[metasystemic/CONSTITUTION.md](metasystemic/CONSTITUTION.md).

## For agents

Arandu is meant to be useful to humans first and legible to machines next. An
agent should be able to ask what a card is, what source it uses, what query
produced it, when it was updated, and what caveats it carries — under the same
rules that bind people.

There's a live **MCP server** ([Model Context Protocol](https://modelcontextprotocol.io))
that exposes the same warehouse data behind the charts, read-only, over streamable
HTTP at `http://localhost:8808/mcp`. Connect any MCP client:

```sh
claude mcp add --transport http arandu http://localhost:8808/mcp
```

It offers four tools — `list_series`, `search_series`, `get_series`, and
`get_series_sources` — each carrying the same provenance the cards carry. Full
details, including the JSON config form, are in
[metasystemic/agent-interface.md](metasystemic/agent-interface.md).

---

*Open source. Open data. Public method. Calm interface.* — v0.1 · Brasil
