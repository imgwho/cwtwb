"""Shared measure-intent helpers.

These helpers keep SDK chart builders and MCP authoring flows aligned on the
same default aggregation behavior:

- Bare, non-calculated measures default to SUM(...)
- Explicit expressions are preserved
- Calculated fields are preserved
"""

from __future__ import annotations

from typing import Iterable

AGGREGATE_FUNCTION_PREFIXES = (
    "sum(",
    "avg(",
    "count(",
    "countd(",
    "min(",
    "max(",
    "median(",
    "attr(",
)


def is_expression(value: str) -> bool:
    """Return whether a string already looks like a Tableau expression."""

    text = str(value).strip()
    if not text:
        return False
    if text.startswith("["):
        return True
    lower = text.casefold()
    return any(lower.startswith(prefix) for prefix in AGGREGATE_FUNCTION_PREFIXES)


def default_measure_expression(
    field_name: str,
    *,
    known_calculated_name: str = "",
    calculated_field_names: set[str] | None = None,
) -> str:
    """Return the canonical view expression for a measure-like field."""

    text = str(field_name).strip()
    if not text:
        return ""
    if is_expression(text):
        return text
    known_text = str(known_calculated_name).strip()
    if known_text:
        return known_text
    if calculated_field_names is None:
        calculated_field_names = set()
    if text in calculated_field_names:
        return text
    normalized = " ".join(text.casefold().replace("_", " ").replace("-", " ").split())
    if normalized == "discount":
        return f"AVG({text})"
    return f"SUM({text})"


def default_view_expression(
    field_name: str,
    *,
    role: str = "",
    is_calculated: bool = False,
    calculated_field_names: set[str] | None = None,
) -> str:
    """Return the canonical view binding for a field.

    Non-calculated measures are promoted to SUM(...). Dimensions and explicit
    expressions are preserved.
    """

    text = str(field_name).strip()
    if not text:
        return ""
    if is_expression(text):
        return text
    if role == "measure" and not is_calculated:
        return default_measure_expression(text, calculated_field_names=calculated_field_names)
    return text


def normalize_measure_args(
    measure_args: dict[str, str],
    *,
    keys: Iterable[str],
    calculated_field_names: set[str] | None = None,
) -> dict[str, str]:
    """Return a copy of measure-like recipe args with default expressions applied."""

    normalized = dict(measure_args)
    for key in keys:
        value = str(normalized.get(key, "")).strip()
        if value:
            normalized[key] = default_measure_expression(
                value,
                calculated_field_names=calculated_field_names,
            )
    return normalized
