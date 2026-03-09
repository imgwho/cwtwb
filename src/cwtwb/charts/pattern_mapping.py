"""Chart pattern normalization helpers.

These helpers keep advanced chart patterns explicit without changing the public
API surface. Core builders can use them to normalize advanced patterns such as
Scatterplot or Tree Map onto the underlying Tableau mark primitives.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternResolution:
    """Normalized mark configuration for basic-chart style builders."""

    requested_mark_type: str
    actual_mark_type: str
    columns: list[str]
    rows: list[str]


def normalize_chart_pattern(
    mark_type: str,
    columns: list[str] | None = None,
    rows: list[str] | None = None,
    color: str | None = None,
) -> PatternResolution:
    """Resolve advanced chart aliases onto their underlying Tableau marks."""

    resolved_columns = list(columns or [])
    resolved_rows = list(rows or [])
    actual_mark_type = mark_type

    if mark_type == "Scatterplot":
        actual_mark_type = "Circle"
    elif mark_type == "Heatmap":
        actual_mark_type = "Square"
        if not color and resolved_columns and resolved_rows:
            # Keep existing behavior. The visual still resolves, but the lack of
            # color remains the caller's responsibility.
            pass
    elif mark_type == "Tree Map":
        actual_mark_type = "Square"
        resolved_columns = []
        resolved_rows = []
    elif mark_type == "Bubble Chart":
        actual_mark_type = "Circle"
        resolved_columns = []
        resolved_rows = []

    return PatternResolution(
        requested_mark_type=mark_type,
        actual_mark_type=actual_mark_type,
        columns=resolved_columns,
        rows=resolved_rows,
    )
