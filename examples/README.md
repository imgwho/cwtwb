# cwtwb SDK Examples

This directory contains various Python scripts and natural language prompts that demonstrate the core capabilities of the `cwtwb` SDK and its MCP Server. You can explore how to flexibly build Tableau Workbooks by executing these scripts or reading the prompts.

## Python Quick Start Scripts

| Script File | Demonstrated Features | How to Run |
| :--- | :--- | :--- |
| **`scripts/demo_declarative_layout.py`** | The most complex and important example. Demonstrates how to use `add_dashboard` with a nested JSON dictionary configuration to declaratively build structurally complex dashboards (e.g., a Dashboard with a sidebar and a fixed-width title bar). Also shows how to assign KPI metrics to Text type charts. | `python examples/scripts/demo_declarative_layout.py` |
| **`scripts/demo_connections.py`** | Demonstrates the powerful data source configuration capabilities of the SDK. This script shows how to hot-swap connections from a base template to: a local MySQL database, and a published data source on Tableau Server. | `python examples/scripts/demo_connections.py` |
| **`scripts/demo_e2e_mcp_workflow.py`** | Demonstrates an end-to-end workflow from the perspective of MCP (Model Context Protocol). Without instantiating underlying SDK objects, the script generates a multi-page workbook with KPI groups entirely by calling the exact same global Python functions that are exposed to Large Language Models. | `python examples/scripts/demo_e2e_mcp_workflow.py` |

## Natural Language Prompts for Large Language Models (LLMs)

If you are using an LLM tool equipped with an MCP client (such as Claude Desktop), you can directly copy the contents of the following files into the chat. The LLM will then act as an automated data analysis assistant, configuring complex Dashboards for you without any code:

- **`prompts/demo_auto_layout_prompt.md`**: [Recommended] An extremely minimalist prompt. Asks the LLM to infer and construct all the necessary complex JSON Layout parameters itself, showcasing the extreme intelligence of LLMs when combined with the `cwtwb` MCP tool.
- **`prompts/demo_c2_layout_prompt.md`**: A short, business-oriented prompt specifically for generating the "C.2 Replica" presentation dashboard (using an external file path for layout).
- **`prompts/demo_declarative_layout_prompt.md`**: A longer, detailed prompt asking the LLM to assemble 8 charts into two different dashboards in a single task execution.

> All output files will be generated in the `output/` folder at the root of the project by default.
