# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-27

### Added

- **Core library** (`cwtwb`):
  - `FieldRegistry`: Field name ↔ TWB internal reference mapping with expression parsing (SUM, AVG, COUNT, YEAR, etc.)
  - `TWBEditor`: lxml-based TWB XML editor supporting:
    - Template loading and field initialization
    - Calculated field management (add/remove)
    - Worksheet creation with configurable chart types (Bar, Line, Pie, Area, Circle, Text, Automatic)
    - Color, size, label, detail, and wedge-size encodings
    - Dashboard creation with layout-flow zone structure (vertical, horizontal, grid-2x2)
    - Valid TWB output compatible with Tableau Desktop

- **MCP Server** (`server.py`):
  - 8 atomic tools: `create_workbook`, `list_fields`, `add_calculated_field`, `remove_calculated_field`, `add_worksheet`, `configure_chart`, `add_dashboard`, `save_workbook`
  - FastMCP-based stdio transport

- **Dashboard layouts**:
  - Verified against Tableau Dashboard Layout Templates (c.2 (2) reference)
  - Dashboard windows use `<viewpoints>` + `<active>` structure (not `<cards>`)
  - Zone structure uses `layout-flow` with `param='vert'/'horz'`

- **Tests**:
  - `test_debug.py`: Step-by-step debug test generating intermediate TWB files
  - `test_e2e.py`: End-to-end integration test covering all MCP tools
  - `test_c2_replica.py`: Full replica of c.2 (2) dashboard layout with 8 worksheets

- **Package configuration**:
  - `pyproject.toml` with hatchling build backend
  - `cwtwb` CLI entry point
