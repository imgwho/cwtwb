"""TWBAssert — Chainable assertion DSL for validating TWB XML structure.

Usage:
    (TWBAssert(editor)
        .xml_valid()
        .worksheet_exists("Sales")
        .mark_type("Sales", "Bar")
        .has_encoding("Sales", "color")
        .dashboard_exists("Overview")
        .dashboard_contains("Overview", "Sales"))
"""

from __future__ import annotations

from lxml import etree


class TWBAssert:
    """Chainable TWB XML structure assertions."""

    def __init__(self, editor):
        self.root = editor.root
        self.editor = editor

    # ---- Basic structural validity ----

    def xml_valid(self) -> TWBAssert:
        """Assert the TWB has valid top-level structure."""
        assert self.root.tag == "workbook", f"Root tag is '{self.root.tag}', expected 'workbook'"
        assert self.root.find("datasources") is not None, "Missing <datasources>"
        assert self.root.find("worksheets") is not None, "Missing <worksheets>"
        assert self.root.find("windows") is not None, "Missing <windows>"
        return self

    # ---- Worksheet assertions ----

    def worksheet_exists(self, name: str) -> TWBAssert:
        """Assert a worksheet with the given name exists."""
        ws = self.root.find(f".//worksheet[@name='{name}']")
        assert ws is not None, f"Worksheet '{name}' not found"
        return self

    def worksheet_count(self, expected: int) -> TWBAssert:
        """Assert the number of worksheets."""
        worksheets = self.root.findall(".//worksheets/worksheet")
        actual = len(worksheets)
        assert actual == expected, f"Expected {expected} worksheets, found {actual}"
        return self

    def mark_type(self, worksheet: str, expected: str) -> TWBAssert:
        """Assert the chart mark type of a worksheet."""
        ws = self._get_worksheet(worksheet)
        mark = ws.find(".//pane/mark")
        assert mark is not None, f"Worksheet '{worksheet}' has no <mark> element"
        actual = mark.get("class")
        assert actual == expected, f"Worksheet '{worksheet}' mark type is '{actual}', expected '{expected}'"
        return self

    def has_rows(self, worksheet: str) -> TWBAssert:
        """Assert the worksheet has non-empty rows."""
        ws = self._get_worksheet(worksheet)
        rows = ws.find(".//table/rows")
        assert rows is not None and rows.text, f"Worksheet '{worksheet}' has empty <rows>"
        return self

    def has_cols(self, worksheet: str) -> TWBAssert:
        """Assert the worksheet has non-empty cols."""
        ws = self._get_worksheet(worksheet)
        cols = ws.find(".//table/cols")
        assert cols is not None and cols.text, f"Worksheet '{worksheet}' has empty <cols>"
        return self

    def rows_contain(self, worksheet: str, text: str) -> TWBAssert:
        """Assert the rows element contains specific text."""
        ws = self._get_worksheet(worksheet)
        rows = ws.find(".//table/rows")
        assert rows is not None and rows.text and text in rows.text, \
            f"Worksheet '{worksheet}' rows do not contain '{text}'"
        return self

    def cols_contain(self, worksheet: str, text: str) -> TWBAssert:
        """Assert the cols element contains specific text."""
        ws = self._get_worksheet(worksheet)
        cols = ws.find(".//table/cols")
        assert cols is not None and cols.text and text in cols.text, \
            f"Worksheet '{worksheet}' cols do not contain '{text}'"
        return self

    # ---- Encoding assertions ----

    def has_encoding(self, worksheet: str, encoding_type: str) -> TWBAssert:
        """Assert the worksheet has an encoding of the given type.
        
        Args:
            encoding_type: One of 'color', 'size', 'text', 'lod', 
                          'wedge-size', 'tooltip', 'geometry'.
        """
        ws = self._get_worksheet(worksheet)
        enc = ws.find(f".//encodings/{encoding_type}")
        assert enc is not None, f"Worksheet '{worksheet}' missing '{encoding_type}' encoding"
        return self

    def encoding_contains(self, worksheet: str, encoding_type: str, text: str) -> TWBAssert:
        """Assert an encoding's column attribute contains specific text."""
        ws = self._get_worksheet(worksheet)
        enc = ws.find(f".//encodings/{encoding_type}")
        assert enc is not None, f"Worksheet '{worksheet}' missing '{encoding_type}' encoding"
        col = enc.get("column", "")
        assert text in col, f"Encoding '{encoding_type}' column='{col}' does not contain '{text}'"
        return self

    # ---- Datasource dependency assertions ----

    def field_in_deps(self, worksheet: str, field_name: str) -> TWBAssert:
        """Assert a field appears in the worksheet's datasource-dependencies."""
        ws = self._get_worksheet(worksheet)
        deps = ws.find(".//datasource-dependencies")
        assert deps is not None, f"Worksheet '{worksheet}' has no datasource-dependencies"
        cols = deps.findall("column")
        found = any(field_name in c.get("name", "") or field_name in c.get("caption", "")
                     for c in cols)
        assert found, f"Field '{field_name}' not found in '{worksheet}' deps"
        return self

    # ---- Filter assertions ----

    def has_filter(self, worksheet: str, field_contains: str) -> TWBAssert:
        """Assert the worksheet view has a filter containing the given field text."""
        ws = self._get_worksheet(worksheet)
        filters = ws.findall(".//filter")
        found = any(field_contains in f.get("column", "") for f in filters)
        assert found, f"No filter containing '{field_contains}' in worksheet '{worksheet}'"
        return self

    # ---- Parameter assertions ----

    def has_parameter(self, name: str) -> TWBAssert:
        """Assert a parameter exists in the editor's tracking."""
        assert name in self.editor._parameters, \
            f"Parameter '{name}' not in tracked parameters: {list(self.editor._parameters.keys())}"
        return self

    def parameter_datasource_exists(self) -> TWBAssert:
        """Assert the Parameters datasource exists in the workbook."""
        params_ds = None
        for ds in self.root.findall(".//datasource"):
            if ds.get("name") == "Parameters":
                params_ds = ds
                break
        assert params_ds is not None, "Parameters datasource not found"
        return self

    # ---- Dashboard assertions ----

    def dashboard_exists(self, name: str) -> TWBAssert:
        """Assert a dashboard with the given name exists."""
        db = self.root.find(f".//dashboards/dashboard[@name='{name}']")
        assert db is not None, f"Dashboard '{name}' not found"
        return self

    def dashboard_contains(self, dashboard: str, worksheet: str) -> TWBAssert:
        """Assert a dashboard contains a zone for the given worksheet."""
        db = self.root.find(f".//dashboards/dashboard[@name='{dashboard}']")
        assert db is not None, f"Dashboard '{dashboard}' not found"
        zones = db.findall(f".//zone[@name='{worksheet}']")
        assert len(zones) > 0, f"Dashboard '{dashboard}' does not contain worksheet zone '{worksheet}'"
        return self

    def dashboard_has_zone_type(self, dashboard: str, zone_type: str) -> TWBAssert:
        """Assert a dashboard contains at least one zone of the given type-v2."""
        db = self.root.find(f".//dashboards/dashboard[@name='{dashboard}']")
        assert db is not None, f"Dashboard '{dashboard}' not found"
        zones = db.findall(f".//zone[@type-v2='{zone_type}']")
        assert len(zones) > 0, f"Dashboard '{dashboard}' has no zone of type '{zone_type}'"
        return self

    # ---- Map-specific assertions ----

    def has_mapsources(self, worksheet: str) -> TWBAssert:
        """Assert the worksheet view has mapsources."""
        ws = self._get_worksheet(worksheet)
        ms = ws.find(".//mapsources")
        assert ms is not None, f"Worksheet '{worksheet}' has no mapsources"
        return self

    # ---- Calculated field assertions ----

    def has_calculated_field(self, field_name: str) -> TWBAssert:
        """Assert a calculated field exists in the datasource."""
        fi = self.editor.field_registry.get(field_name)
        assert fi is not None, f"Calculated field '{field_name}' not registered"
        assert fi.is_calculated, f"Field '{field_name}' exists but is not calculated"
        return self

    # ---- Helpers ----

    def _get_worksheet(self, name: str):
        ws = self.root.find(f".//worksheet[@name='{name}']")
        assert ws is not None, f"Worksheet '{name}' not found"
        return ws
