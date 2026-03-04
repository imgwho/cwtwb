---
description: 复刻 Superstore Overview Dashboard 第一页 — 完整版（包含所有功能细节）
---

# Superstore Overview Dashboard — 完整复刻

使用 Superstore 数据源模板 `examples/templates/twb/superstore.twb` 创建一个 Profitability Overview 仪表板。请严格按以下步骤执行：

## 1. 创建工作簿
- 模板: `examples/templates/twb/superstore.twb`
- 工作簿名称: "Overview Dashboard"

## 2. 添加 3 个参数
- **Target Profit**: real, range, default=10000, min=-30000, max=100000, granularity=10000
- **Churn Rate**: real, range, default=0.168, min=0, max=1, granularity=0.05
- **New Business Growth**: real, range, default=0.599, min=0, max=1, granularity=0.05

## 3. 添加 6 个计算字段
- **Profit Ratio** (real): `SUM([Profit])/SUM([Sales])`
- **Order Profitable?** (string): `IF SUM([Profit]) > [Target Profit] THEN 'Profitable' ELSE 'Unprofitable' END`
- **Sales estimate** (real): `[Sales]*(1-[Churn Rate])*(1+[New Business Growth])`
- **Profit per Customer** (real): `SUM([Profit])/COUNTD([Customer Name])`
- **Profit per Order** (real): `SUM([Profit])/COUNTD([Order ID])`
- **Units estimate** (real): `ROUND([Quantity]*(1-[Churn Rate])*(1+[New Business Growth]),0)`

## 4. 添加 4 个 Worksheet
- **SaleMap**: 地图图表
  - mark_type="Map"
  - geographic_field="State/Province"
  - color="Order Profitable?"
  - size="SUM(Sales)"
  - tooltip="SUM(Profit)"

- **SalesbyProduct**: 面积图
  - mark_type="Area"
  - columns=["MONTH(Order Date)"]
  - rows=["SUM(Sales)"]
  - color="Order Profitable?"
  - detail="Category"
  - tooltip="SUM(Profit)"

- **SalesbySegment**: 面积图
  - mark_type="Area"
  - columns=["MONTH(Order Date)"]
  - rows=["SUM(Sales)"]
  - color="Order Profitable?"
  - detail="Segment"
  - tooltip="SUM(Profit)"

- **Total Sales**: KPI 卡片（Measure Names/Values）
  - mark_type="Text"
  - measure_values=["SUM(Sales)", "SUM(Profit)", "Profit Ratio", "SUM(Quantity)", "AVG(Discount)", "Profit per Customer", "Profit per Order"]

## 5. 创建 Dashboard
- 名称: "Overview"
- 尺寸: 936×650
- Layout 结构（纵向）：
  - **顶部** (15%): Total Sales KPI 条
  - **下方** (85%, 横向):
    - **左侧栏** (18%, 纵向):
      - filter: SaleMap / Order Date
      - filter: SaleMap / Region (dropdown)
      - filter: SaleMap / State/Province (checkdropdown)
      - filter: SaleMap / Profit Ratio
      - color legend: SaleMap / Order Profitable?
    - **主区域** (82%, 纵向):
      - SaleMap 地图 (55%)
      - 底部 (45%, 横向): SalesbySegment + SalesbyProduct 各 50%

先用 `generate_layout_json` 生成 layout JSON 文件，再传路径给 `add_dashboard`。

## 6. 添加 Dashboard Actions
- **State Filter**: filter action, source=SaleMap, target=SalesbyProduct, fields=["State/Province"], on-select
- **State Highlight**: highlight action, source=SaleMap, target=SalesbySegment, fields=["State/Province"], on-select

## 7. 保存
- 输出: `output/overview_dashboard.twb`
