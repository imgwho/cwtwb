"""TWB runtime validator — structural checks before saving.

This module provides lightweight validation that runs automatically
when TWBEditor.save() is called. It catches common structural issues
before writing the file to disk.

Unlike the test-time TWBAssert DSL (in tests/twb_assert.py), this
validator is designed for production use: it logs warnings instead of
raising exceptions for non-critical issues, and only raises
TWBValidationError for truly broken structures.

XSD-based validation is available via validate_against_schema() and
TWBEditor.validate_schema(). It is intentionally separate from the
save-time structural checks because XSD errors are non-fatal — Tableau
itself generates workbooks that occasionally deviate from the schema.
"""

from __future__ import annotations

import logging
import re
import io
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

logger = logging.getLogger(__name__)

# Path candidates for the vendored official Tableau TWB XSD schema.
#
# In an installed wheel (including uvx), the schema is packaged under
# cwtwb/vendor/.... In a source checkout, it lives under the repository-level
# vendor/ directory. Check both so validation works in both environments.
_PACKAGE_SCHEMA_PATH = (
    Path(__file__).parent
    / "vendor/tableau-document-schemas/schemas/2026_1/twb_2026.1.0.xsd"
)
_SOURCE_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent
    / "vendor/tableau-document-schemas/schemas/2026_1/twb_2026.1.0.xsd"
)
_SCHEMA_PATH_CANDIDATES = (_PACKAGE_SCHEMA_PATH, _SOURCE_SCHEMA_PATH)


def _resolve_schema_path() -> Path:
    """Return the first available Tableau XSD path for package/source usage."""

    for candidate in _SCHEMA_PATH_CANDIDATES:
        if candidate.exists():
            return candidate
    return _PACKAGE_SCHEMA_PATH


_SCHEMA_PATH = _resolve_schema_path()

# The TWB XSD imports two external namespaces without bundling their schemas:
#   1. http://www.tableausoftware.com/xml/user  — defines UserAttributes-AG
#   2. http://www.w3.org/XML/1998/namespace      — standard XML namespace (xml:base etc.)
# We patch the xs:import lines to add schemaLocation pointing to local stubs so
# lxml can resolve them without network access.

_STUBS: dict[str, bytes] = {
    "_user_ns_stub.xsd": b"""<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.tableausoftware.com/xml/user">
  <xs:attributeGroup name="UserAttributes-AG">
    <xs:anyAttribute namespace="##any" processContents="lax"/>
  </xs:attributeGroup>
</xs:schema>""",
    "_xml_ns_stub.xsd": b"""<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.w3.org/XML/1998/namespace">
  <xs:attribute name="lang" type="xs:language"/>
  <xs:attribute name="space">
    <xs:simpleType>
      <xs:restriction base="xs:NCName">
        <xs:enumeration value="default"/>
        <xs:enumeration value="preserve"/>
      </xs:restriction>
    </xs:simpleType>
  </xs:attribute>
  <xs:attribute name="base" type="xs:anyURI"/>
  <xs:attribute name="id" type="xs:ID"/>
</xs:schema>""",
}

_IMPORT_PATCHES: list[tuple[bytes, bytes]] = [
    (
        b'<xs:import namespace="http://www.tableausoftware.com/xml/user"/>',
        b'<xs:import namespace="http://www.tableausoftware.com/xml/user"'
        b' schemaLocation="_user_ns_stub.xsd"/>',
    ),
    (
        b'<xs:import namespace="http://www.w3.org/XML/1998/namespace"/>',
        b'<xs:import namespace="http://www.w3.org/XML/1998/namespace"'
        b' schemaLocation="_xml_ns_stub.xsd"/>',
    ),
]

# Cached parsed schema (loaded once on first use)
_xsd_schema: etree.XMLSchema | None = None
_xsd_load_error: str | None = None
_WORKBOOK_TAIL_COMPATIBILITY_RE = re.compile(
    r"Element 'workbook': Missing child element\(s\)\. Expected is one of \((?P<expected>[^)]+)\)\."
)
_KNOWN_WORKBOOK_TAIL_CHILDREN = {
    "datagraph",
    "thumbnails",
    "external",
    "referenced-extensions",
    "explain-data",
}


def _ensure_stubs() -> None:
    """Write stub XSD files alongside the main schema if they don't exist yet."""
    for filename, content in _STUBS.items():
        stub_path = _SCHEMA_PATH.parent / filename
        if not stub_path.exists():
            stub_path.write_bytes(content)


def _patched_xsd_bytes() -> bytes:
    """Return the main XSD bytes with missing imports given schemaLocation attributes."""
    raw = _SCHEMA_PATH.read_bytes()
    for old, new in _IMPORT_PATCHES:
        raw = raw.replace(old, new, 1)
    return raw


def _load_schema() -> etree.XMLSchema | None:
    """Load and cache the XSD schema. Returns None if unavailable."""
    global _xsd_schema, _xsd_load_error
    if _xsd_schema is not None:
        return _xsd_schema
    if _xsd_load_error is not None:
        return None
    if not _SCHEMA_PATH.exists():
        _xsd_load_error = f"Schema file not found: {_SCHEMA_PATH}"
        return None
    try:
        import io as _io
        _ensure_stubs()
        patched = _patched_xsd_bytes()
        # Parse with base_url so relative schemaLocation attributes resolve correctly
        xsd_doc = etree.parse(_io.BytesIO(patched), base_url=_SCHEMA_PATH.as_uri())
        _xsd_schema = etree.XMLSchema(xsd_doc)
        return _xsd_schema
    except Exception as exc:  # pragma: no cover
        _xsd_load_error = f"Failed to parse XSD schema: {exc}"
        logger.warning("XSD schema load error: %s", exc)
        return None


@dataclass
class SchemaValidationResult:
    """Result of XSD schema validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    compatibility_warnings: list[str] = field(default_factory=list)
    schema_available: bool = True

    @property
    def compatibility_only(self) -> bool:
        return not self.errors and bool(self.compatibility_warnings)

    def to_text(self) -> str:
        """Render a user-facing PASS/FAIL summary string for MCP responses."""
        if not self.schema_available:
            return (
                "XSD schema not available — Tableau TWB schema was not found "
                "in the installed package or source checkout. If running from "
                "source, run: git submodule update --init vendor/tableau-document-schemas"
            )
        if self.valid:
            return "PASS  Workbook is valid against Tableau TWB XSD schema (2026.1)"
        if self.compatibility_only:
            lines = [
                "WARN  Workbook only failed strict XSD checks on known Tableau-compatibility issues:"
            ]
            for warning in self.compatibility_warnings:
                lines.append(f"  * {warning}")
            lines.append("  * Tableau Desktop often opens these workbooks despite the strict schema mismatch.")
            return "\n".join(lines)

        issue_count = len(self.errors) + len(self.compatibility_warnings)
        lines = [f"FAIL  Schema validation failed ({issue_count} issue(s)):"]
        for err in self.errors:
            lines.append(f"  * {err}")
        for warning in self.compatibility_warnings:
            lines.append(f"  * Known compatibility issue: {warning}")
        return "\n".join(lines)


def _is_known_workbook_tail_compatibility_issue(error: str) -> bool:
    match = _WORKBOOK_TAIL_COMPATIBILITY_RE.search(error)
    if match is None:
        return False
    # validate_twb() already catches missing critical workbook children such as
    # <datasources>. Remaining top-level "missing child" failures are caused by
    # Tableau's XSD expecting optional tail containers that Desktop itself may
    # omit in otherwise openable workbooks.
    if "Element 'workbook': Missing child element(s)." in error:
        return True
    expected = {
        token.strip()
        for token in match.group("expected").split(",")
        if token.strip()
    }
    return bool(expected) and expected.issubset(_KNOWN_WORKBOOK_TAIL_CHILDREN)


def _is_known_tableau_user_specific_attribute_issue(error: str) -> bool:
    return (
        "The attribute '" in error
        and "...user-specific' is not allowed" in error
    )


def validate_against_schema(root: etree._Element) -> SchemaValidationResult:
    """Validate a TWB root element against the official Tableau XSD schema.

    Args:
        root: The root <workbook> element.

    Returns:
        SchemaValidationResult with validity flag and error list.
    """
    schema = _load_schema()
    if schema is None:
        return SchemaValidationResult(valid=True, schema_available=False)

    tree = root.getroottree()
    is_valid = schema.validate(tree)
    strict_errors: list[str] = []
    compatibility_warnings: list[str] = []
    for raw_error in schema.error_log:
        error = str(raw_error)
        if (
            _is_known_workbook_tail_compatibility_issue(error)
            or _is_known_tableau_user_specific_attribute_issue(error)
        ):
            compatibility_warnings.append(error)
        else:
            strict_errors.append(error)
    return SchemaValidationResult(
        valid=is_valid,
        errors=strict_errors,
        compatibility_warnings=compatibility_warnings,
    )


class TWBValidationError(Exception):
    """Raised when the TWB structure is fundamentally broken."""
    pass


def load_workbook_root(file_path: str | Path) -> etree._Element:
    """Parse a .twb or packaged .twbx file and return its workbook root."""

    path = Path(file_path)
    parser = etree.XMLParser(remove_blank_text=False)
    if path.suffix.lower() == ".twbx":
        with zipfile.ZipFile(path) as zf:
            twb_names = [name for name in zf.namelist() if name.lower().endswith(".twb")]
            if not twb_names:
                raise TWBValidationError(f"No .twb file found inside {path}")
            return etree.parse(io.BytesIO(zf.read(twb_names[0])), parser).getroot()
    return etree.parse(str(path), parser).getroot()


def validate_workbook_file(
    file_path: str | Path,
    *,
    require_schema: bool = False,
) -> SchemaValidationResult:
    """Run the save-time validation chain against a serialized workbook file.

    The chain is:
      1. parse the saved .twb/.twbx back from disk,
      2. run runtime structural validation,
      3. run strict XSD validation when the vendored schema is available.

    Known Tableau/XSD compatibility warnings are reported but do not fail the
    save gate. Strict XSD errors raise TWBValidationError.
    """

    root = load_workbook_root(file_path)
    validate_twb(root)
    schema_result = validate_against_schema(root)
    if require_schema and not schema_result.schema_available:
        raise TWBValidationError("XSD schema is not available for save validation")
    if schema_result.errors:
        details = "\n".join(f"  * {error}" for error in schema_result.errors)
        raise TWBValidationError(
            "Saved workbook failed Tableau TWB XSD validation:\n" + details
        )
    return schema_result


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
        if len(worksheets_el.findall("worksheet")) == 0:
            raise TWBValidationError("<worksheets> exists but contains no <worksheet> elements")
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
        if len(dashboards_el.findall("dashboard")) == 0:
            raise TWBValidationError("<dashboards> exists but contains no <dashboard> elements")
        for db in dashboards_el.findall("dashboard"):
            db_name = db.get("name", "<unnamed>")

            # Dashboard should have zones
            zones = db.find(".//zone")
            if zones is None:
                warnings.append(
                    f"Dashboard '{db_name}' has no <zone> elements")

    windows_el = root.find("windows")
    if windows_el is not None and len(windows_el.findall("window")) == 0:
        raise TWBValidationError("<windows> exists but contains no <window> elements")

    # === Log warnings ===

    for w in warnings:
        logger.warning("TWB validation: %s", w)

    return warnings
