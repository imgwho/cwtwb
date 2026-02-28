# cwtwb

> **Tableau Workbook (.twb) Generation MCP Server**  
> Programmatically create Tableau workbooks with calculated fields, multiple chart types, and dashboard layouts.

## Overview

**cwtwb** is a Model Context Protocol (MCP) server that generates Tableau Desktop workbook files (`.twb`) from AI-driven tool calls. It provides atomic operations for building visualizations step by step:

1. Load a TWB template with data connections
2. Add calculated fields
3. Create worksheets with various chart types
4. Assemble dashboards with flexible layouts
5. Save valid `.twb` files that open directly in Tableau Desktop

## Installation

```bash
pip install -e .
```

### Requirements

- Python ≥ 3.10
- [lxml](https://lxml.de/) ≥ 5.0
- [mcp](https://pypi.org/project/mcp/) ≥ 1.0

## Quick Start

### As MCP Server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "cwtwb": {
      "command": "cwtwb",
      "args": []
    }
  }
}
```

Or run directly:

```bash
cwtwb
```

### As Python Library

```python
from cwtwb.twb_editor import TWBEditor

editor = TWBEditor("templates/twb/superstore.twb")
editor.clear_worksheets()

# Add a calculated field
editor.add_calculated_field("Profit Ratio", "SUM([Profit])/SUM([Sales])")

# Create a bar chart
editor.add_worksheet("Sales by Category")
editor.configure_chart(
    worksheet_name="Sales by Category",
    mark_type="Bar",
    rows=["Category"],
    columns=["SUM(Sales)"],
)

# Create a pie chart
editor.add_worksheet("Segment Pie")
editor.configure_chart(
    worksheet_name="Segment Pie",
    mark_type="Pie",
    color="Segment",
    wedge_size="SUM(Sales)",
)

# Build a dashboard
editor.add_dashboard(
    dashboard_name="Overview",
    worksheet_names=["Sales by Category", "Segment Pie"],
    layout="horizontal",
)

editor.save("output/my_workbook.twb")
```

## MCP Tools

| Tool | Description |
|---|---|
| `create_workbook` | Load a TWB template and initialize the workspace |
| `list_fields` | List all available dimensions and measures |
| `add_calculated_field` | Add a calculated field with Tableau formula |
| `remove_calculated_field` | Remove a previously added calculated field |
| `add_worksheet` | Add a new blank worksheet |
| `configure_chart` | Configure chart type and field mappings |
| `add_dashboard` | Create a dashboard combining worksheets |
| `set_mysql_connection` | Configure the datasource to use a local MySQL connection |
| `set_tableauserver_connection` | Configure connection to an online Tableau Server |
| `save_workbook` | Save the final TWB file |

## Supported Chart Types

- **Bar** — horizontal/vertical bar charts
- **Line** — line charts and trends
- **Pie** — pie charts with color and wedge-size encodings
- **Area** — area charts
- **Circle** / **Square** — shape marks
- **Text** — text tables
- **Automatic** — Tableau's automatic mark type

## Dashboard Layouts

| Layout | Description |
|---|---|
| `vertical` | Stack worksheets top to bottom |
| `horizontal` | Place worksheets side by side |
| `grid-2x2` | 2×2 grid layout (up to 4 worksheets) |
| `dict` (JSON) | **Declarative Custom Layouts**: An infinitely nestable FlexBox-style JSON structure for enterprise dashboards. |

Custom layouts can be built programmatically using the `TWBEditor` API by passing a `layout` nested dictionary. See `examples/scripts/demo_declarative_layout.py` for a complete example of generating a side-bar executive dashboard.

## Project Structure

```
cwtwb/
├── src/cwtwb/
│   ├── __init__.py          # Package init
│   ├── field_registry.py    # Field name ↔ TWB reference mapping
│   ├── twb_editor.py        # Core TWB XML editor (lxml)
│   └── server.py            # MCP server with FastMCP
├── tests/
│   ├── test_debug.py        # Step-by-step debug tests
│   ├── test_e2e.py          # End-to-end integration test
│   └── test_c2_replica.py   # Full dashboard layout replica
├── templates/
│   ├── superstore.twb       # Base TWB template with data connection
├── examples/                # Example scripts and prompts
│   ├── scripts/             # Python examples for SDK and workflow
│   ├── prompts/             # Natural language prompts for MCP LLM
│   └── layouts/             # JSON declarative layout definitions
├── docs/                    # Design documents
├── pyproject.toml           # Package configuration
└── README.md
```

## Development

```bash
# Install in editable mode
pip install -e .

# Run tests
python tests/test_e2e.py
python tests/test_c2_replica.py

# Start MCP server
cwtwb
```

## License

MIT
