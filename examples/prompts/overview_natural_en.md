---
description: Natural Language Prompt (English) — Fully replicating overview_full correct.twb
---

# Help me create a Superstore Profitability Overview Dashboard

Please create a workbook using the Superstore template and save it to `output/overview_natural_en.twb`.

## Analysis Context

I want to analyze the profitability of our stores across three dimensions: geography, product categories, and customer segments. I also need to perform "What-If" analysis using parameters.

## Three What-If Analysis Parameters

Please add three slider controls for me:
- **Target Profit**: Default $10,000, range from -$30,000 to $100,000, with a step of 10,000.
- **Churn Rate**: Default 0.168, range from 0 to 1, with a step of 0.05.
- **New Business Growth**: Default 0.599, range from 0 to 1, with a step of 0.05.

## Six Analytical Metrics

Please calculate the core metrics: **Profit Ratio**, **Profit per Customer**, and **Profit per Order**. Add an **Order Profitable?** status based on whether profit exceeds the Target Profit. Finally, project **Sales & Units estimates** using the logic: `Base * (1 - Churn Rate) * (1 + Growth)` (round Units to the nearest integer).

## Four Visualizations

First, summarize our performance with a **Total Sales** KPI bar displaying all seven core metrics (from Sales and Profit to Profit per Order). 

Next, visualize geography with a **SaleMap**. Color each state by its profit status and scale the marks by sales volume, showing profit in the tooltips.

Finally, create two trend charts: **SalesbyProduct** and **SalesbySegment**. These should be monthly area charts showing sales over time, faceted by Category and Segment respectively. Color them by profit status and include profit details in the tooltips.

## Dashboard Layout (1200 * 1150)

The dashboard, named "Overview", should be split into two main sections. The top 15% of the height should be the Total Sales KPI bar. The remaining 85% below should be divided into two columns.

The left sidebar should occupy about 18% of the width. From top to bottom, it should contain: an Order Date range filter, a Region dropdown filter, a State/Province multi-select dropdown filter (checkdropdown), a Profit Ratio range filter, and the color legend for "Order Profitable?". All these filters and legends should be linked to the SaleMap sheet.

The main area on the right takes up the remaining 82% of the width. The upper 55% of this section should be the SaleMap. The lower 45% should consist of two area charts placed side-by-side: SalesbySegment on the left and SalesbyProduct on the right, each taking 50% of the width.

Please use json tool to create the layout JSON , then pass that file path to generate dashboard.

## Two Interaction Actions

When I click a State on the map, it should filter the SalesbyProduct chart and highlight the SalesbySegment chart, both based on the State/Province field.
