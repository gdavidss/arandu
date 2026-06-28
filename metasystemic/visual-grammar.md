# Visual grammar

This document is the calm visual standard — [constitution](./CONSTITUTION.md) section 11 — made concrete for arandu.ai. It belongs to the **metasystemic** layer: it describes the lens, not the picture. Changing what is written here changes how every card looks, so it is a metasystemic change. See [governance](../GOVERNANCE.md).

> The interface should be calm. Readable. Sparse. Respectful of attention. No alarmism. No decorative noise. No manipulation by color. No chartjunk. No hiding uncertainty. No false precision.
>
> The interface should feel like a public library. Not a casino. Not a campaign room. Not a trading desk.

A casino dramatizes. A campaign room persuades. A trading desk alarms. A public library lets you read. arandu.ai is a public library.

The visual grammar exists for the same reason as the [data standard](../systemic/data-standard.md): to make interpretation auditable. A chart can lie without changing a single number — through scale, color, framing, or a title that tells you what to conclude. The data standard governs the numbers. The visual grammar governs how they are drawn.

## The rules

These are the section 11 rules, restated as working constraints. They are not preferences. A pull request that breaks one needs a reason or a fix.

- **Readable.** Direct labels, legible axes, metadata near the chart. The reader should not have to decode.
- **Sparse.** One question per card. High data-ink ratio. Remove anything that is not the data or a label the data needs.
- **No alarmism.** A number may be inconvenient and a trend may disturb a preferred story — that is allowed ([constitution](./CONSTITUTION.md) section 09). What is not allowed is staging it for shock: no all-red palettes, no exclamation, no urgency that the data does not itself carry.
- **No decorative noise.** No 3D, no gradients used as decoration, no gauges, no background images, no ornament.
- **No manipulation by color.** Color encodes a series or a category. It never says "this is bad" or "this is good." The brand color in particular never touches data (see below).
- **No chartjunk.** No moiré, no redundant grids, no labels repeating what an axis already says. (See the [tufte-viz](https://github.com/gdavidss/arandu) guidance the project follows: data-ink ratio, lie factor, chartjunk elimination, small multiples.)
- **No hiding uncertainty.** When data is incomplete, the incompleteness is visible. Older period presets show only the series that existed then; that gap is shown, not back-filled. Forecasts and expectations are labeled as such (e.g. the Focus expectation series is named as an expectation, not as a measurement).
- **No false precision.** Decimals match the precision the source supports. Percent series carry a `%` suffix and a sensible decimal count; counts are integers. We do not render two decimals on a number that is only known to one.

A beautiful card with a manipulative lens is not accepted. A plain card drawn honestly is welcome.

## The applied grammar

This is how the rules translate into the concrete choices every card makes. Most of it is enforced in code so a card cannot drift from it by accident — see [Where this is enforced](#where-this-is-enforced).

### The brand color is structural, never data

arandu green **`#0B5E3A`** is the brand and structural color. It is used **only** for the wordmark and the surrounding chrome (the shell, the frame, the identity of the site).

It is **never** used to encode data and never used to dramatize it. No series is green-because-brand. No bar is tinted green to draw the eye. The moment the brand color appears inside a chart, it stops being identity and starts being an argument — and the lens is supposed to be impartial. Keep the brand at the edges of the page; keep it out of the plot.

### Chart palettes are neutral and Tufte-style

Data series use the neutral categorical palette `CHART_COLORS` — a muted qualitative set (`#1f77b4`, `#d62728`, `#2ca02c`, `#9467bd`, `#ff7f0e`, `#17becf`, `#8c564b`, `#e377c2`). Color distinguishes one series from another. That is all it does.

It does not carry a verdict. Red is not "danger" and green is not "good"; they are just two of eight hues. A few tabs carry a cohesive non-red identity on purpose — for example the betting/lottery cards use a warm gold/amber set (`BETS_GOLD`, `BETS_BROWN`, `BETS_DEEP`, with a neutral grey second series) specifically to avoid an alarmist all-red look. Secondary or de-emphasized series are drawn in neutral grey (`#9aa0a6`), so the eye reads the primary line first without color implying that the secondary one is lesser in meaning.

### Chart titles are impartial

A title describes **what is shown**, not **what to conclude**. "Resultado primário (% do PIB)" describes the series. "Crise fiscal se aprofunda" tells you what to believe — that is a campaign room, not a library.

Axis titles follow the same rule and are factual: the time axis is "Data", the value axis is the unit ("% do PIB", "R$ milhões", "Taxa (% a.a.)"). The unit is part of the title's honesty — a number without a unit is an invitation to misread.

### Ordinal axes for annual bars

Annual bar charts use an **ordinal** x-axis (`graph.x_axis.scale: "ordinal"`), one bar per year, evenly spaced. A time-scaled axis would space bars by date distance and imply a continuous quantity where the data is a discrete set of years; ordinal spacing draws each year as the discrete observation it is.

### Show full ranges — no truncation

Value axes show the full range. We do not truncate a bar axis to a non-zero baseline to exaggerate a difference (the classic lie-factor move). Where a baseline carries meaning — a fiscal balance of zero — it is drawn explicitly as a labelled goal line (e.g. "Equilíbrio (0)"), not faked by cropping the axis. A log scale, where used, is a deliberate and labelled choice for a series that spans orders of magnitude, never a quiet way to flatten a trend.

### Composition uses normalized stacks

When a card shows composition — parts of a whole over time — it uses a **normalized** stack (`stackable.stack_type: "normalized"`), so the reader sees shares of 100%. This answers the composition question directly and avoids the ambiguity of a raw stack where both the total and the parts move at once. Pie charts are not used for time or for many-category breakdowns.

### No data tables as cards

A dashboard card is a chart, not a table dressed up as a card. Where an exact or latest value matters, it is shown as a chart that carries the value (a KPI/scalar, a labelled bar) rather than a grid of cells. Tables belong to the data catalog and the downloadable data, where the reader has come to read rows; on a dashboard a wall of numbers is noise, not signal.

## Where this is enforced

The grammar lives in code in [`ingestion/arandu/metabase_setup.py`](../ingestion/arandu/metabase_setup.py), so cards are seeded consistently and a deviation is visible in review:

- **`line_settings` / `bar_settings` / `time_bar_settings`** — the `*_settings` helpers that build each chart's `visualization_settings`. They set the dimensions, metric, palette (defaulting to `CHART_COLORS`), and factual axis titles ("Data" and the unit). A card built through these helpers inherits the neutral palette and impartial axes by default.
- **`CHART_COLORS`** — the neutral categorical palette. The brand color `#0B5E3A` is deliberately absent from it.
- **`VIZ_PATCHES`** — the per-card visual overrides (legend visibility, marker/interpolation, goal lines, decimal precision, the grey de-emphasis of secondary series, ordinal/log scales, normalized stacks). Deep-merged into each card's settings by the apply loop. This is where the honest-baseline goal lines and the no-false-precision decimal counts are set per card.
- **`_grid`** — lays every card out uniformly, three same-size cards per row, so the dashboard reads as an even grid rather than a hierarchy of attention-grabbing tiles. Sparseness and respect-for-attention are structural, not per-card.
- **`MANDATOS`** — the period presets (Tudo, Últimos 10 anos, and the presidential terms). These bound the time axis without hiding that coverage varies: older presets honestly show only the series that existed then.

A comment block above `DASHBOARD_TABS` in the same file names this explicitly: the `_grid`, the `*_settings` helpers, the period presets, and the calm palette together *are* the visual grammar, and changing them is a metasystemic change.

## Changing the visual grammar is metasystemic

Adding a card, fixing a label, choosing among the existing palette colors for a new series — these are **systemic** changes ([constitution](./CONSTITUTION.md) sections 03–04). They happen inside this grammar.

Changing the grammar itself — a new palette, allowing the brand color into charts, truncating axes, switching composition away from normalized stacks, adding data tables as cards, changing the title convention — is a **metasystemic** change ([constitution](./CONSTITUTION.md) sections 03 and 05). It changes the lens for every card at once.

A change to the visual grammar requires, per the constitution, a written proposal, a reason, a bias impact note, a migration plan, a rollback plan, and a public discussion period. Label it `metasystemic-change`.

The lens is part of the data. Do not change it quietly.

## See also

- [constitution](./CONSTITUTION.md) — sections 03, 05, 09, 10, 11
- [governance](../GOVERNANCE.md) — how metasystemic changes are proposed and decided
- [tabs](./tabs.md) — the canonical public rooms (also metasystemic)
- [agents](./agent-interface.md) — machine access preserves the same constitutional rules
- [../systemic/](../systemic/) — the content layer: the cards, queries, and sources that live inside this grammar
