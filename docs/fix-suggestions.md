# Fix Suggestions for `authoring_run.py` Guided Authoring Flow

This document describes **9 specific bugs and UX issues** found in the current codebase.
Each section explains the problem clearly, shows the exact problematic code, and describes
what the fix should do. These are ordered by severity (P0 = most critical).

---

## FIX 1 (P0) — `validate_generated_workbook_semantics` is never called

### Problem

The function `validate_generated_workbook_semantics` (line ~3643) is fully implemented.
It reads the final `.twb` file and checks:
- Every worksheet from the contract is present in the dashboard
- Chart encodings (columns, rows, KPIs, map fields) match what was agreed
- Dashboard actions exist

However, **this function is never called** during `generate_workbook_from_run`.
The `post_checks` in the execution plan only include `validate_workbook` (XSD schema check)
and `analyze_twb` (capability analysis). Neither checks whether the TWB content
matches the confirmed contract.

As a result, a generated workbook can be completely wrong — missing worksheets,
wrong chart type, no actions — and the flow still reports `STATUS_GENERATED` with no errors.

### Where the problem is

In `build_execution_plan` (line ~3440), the post_checks list is hardcoded:

```python
"post_checks": [
    {"tool": "validate_workbook", "args": {}},
    {"tool": "analyze_twb", "args": {}},
]
```

The `generate_workbook_from_run` MCP tool (in `tools_authoring.py`) executes these
post_checks but never calls `validate_generated_workbook_semantics`.

### What the fix should do

After the workbook is saved and `mark_generation_success` is called, call
`validate_generated_workbook_semantics(run_id, final_workbook_path)`.

If semantic errors are found, they should be stored in `last_error` (similar to
`mark_generation_failed`) and surfaced in the `get_run_status` response under a new
key like `semantic_warnings`. The run should still be marked `STATUS_GENERATED`
(not failed) because some mismatches may be acceptable — but the errors must be
visible to the user.

Specifically, in `tools_authoring.py` inside `generate_workbook_from_run`, after
the workbook is saved, add:

```python
semantic_result = validate_generated_workbook_semantics(run_id, final_workbook_path)
if semantic_result.get("errors"):
    # store as warnings in manifest, do not fail the run
    manifest["semantic_warnings"] = semantic_result["errors"]
    _write_json(Path(manifest["run_dir"]) / MANIFEST_NAME, manifest)
```

Also add `semantic_warnings` to the `get_run_status` response.

---

## FIX 2 (P0) — `agent_first` mode has a hidden requirement not explained in tool output

### Problem

`agent_first` is the **default** `authoring_mode`. In this mode, `build_analysis_brief`
returns an empty payload:

```python
# _build_agent_first_analysis_brief_payload (line ~1834)
{
    "directions": [],             # empty — agent must fill this in
    "selected_direction_id": "",  # also empty
    "direction_template": {...},  # just a template for reference
}
```

The agent must then call `finalize_analysis_brief(user_answers_json=...)` and pass
a full `directions` list plus a `selected_direction_id` that matches one of those directions.

BUT: `confirm_authoring_stage('analysis')` calls `_selected_analysis_direction()`
which raises `RuntimeError("does not have a valid selected_direction_id")` if the
directions list is empty or the ID doesn't match.

There is **no warning** in the `build_analysis_brief` response that the agent MUST
call `finalize_analysis_brief` before confirming. The agent sees `direction_count: 0`
but gets no instruction on what to do next.

### Where the problem is

In `build_analysis_brief` (line ~2515), the return value:

```python
return _json_response(
    run_id=run_id,
    status=manifest["status"],
    artifact=str(artifact_path),
    review_artifact=str(_current_review_artifact_path(manifest, ARTIFACT_ANALYSIS_BRIEF)),
    direction_count=len(payload.get("directions", [])),
    # ← no guidance here for agent_first mode
)
```

### What the fix should do

When `authoring_mode == "agent_first"` and `direction_count == 0`, add a
`required_next_step` field to the JSON response:

```python
required_next_step = (
    "Call finalize_analysis_brief with user_answers_json containing "
    "a 'directions' list (2-4 items using the direction_template schema) "
    "and a 'selected_direction_id' that matches one direction's 'id' field. "
    "The stage cannot be confirmed until directions are provided."
    if not _allow_legacy_inference(manifest) and direction_count == 0
    else ""
)
```

Include `required_next_step` in the return value. Also add this same message to
the Markdown review file rendered by `_render_analysis_brief_markdown` when
`directions` is empty — the note already exists in text but should be more prominent
(e.g., prefix with "⚠ ACTION REQUIRED:").

---

## FIX 3 (P1) — `_is_expression` falsely matches field names containing parentheses

### Problem

```python
def _is_expression(value: str) -> bool:
    text = str(value).strip()
    if not text:
        return False
    return (
        "(" in text          # ← THIS LINE is the bug
        or text.startswith("[")
        or text.casefold().startswith(("sum(", "avg(", ...))
    )
```

The check `"(" in text` matches field names like:
- `"Product (ID)"`
- `"Revenue (USD)"`
- `"Customer (Name)"`
- `"Ship Mode (Adjusted)"`

These are plain dimension/measure names, not Tableau expressions.
When `_is_expression` returns `True` for them, the calling code skips
`_available_field_lookup()` and returns the field name as-is without schema validation.
This silently bypasses the fuzzy name resolution, and Tableau will fail at runtime
with "field not found."

### Where the problem is

`_is_expression` at line ~1114. Also affects `_default_measure_expression` at line ~1138
and `_resolve_field_name` at line ~1129.

### What the fix should do

Remove the bare `"(" in text` check. Instead, only detect expressions when the
**opening parenthesis immediately follows an aggregation function name**:

```python
def _is_expression(value: str) -> bool:
    text = str(value).strip()
    if not text:
        return False
    # A Tableau expression starts with [field], or aggregation_function(
    if text.startswith("["):
        return True
    lower = text.casefold()
    agg_prefixes = ("sum(", "avg(", "count(", "countd(", "min(", "max(",
                    "month(", "year(", "quarter(", "day(", "attr(", "median(")
    return any(lower.startswith(prefix) for prefix in agg_prefixes)
```

This way `"Product (ID)"` → `False` (goes through field lookup),
but `"SUM(Sales)"` → `True` (treated as expression). The `or text.startswith("[")` case
already handles `[Field Name]` references.

---

## FIX 4 (P1) — KPI fields with unknown formulas are silently dropped from execution plan

### Problem

In `_plan_calculated_fields` (line ~2949):

```python
for kpi in requested_fields:
    if kpi in available_fields:
        continue          # field exists in schema → skip (correct)
    formula = KNOWN_CALCULATED_FORMULAS.get(kpi)
    if formula:
        steps.append({"tool": "add_calculated_field", ...})
    # If kpi is NOT in available_fields AND NOT in KNOWN_CALCULATED_FORMULAS:
    # → silently do nothing. The field just disappears from the execution plan.
```

`KNOWN_CALCULATED_FORMULAS` only contains one entry: `"Profit Ratio"`.

In `agent_first` mode, an LLM agent may specify KPIs like `"YoY Growth"`,
`"Conversion Rate"`, or `"Market Share"` in the contract. These pass contract
validation (the spec only checks mark_type and encodings). But at plan time they
are silently dropped, so the generated dashboard is missing those KPIs entirely.

The user sees no error. The execution plan lists no `add_calculated_field` step.
Tableau opens successfully. The KPI cards are blank or show Measure Values from
whatever fields happen to be available.

### Where the problem is

`_plan_calculated_fields` at line ~2949 and `KNOWN_CALCULATED_FORMULAS` at line ~213.

### What the fix should do

**Do not silently skip.** When a KPI is not in `available_fields` and not in
`KNOWN_CALCULATED_FORMULAS`, raise a `RuntimeError` with a clear message
telling the agent what to do:

```python
raise RuntimeError(
    f"KPI '{kpi}' is not available in the schema and has no known formula. "
    "Either remove it from the contract's KPI list, add it as an existing field name "
    "from the schema, or provide its Tableau formula in the contract's "
    "'calculated_fields' list: [{\"name\": \"" + kpi + "\", \"formula\": \"...\"}]."
)
```

Additionally, add a `calculated_fields` key to the contract schema so the agent
can supply custom formulas. Example contract addition:

```json
"calculated_fields": [
    {"name": "YoY Growth", "formula": "(SUM([Sales]) - LOOKUP(SUM([Sales]), -12)) / ABS(LOOKUP(SUM([Sales]), -12))"}
]
```

Then `_plan_calculated_fields` should read from `contract.get("calculated_fields", [])`
first, before checking `KNOWN_CALCULATED_FORMULAS`.

---

## FIX 5 (P1) — `_resolve_field_name` silently returns unmatched field names

### Problem

```python
def _resolve_field_name(field_name: str, available_fields: list[str]) -> str:
    text = str(field_name).strip()
    if not text:
        return ""
    if _is_expression(text) or text in KNOWN_CALCULATED_FORMULAS:
        return text
    return _available_field_lookup(available_fields).get(_normalize_field_key(text), text)
    #                                                                              ^^^
    # Falls back to returning the original `text` if not found in schema
```

If a field name doesn't fuzzy-match any schema field, the function returns the
original string unchanged. The caller has no way to know whether the returned value
was resolved or not.

Examples that silently slip through:
- `"Saless"` (typo) → returned as `"Saless"`, Tableau fails at runtime
- `"order date"` (wrong case for a field named `"Order Date"`) → the normalize
  function should catch this one, but `"order_date"` vs `"Order Date"` in a
  different source object may not

### Where the problem is

`_resolve_field_name` at line ~1129.

### What the fix should do

Return a `(resolved_name, was_found: bool)` tuple so callers can detect misses,
OR add a separate `_resolve_field_name_strict` variant that raises on miss.

For the execution spec path (which uses `fail_on_unresolved=True`), apply strict
resolution and raise with a message like:

```
Field 'Saless' was not found in the schema for datasource 'Orders'.
Available fields: Sales, Profit, Quantity, Discount, ...
Check the field name spelling in the contract and correct it before confirming.
```

For the inference path (legacy mode, `fail_on_unresolved=False`), keep the
current silent fallback but add the unresolved field name to a `warnings` list
that gets stored in the artifact.

Concretely: add a `resolution_warnings` list to `_ensure_worksheet_execution_spec`
that collects all unresolved field names, and include it in the `contract_final.json`
under a `resolution_warnings` key. Surface it in `get_run_status`.

---

## FIX 6 (P2) — `reopen_authoring_stage('contract')` leaves agent without clear next-step guidance

### Problem

When `reopen_authoring_stage('contract')` is called:
1. Status is set to `STATUS_CONTRACT_FINALIZED`
2. Wireframe and execution plan artifacts are cleared

The correct sequence after this is:
1. `finalize_authoring_contract` (re-run execution spec, possibly with edits)
2. `interactive_stage_confirmation('contract')`
3. `confirm_authoring_stage('contract', approved=True)`
4. `build_wireframe` (must be rebuilt since it was cleared)
5. ... and so on

However, the tool response only says:
```json
{
  "status": "contract_finalized",
  "stage": "contract",
  "cleared_artifacts": ["wireframe", "execution_plan"]
}
```

Agents that don't know this workflow will try to call `confirm_authoring_stage('contract')`
directly, which fails because there is no pending confirmation. Or they will try
`build_wireframe`, which fails because status is `contract_finalized` and
`build_wireframe` requires `STATUS_CONTRACT_CONFIRMED`.

### What the fix should do

Add a `next_steps` list to the `reopen_authoring_stage` response that explicitly
tells the agent the required sequence:

```python
next_steps_map = {
    ANALYSIS_STAGE: [
        "Call finalize_analysis_brief (edit directions if needed)",
        "Call interactive_stage_confirmation('analysis')",
        "Call confirm_authoring_stage('analysis', approved=True)",
        "Then proceed to draft_authoring_contract",
    ],
    CONTRACT_STAGE: [
        "Call finalize_authoring_contract (with any edits as user_answers_json)",
        "Call interactive_stage_confirmation('contract')",
        "Call confirm_authoring_stage('contract', approved=True)",
        "Then call build_wireframe to rebuild the cleared wireframe",
    ],
    WIREFRAME_STAGE: [
        "Call finalize_wireframe (with any edits)",
        "Call interactive_stage_confirmation('wireframe')",
        "Call confirm_authoring_stage('wireframe', approved=True)",
        "Then call build_execution_plan to rebuild the cleared plan",
    ],
    EXECUTION_STAGE: [
        "Call build_execution_plan to regenerate the plan",
        "Call interactive_stage_confirmation('execution_plan')",
        "Call confirm_authoring_stage('execution_plan', approved=True)",
        "Then call generate_workbook_from_run",
    ],
}
```

Include `next_steps` in the return value of `reopen_authoring_stage`.

---

## FIX 7 (P2) — `start_authoring_run(resume_if_exists=True)` ignores `authoring_mode` mismatch

### Problem

```python
def start_authoring_run(..., authoring_mode="agent_first"):
    if resume_if_exists:
        for run_id, info in index_payload.get("runs", {}).items():
            if info.get("datasource_path") == normalized_path:
                # Returns the existing run without checking authoring_mode
                return _json_response(run_id=run_id, ...)
```

If a user previously started a run with `authoring_mode="legacy"` and now calls
`start_authoring_run(datasource_path=..., authoring_mode="agent_first", resume_if_exists=True)`,
they silently get the old `legacy` run back. The response shows `authoring_mode: "legacy"`
which may confuse the agent.

There is also no way to start a fresh run for a datasource that already has an
existing run, other than manually deleting files.

### What the fix should do

Two changes:

**1.** When `resume_if_exists=True` and the found run's `authoring_mode` differs
from the requested one, add a `mode_mismatch` warning to the response:

```python
existing_mode = _authoring_mode(manifest)
if existing_mode != normalized_mode:
    return _json_response(
        run_id=run_id,
        status=manifest["status"],
        authoring_mode=existing_mode,
        resumed=True,
        mode_mismatch=True,
        mode_mismatch_note=(
            f"Resumed existing run with authoring_mode='{existing_mode}'. "
            f"Requested mode='{normalized_mode}' was ignored. "
            "To start fresh with a different mode, call start_authoring_run "
            "without resume_if_exists=True."
        ),
    )
```

**2.** Optionally add a `force_new: bool = False` parameter that skips the resume
check and always creates a new run, even if one exists for the same datasource.

---

## FIX 8 (P3) — Wireframe ASCII diagram doesn't show layout proportions

### Problem

The ASCII wireframe generated by `_build_wireframe_payload` shows a flat list of
zones with no visual sizing:

```
+----------------------------------------------------------------------+
|Executive Overview                                                    |
|KPI Zone: Sales | Profit | Quantity                                   |
|Primary View: Primary View                                            |
|Which region is driving Sales?                                        |
|Detail View: Detail View                                              |
|How does Sales change over time?                                      |
+----------------------------------------------------------------------+
```

This gives no information about:
- Relative heights (KPI strip vs chart area)
- Horizontal vs vertical split (is Detail side-by-side or below Primary?)
- Approximate proportions

When users confirm this wireframe, they believe they are confirming a **layout**,
but they are actually only confirming a **list of named zones**. The actual layout
in the generated TWB defaults to `layout="vertical"` with equal-height zones.

### What the fix should do

The wireframe payload already has `layout_pattern` from the contract (e.g.,
`"executive overview"`, `"side by side"`, `"top and detail"`).

Use this to render a more expressive ASCII diagram. For example, for
`"executive overview"`:

```
+----------------------------------------------------------------------+
| DASHBOARD: Executive Overview                                        |
+------------------+---------------------------------------------------+
| KPI STRIP (20%)  |  Sales  |  Profit  |  Quantity                   |
+------------------+---------------------------------------------------+
|                                                                      |
|  PRIMARY VIEW (50%)                                                  |
|  Which region is driving Sales? [Bar/Map]                            |
|                                                                      |
+----------------------------------------------------------------------+
|                                                                      |
|  DETAIL VIEW (30%)                                                   |
|  How does Sales change over time? [Line]                             |
|                                                                      |
+----------------------------------------------------------------------+
|  Filters: Order Date | Region | Category                            |
+----------------------------------------------------------------------+
```

The `_ascii_box` helper at line ~2150 already exists. Create a second helper
`_ascii_layout_box(wireframe_payload, contract)` that reads `layout_pattern`
and renders a structured two-column or stacked diagram.

Also: add a `layout_description` string to the wireframe payload (e.g.,
`"KPI strip on top, Primary and Detail stacked vertically"`) so even without
reading the ASCII diagram the agent can describe the layout to the user.

---

## FIX 9 (P3) — Date field detection in Excel intake still uses keyword-only heuristic

### Problem

In `connections.py` (line ~131), `_infer_excel_datatype`:

```python
def _infer_excel_datatype(header: str, values: list[Any]) -> str:
    lower = header.casefold()
    non_blank = [v for v in values if v not in ("", None)]
    if any(token in lower for token in ("date", "month", "year", "day", "time")):
        return "date"
    ...
    if any(isinstance(value, (datetime, date)) for value in non_blank):
        return "date"
```

The keyword check runs first. If it doesn't match (e.g., field named `"dt"`,
`"period"`, `"transaction_ts"`, `"created_at"`, `"fiscal_wk"`), the function falls
through to check actual values. This part is correct — it detects `datetime` objects.

**However**, for string-typed Excel cells that contain ISO date strings
(e.g., `"2024-01-15"`), neither the keyword check nor the `isinstance(datetime)` check
fires. These columns are returned as `"string"` type even though they are clearly dates.

As a result, date fields are not added to `field_candidates["date_fields"]`, so
the analysis directions don't suggest time-series views, and the wireframe's
"Detail View" defaults to Bar instead of Line.

### What the fix should do

After the `isinstance(datetime, date)` check, add a **value-sample date detection**:
Check whether >50% of non-blank string values in the sample match a common date
pattern (ISO 8601, `YYYY-MM-DD`, `MM/DD/YYYY`, etc.) using a regex or `dateutil.parser`.

```python
import re

_DATE_PATTERNS = [
    re.compile(r"^\d{4}-\d{2}-\d{2}"),         # 2024-01-15
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}"),   # 1/15/2024
    re.compile(r"^\d{4}/\d{2}/\d{2}"),          # 2024/01/15
    re.compile(r"^\d{4}-\d{2}$"),               # 2024-01 (month period)
]

def _looks_like_date_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return any(pattern.match(value.strip()) for pattern in _DATE_PATTERNS)
```

Apply this in `_infer_excel_datatype`: if >50% of string sample values match,
return `"date"`. This is purely additive and doesn't change existing behavior
for numeric or actual `datetime` columns.

---

## Summary Table

| # | Severity | Function/Location | One-line description |
|---|----------|-------------------|----------------------|
| 1 | **P0** | `generate_workbook_from_run` in tools_authoring.py | Semantic validation never called after generation |
| 2 | **P0** | `build_analysis_brief` line ~2515 | agent_first mode missing required_next_step in response |
| 3 | **P1** | `_is_expression` line ~1114 | `"(" in text` falsely matches field names with parentheses |
| 4 | **P1** | `_plan_calculated_fields` line ~2949 | Unknown KPI formulas silently dropped from execution plan |
| 5 | **P1** | `_resolve_field_name` line ~1129 | Unmatched field names silently pass through as-is |
| 6 | **P2** | `reopen_authoring_stage` line ~2901 | Response missing `next_steps` guidance after reopen |
| 7 | **P2** | `start_authoring_run` line ~2340 | `resume_if_exists` ignores `authoring_mode` mismatch |
| 8 | **P3** | `_build_wireframe_payload` line ~2160 | ASCII wireframe shows no layout proportions |
| 9 | **P3** | `_infer_excel_datatype` in connections.py ~131 | String-typed date columns not detected by value sampling |
