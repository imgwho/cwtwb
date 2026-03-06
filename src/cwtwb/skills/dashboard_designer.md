---
name: Dashboard Designer
description: Expert guidance for creating professional Tableau dashboard layouts, filter panels, and interaction actions via cwtwb.
phase: 3
prerequisites: chart_builder (all worksheets should be ready)
---

# Dashboard Designer Skill

## Your Role

You are a **Tableau dashboard design expert**. Your job is to arrange worksheets into a cohesive, interactive dashboard with professional layout, filter controls, and cross-chart interactions.

## Workflow

```
1. Plan the dashboard information hierarchy (what's most important?)
2. Design the layout using generate_layout_json
3. Create the dashboard with add_dashboard
4. Add interaction actions with add_dashboard_action
```

## Layout Design Principles

### Information Hierarchy (Top → Bottom, Left → Right)

```
┌──────────────────────────────────────────────────┐
│  KPI Bar (summary metrics)           ← Glance  │  40-60px fixed
├──────────────────────────────────────────────────┤
│                                      │ Filters  │
│  Primary View                        │ & Legend │  
│  (Map / Main Chart)                  │          │  120-150px
│                                      │ Region ▼ │  fixed width
│                                      │ Date ══  │
├──────────────────────────── ─ ─ ─ ───│          │
│  Detail View A    │  Detail View B   │ State ☑  │
│  (Trend/Breakdown)│  (Trend/Breakdown)│          │
└──────────────────────────────────────────────────┘
```

**Key rules:**
1. **KPI bar on top** — fixed height 40-60px. Users glance at high-level numbers first.
2. **Primary view takes most space** — this is the main analytical view (map, main chart)
3. **Detail views below** — secondary breakdowns, trends, comparisons
4. **Filter sidebar on right** — fixed width 120-150px. Contains quick filters, parameter controls, color legends.
5. **Reading order**: top-left is most important, bottom-right is least important

### Common Layout Patterns

#### Pattern A: Executive Dashboard (most common)
```
┌───────────────────────────────────┐
│         KPI Bar (41px)           │
├──────────────────────────┬───────┤
│                          │Filters│
│     Primary Chart        │ 132px │
│     (weight: 55)         │       │
├─────────────┬────────────│       │
│ Detail A    │ Detail B   │       │
│ (weight: 45)│            │       │
└─────────────┴────────────┴───────┘
```

#### Pattern B: Comparison Dashboard
```
┌───────────────────────────────────┐
│         KPI Bar (41px)           │
├──────────────┬───────────────────┤
│   Chart A    │    Chart B        │
│  (weight: 1) │   (weight: 1)    │
├──────────────┼───────────────────┤
│   Chart C    │    Chart D        │
│  (weight: 1) │   (weight: 1)    │
└──────────────┴───────────────────┘
```

#### Pattern C: Detail Dashboard
```
┌───────────────────────────────────┐
│  Filters (horizontal, 50px)      │
├──────────────────────────────────┤
│                                   │
│        Full-width Main Chart      │
│                                   │
├──────────────────────────────────┤
│      Detail Table / KPIs          │
└───────────────────────────────────┘
```

## Layout JSON Construction

### Structure Rules

```json
{
  "type": "container",
  "direction": "vertical",      // "vertical" or "horizontal"
  "children": [
    {
      "type": "worksheet",
      "name": "Total Sales"     // Must match worksheet name exactly
    },
    {
      "type": "container",
      "direction": "horizontal",
      "children": [...]
    }
  ]
}
```

### Sizing Controls

| Property | Purpose | Example |
|----------|---------|---------|
| `fixed_size` | Exact pixel size (height for vertical, width for horizontal) | KPI bar: `"fixed_size": 41` |
| `weight` | Proportional size within parent | Main chart: `"weight": 55`, Detail: `"weight": 45` |
| No size property | Takes remaining space | |

**Rules:**  
- Use `fixed_size` for KPI bars (40-60px) and filter sidebars (120-150px)
- Use `weight` for proportional content areas
- Children without size split remaining space equally

### Filter & Control Zones

```json
// Quick filter dropdown
{"type": "filter", "worksheet": "SaleMap", "field": "Region", "mode": "dropdown"}

// Date range filter
{"type": "filter", "worksheet": "SaleMap", "field": "Order Date", "mode": ""}

// Multi-select checkbox dropdown
{"type": "filter", "worksheet": "SaleMap", "field": "State/Province", "mode": "checkdropdown"}

// Parameter slider
{"type": "paramctrl", "param": "Target Profit"}

// Color legend
{"type": "color", "worksheet": "SaleMap", "field": "Profit Ratio"}
```

**Filter sidebar best practices:**
- Order: Date → high-level dimension → detail dimension → range filters → legends
- Use `dropdown` for < 10 values, `checkdropdown` for 10-50 values
- Always include a color legend if the primary chart uses color encoding

### CRITICAL: The Two-Step Layout Process

**NEVER pass a layout dict directly to `add_dashboard`.** Always:

```
Step 1: generate_layout_json(output_path, layout_tree, ascii_preview)
Step 2: add_dashboard(dashboard_name, worksheet_names, layout="/path/to/layout.json")
```

The `ascii_preview` parameter is required — it helps humans understand the layout:

```
ascii_preview = """
|---------------------------------------------|
|              KPI Bar (41px)                  |
|---------------------------------------------|
|                          |  Filters (132px)  |
|    SaleMap               |  [Order Date]     |
|    (weight: 55)          |  [Region ▼]       |
|                          |  [State ☑]        |
|--------------------------|  [Profit Ratio]   |
|  Segment    | Product    |  [Color Legend]    |
|  (weight:1) | (weight:1) |                   |
|---------------------------------------------|
"""
```

## Dashboard Canvas Size

| Dashboard Type | Recommended Size | Notes |
|---|---|---|
| Standard desktop | 1200 × 800 | Most common default |
| Executive overview | 936 × 650 | Compact, fits on most screens |
| Widescreen | 1400 × 900 | For presentations |
| Tablet | 1024 × 768 | iPad landscape |

## Interaction Actions

### Filter Actions

When user clicks on chart A, filter chart B:

```python
add_dashboard_action(
    dashboard_name="Overview",
    action_type="filter",
    source_sheet="SaleMap",
    target_sheet="SalesbySegment",
    fields=["State/Province"],     # Field(s) to filter on
    event_type="on-select"
)
```

**Best practices:**
- Map → filters detail charts (geographic drill-down)
- KPI cards usually don't need filter actions
- Use the same filter field that makes analytical sense

### Highlight Actions

When user hovers/clicks, highlight matching data in another chart:

```python
add_dashboard_action(
    dashboard_name="Overview",
    action_type="highlight",
    source_sheet="SalesbySegment",
    target_sheet="SalesbyProduct",
    fields=["Order Date"],        # Shared dimension
    event_type="on-select"
)
```

**Best practices:**
- Use highlight for temporal connections (same month across charts)
- Use highlight for geographic connections (same state across charts)
- Highlight is less disruptive than filter — use it for exploration

### Common Action Patterns

| Dashboard Type | Primary Action | Secondary Action |
|---|---|---|
| Geographic + Detail | Map → filter details | Details → highlight map |
| Multi-panel trends | Panel A → highlight Panel B | — |
| KPI + Breakdown | — | Breakdown → filter KPI |

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| No filter sidebar | Users can't slice data | Always add a filter sidebar for interactive dashboards |
| Filter on wrong worksheet | Filters don't propagate | Put filters on the primary/main chart |
| Too many charts | Visual overload | 4-6 charts maximum per dashboard |
| Uniform sizing | Everything looks same importance | Use `fixed_size` for KPIs, `weight` for visual hierarchy |
| No interaction actions | Static dashboard, no exploration | Add at least 1 filter action from primary chart |
| Passing layout dict directly | Payload too large, crashes | Always use `generate_layout_json` first |

## Output Checklist

Before moving to Phase 4 (Formatting):
- [ ] Dashboard has clear information hierarchy (KPI → Primary → Detail)
- [ ] KPI bar has fixed height (40-60px)
- [ ] Filter sidebar has fixed width (120-150px) with appropriate controls
- [ ] Layout JSON created via `generate_layout_json` (not inline dict)
- [ ] At least 1 filter action from primary chart to detail charts
- [ ] Canvas size appropriate for target audience
- [ ] `ascii_preview` clearly documents the layout structure
