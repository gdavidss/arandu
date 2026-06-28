"""Systemic layer — the content that appears inside arandu.ai's structure.

A *systemic* change adds, edits, or removes content inside the current structure: a new
card, a new query, a new data source, a better label, or a correction. It does not change
how the project is organized. Systemic changes are the daily life of the project and should
be welcomed (see CONTRIBUTING.md, "Two kinds of change").

This module is a thin, importable surface over the systemic artifacts so that humans and
agents can reach the content layer without depending on internal module layout.
"""

from arandu.metabase_setup import CHART_SOURCES, CHARTS, SERIES_LABELS

__all__ = ["CHARTS", "CHART_SOURCES", "SERIES_LABELS"]
