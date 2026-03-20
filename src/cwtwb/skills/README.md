# cwtwb Skills

Skills are expert-level guidance files that help AI agents produce
professional Tableau workbooks. Prompts explain what to build. Skills explain
how to build it well, phase by phase.

## Workflow Phases

```text
Phase 0: authoring_workflow    -> Run the gated datasource -> schema -> analysis -> contract -> wireframe -> execution workflow
Phase 1: calculation_builder   -> Define parameters, calculated fields, LOD logic
Phase 2: chart_builder         -> Choose chart types, configure encodings, filters
Phase 3: dashboard_designer    -> Layout, worksheet captions, interaction actions
Phase 4: formatting            -> Number formats, colors, sorting, tooltips
```

## Recommended Resource Flow

```text
1. start_authoring_run(...)
2. intake_datasource_schema(...)
3. interactive_stage_confirmation(..., stage="schema")
4. confirm_authoring_stage(..., stage="schema")  # only if chat fallback was required
5. build_analysis_brief(...)
6. finalize_analysis_brief(...)
7. interactive_stage_confirmation(..., stage="analysis")
8. confirm_authoring_stage(..., stage="analysis")  # only if chat fallback was required
9. read_resource("cwtwb://contracts/dashboard_authoring_v1")
10. read_resource("cwtwb://profiles/index")
11. draft_authoring_contract(...)
12. review_authoring_contract_for_run(...)
13. finalize_authoring_contract(...)
14. interactive_stage_confirmation(..., stage="contract")
15. confirm_authoring_stage(..., stage="contract")  # only if chat fallback was required
16. build_wireframe(...)
17. finalize_wireframe(...)
18. interactive_stage_confirmation(..., stage="wireframe")
19. confirm_authoring_stage(..., stage="wireframe")  # only if chat fallback was required
20. build_execution_plan(...)
21. interactive_stage_confirmation(..., stage="execution_plan")
22. confirm_authoring_stage(..., stage="execution_plan")  # only if chat fallback was required
23. read_resource("cwtwb://skills/authoring_workflow")
24. read_resource("cwtwb://skills/calculation_builder")
25. read_resource("cwtwb://skills/chart_builder")
26. read_resource("cwtwb://skills/dashboard_designer")
27. read_resource("cwtwb://skills/formatting")
28. generate_workbook_from_run(...)
```

## Design Philosophy

- Skills are phase-specific, not generic prompt stuffing.
- Load only the skill needed for the current phase.
- Keep the workflow contract-first, skill-guided, and self-validating.
- Use light elicitation: ask follow-up questions only when the contract misses critical intent.
- Prefer MCP form elicitation for approval gates, with chat fallback when the client does not support it.
