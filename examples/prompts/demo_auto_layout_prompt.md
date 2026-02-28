# Auto Layout Generation Prompt

Use the following natural language prompt with an MCP-enabled LLM to see it automatically build a complete dashboard, inferring the necessary JSON layout structure entirely from your description.

## The Prompt

```text
Build a sales dashboard for me using `examples/templates/twb/superstore.twb`.

1. Create 3 Bar charts: "Sales By Category", "Profit Map", and "Daily Highlights".
2. Arrange them in a new dashboard (1200x800) called "Auto Layout Demo".
3. Layout: Top half is split horizontally between "Sales By Category" and "Profit Map". Bottom half is "Daily Highlights" taking up the full width. 
4. Save to `output/demo_auto_layout.twb`.
```
