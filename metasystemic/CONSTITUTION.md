# arandu.ai — A Constitution for Public Data

> version v0.1 · place Brazil · mode GitHub native
>
> This is the canonical text. Changing it is a metasystemic change. See [../GOVERNANCE.md](../GOVERNANCE.md).

Open source. Open data. Public method. Calm interface.

## 01 · Opening

A public lens for Brazil.

arandu.ai is a public interface for Brazilian fiscal and economic data. It is built on open source tools. It is maintained in public. It exists so citizens, researchers, journalists, builders, students, and agents can see the same numbers and ask better questions.

arandu.ai is not a party. It is not a campaign. It is not a ministry. It is not a newspaper. It is a civic instrument.

The goal is not to remove interpretation. The goal is to make interpretation auditable.

## 02 · Contributor Terms

What every contributor accepts.

By contributing to arandu.ai, I acknowledge the following terms.

I understand that I can be a source of data bias. I understand that other contributors can be a source of data bias. I understand that institutions, datasets, categories, charts, colors, labels, tabs, filters, and missing data can also carry bias.

I will not pretend that data is neutral. I will try to make the work more inspectable, more reproducible, and more honest.

I understand that every change touches a layer of the system. Some changes add content. Some changes change the lens itself.

## 03 · Grammar

Two kinds of change. Every pull request should know what layer it is touching.

**systemic:** Changes what appears inside the current structure. Examples: New card. New query. New data source. Better label. Correction.

**metasystemic:** Changes how the system itself is organized. Examples: New tab. Tab removal. Governance rule. Visual grammar. Agent interface.

## 04 · Systemic

Systemic changes.

A systemic change adds, edits, or removes content inside the current structure. Examples include a new card, a new SQL query, a new economic indicator, a correction to a chart, a new data source, a better label, a better tooltip, or a clearer methodology note.

Systemic changes should be welcomed. They are the daily life of the project.

A systemic change must include source, method, reason, known limitations, and update cadence when relevant.

A systemic change should not smuggle in a political conclusion. It may show debt, inflation, revenue, spending, poverty, growth, or uncertainty. It should not tell the user what to believe.

## 05 · Metasystemic

Metasystemic changes.

A metasystemic change changes the structure that organizes the project. Examples include adding a tab, removing a tab, renaming a tab, changing the dashboard taxonomy, changing the visual grammar, changing moderation rules, changing voting rules, changing the data acceptance standard, or changing this constitution.

Metasystemic changes are slower. They require more care. They change the lens, not only the picture.

A metasystemic change must include a written proposal, a reason, a bias impact note, a migration plan, a rollback plan, a public discussion period, and a vote when it affects tabs, governance, or public structure.

## 06 · Tabs

Tabs are constitutional.

Tabs are not decoration. Tabs define the public rooms of arandu.ai. The canonical tabs should remain stable unless changed by vote.

Initial canonical tabs: Overview. Fiscal Pulse. Governo Central. Debt. Inflation and Monetary. Federal Budget. States and Municipalities. Data Catalog.

A pull request may add cards inside a tab. A pull request may improve a tab. A pull request may clarify a tab. But no pull request may add, remove, rename, or reorder a canonical tab without a metasystemic proposal.

## 07 · Voting

Voting on structure.

A vote is required for adding a canonical tab, removing a canonical tab, renaming a canonical tab, changing the order or public meaning of canonical tabs, changing this constitution, changing voting rights, or changing maintainer powers.

A proposal must stay open for at least 14 days before a vote. During that period, contributors may ask for data, alternatives, risks, and examples.

To pass, a proposal needs at least 5 eligible voters, at least 2 maintainer approvals, a two-thirds majority of eligible votes, no unresolved reproducibility objection, and no unresolved governance objection.

If fewer than 5 eligible voters exist, maintainers may pass a provisional decision. A provisional decision expires after 90 days unless ratified.

## 08 · Voters

Voting power comes from contribution.

Voting power must come from contribution, not ideology. Eligible voters are people who have shown care for the project.

A contributor becomes eligible after two merged pull requests, one merged data source contribution, one accepted methodology review, one accepted governance proposal, or maintainer invitation based on public project work.

No person may vote with more than one identity. No organization may control more than 40 percent of counted votes on a metasystemic decision.

If coordinated capture is suspected, maintainers may pause the vote and open a governance review.

This is not to block disagreement. Disagreement is healthy. This is to block coups.

## 09 · Moderation

Bad method is not allowed.

Moderators and maintainers must protect the project from uncited claims, cherry-picked datasets, misleading chart scales, partisan framing, source laundering, methodological opacity, spam, harassment, coordinated capture, and low-quality automated pull requests.

Moderators must not block a contribution because they dislike its political implications.

A chart may be uncomfortable. A number may be inconvenient. A trend may disturb a preferred story. That is allowed. Bad method is not.

## 10 · Data Standard

Every card answers four questions.

Where did this data come from? How was it transformed? When was it last updated? What should the viewer be careful about?

Preferred sources are public, stable, documented, and reproducible. When using secondary sources, the card must explain why the original source was not used. When data is incomplete, the incompleteness must be visible. When a category is constructed, the construction must be explained.

A beautiful dashboard with weak provenance is not accepted. A simple chart with strong provenance is welcome.

## 11 · Visual Standard

The interface should be calm.

Readable. Sparse. Respectful of attention. No alarmism. No decorative noise. No manipulation by color. No chartjunk. No hiding uncertainty. No false precision.

The interface should feel like a public library. Not a casino. Not a campaign room. Not a trading desk.

## 12 · Agents

Humans first, agents next.

arandu.ai should be useful to humans first. But it should also be legible to machines.

The project may support future agent access through structured metadata, APIs, streams, or MCP-compatible interfaces.

Agents should be able to ask what a card is, what source it uses, what query produced it, when it was updated, what caveats it carries, and what changed since the last version.

Machine access must preserve the same constitutional rules.

Agents may help maintain the lens. They may not quietly rewrite the lens.

## 13 · GitHub Labels

Labels are public grammar.

Use `systemic-change` for cards, data, queries, labels, sources, and dashboard content. Use `metasystemic-change` for tabs, governance, architecture, moderation rules, visual grammar, and constitutional structure. Use `correction` for factual, methodological, or data fixes. Use `data-source` for new or changed data sources. Use `governance` for voting, moderation, maintainership, and constitutional changes. Use `agent-interface` for MCP, API, stream, or machine-readable context changes.

Other useful labels include `tab-change`, `needs-methodology`, `needs-source`, `needs-bias-note`, and `good-first-card`.

The label is not bureaucracy. The label tells the community what layer of the lens is being touched.

## 14 · Pledge

Contributor pledge.

Before contributing, I affirm:

I am contributing to a public civic instrument. I will make my work reproducible. I will cite sources. I will separate data from interpretation. I will disclose uncertainty. I will welcome correction. I will not use arandu.ai to hide bias behind charts. I will not change the structure of the project without the project consent.

I understand that the lens is part of the data.
