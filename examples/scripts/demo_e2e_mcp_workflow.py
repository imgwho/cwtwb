"""Demo: End-to-End MCP Server Workflow

This script demonstrates how to use the exact same functions that the MCP server exposes 
to build a complete dashboard workflow: from loading a template to adding fields, 
creating charts, and building a layout.

Usage:
    python examples/demo_e2e_mcp_workflow.py
"""

import sys
from pathlib import Path

# Add src to path so we can import local cwtwb server tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# These are the actual tool functions exposed to the LLM via FastMCP
from cwtwb.server import (
    create_workbook,
    list_fields,
    add_calculated_field,
    add_worksheet,
    configure_chart,
    add_dashboard,
    save_workbook,
)

def main():
    project_root = Path(__file__).parent.parent.parent
    template = str(project_root / "templates" / "twb" / "superstore.twb")
    output = str(project_root / "output" / "demo_e2e_mcp_workflow.twb")

    print("=== Demo: End-to-End MCP Workflow ===")

    # 1. Initialize the global workbook state
    print("\n1. Calling `create_workbook`...")
    result = create_workbook(template, "Sales Overview")
    print(f"   -> Read {len(result.splitlines())} lines of field metadata.")

    # 2. Add a calculated field using Tableau syntax
    print("\n2. Calling `add_calculated_field`...")
    result = add_calculated_field(
        field_name="Profit Ratio",
        formula="SUM([Profit])/SUM([Sales])",
        datatype="real",
    )
    print(f"   -> {result}")

    # 3. List available fields to verify
    print("\n3. Calling `list_fields`...")
    result = list_fields()
    if "Profit Ratio" in result:
        print("   -> Success: Found 'Profit Ratio' in the metadata!")

    # 4. Create blank worksheets
    print("\n4. Calling `add_worksheet`...")
    print(f"   -> {add_worksheet('Sales by Category')}")
    print(f"   -> {add_worksheet('Segment Breakdown')}")

    # 5. Configure Visualizations
    print("\n5. Calling `configure_chart`...")
    
    # Configure a Bar chart
    result = configure_chart(
        worksheet_name="Sales by Category",
        mark_type="Bar",
        rows=["Category"],
        columns=["SUM(Sales)"],
        sort_descending="SUM(Sales)" # Sort Category by Sales desc
    )
    print(f"   -> {result}")

    # Configure a Pie chart
    result = configure_chart(
        worksheet_name="Segment Breakdown",
        mark_type="Pie",
        color="Segment",
        wedge_size="SUM(Sales)",
    )
    print(f"   -> {result}")

    # 6. Assemble into a Dashboard layout
    print("\n6. Calling `add_dashboard`...")
    result = add_dashboard(
        dashboard_name="Sales Executive View",
        worksheet_names=["Sales by Category", "Segment Breakdown"],
        layout="horizontal", # Simple side-by-side flex layout
    )
    print(f"   -> {result}")

    # 7. Finalize and Save
    print("\n7. Calling `save_workbook`...")
    result = save_workbook(output)
    print(f"   -> {result}")

    print("\nSuccess! You have just simulated a complete MCP LLM thought-process.")
    print(f"Open {output} in Tableau Desktop to explore.")

if __name__ == "__main__":
    main()
