"""Shared measure-intent helpers.

These helpers keep SDK chart builders and MCP authoring flows aligned on the
same default view-binding behavior:

- Bare, non-calculated numeric measures default to SUM(...)
- Bare date/time-like fields default to MONTH(...)
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
    "month(",
    "quarter(",
    "year(",
    "week(",
    "weekday(",
    "day(",
    "hour(",
    "minute(",
    "second(",
    "date(",
    "datetime(",
    "dateadd(",
    "datediff(",
    "datetrunc(",
    "dateparse(",
    "my(",
    "daytrunc(",
)

DATE_FIELD_HINTS = (
    "date",
    "time",
    "year",
    "month",
    "quarter",
    "week",
    "weekday",
    "day",
    "hour",
    "minute",
    "second",
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


def looks_like_date_field_name(field_name: str) -> bool:
    """Return whether a bare field name looks like a date or time field."""

    text = str(field_name).strip()
    if not text:
        return False
    normalized = " ".join(text.casefold().replace("_", " ").replace("-", " ").split())
    return any(token in normalized for token in DATE_FIELD_HINTS)


def default_date_expression(field_name: str) -> str:
    """Return the default Tableau date binding for a bare field name."""

    text = str(field_name).strip()
    if not text:
        return ""
    if is_expression(text):
        return text
    return f"MONTH({text})"


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
    if looks_like_date_field_name(text):
        return default_date_expression(text)
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
        if looks_like_date_field_name(text):
            return default_date_expression(text)
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
