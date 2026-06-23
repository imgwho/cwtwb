# Auto Layout Feature - Changes Summary

## Problem

The default dashboard layout (`"vertical"`) only creates simple vertical stacking of worksheets, which doesn't meet real-world dashboard requirements. Most dashboards need mixed layouts with both horizontal and vertical containers (e.g., top KPI cards in a row, middle sections side-by-side, bottom full-width charts).

## Solution

Added a new `"auto"` layout strategy that automatically generates intelligent mixed layouts based on the number of worksheets.

## Files Modified

### 1. `src/cwtwb/dashboards.py`

**Added `_generate_auto_layout()` function** (before `resolve_dashboard_layout()`):
- Generates intelligent mixed layouts based on worksheet count
- Layout strategy:
  - 1 worksheet: simple vertical
  - 2 worksheets: side-by-side (horizontal)
  - 3 worksheets: top 1 + bottom 2 side-by-side
  - 4 worksheets: 2x2 grid
  - 5 worksheets: top 2 + middle 2 + bottom 1
  - 6 worksheets: top 2 + middle 2 + bottom 2
  - 7+ worksheets: top row (up to 4 KPIs) + remaining in 2-column grid

**Modified `resolve_dashboard_layout()` function**:
- Added handling for `layout == "auto"` that calls `_generate_auto_layout()`
- Updated docstring to document all supported layout options

**Modified `add_dashboard()` method**:
- Changed default parameter from `layout: str | dict = "vertical"` to `layout: str | dict = "auto"`

### 2. `src/cwtwb/mcp/tools_workbook.py`

**Modified `add_dashboard()` MCP tool**:
- Changed default parameter from `layout: str | dict = "vertical"` to `layout: str | dict = "auto"`
- Added docstring explaining all layout options

### 3. `tests/test_declarative_dashboards.py`

**Added 5 new test cases**:
- `test_auto_layout_with_2_worksheets`: Verifies 2 worksheets create horizontal layout
- `test_auto_layout_with_3_worksheets`: Verifies 3 worksheets create mixed layout (top 1 + bottom 2)
- `test_auto_layout_with_4_worksheets`: Verifies 4 worksheets create 2x2 grid
- `test_auto_layout_with_6_worksheets`: Verifies 6 worksheets create 3 rows of 2
- `test_auto_layout_with_9_worksheets`: Verifies 9 worksheets create top row + 2-column grid

### 4. `examples/demo_auto_layout.py`

**Added example script** demonstrating the new auto layout feature with 9 worksheets.

## Layout Examples

### 2 Worksheets (Horizontal)
```
┌─────────────────┬─────────────────┐
│       S1        │       S2        │
└─────────────────┴─────────────────┘
```

### 3 Worksheets (Mixed)
```
┌───────────────────────────────────┐
│               S1                  │
├─────────────────┬─────────────────┤
│       S2        │       S3        │
└─────────────────┴─────────────────┘
```

### 4 Worksheets (2x2 Grid)
```
┌─────────────────┬─────────────────┐
│       S1        │       S2        │
├─────────────────┼─────────────────┤
│       S3        │       S4        │
└─────────────────┴─────────────────┘
```

### 6 Worksheets (3 Rows)
```
┌─────────────────┬─────────────────┐
│       S1        │       S2        │
├─────────────────┼─────────────────┤
│       S3        │       S4        │
├─────────────────┼─────────────────┤
│       S5        │       S6        │
└─────────────────┴─────────────────┘
```

### 9 Worksheets (Top Row + Grid)
```
┌───────┬───────┬───────┬───────┐
│  S1   │  S2   │  S3   │  S4   │
├───────┴───────┼───────┴───────┤
│      S5       │      S6       │
├───────────────┼───────────────┤
│      S7       │      S8       │
├───────────────┴───────────────┤
│              S9               │
└───────────────────────────────┘
```

## Usage

### Using Auto Layout (Default)
```python
editor.add_dashboard(
    dashboard_name="My Dashboard",
    worksheet_names=["KPI1", "KPI2", "Chart1", "Chart2"],
    # layout="auto"  # This is the default
)
```

### Using Other Layouts
```python
# Vertical (old default)
editor.add_dashboard("My Dashboard", layout="vertical", worksheet_names=[...])

# Horizontal
editor.add_dashboard("My Dashboard", layout="horizontal", worksheet_names=[...])

# 2x2 Grid
editor.add_dashboard("My Dashboard", layout="grid-2x2", worksheet_names=[...])

# Custom declarative layout
editor.add_dashboard("My Dashboard", layout={...}, worksheet_names=[...])
```

## Testing

All existing tests pass, plus 5 new tests added:

```bash
python -m pytest tests/test_declarative_dashboards.py -v
```

## Backward Compatibility

- The change is fully backward compatible
- Existing code using `layout="vertical"` or `layout="horizontal"` continues to work
- Only the default behavior changes from "vertical" to "auto"
- Users can explicitly set `layout="vertical"` to get the old behavior
