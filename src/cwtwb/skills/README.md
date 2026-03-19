# cwtwb Skills

Skills are expert-level guidance files that help AI agents produce
professional Tableau workbooks. Prompts explain what to build. Skills explain
how to build it well, phase by phase.

## Workflow Phases

```text
Phase 0: authoring_workflow    -> Run the gated datasource -> schema -> contract -> execution workflow
Phase 1: calculation_builder   -> Define parameters, calculated fields, LOD logic
Phase 2: chart_builder         -> Choose chart types, configure encodings, filters
Phase 3: dashboard_designer    -> Layout, worksheet captions, interaction actions
Phase 4: formatting            -> Number formats, colors, sorting, tooltips
```

## Recommended Resource Flow

```text
1. start_authoring_run(...)
2. intake_datasource_schema(...)
3. confirm_authoring_stage(..., stage="schema")
4. read_resource("cwtwb://contracts/dashboard_authoring_v1")
5. read_resource("cwtwb://profiles/index")
6. draft_authoring_contract(...)
7. review_authoring_contract_for_run(...)
8. finalize_authoring_contract(...)
9. confirm_authoring_stage(..., stage="contract")
10. build_execution_plan(...)
11. confirm_authoring_stage(..., stage="execution_plan")
12. read_resource("cwtwb://skills/authoring_workflow")
13. read_resource("cwtwb://skills/calculation_builder")
14. read_resource("cwtwb://skills/chart_builder")
15. read_resource("cwtwb://skills/dashboard_designer")
16. read_resource("cwtwb://skills/formatting")
17. generate_workbook_from_run(...)
```

## Design Philosophy

- Skills are phase-specific, not generic prompt stuffing.
- Load only the skill needed for the current phase.
- Keep the workflow contract-first, skill-guided, and self-validating.
- Use light elicitation: ask follow-up questions only when the contract misses critical intent.
