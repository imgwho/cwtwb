"""Demonstrate the new 'auto' layout feature for dashboards.

The 'auto' layout automatically creates intelligent mixed layouts
based on the number of worksheets:

- 1 worksheet: simple vertical
- 2 worksheets: side-by-side (horizontal)
- 3 worksheets: top 1 + bottom 2 side-by-side
- 4 worksheets: 2x2 grid
- 5 worksheets: top 2 + middle 2 + bottom 1
- 6 worksheets: top 2 + middle 2 + bottom 2
- 7+ worksheets: top row (up to 4 KPIs) + remaining in 2-column grid
"""

from pathlib import Path
from cwtwb import TWBEditor


def main():
    # Use the Superstore sample template
    template = Path(__file__).parent.parent / "templates" / "twb" / "superstore.twb"
    if not template.exists():
        print(f"Template not found: {template}")
        return

    editor = TWBEditor(str(template))
    editor.clear_worksheets()

    # Create sample worksheets
    worksheets = [
        "总收入KPI",
        "总成本KPI",
        "总毛利KPI",
        "毛利率KPI",
        "分公司业绩对比",
        "业务类型毛利率",
        "月度收入趋势",
        "客户级别分析",
        "行业贡献分析",
    ]

    for ws_name in worksheets:
        editor.add_worksheet(ws_name)

    # Create dashboard with auto layout (default)
    editor.add_dashboard(
        dashboard_name="物流业务分析看板",
        worksheet_names=worksheets,
        width=1200,
        height=800,
        # layout="auto"  # This is the default, can be omitted
    )

    # Save the workbook
    out_path = Path(__file__).parent.parent / "output" / "demo_auto_layout.twb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    editor.save(str(out_path))

    print(f"Created dashboard with auto layout: {out_path}")
    print(f"Worksheets: {len(worksheets)}")
    print()
    print("Auto layout strategy:")
    print("  - Top row: 4 KPI cards (horizontal)")
    print("  - Middle row: 分公司对比 + 业务类型 (horizontal)")
    print("  - Bottom row: 月度趋势 + 客户级别 (horizontal)")
    print("  - Last row: 行业分析 (standalone)")


if __name__ == "__main__":
    main()
