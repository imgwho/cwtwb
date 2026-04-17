---
step: 11
level: "⭐⭐ Intermediate"
demonstrates: "Clone an existing KPI worksheet, preview a worksheet-scoped Sales-to-Profit refactor, apply it only to the cloned worksheet, unhide the cloned sheet, and save a new workbook"
requires: "examples/worksheet_refactor_kpi_profit/5 KPI Design Ideas (2).twb"
---

# Worksheet Clone And Refactor - Natural language MCP Prompt

You can use the following conversational prompt with any LLM connected to the `cwtwb` MCP server to clone an existing worksheet and refactor only the cloned worksheet's calculation chain.

## The Prompt

```text
Hi! I want to reuse an existing KPI worksheet inside a Tableau workbook with the cwtwb MCP tools.

Please open the workbook `examples/worksheet_refactor_kpi_profit/5 KPI Design Ideas (2).twb`.

Inside that workbook, clone the worksheet `1. KPI` into a new worksheet named `1. KPI Profit`.

Before applying any changes, preview a worksheet-scoped refactor that replaces `Sales` with `Profit` only inside `1. KPI Profit`. Please briefly summarize what will be rewritten.

Then apply that refactor only to `1. KPI Profit`. Do not modify the original `1. KPI` worksheet.

After the refactor is applied, make sure `1. KPI Profit` is visible in Tableau worksheet tabs instead of hidden.

Finally, save the workbook to:
`examples/worksheet_refactor_kpi_profit/5 KPI Design Ideas (2) - KPI Profit Worksheet Example.twb`

Thanks!
```
