# Guided MCP Authoring Run

This folder is the recommended Excel-first demo for Guided MCP Authoring Run V1.

Use the local datasource in this folder:

```text
examples/agentic_mcp_authoring/Sample - Superstore.xls
```

This workbook has a single `Orders` sheet, which keeps the live demo focused on
the authoring workflow instead of multi-sheet intake decisions.

## What This Demo Proves

The goal is not "AI can draw a chart". The goal is to show a controlled
Agentic BI workflow:

```text
real datasource -> schema summary -> analysis brief -> contract -> wireframe -> execution plan -> workbook
```

The strongest Matthew-facing checkpoints are:

1. `schema_summary.json`
2. `analysis_brief.json`
3. `contract_final.json`
4. `wireframe.json`
5. `execution_plan.json`
6. `final_workbook.twb`
7. `validation_report.json`
8. `analysis_report.json`

## Demo Mode 1: Live MCP Client

Start the server from the project root:

```bash
python -m cwtwb.mcp
```

You can also use `uvx cwtwb` when your local environment supports it.

Then connect from an MCP-capable client such as Claude Desktop, Cursor, VSCode,
or Codex, and use this brief plus datasource path:

```text
Build an executive sales performance dashboard for Matthew.
Audience: sales leaders
Primary question: Which regions, categories, and sub-categories are driving sales and profit, and where should leaders drill deeper?
Please include interactive filtering from the top view into detail, and keep the dashboard simple enough for a polished demo.

Datasource path:
C:\Users\imgwho\Desktop\projects\20260227-cwtwb\examples\agentic_mcp_authoring\Sample - Superstore.xls
```

Recommended live sequence:

1. Ask the client to use the `guided_dashboard_authoring` prompt.
2. Let it call `start_authoring_run(...)`.
3. Let it call `intake_datasource_schema(...)`.
4. Show the generated schema summary and confirm it.
5. Prefer `interactive_stage_confirmation(..., stage="schema")`.
6. If the client reports `chat_fallback`, answer in chat and then make sure it calls `confirm_authoring_stage(..., stage="schema")`.
7. Let it build and finalize the analysis brief.
8. Show the candidate directions and confirm the selected analysis direction.
9. Prefer `interactive_stage_confirmation(..., stage="analysis")`.
10. If the client reports `chat_fallback`, answer in chat and then make sure it calls `confirm_authoring_stage(..., stage="analysis")`.
11. Let it draft, review, and finalize the contract.
12. Show the finalized contract and confirm it.
13. Prefer `interactive_stage_confirmation(..., stage="contract")`.
14. If the client reports `chat_fallback`, answer in chat and then make sure it calls `confirm_authoring_stage(..., stage="contract")`.
15. Let it build and finalize the ASCII wireframe.
16. Show the wireframe and support/workaround notes, then confirm it.
17. Prefer `interactive_stage_confirmation(..., stage="wireframe")`.
18. If the client reports `chat_fallback`, answer in chat and then make sure it calls `confirm_authoring_stage(..., stage="wireframe")`.
19. Let it build the execution plan as an internal artifact.
20. Do not ask the human to approve the execution plan unless they explicitly want to inspect the step-by-step build.
21. Let it call `generate_workbook_from_run(...)`.
22. End by showing the final workbook path plus validation and analysis artifacts.

What to emphasize while speaking:

- The system starts from a real Excel file, not a baked demo JSON.
- The agent pauses at `schema`, `analysis`, `contract`, and `wireframe` by default.
- When the client supports MCP elicitation, the preferred gate is `interactive_stage_confirmation(...)`.
- When the client does not support elicitation, the workflow degrades cleanly to chat confirmation plus `confirm_authoring_stage(...)`.
- The prompts guide; the tools write files and move run state.
- The run is resumable because artifacts live under `tmp/agentic_run/{run_id}/`.
- The human-facing review surface is now paired Markdown artifacts, not just JSON.
- `execution_plan` is still written, but it is an internal read-only artifact unless the human explicitly asks to review it.

## Demo Mode 2: Deterministic Real MCP Client Script

If you want a reproducible fallback that still uses the real MCP protocol, run:

```bash
python examples/agentic_mcp_authoring/demo_guided_authoring_mcp_client.py
```

This script does not call Python functions directly. It uses the official
`mcp` client over stdio to connect to `python -m cwtwb.mcp`, then executes the
full guided flow and prints each checkpoint. It also demonstrates client
capability detection and shows the `chat_fallback` path when the raw Python MCP
client does not advertise form elicitation support.

Useful overrides:

```bash
python examples/agentic_mcp_authoring/demo_guided_authoring_mcp_client.py ^
  --datasource "C:\path\to\your.xls" ^
  --output-dir "tmp/agentic_run" ^
  --brief "Build a sales dashboard for regional leaders." ^
  --user-answers-json "{\"audience\":\"regional leaders\",\"primary_question\":\"Which regions need attention first?\",\"require_interaction\":true}"
```

## What Gets Written

Each run writes its own artifacts under:

```text
tmp/agentic_run/{run_id}/
```

Typical output:

```text
tmp/agentic_run/20260319-153045-a1b2c3d4/manifest.json
tmp/agentic_run/20260319-153045-a1b2c3d4/schema_summary.20260319-153046.json
tmp/agentic_run/20260319-153045-a1b2c3d4/schema_summary.20260319-153046.md
tmp/agentic_run/20260319-153045-a1b2c3d4/analysis_brief.20260319-153055.json
tmp/agentic_run/20260319-153045-a1b2c3d4/analysis_brief.20260319-153055.md
tmp/agentic_run/20260319-153045-a1b2c3d4/contract_final.20260319-153120.json
tmp/agentic_run/20260319-153045-a1b2c3d4/contract_final.20260319-153120.md
tmp/agentic_run/20260319-153045-a1b2c3d4/wireframe.20260319-153140.json
tmp/agentic_run/20260319-153045-a1b2c3d4/wireframe.20260319-153140.md
tmp/agentic_run/20260319-153045-a1b2c3d4/execution_plan.20260319-153155.json
tmp/agentic_run/20260319-153045-a1b2c3d4/execution_plan.20260319-153155.md
tmp/agentic_run/20260319-153045-a1b2c3d4/final_workbook.twb
tmp/agentic_run/20260319-153045-a1b2c3d4/validation_report.20260319-153205.json
tmp/agentic_run/20260319-153045-a1b2c3d4/analysis_report.20260319-153206.json
```

Use `list_authoring_runs()` and `get_run_status(run_id)` to recover a run after
the client or server restarts. If generation fails, use
`reopen_authoring_stage(run_id, stage, notes)` instead of editing run artifacts
by hand.
