"""FastMCP server singleton for the cwtwb MCP server.

This module creates the single FastMCP `server` instance that all tool and
resource modules register against via @server.tool() and @server.resource().

Import order matters: app.py must be imported before tools_*.py and resources.py
so that `server` exists when the decorators run.  The entry point (typically
run via `mcp run` or `python -m cwtwb.mcp`) imports all tool modules, which
self-register, and then starts the server transport.

The `instructions` string is what AI agents read when they first connect —
it summarises the required call order and points agents to skill resources.
"""

from mcp.server.fastmcp import FastMCP


server = FastMCP(
    "cwtwb",
    instructions="Tableau Workbook (.twb) generation MCP Server. "
    "Prefer the guided_dashboard_authoring prompt for natural-language dashboard requests. "
    "For guided authoring, start_authoring_run first, then intake_datasource_schema, "
    "wait for human confirmation on schema, then draft_authoring_contract, review_authoring_contract_for_run, "
    "finalize_authoring_contract, confirm_authoring_stage('contract'), build_execution_plan, "
    "confirm_authoring_stage('execution_plan'), and finally generate_workbook_from_run. "
    "Use dashboard_brief_to_contract, light_elicitation, and authoring_execution_plan prompts only to guide the agent workflow between those tool calls. "
    "Read the dashboard contract template (cwtwb://contracts/dashboard_authoring_v1) and inspect dataset profiles via cwtwb://profiles/index when needed. "
    "Manual workbook editing still follows create_workbook or open_workbook first, then add_worksheet + configure_chart, and finally save_workbook. "
    "Prefer core primitives first, and use list_capabilities or describe_capability "
    "when you need to check whether a chart or feature is core, advanced, or recipe-only. "
    "For professional-quality output, read the agent skills "
    "(cwtwb://skills/index) before starting each phase.",
)
