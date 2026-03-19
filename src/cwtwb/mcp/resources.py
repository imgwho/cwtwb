"""MCP resources exposed by cwtwb — read-only reference data for AI agents.

Resources are different from tools: they are read-only data blobs that an
AI agent fetches for context, not actions that modify state.

AVAILABLE RESOURCES
-------------------
  file://docs/tableau_all_functions.json
      Complete list of Tableau calculation functions with syntax and examples.
      Source: docs/tableau_all_functions.json (bundled with cwtwb).
      Use this to look up function signatures when writing calculated fields.

  cwtwb://skills/index
      Markdown index listing all available agent skill files with descriptions.
      Read this first to understand which skills exist before fetching one.

  cwtwb://skills/{skill_name}
      A specific agent skill Markdown file.  Skills are expert-level guides
      for common phases of workbook construction:
        - calculation_builder  → writing Tableau formulas and calculated fields
        - chart_builder        → choosing mark types and encoding best practices
        - dashboard_designer   → layout patterns, zone sizing, action wiring
        - formatting           → color palettes, font choices, style consistency

USAGE PATTERN (recommended by server instructions)
---------------------------------------------------
  Before each major phase, fetch the relevant skill:
    read_resource("cwtwb://skills/chart_builder")    # before configure_chart
    read_resource("cwtwb://skills/dashboard_designer") # before add_dashboard
"""

from __future__ import annotations

from ..config import SKILLS_DIR, TABLEAU_FUNCTIONS_JSON
from .app import server


@server.resource("file://docs/tableau_all_functions.json")
def read_tableau_functions() -> str:
    """Read the complete list of Tableau calculation functions."""

    if not TABLEAU_FUNCTIONS_JSON.exists():
        raise FileNotFoundError(f"Tableau functions JSON not found at: {TABLEAU_FUNCTIONS_JSON}")

    with TABLEAU_FUNCTIONS_JSON.open("r", encoding="utf-8") as f:
        return f.read()


_SKILL_NAMES = [
    "calculation_builder",
    "chart_builder",
    "dashboard_designer",
    "formatting",
]


@server.resource("cwtwb://skills/index")
def read_skills_index() -> str:
    """List all available cwtwb agent skills."""

    lines = [
        "# cwtwb Agent Skills",
        "",
        "Load a skill before each phase for expert-level guidance.",
        "Read a skill with: read_resource('cwtwb://skills/<skill_name>')",
        "",
        "## Available Skills (in recommended order)",
        "",
    ]
    for name in _SKILL_NAMES:
        skill_path = SKILLS_DIR / f"{name}.md"
        if skill_path.exists():
            content = skill_path.read_text(encoding="utf-8")
            desc = ""
            for line in content.split("\n"):
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    break
            lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)


@server.resource("cwtwb://skills/{skill_name}")
def read_skill(skill_name: str) -> str:
    """Read a specific cwtwb agent skill."""

    skill_path = SKILLS_DIR / f"{skill_name}.md"
    if not skill_path.exists():
        available = ", ".join(_SKILL_NAMES)
        raise FileNotFoundError(
            f"Skill '{skill_name}' not found. Available skills: {available}"
        )
    return skill_path.read_text(encoding="utf-8")
