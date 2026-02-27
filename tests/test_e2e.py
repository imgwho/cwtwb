"""End-to-end test: exercise all MCP tools through direct Python calls.

This test simulates the full workflow:
1. create_workbook
2. list_fields
3. add_calculated_field
4. add_worksheet x2
5. configure_chart (bar + pie)
6. add_dashboard
7. save_workbook

Output: output/e2e_test.twb
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
    project_root = Path(__file__).parent.parent
    template = str(project_root / "template.twb")
    output = str(project_root / "output" / "e2e_test.twb")

    # 1. Create workbook
    print("=== 1. create_workbook ===")
    result = create_workbook(template, "E2E Test")
    print(result[:200], "...")
    print()

    # 2. List fields
    print("=== 2. list_fields ===")
    result = list_fields()
    print(result[:200], "...")
    print()

    # 3. Add calculated field
    print("=== 3. add_calculated_field ===")
    result = add_calculated_field(
        "Profit Ratio",
        "SUM([Profit (Orders)])/SUM([Sales (Orders)])",
        "real",
    )
    print(result)
    print()

    # Verify it shows up
    result = list_fields()
    assert "Profit Ratio" in result, "Calculated field not found!"
    print("[PASS] Calculated field registered")
    print()

    # 4. Add worksheets
    print("=== 4. add_worksheet ===")
    result = add_worksheet("Sales by Category")
    print(result)
    result = add_worksheet("Segment Pie")
    print(result)
    print()

    # 5. Configure charts
    print("=== 5. configure_chart ===")

    # Bar chart
    result = configure_chart(
        worksheet_name="Sales by Category",
        mark_type="Bar",
        rows=["Category"],
        columns=["SUM(Sales)"],
    )
    print(result)

    # Pie chart
    result = configure_chart(
        worksheet_name="Segment Pie",
        mark_type="Pie",
        color="Segment",
        wedge_size="SUM(Sales)",
    )
    print(result)
    print()

    # 6. Add dashboard
    print("=== 6. add_dashboard ===")
    result = add_dashboard(
        dashboard_name="Overview",
        worksheet_names=["Sales by Category", "Segment Pie"],
        layout="horizontal",
    )
    print(result)
    print()

    # 7. Save
    print("=== 7. save_workbook ===")
    result = save_workbook(output)
    print(result)
    print()

    print("ALL TESTS PASSED!")
    print(f"Open {output} in Tableau Desktop to verify.")


if __name__ == "__main__":
    main()
