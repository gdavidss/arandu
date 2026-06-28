# GitHub labels

Labels are public grammar — they tell the community what layer of the lens is being touched.

A label is not bureaucracy. It is a signal: it names which part of the system a pull request or issue reaches into, so reviewers and readers know what kind of care is owed. See section 13 of the [constitution](../metasystemic/constitution.md).

The palette is a calm green family, anchored on arandu green `#0B5E3A`. Darker greens mark structure (metasystemic, governance, tabs); lighter greens and sage mark content (systemic, correction, data, agents). The `needs-*` labels are muted amber and gray — they request, they do not accuse. The brand green is structural chrome only; it never encodes or dramatizes data.

## Labels

| Label | What it marks | Color |
| --- | --- | --- |
| `systemic-change` | Content inside the current structure: cards, queries, data, sources, labels, tooltips, methodology notes, dashboard content. The daily life of the project. | `2E8B57` |
| `metasystemic-change` | Changes to the structure that organizes the project: tabs, governance, architecture, moderation rules, visual grammar, constitutional structure. Changes the lens, not only the picture. | `0B5E3A` |
| `correction` | A factual, methodological, or data fix. | `4C9A6E` |
| `data-source` | A new or changed data source. | `6BAE85` |
| `governance` | Voting, moderation, maintainership, and constitutional changes. | `0B5E3A` |
| `agent-interface` | MCP, API, stream, or machine-readable context changes. | `5FA37E` |
| `tab-change` | Adds, removes, renames, or reorders a canonical tab. Metasystemic; requires a proposal and a vote. | `08402A` |
| `needs-methodology` | The change must explain how the data was transformed before it can be accepted. | `B8860B` |
| `needs-source` | The change must cite where the data came from before it can be accepted. | `C9971F` |
| `needs-bias-note` | The change must state what the viewer should be careful about before it can be accepted. | `A98A4B` |
| `good-first-card` | A small, well-scoped systemic change suited to a first contribution. | `A8D5BA` |

## Creating the labels

These are 6-hex colors with no leading `#`, ready for `gh label create`:

```bash
gh label create systemic-change     --color 2E8B57 --description "Content inside the current structure: cards, queries, data, sources, labels, dashboard content"
gh label create metasystemic-change --color 0B5E3A --description "Changes the structure that organizes the project: tabs, governance, architecture, visual grammar"
gh label create correction          --color 4C9A6E --description "A factual, methodological, or data fix"
gh label create data-source         --color 6BAE85 --description "A new or changed data source"
gh label create governance          --color 0B5E3A --description "Voting, moderation, maintainership, and constitutional changes"
gh label create agent-interface     --color 5FA37E --description "MCP, API, stream, or machine-readable context changes"
gh label create tab-change          --color 08402A --description "Adds, removes, renames, or reorders a canonical tab (metasystemic; needs a vote)"
gh label create needs-methodology   --color B8860B --description "Must explain how the data was transformed before acceptance"
gh label create needs-source        --color C9971F --description "Must cite where the data came from before acceptance"
gh label create needs-bias-note     --color A98A4B --description "Must state what the viewer should be careful about before acceptance"
gh label create good-first-card     --color A8D5BA --description "A small, well-scoped systemic change suited to a first contribution"
```

## Choosing a label

Most pull requests carry one of the two layer labels, plus any that apply.

- Systemic work — a new card, a new query, a new source, a correction — uses `systemic-change`, and `correction`, `data-source`, or `good-first-card` when they fit.
- Anything that touches a canonical tab, governance, architecture, moderation, the visual grammar, or this constitution uses `metasystemic-change`, with `tab-change` or `governance` when they fit. These changes are slower and usually require a vote; see [GOVERNANCE.md](../GOVERNANCE.md) and [tabs.md](../metasystemic/tabs.md).
- The `needs-*` labels are added by reviewers when a change is missing source, method, or a bias note. They are requests, not rejections. A chart may be uncomfortable; bad method is not allowed.

Before opening a pull request, read [CONTRIBUTING.md](../CONTRIBUTING.md) and choose your layer in the [pull request template](PULL_REQUEST_TEMPLATE.md).
