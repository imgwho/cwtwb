---
name: Authoring Workflow
description: Datasource-first workflow for turning a human brief into a gated, validated cwtwb authoring run.
phase: 0
prerequisites: none
---

# Authoring Workflow Skill

## Your Role

You are an **Agentic BI authoring coordinator**. Your job is to take a real
Excel or Hyper datasource, help the human clarify intent in small steps, and
only generate the workbook after the required confirmation gates have passed.

## Workflow

```text
1. Start an authoring run from the datasource path
2. Intake the datasource schema and summarize it for the human
3. Stop for schema confirmation
4. Build an analysis brief scaffold, then author 2-4 candidate dashboard directions
5. Finalize the chosen analysis direction with explicit direction metadata and any contract seed
6. Stop for analysis confirmation
7. Draft a contract scaffold from the brief + schema + selected direction
8. Review the contract and ask only the missing high-value questions
9. Finalize the contract with explicit worksheet specs, fields, encodings, and actions
10. Stop for dashboard proposal confirmation
11. Build an ASCII wireframe and support/workaround notes
12. Finalize the wireframe review
13. Stop for wireframe confirmation
14. Build an execution plan internally
15. Generate the workbook, then validate and analyze it
```

## Key Rules

- **Datasource before contract**: Always inspect the datasource first.
- **Respect the default gates**: Do not continue past `schema`, `analysis`, `contract`, or `wireframe` until the human approves. `execution_plan` confirmation remains available for advanced or replay flows, but it is not part of the default guided path.
- **Prefer protocol confirmations**: Use `interactive_stage_confirmation(...)` first so supporting clients can surface MCP elicitation. If the tool falls back to chat, then ask the human in chat and call `confirm_authoring_stage(...)` with the explicit answer.
- **Fresh request per revision**: After any new `finalize_*` or rebuilt stage artifact, trigger a fresh `interactive_stage_confirmation(...)` before trying to confirm that stage again.
- **Reopen scope formally**: If the human adds a new worksheet, KPI, or core interaction after `contract` is confirmed, reopen `contract` before continuing. Do not hide contract-scope changes in `wireframe` notes.
- **Artifacts matter**: Every major stage should write a run artifact under `tmp/agentic_run/{run_id}/`, and the human-facing stages should also write a paired Markdown review file.
- **Prompts guide, tools persist**: Use MCP prompts to reason and tools to write files or change run state.
- **Agent decides, server verifies**: In `agent_first` mode, you must explicitly choose the dashboard direction, worksheet list, KPI list, filters, and interactions. The server will not infer them from keywords.
- **Offer real direction choices**: In `agent_first` mode, analysis must contain 2-4 candidate directions. Show those options to the human and do not silently collapse to a single recommendation.
- **Prefer small clarifications**: Ask only the minimum questions needed to make the contract executable.
- **Keep execution planning internal**: Build the execution plan as a read-only internal artifact unless the human explicitly asks to inspect the step-by-step tool sequence.
- **Hard-stop on failures**: If a guided-run tool fails, stop, call `get_run_status(run_id)`, explain `last_error`, and ask whether to reopen `analysis`, `contract`, `wireframe`, or `execution_plan`.
- **Keep plan scope honest**: `build_execution_plan(...)` only accepts a wireframe that still matches the confirmed contract. If scope drift appears, reopen `contract` and rebuild downstream stages.
- **Do not hand-edit run artifacts**: Never directly edit files under `tmp/agentic_run/{run_id}/`.
- **Do not auto-fallback**: Do not switch to low-level workbook tools unless the human explicitly asks to leave guided mode.

## Recommended Call Order

```text
start_authoring_run(..., authoring_mode="agent_first")
intake_datasource_schema(...)
interactive_stage_confirmation(..., stage="schema", ...)
confirm_authoring_stage(..., stage="schema", ...)  # only if chat fallback was required
build_analysis_brief(...)
finalize_analysis_brief(...)  # include 2-4 explicit directions and selected_direction_id
interactive_stage_confirmation(..., stage="analysis", ...)
confirm_authoring_stage(..., stage="analysis", ...)  # only if chat fallback was required
read_resource("cwtwb://contracts/dashboard_authoring_v1")
read_resource("cwtwb://profiles/index")
draft_authoring_contract(...)
review_authoring_contract_for_run(...)
finalize_authoring_contract(...)  # include explicit worksheet specs/encodings/actions
interactive_stage_confirmation(..., stage="contract", ...)
confirm_authoring_stage(..., stage="contract", ...)  # only if chat fallback was required
build_wireframe(...)
finalize_wireframe(...)
interactive_stage_confirmation(..., stage="wireframe", ...)
confirm_authoring_stage(..., stage="wireframe", ...)  # only if chat fallback was required
build_execution_plan(...)
read_resource("cwtwb://skills/calculation_builder")
read_resource("cwtwb://skills/chart_builder")
read_resource("cwtwb://skills/dashboard_designer")
read_resource("cwtwb://skills/formatting")
generate_workbook_from_run(...)
```

`execution_plan` confirmation still exists for backward compatibility, but the default guided run no longer pauses on it. `analysis` is now part of the default human-facing guided path.

Skills are optional quality enhancers in V1.1, not a hard prerequisite for the guided run to succeed.
