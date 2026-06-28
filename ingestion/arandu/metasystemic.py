"""Metasystemic layer — the structure that organizes arandu.ai.

A *metasystemic* change changes the lens itself: adding, removing, renaming, or reordering
a tab; changing the dashboard taxonomy; changing the visual grammar; or changing
governance. It is slower and requires more care — a proposal, a bias-impact note, and a
vote when it touches public structure (see GOVERNANCE.md and metasystemic/CONSTITUTION.md).

This module is a thin, importable surface over the structural artifacts: the canonical
tabs, the period presets, and the calm visual grammar.
"""

from arandu.metabase_setup import (
    DASHBOARD_TABS,
    DISPLAY_OVERRIDES,
    MANDATOS,
    VIZ_PATCHES,
    _grid,
    bar_settings,
    line_settings,
    time_bar_settings,
)

__all__ = [
    "DASHBOARD_TABS",
    "VIZ_PATCHES",
    "DISPLAY_OVERRIDES",
    "MANDATOS",
    "_grid",
    "line_settings",
    "bar_settings",
    "time_bar_settings",
]
