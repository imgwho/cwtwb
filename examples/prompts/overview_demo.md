---
description: 演示级提示词 — 面向 Tableau 高管展示 AI 自动创建仪表板的能力（自然语言风格，精准控制）
---

# 请帮我创建一个 Superstore 盈利分析仪表板

使用 Superstore 模板创建工作簿，保存到 `output/overview_demo.twb`。

---

## 业务场景

我是一个零售分析师，需要一个仪表板来回答核心问题：**哪些州的订单是盈利的？不同产品线和客户群体的盈利趋势如何？**

---

## 交互控件

我需要 3 个滑块参数让用户可以做 What-If 分析：

| 参数名 | 默认值 | 范围 | 步长 |
|--------|--------|------|------|
| Target Profit | 10000 | -30000 ~ 100000 | 10000 |
| Churn Rate | 0.168 | 0 ~ 1 | 0.05 |
| New Business Growth | 0.599 | 0 ~ 1 | 0.05 |

## 计算指标

请创建以下分析指标：

- **Profit Ratio** = `SUM([Profit])/SUM([Sales])`
- **Order Profitable?** = 当 `SUM([Profit]) > [Target Profit]` 时返回 `"Profitable"`，否则 `"Unprofitable"`（string 类型）
- **Sales estimate** = `[Sales]*(1-[Churn Rate])*(1+[New Business Growth])`
- **Units estimate** = `ROUND([Quantity]*(1-[Churn Rate])*(1+[New Business Growth]),0)`
- **Profit per Customer** = `SUM([Profit])/COUNTD([Customer Name])`
- **Profit per Order** = `SUM([Profit])/COUNTD([Order ID])`

---

## 四张可视化工作表

### 1. Total Sales — KPI 概览卡片
用 Text 标记类型 + measure_values 展示 7 个核心指标：
`SUM(Sales)`, `SUM(Profit)`, `Profit Ratio`, `SUM(Quantity)`, `AVG(Discount)`, `Profit per Customer`, `Profit per Order`

### 2. SaleMap — 盈利地图
- 地图类型（Map），按 **State/Province** 划分地理区域
- 颜色编码 = Order Profitable?（盈利/亏损一目了然）
- 气泡大小 = SUM(Sales)
- 提示信息 = SUM(Profit)

### 3. SalesbyProduct — 按产品线的销售趋势
- 面积图（Area），X 轴 = MONTH(Order Date)，Y 轴 = SUM(Sales)
- 用 detail = Category 分面显示三条产品线
- 颜色 = Order Profitable?，tooltip = SUM(Profit)

### 4. SalesbySegment — 按客户群体的销售趋势
- 面积图（Area），X 轴 = MONTH(Order Date)，Y 轴 = SUM(Sales)
- 用 detail = Segment 分面显示三个客群
- 颜色 = Order Profitable?，tooltip = SUM(Profit)

---

## Dashboard 布局（936×650）

仪表板名称："Overview"，布局如下：

```
┌─────────────────────────────────────────────┐
│              Total Sales KPI 条 (15%)        │
├──────────┬──────────────────────────────────┤
│ 筛选器   │         SaleMap 地图              │
│ 侧边栏   │           (55%)                   │
│ (18%)    ├────────────────┬─────────────────┤
│ · 日期    │ SalesbySegment │ SalesbyProduct  │
│ · 地区    │    (45%)       │    (45%)        │
│ · 州省    │                │                 │
│ · 利润率  │                │                 │
│ · 图例    │                │                 │
└──────────┴────────────────┴─────────────────┘
```

左侧栏包含（自上而下）：
1. Order Date 日期范围筛选器
2. Region 下拉筛选器（dropdown）
3. State/Province 多选下拉筛选器（checkdropdown）
4. Profit Ratio 数值筛选器
5. Order Profitable? 颜色图例

请先用 `generate_layout_json` 生成 layout JSON，再传路径给 `add_dashboard`。

---

## 交互动作

- **State Filter**: 在地图上点选某个州 → 过滤 SalesbyProduct 工作表，按 State/Province 字段
- **State Highlight**: 在地图上点选某个州 → 高亮 SalesbySegment 工作表，按 State/Province 字段
