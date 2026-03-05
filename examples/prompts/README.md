# CWTWB Prompts Examples Directory

This directory contains a collection of prompt examples for interacting with the `cwtwb` MCP server. You can copy and paste these prompts directly to an MCP-enabled AI assistant (like Cline, Cursor, Gemini, etc.) to automate the generation of complex Tableau workbooks (.twb).

These examples demonstrate how to use natural language commands to instruct the AI assistant to leverage `cwtwb`'s capabilities, including automated data processing, parameter configuration, chart generation, and complex dashboard layouts.

## Examples List

### 1. Basic & Declarative Layout Examples
- **`demo_simple.md`**: Basic example. Instructs the AI to create 4 simple charts (KPIs and Bar charts) using the `superstore.twb` template, and guides it to use the `generate_layout_json` tool to arrange them in a combined vertical and horizontal layout.
- **`demo_auto_layout_prompt.md`**: Auto layout prompt example. With very brief natural language, it lets the LLM infer and build an adaptive dashboard layout combining 3 charts.
- **`demo_auto_layout4_prompt.md`**: Demonstrates the latest Declarative Layout features and handling of fixed sizing in Tableau.
- **`demo_c2_layout_prompt.md`**: A quick example showing how to command the AI to directly read an existing external JSON layout configuration (`layout_c2.json`) and apply it to a new dashboard.
- **`demo_declarative_layout_prompt.md`**: Advanced declarative layout demonstration. Creates 8 charts in bulk and instructs the AI to read two different external JSON layout files (`layout_executive.json` and `layout_c2.json`) to map out two different dashboards.

### 2. Comprehensive Business Dashboard Examples (Overview Dashboard)
These prompts show how to create a fully functional, interactive business dashboard including "What-If" analysis, calculated fields, maps, filter actions, and complex layouts.
- **`overview_business_demo.md`**: Framed as a business executive's requirements, demonstrating how to use natural business language to guide the AI to build a complete "Superstore Profitability Overview" dashboard.
- **`overview_natural_en.md`**: Detailed English natural language prompt. Contains very specific technical metric definitions and layout dimensions for accurately recreating a given Overview dashboard.
- **`overview_natural zh_cn.md`**: The **Chinese version** natural language prompt for the fully featured Overview dashboard mentioned above.

### 3. Testing and Debugging Cases
- **`test_parameter_prefix_bug.md`**: A specific test prompt to verify whether `cwtwb` correctly parses calculation logic when referencing parameters (with or without the `[Parameters].` prefix).

---

> **💡 Tip:**
> If you encounter context truncation or memory issues due to excessively long payloads when using these instructions, please pay special attention to the standard execution step (Best Practice) shown in files like `demo_simple.md`: **"Call the `generate_layout_json` tool first to write the local JSON file, and then pass the absolute file path to `add_dashboard`."**
