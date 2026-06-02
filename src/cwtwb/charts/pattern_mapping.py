"""Chart pattern normalization helpers.

These helpers keep advanced chart patterns explicit without changing the public
API surface. Core builders can use them to normalize advanced chart patterns such as
Scatterplot or Tree Map onto the underlying Tableau mark primitives.
"""
from __future__ import annotations

from dataclasses import dataclass


# Tableau 18.1 mark class enumeration (from workbook XSD).
# Any mark class not in this set is rejected by the runtime, so we never write
# an invalid value into <mark class="…"/>.
# ``Multipolygon`` is a map-layer-only class accepted by the same schema.
TABLEAU_MARK_CLASSES: frozenset[str] = frozenset({
    "Automatic",
    "Bar",
    "Line",
    "Area",
    "Circle",
    "Square",
    "Shape",
    "Pie",
    "Polygon",
    "GanttBar",
    "Text",
    "Map",
    "Multipolygon",
})

# Friendly aliases → underlying Tableau mark class.
# Keep the alias set conservative: every key must map to a real Tableau class.
MARK_ALIASES: dict[str, str] = {
    "Scatterplot": "Circle",
    "Scatter": "Circle",         # cwtwb extension: short alias for the common case
    "Bubble Chart": "Circle",
    "Heatmap": "Square",
    "Tree Map": "Square",
}


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
    """Resolve advanced chart aliases onto their underlying Tableau marks.

    Known aliases (e.g. ``"Scatterplot"``, ``"Tree Map"``) and the canonical
    Tableau mark classes are mapped to a primitive mark string.  Unrecognised
    inputs are passed through unchanged so that recipe-level patterns such as
    ``"Donut"`` can still reach their specialised handling downstream.

    The canonical mark-class list is exported as :data:`TABLEAU_MARK_CLASSES`
    and the alias mapping as :data:`MARK_ALIASES` so that builders can perform
    their own validation at XML-write time without affecting routing policy.
    """

    resolved_columns = list(columns or [])
    resolved_rows = list(rows or [])

    if mark_type in MARK_ALIASES:
        actual_mark_type = MARK_ALIASES[mark_type]
    else:
        # Pass through unknown mark types (e.g. recipe-level "Donut") so that
        # higher-level routing can decide how to handle them.  The mark-class
        # whitelist check happens in the builder when writing the XML.
        actual_mark_type = mark_type

    if mark_type in ("Tree Map", "Bubble Chart"):
        resolved_columns = []
        resolved_rows = []

    return PatternResolution(
        requested_mark_type=mark_type,
        actual_mark_type=actual_mark_type,
        columns=resolved_columns,
        rows=resolved_rows,
    )
