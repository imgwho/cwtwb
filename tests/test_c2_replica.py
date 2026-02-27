"""完全复刻 c.2 (2) Dashboard 布局。

从 Tableau Dashboard Layout Templates.twb 的 c.2 (2) 布局提取的精确 zone 结构：
- 标题行: LOGO + TITLE (text zones)
- 筛选栏: dark background text zone
- KPI 行: 4 个工作表 (Sales, Profit, Discount, Quantity) distribute-evenly
- 视图区: 2×2 grid
  - 左列: Sub-Category sales (bar) + segment sales (pie)
  - 右列: date profit (line) + category detail (text table)
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lxml import etree
from cwtwb.twb_editor import TWBEditor, _generate_uuid


def main():
    project_root = Path(__file__).parent.parent
    editor = TWBEditor(project_root / "templates" / "superstore.twb")
    editor.clear_worksheets()

    # ============================================================
    # 1) 创建 8 个工作表
    # ============================================================

    # KPI 工作表 (简单度量)
    for name, measure_expr in [
        ("Sales", "SUM(Sales)"),
        ("Profit", "SUM(Profit)"),
        ("Discount", "SUM(Discount)"),
        ("Quanity", "SUM(Quantity)"),
    ]:
        editor.add_worksheet(name)
        editor.configure_chart(
            worksheet_name=name,
            mark_type="Automatic",
            columns=[measure_expr],
        )

    # Sub-Category sales 柱状图
    editor.add_worksheet("Sub-Category sales")
    editor.configure_chart(
        worksheet_name="Sub-Category sales",
        mark_type="Bar",
        rows=["Sub-Category"],
        columns=["SUM(Sales)"],
    )

    # date profit 折线图
    editor.add_worksheet("date profit")
    editor.configure_chart(
        worksheet_name="date profit",
        mark_type="Line",
        columns=["Order Date"],
        rows=["SUM(Profit)"],
    )

    # segment sales 饼图
    editor.add_worksheet("segment sales")
    editor.configure_chart(
        worksheet_name="segment sales",
        mark_type="Pie",
        color="Segment",
        wedge_size="SUM(Sales)",
    )

    # category detail 文本表（简化为单度量）
    editor.add_worksheet("category detail")
    editor.configure_chart(
        worksheet_name="category detail",
        mark_type="Automatic",
        rows=["Category"],
        columns=["SUM(Sales)"],
    )

    # ============================================================
    # 2) 手动构建 c.2 (2) 精确 dashboard XML
    # ============================================================
    all_ws_names = [
        "Sales", "Profit", "Discount", "Quanity",
        "Sub-Category sales", "date profit",
        "segment sales", "category detail",
    ]

    _build_c2_dashboard(editor, "Overview", all_ws_names)

    # ============================================================
    # 3) 保存
    # ============================================================
    out = project_root / "output" / "c2_replica.twb"
    editor.save(out)
    print(f"c.2 (2) replica => {out}")
    print("Please open in Tableau Desktop to verify.")


def _next_id():
    """简单递增 zone id 计数器。"""
    _next_id.counter += 1
    return str(_next_id.counter)

_next_id.counter = 0


def _add_zone_style(parent, margin="4", bg_color=None, **extra):
    """为 zone 添加 zone-style。"""
    zs = etree.SubElement(parent, "zone-style")
    for attr_name, attr_val in [
        ("border-color", "#000000"),
        ("border-style", "none"),
        ("border-width", "0"),
    ]:
        fmt = etree.SubElement(zs, "format")
        fmt.set("attr", attr_name)
        fmt.set("value", attr_val)
    if margin:
        fmt = etree.SubElement(zs, "format")
        fmt.set("attr", "margin")
        fmt.set("value", margin)
    if bg_color:
        fmt = etree.SubElement(zs, "format")
        fmt.set("attr", "background-color")
        fmt.set("value", bg_color)
    for attr_name, attr_val in extra.items():
        fmt = etree.SubElement(zs, "format")
        fmt.set("attr", attr_name.replace("_", "-"))
        fmt.set("value", attr_val)


def _add_text_zone(parent, zone_id, text, h, w, x, y,
                   font_size="12", font_color="#111e29",
                   bold=True, fixed_size=None, is_fixed=False,
                   bg_color=None, margin="4", **extra_margins):
    """创建文本 zone。"""
    z = etree.SubElement(parent, "zone")
    if fixed_size:
        z.set("fixed-size", str(fixed_size))
    z.set("forceUpdate", "true")
    z.set("h", str(h))
    z.set("id", zone_id)
    if is_fixed:
        z.set("is-fixed", "true")
    z.set("type-v2", "text")
    z.set("w", str(w))
    z.set("x", str(x))
    z.set("y", str(y))

    ft = etree.SubElement(z, "formatted-text")
    run = etree.SubElement(ft, "run")
    if bold:
        run.set("bold", "true")
    run.set("fontalignment", "1")
    run.set("fontcolor", font_color)
    run.set("fontsize", font_size)
    run.text = text

    _add_zone_style(z, margin=margin, bg_color=bg_color, **extra_margins)
    return z


def _add_viz_zone(parent, zone_id, ws_name, h, w, x, y, bg_color="#ffffff", margin="10"):
    """创建引用工作表的 viz zone。"""
    z = etree.SubElement(parent, "zone")
    z.set("h", str(h))
    z.set("id", zone_id)
    z.set("name", ws_name)
    z.set("w", str(w))
    z.set("x", str(x))
    z.set("y", str(y))
    _add_zone_style(z, margin=margin, bg_color=bg_color)
    return z


def _build_c2_dashboard(editor, dashboard_name, ws_names):
    """构建完全复刻 c.2 (2) 的 dashboard XML。"""
    root = editor.root

    # 获取/创建 dashboards
    dashboards = root.find("dashboards")
    if dashboards is None:
        ws_el = root.find("worksheets")
        if ws_el is not None:
            idx = list(root).index(ws_el) + 1
            dashboards = etree.Element("dashboards")
            root.insert(idx, dashboards)
        else:
            dashboards = etree.SubElement(root, "dashboards")

    # dashboard 元素
    db = etree.SubElement(dashboards, "dashboard")
    db.set("name", dashboard_name)

    # style: 灰色背景
    style = etree.SubElement(db, "style")
    sr = etree.SubElement(style, "style-rule")
    sr.set("element", "table")
    fmt = etree.SubElement(sr, "format")
    fmt.set("attr", "background-color")
    fmt.set("value", "#e6e6e6")

    # size
    size_el = etree.SubElement(db, "size")
    size_el.set("maxheight", "800")
    size_el.set("maxwidth", "1200")
    size_el.set("minheight", "800")
    size_el.set("minwidth", "1200")

    # ======================== zones ========================
    zones = etree.SubElement(db, "zones")

    # --- 主容器: v.Dash Container ---
    dash_container = etree.SubElement(zones, "zone")
    dash_container.set("h", "100000")
    dash_container.set("id", _next_id())
    dash_container.set("param", "vert")
    dash_container.set("type-v2", "layout-flow")
    dash_container.set("w", "100000")
    dash_container.set("x", "0")
    dash_container.set("y", "0")

    # --- 1. 标题行: h.Title Container ---
    title_container = etree.SubElement(dash_container, "zone")
    title_container.set("fixed-size", "70")
    title_container.set("h", "8750")
    title_container.set("id", _next_id())
    title_container.set("is-fixed", "true")
    title_container.set("param", "horz")
    title_container.set("type-v2", "layout-flow")
    title_container.set("w", "100000")
    title_container.set("x", "0")
    title_container.set("y", "0")

    # Logo
    _add_text_zone(title_container, _next_id(), "LOGO PLACEHOLDER",
                   h=8750, w=16667, x=667, y=0,
                   font_size="12", fixed_size=192, is_fixed=True)

    # Title
    _add_text_zone(title_container, _next_id(), "TITLE PLACEHOLDER",
                   h=8750, w=81999, x=17334, y=0,
                   font_size="20")

    # Title container style
    _add_zone_style(title_container, margin=None, bg_color="#ffffff",
                    margin_right="8", margin_left="8")

    # --- 2. 筛选栏: h.Filter Container ---
    filter_container = etree.SubElement(dash_container, "zone")
    filter_container.set("fixed-size", "30")
    filter_container.set("h", "3750")
    filter_container.set("id", _next_id())
    filter_container.set("is-fixed", "true")
    filter_container.set("param", "horz")
    filter_container.set("type-v2", "layout-flow")
    filter_container.set("w", "100000")
    filter_container.set("x", "0")
    filter_container.set("y", "8750")

    _add_text_zone(filter_container, _next_id(),
                   "FILTERS HORIZONTAL CONTAINER PLACEHOLDER",
                   h=3750, w=98666, x=667, y=8750,
                   font_size="12", font_color="#ffffff")

    _add_zone_style(filter_container, margin=None, bg_color="#192f3e",
                    margin_right="8", margin_left="8")

    # --- 3. KPI 行: h.KPI Container ---
    kpi_container = etree.SubElement(dash_container, "zone")
    kpi_container.set("fixed-size", "100")
    kpi_container.set("h", "12500")
    kpi_container.set("id", _next_id())
    kpi_container.set("is-fixed", "true")
    kpi_container.set("layout-strategy-id", "distribute-evenly")
    kpi_container.set("param", "horz")
    kpi_container.set("type-v2", "layout-flow")
    kpi_container.set("w", "100000")
    kpi_container.set("x", "0")
    kpi_container.set("y", "12500")

    # 4 个 KPI viz zones
    kpi_names = ["Sales", "Profit", "Discount", "Quanity"]
    for i, kpi_name in enumerate(kpi_names):
        _add_viz_zone(kpi_container, _next_id(), kpi_name,
                      h=12500, w=25000, x=i * 25000, y=12500)

    _add_zone_style(kpi_container, margin="0", margin_top="0")

    # --- 4. 视图区: h.Views Container ---
    views_container = etree.SubElement(dash_container, "zone")
    views_container.set("fixed-size", "1100")
    views_container.set("h", "75000")
    views_container.set("id", _next_id())
    views_container.set("is-fixed", "true")
    views_container.set("layout-strategy-id", "distribute-evenly")
    views_container.set("param", "horz")
    views_container.set("type-v2", "layout-flow")
    views_container.set("w", "100000")
    views_container.set("x", "0")
    views_container.set("y", "25000")

    # 左列
    left_col = etree.SubElement(views_container, "zone")
    left_col.set("h", "75000")
    left_col.set("id", _next_id())
    left_col.set("layout-strategy-id", "distribute-evenly")
    left_col.set("param", "vert")
    left_col.set("type-v2", "layout-flow")
    left_col.set("w", "50000")
    left_col.set("x", "0")
    left_col.set("y", "25000")

    _add_viz_zone(left_col, _next_id(), "Sub-Category sales",
                  h=37500, w=50000, x=0, y=25000)
    _add_viz_zone(left_col, _next_id(), "segment sales",
                  h=37500, w=50000, x=0, y=62500)

    # 右列
    right_col = etree.SubElement(views_container, "zone")
    right_col.set("h", "75000")
    right_col.set("id", _next_id())
    right_col.set("layout-strategy-id", "distribute-evenly")
    right_col.set("param", "vert")
    right_col.set("type-v2", "layout-flow")
    right_col.set("w", "50000")
    right_col.set("x", "50000")
    right_col.set("y", "25000")

    _add_viz_zone(right_col, _next_id(), "date profit",
                  h=37500, w=50000, x=50000, y=25000)
    _add_viz_zone(right_col, _next_id(), "category detail",
                  h=37500, w=50000, x=50000, y=62500)

    # simple-id
    simple_id = etree.SubElement(db, "simple-id")
    simple_id.set("uuid", _generate_uuid())

    # ======================== window ========================
    editor._add_window(dashboard_name, window_class="dashboard",
                       worksheet_names=ws_names)


if __name__ == "__main__":
    main()
