"""Integration test: generate a TWB replicating the Overview dashboard structure.

Output: output/overview_replica.twb
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwtwb.server import (
    create_workbook,
    add_parameter,
    add_calculated_field,
    add_worksheet,
    configure_chart,
    add_dashboard,
    save_workbook,
)


def main():
    project_root = Path(__file__).parent.parent
    template = str(project_root / "templates" / "twb" / "superstore.twb")
    output = str(project_root / "output" / "overview_replica.twb")

    # 1. Create workbook
    print("=== 1. Create workbook ===")
    result = create_workbook(template, "Overview Replica")
    print(result[:200], "...\n")

    # 2. Add parameters
    print("=== 2. Add parameters ===")
    result = add_parameter(
        name="Target Profit",
        datatype="real",
        default_value="10000.0",
        domain_type="range",
        min_value="-30000.0",
        max_value="100000.0",
        granularity="10000.0",
    )
    print(result)

    result = add_parameter(
        name="Churn Rate",
        datatype="real",
        default_value="0.1",
        domain_type="range",
        min_value="0.0",
        max_value="1.0",
        granularity="0.05",
    )
    print(result)
    print()

    # 3. Add calculated fields
    print("=== 3. Add calculated fields ===")
    result = add_calculated_field(
        "Profit Ratio",
        "SUM([Profit])/SUM([Sales])",
        "real",
    )
    print(result)

    result = add_calculated_field(
        "Order Profitable?",
        "IF SUM([Profit]) > 0 THEN 'Profitable' ELSE 'Unprofitable' END",
        "string",
    )
    print(result)
    print()

    # 4. Add worksheets
    print("=== 4. Add worksheets ===")

    add_worksheet("SaleMap")
    print("Added: SaleMap")

    add_worksheet("SalesbyProduct")
    print("Added: SalesbyProduct")

    add_worksheet("SalesbySegment")
    print("Added: SalesbySegment")

    add_worksheet("Total Sales")
    print("Added: Total Sales")
    print()

    # 5. Configure charts
    print("=== 5. Configure charts ===")

    # Map chart
    result = configure_chart(
        worksheet_name="SaleMap",
        mark_type="Map",
        geographic_field="State/Province",
        color="SUM(Profit)",
        size="SUM(Sales)",
    )
    print(result)

    # Area chart: Sales by Product
    result = configure_chart(
        worksheet_name="SalesbyProduct",
        mark_type="Area",
        columns=["MONTH(Order Date)"],
        rows=["SUM(Sales)"],
        color="Category",
    )
    print(result)

    # Area chart: Sales by Segment
    result = configure_chart(
        worksheet_name="SalesbySegment",
        mark_type="Area",
        columns=["MONTH(Order Date)"],
        rows=["SUM(Sales)"],
        color="Segment",
    )
    print(result)

    # KPI: Total Sales (as Text chart)
    result = configure_chart(
        worksheet_name="Total Sales",
        mark_type="Text",
        label="SUM(Sales)",
    )
    print(result)
    print()

    # 6. Add dashboard with filter & paramctrl zones
    print("=== 6. Add dashboard ===")
    layout = {
        "type": "container",
        "direction": "horizontal",
        "children": [
            {
                "type": "container",
                "direction": "vertical",
                "weight": 3,
                "children": [
                    {
                        "type": "container",
                        "direction": "horizontal",
                        "children": [
                            {"type": "worksheet", "name": "SaleMap", "weight": 2},
                            {"type": "worksheet", "name": "Total Sales", "weight": 1},
                        ]
                    },
                    {
                        "type": "container",
                        "direction": "horizontal",
                        "children": [
                            {"type": "worksheet", "name": "SalesbyProduct"},
                            {"type": "worksheet", "name": "SalesbySegment"},
                        ]
                    },
                ]
            },
            {
                "type": "container",
                "direction": "vertical",
                "fixed_size": 180,
                "children": [
                    {"type": "filter", "worksheet": "SaleMap",
                     "field": "Region", "mode": "dropdown", "fixed_size": 60},
                    {"type": "filter", "worksheet": "SaleMap",
                     "field": "State/Province", "mode": "checkdropdown", "fixed_size": 60},
                    {"type": "paramctrl", "parameter": "Target Profit",
                     "mode": "slider", "fixed_size": 60},
                ]
            }
        ]
    }
    result = add_dashboard(
        dashboard_name="Overview",
        worksheet_names=["SaleMap", "SalesbyProduct", "SalesbySegment", "Total Sales"],
        width=936,
        height=650,
        layout=layout,
    )
    print(result)
    print()

    # 7. Save
    print("=== 7. Save ===")
    result = save_workbook(output)
    print(result)
    print()

    print("INTEGRATION TEST PASSED!")
    print(f"Open {output} in Tableau Desktop to verify.")


if __name__ == "__main__":
    main()
