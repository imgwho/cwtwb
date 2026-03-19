# Guided MCP Authoring Run

This example folder no longer stores pre-baked `brief`, `contract`, or `review`
artifacts.

The intended demo now starts from a real datasource file and lets the MCP
workflow create run artifacts dynamically under:

```text
tmp/agentic_run/{run_id}/
```

## Recommended Demo Flow

1. Start with a real datasource:
   - Excel: `templates/Sample - Superstore - simple.xls`
   - Hyper: `templates/dashboard/Sample _ Superstore.hyper`
2. In the MCP client, start with a natural-language dashboard request and let
   the server use the `guided_dashboard_authoring` prompt internally.
3. Let the agent call:
   - `start_authoring_run(...)`
   - `intake_datasource_schema(...)`
4. Review the generated `schema_summary` and confirm the schema.
5. Let the agent draft, review, and finalize the contract.
6. Confirm the finalized contract.
7. Let the agent build an execution plan.
8. Confirm the execution plan.
9. Let the agent call `generate_workbook_from_run(...)`.

The server-side prompts most relevant to this flow are:

- `guided_dashboard_authoring`
- `dashboard_brief_to_contract`
- `light_elicitation`
- `authoring_execution_plan`

## What Gets Written

Each run writes its own artifacts, for example:

```text
tmp/agentic_run/20260319-153045-a1b2c3d4/manifest.json
tmp/agentic_run/20260319-153045-a1b2c3d4/schema_summary.20260319-153046.json
tmp/agentic_run/20260319-153045-a1b2c3d4/contract_final.20260319-153120.json
tmp/agentic_run/20260319-153045-a1b2c3d4/execution_plan.20260319-153155.json
tmp/agentic_run/20260319-153045-a1b2c3d4/final_workbook.twb
```

Use `list_authoring_runs()` and `get_run_status(run_id)` to recover a run after
the client or server restarts.
