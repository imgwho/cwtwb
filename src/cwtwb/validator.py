"""TWB runtime validator — structural checks before saving.

This module provides lightweight validation that runs automatically
when TWBEditor.save() is called. It catches common structural issues
before writing the file to disk.

Unlike the test-time TWBAssert DSL (in tests/twb_assert.py), this
validator is designed for production use: it logs warnings instead of
raising exceptions for non-critical issues, and only raises
TWBValidationError for truly broken structures.
"""

from __future__ import annotations

import logging
from lxml import etree

logger = logging.getLogger(__name__)


class TWBValidationError(Exception):
    """Raised when the TWB structure is fundamentally broken."""
    pass


def validate_twb(root: etree._Element) -> list[str]:
    """Validate TWB XML structure before saving.

    Args:
        root: The root <workbook> element.

    Returns:
        List of warning messages (non-fatal issues).

    Raises:
        TWBValidationError: If the structure is fundamentally broken.
    """
    warnings = []

    # === Critical checks (raise on failure) ===

    if root.tag != "workbook":
        raise TWBValidationError(
            f"Root element is <{root.tag}>, expected <workbook>")

    datasources = root.find("datasources")
    if datasources is None:
        raise TWBValidationError("Missing <datasources> element")

    if len(datasources.findall("datasource")) == 0:
        raise TWBValidationError("No <datasource> elements found")

    # === Worksheet checks ===

    worksheets_el = root.find("worksheets")
    if worksheets_el is not None:
        for ws in worksheets_el.findall("worksheet"):
            ws_name = ws.get("name", "<unnamed>")

            # Every worksheet must have a <table>
            table = ws.find("table")
            if table is None:
                raise TWBValidationError(
                    f"Worksheet '{ws_name}' is missing <table> element")

            # Table should have <view>
            view = table.find("view")
            if view is None:
                warnings.append(
                    f"Worksheet '{ws_name}' has no <view> element")

            # Table should have <panes> or <pane>
            panes = table.find("panes")
            pane = table.find("pane")
            if panes is None and pane is None:
                warnings.append(
                    f"Worksheet '{ws_name}' has no <panes>/<pane> element")

            # Check mark type exists
            mark = ws.find(".//mark[@class]")
            if mark is None:
                warnings.append(
                    f"Worksheet '{ws_name}' has no <mark> with class attribute")

    # === Dashboard checks ===

    dashboards_el = root.find("dashboards")
    if dashboards_el is not None:
        for db in dashboards_el.findall("dashboard"):
            db_name = db.get("name", "<unnamed>")

            # Dashboard should have zones
            zones = db.find(".//zone")
            if zones is None:
                warnings.append(
                    f"Dashboard '{db_name}' has no <zone> elements")

    # === Log warnings ===

    for w in warnings:
        logger.warning("TWB validation: %s", w)

    return warnings
