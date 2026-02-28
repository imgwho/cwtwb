"""cwtwb MCP Server — Tableau Workbook (.twb) generation tools.

Provides the following MCP tools:
- create_workbook: Create a new workbook from template
- list_fields: List datasource fields
- add_calculated_field: Add a calculated field
- remove_calculated_field: Remove a calculated field
- add_worksheet: Add a worksheet
- configure_chart: Configure chart type and encodings
- add_dashboard: Create a dashboard
- save_workbook: Save the TWB file
"""

import json
import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .twb_editor import TWBEditor

logger = logging.getLogger(__name__)

# Resource paths
REFERENCES_DIR = Path(__file__).parent / "references"
TABLEAU_FUNCTIONS_JSON = REFERENCES_DIR / "tableau_all_functions.json"

# ---------- MCP Server ----------

server = FastMCP(
    "cwtwb",
    instructions="Tableau Workbook (.twb) generation MCP Server. "
    "Create visualizations by calling create_workbook first, "
    "then add_worksheet + configure_chart, and finally save_workbook.",
)

# Global state: current active TWBEditor instance
_editor: Optional[TWBEditor] = None


def _get_editor() -> TWBEditor:
    """Get the current editor instance, raising if none exists."""
    if _editor is None:
        raise RuntimeError(
            "No active workbook. Call create_workbook first."
        )
    return _editor


# ---------- Resources ----------

@server.resource("file://docs/tableau_all_functions.json")
def read_tableau_functions() -> str:
    """Read the complete list of Tableau calculation functions.
    
    Returns a JSON array of function objects, containing the syntax,
    definition, examples, and output data types for all documented
    Tableau functions.
    """
    if not TABLEAU_FUNCTIONS_JSON.exists():
        raise FileNotFoundError(f"Tableau functions JSON not found at: {TABLEAU_FUNCTIONS_JSON}")
    
    with TABLEAU_FUNCTIONS_JSON.open("r", encoding="utf-8") as f:
        return f.read()


# ---------- Tools ----------


@server.tool()
def create_workbook(template_path: str, workbook_name: str = "") -> str:
    """Create a new workbook from a TWB template file.

    This must be called first before using any other tools.
    It loads the template, parses all datasource fields,
    and clears existing worksheets.

    Args:
        template_path: Absolute path to the TWB template file.
        workbook_name: Optional display name for the workbook.

    Returns:
        Summary of loaded datasource and available fields.
    """
    global _editor
    _editor = TWBEditor(template_path)
    _editor.clear_worksheets()

    lines = []
    if workbook_name:
        lines.append(f"Workbook created: {workbook_name}")
    else:
        lines.append("Workbook created from template")
    lines.append("")
    lines.append(_editor.list_fields())
    return "\n".join(lines)


@server.tool()
def list_fields() -> str:
    """List all available fields in the current workbook datasource.

    Shows dimensions and measures with their data types.
    Calculated fields are marked with [calculated].

    Returns:
        Formatted list of all fields.
    """
    editor = _get_editor()
    return editor.list_fields()


@server.tool()
def add_calculated_field(
    field_name: str,
    formula: str,
    datatype: str = "real",
) -> str:
    """Add a calculated field to the datasource.

    The formula should use Tableau calculation syntax.
    Field names in the formula should use the display names
    shown by list_fields (e.g. Sales, Profit).

    Args:
        field_name: Display name for the calculated field (e.g. "Profit Ratio").
        formula: Tableau calculation formula.
            Use field names wrapped in brackets, e.g.:
            - SUM([Profit])/SUM([Sales])
            - IF [Category] = "Technology" THEN 1 ELSE 0 END
        datatype: Result data type: real, string, integer, date, boolean.
            Default: real.

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.add_calculated_field(field_name, formula, datatype)


@server.tool()
def remove_calculated_field(field_name: str) -> str:
    """Remove a previously added calculated field.

    Args:
        field_name: Display name of the calculated field to remove.

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.remove_calculated_field(field_name)


@server.tool()
def add_worksheet(worksheet_name: str) -> str:
    """Add a new blank worksheet to the workbook.

    After adding, use configure_chart to set the chart type and fields.

    Args:
        worksheet_name: Name for the new worksheet.

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.add_worksheet(worksheet_name)


@server.tool()
def configure_chart(
    worksheet_name: str,
    mark_type: str = "Automatic",
    columns: list[str] | None = None,
    rows: list[str] | None = None,
    color: str | None = None,
    size: str | None = None,
    label: str | None = None,
    detail: str | None = None,
    wedge_size: str | None = None,
    sort_descending: str | None = None,
) -> str:
    """Configure chart type and field mappings for a worksheet.

    Field expressions use the format: AGGREGATION(FieldName) or just FieldName.

    Supported aggregations: SUM, AVG, COUNT, COUNTD, MIN, MAX, MEDIAN, ATTR.
    Supported date parts: YEAR, QUARTER, MONTH, DAY.

    For Pie charts, use 'color' for the slice dimension
    and 'wedge_size' for the measure (leave columns/rows empty).

    For Bar/Line charts, put dimensions in rows and measures in columns
    (or vice versa).

    Args:
        worksheet_name: Target worksheet name.
        mark_type: Chart mark type. One of:
            Bar, Line, Pie, Area, Circle, Square, Text, Automatic.
        columns: Column shelf field expressions (e.g. ["SUM(Sales)"]).
        rows: Row shelf field expressions (e.g. ["Category"]).
        color: Color encoding field expression.
        size: Size encoding field expression.
        label: Label encoding field expression.
        detail: Detail encoding field expression.
        wedge_size: Pie chart wedge size field expression (e.g. "SUM(Sales)").
        sort_descending: Sort dimension descending by this measure (e.g. "SUM(Sales)").

    Returns:
        Confirmation message.

    Examples:
        # Bar chart: Category vs Sales
        configure_chart("Sheet1", mark_type="Bar",
                        rows=["Category"], columns=["SUM(Sales)"])

        # Pie chart: Segment by Sales
        configure_chart("Sheet1", mark_type="Pie",
                        color="Segment", wedge_size="SUM(Sales)")

        # Line chart: Monthly sales trend
        configure_chart("Sheet1", mark_type="Line",
                        columns=["MONTH(Order Date)"],
                        rows=["SUM(Sales)"])
    """
    editor = _get_editor()
    return editor.configure_chart(
        worksheet_name=worksheet_name,
        mark_type=mark_type,
        columns=columns,
        rows=rows,
        color=color,
        size=size,
        label=label,
        detail=detail,
        wedge_size=wedge_size,
        sort_descending=sort_descending,
    )


@server.tool()
def set_mysql_connection(
    server: str,
    dbname: str,
    username: str,
    table_name: str,
    port: str = "3306",
) -> str:
    """Configure the workbook datasource to use a Local MySQL connection.

    Args:
        server: MySQL server address (e.g. "127.0.0.1")
        dbname: Database name
        username: Database username
        table_name: Table name to query
        port: MySQL port (default: 3306)

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.set_mysql_connection(
        server=server,
        dbname=dbname,
        username=username,
        table_name=table_name,
        port=port,
    )


@server.tool()
def set_tableauserver_connection(
    server: str,
    dbname: str,
    username: str,
    table_name: str,
    directory: str = "/dataserver",
    port: str = "82",
) -> str:
    """Configure the workbook datasource to use a Tableau Server connection.

    Args:
        server: Tableau Server address (e.g. "xxx.com")
        dbname: Database name on Tableau Server
        username: Username (can be empty)
        table_name: Target table name
        directory: Directory path on server (default: "/dataserver")
        port: Port number (default: 82. Common options: 80, 443, 82)

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.set_tableauserver_connection(
        server=server,
        dbname=dbname,
        username=username,
        table_name=table_name,
        directory=directory,
        port=port,
    )


@server.tool()
def add_dashboard(
    dashboard_name: str,
    worksheet_names: list[str],
    width: int = 1200,
    height: int = 800,
    layout: str | dict = "vertical",
) -> str:
    """Create a dashboard combining multiple worksheets.

    Args:
        dashboard_name: Name for the dashboard.
        worksheet_names: List of worksheet names to include.
        width: Canvas width in pixels. Default: 1200.
        height: Canvas height in pixels. Default: 800.
        layout: Layout type. One of:
            - "vertical": Stack worksheets vertically.
            - "horizontal": Place worksheets side by side.
            - "grid-2x2": 2x2 grid layout (max 4 worksheets).
            - A nested `dict` defining a complex declarative JSON layout.
            - An absolute file path to a .json file containing the layout dictionary.

    Returns:
        Confirmation message.
    """
    editor = _get_editor()
    return editor.add_dashboard(
        dashboard_name=dashboard_name,
        width=width,
        height=height,
        layout=layout,
        worksheet_names=worksheet_names,
    )


@server.tool()
def save_workbook(output_path: str) -> str:
    """Save the workbook as a TWB file.

    The file can be opened directly with Tableau Desktop.

    Args:
        output_path: Absolute path for the output .twb file.

    Returns:
        Confirmation message with the output path.
    """
    editor = _get_editor()
    return editor.save(output_path)


# ---------- Entry point ----------


def main():
    """Run the MCP server via stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
