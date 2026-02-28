# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-28

### Added

- **Agentic UX Tool: `generate_layout_json`**:
  - Introduced a dedicated MCP tool tailored for Language Models to handle complex dashboard layouts gracefully avoiding `EOF` (End of File) payload oversize crashes.
  - Automatically wraps standard nested `layout` dicts inside the payload with a human-readable `_ascii_layout_preview`, persisting an easy-to-review design draft to local disk.
  - Generates perfectly calculated XML `<zone>` absolute coordinates (in Tableau's 100,000 scale) for both relative weighting (`weight`) and exact sizes (`fixed_size`).
- `TWBEditor.add_dashboard()` intelligent parsing:
  - If given a file path, it now smartly unpacks the layout JSON, automatically extracting `"layout_schema"` and safely discarding extraneous metadata (like the ASCII diagram).
- **Prompt Strategies (`demo_simple.md`)**:
  - Updated the golden prompt strategy guide showing models how to seamlessly split reasoning logic: Step 1 (Tool: write layout to disk) -> Step 2 (Tool: pass file path to build dashboard).

## [0.2.0] - 2026-02-28

### Added

- **Database Connections**:
  - `TWBEditor.set_mysql_connection`: Configure TWB to load data from a Local MySQL database.
  - `TWBEditor.set_tableauserver_connection`: Configure TWB for a Tableau Server hosted datasource.
  - Automatically clears template-included dashboards, worksheets, metadata, and column aliases during config to prevent phantom "ghost" fields.
- **Dynamic Field Registration**:
  - The `field_registry` will now automatically infer the field type natively via naming heuristics when initializing `configure_chart` on strictly offline unknown schemas.
- **Declarative JSON Dashboard Layouts**:
  - `add_dashboard` now accepts a deeply nested dictionary (JSON-friendly) `layout` schema, allowing complex, FlexBox-like hierarchical layouts.
  - `add_dashboard` `layout` parameter also directly accepts a file path (string) to a `.json` file, easing the payload size for MCP LLM calls.
  - Generates perfectly calculated XML `<zone>` absolute coordinates (in Tableau's 100,000 scale) for both relative weighting (`weight`) and exact sizes (`fixed_size`).
  - Added `demo_declarative_layout.py` showcasing the JSON engine.
- **MCP Server Tools**:
  - Exposed `set_mysql_connection` and `set_tableauserver_connection` to the MCP Server.
  - Upgraded `add_dashboard` MCP tool to accept JSON-based dictionaries and JSON file paths for the `layout` schema.
- **Examples & Documentation**:
  - Reorganized the `examples/` directory into `scripts/` (for Python demos) and `prompts/` (for natural language MCP prompts).
  - Extracted test workflows into runnable demos (`demo_e2e_mcp_workflow.py` and `demo_connections.py`).

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
