# cwtwb Skills — Specialized Agent Workflow

Skills are expert-level guidance files that help AI agents produce **professional-quality** Tableau workbooks. Each skill focuses on one phase of the dashboard creation process.

## Workflow Phases

```
Phase 1: calculation_builder  →  Define parameters, calculated fields, LOD expressions
Phase 2: chart_builder         →  Choose chart types, configure encodings, filters
Phase 3: dashboard_designer    →  Layout, filter panels, interaction actions  
Phase 4: formatting            →  Number formats, colors, sorting, tooltips
```

## How to Use

### For AI Agents (via MCP Resources)

Read skills as needed during dashboard creation:

```
1. read_resource("cwtwb://skills/index")           → See available skills
2. read_resource("cwtwb://skills/calculation_builder") → Load Phase 1 expertise
3. read_resource("cwtwb://skills/chart_builder")       → Load Phase 2 expertise
4. read_resource("cwtwb://skills/dashboard_designer")  → Load Phase 3 expertise
5. read_resource("cwtwb://skills/formatting")          → Load Phase 4 expertise
```

### For Humans

Include a skill reference in your prompt:

```
Please read the cwtwb chart_builder and dashboard_designer skills, 
then create a sales analysis dashboard for me.
```

## Design Philosophy

- **Skills ≠ Prompts**: Prompts tell AI *what to build*. Skills tell AI *how to build it well*.
- **Load on demand**: Don't load all skills at once. Load the relevant skill when entering each phase.
- **Domain expertise**: Each skill encodes best practices from Tableau experts — chart type selection, layout ratios, interaction patterns, etc.
