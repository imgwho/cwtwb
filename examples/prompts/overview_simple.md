---
description: 复刻 Superstore Overview Dashboard 第一页 — 简单版（高层描述让 AI 自行推断细节）
---

# Superstore Overview Dashboard

使用 `examples/templates/twb/superstore.twb` 模板创建一个 Superstore Profitability Overview 仪表板（1400×1150），保存到 `output/overview_simple.twb`。

## 需要的内容

### 参数
- Target Profit (range滑块, 默认10000)
- Churn Rate (range滑块, 默认0.168)
- New Business Growth (range滑块, 默认0.599)

### 计算字段
- Profit Ratio = SUM(Profit)/SUM(Sales)
- Order Profitable? = 利润是否超过 Target Profit 参数（返回 Profitable/Unprofitable）
- Profit per Customer = SUM(Profit)/COUNTD(Customer Name)
- Profit per Order = SUM(Profit)/COUNTD(Order ID)

### 四个 Worksheet
1. **Total Sales** — KPI 卡（Text），用 measure_values 展示：SUM(Sales), SUM(Profit), Profit Ratio, SUM(Quantity), AVG(Discount), Profit per Customer, Profit per Order
2. **SaleMap** — 地图（Map），按 State/Province 分地理区域，颜色=Order Profitable?，大小=SUM(Sales)
3. **SalesbyProduct** — 面积图（Area），月度趋势，按 Category 分面，颜色=Order Profitable?
4. **SalesbySegment** — 面积图（Area），月度趋势，按 Segment 分面，颜色=Order Profitable?

### Dashboard 布局
- 顶部: Total Sales KPI 条（短，约15%高度）
- 左侧栏: Order Date、Region(dropdown)、State(checkdropdown)、Profit Ratio 的筛选器 + Order Profitable? 颜色图例
- 右侧主区域: 上方 SaleMap 地图，下方两个面积图左右排列

### Actions
- 点击地图 State 过滤到 SalesbyProduct
- 点击地图 State 高亮到 SalesbySegment
