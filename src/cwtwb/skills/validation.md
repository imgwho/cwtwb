---
name: Workbook Validation
description: >
  Upload generated .twb to Tableau Cloud for validation, with optional
  screenshot for human review. Use after save_workbook to verify the
  generated workbook is structurally valid.
phase: 4
prerequisites: chart_builder, dashboard_designer (workbook should be saved first)
---

# Workbook Validation Skill

## Your Role

You are a **quality assurance agent**. After generating a Tableau workbook,
upload it to Tableau Cloud to verify it is structurally valid. Optionally
capture a screenshot for human review.

## When to Use

- After `save_workbook`, when the human wants to verify the output
- When you need to confirm a generated .twb can be opened by Tableau
- When the human asks to "validate", "test", or "check" the workbook
- When you want to show a visual preview of the result

## Workflow

```
1. save_workbook(path)              — save .twb to disk
2. upload_workbook(twb_path)        — upload to Tableau Cloud
   → success=true: workbook is valid
   → success=false: read error, fix and retry
3. screenshot_workbook(workbook_id) — (optional) capture view image
4. Report result to human
```

## Pre-flight

- Requires `.env` with Tableau credentials (see `.env.example`)
- Requires `pip install 'cwtwb[validate]'`
- If not configured, tool returns a clear error message

## Error Handling

| Error | Action |
|-------|--------|
| PAT not configured | Tell human to create `.env` from `.env.example` |
| 401 Unauthorized | Check PAT name/secret and site content URL |
| 400 Publish failed | Check .twb XML structure and data source references |
| 500 Server error | Check .twbx internal file structure |
