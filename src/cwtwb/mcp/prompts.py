"""MCP prompts for guided datasource-first dashboard authoring."""

from __future__ import annotations

import json

from .app import server
from .resources import read_dashboard_authoring_contract, read_profiles_index


@server.prompt(
    name="guided_dashboard_authoring",
    title="Guided Dashboard Authoring",
    description="Turn a natural-language dashboard brief plus a datasource path into a gated cwtwb authoring run.",
)
def guided_dashboard_authoring(
    brief: str,
    datasource_path: str,
    output_dir: str = "tmp/agentic_run",
) -> list[dict[str, str]]:
    """Guide the full datasource-first workflow with explicit confirmation gates."""

    return [
        {
            "role": "user",
            "content": (
                "You are orchestrating a cwtwb MCP dashboard authoring run.\n"
                "The human interaction must stay natural-language, but your internal workflow must be datasource-first and gated.\n\n"
                "Required workflow:\n"
                "1. Call start_authoring_run with the datasource path.\n"
                "2. Call intake_datasource_schema and summarize the resulting schema_summary artifact.\n"
                "3. Stop and ask the human to confirm the schema before continuing.\n"
                "4. Call dashboard_brief_to_contract to think about the draft shape, then call draft_authoring_contract.\n"
                "5. Call review_authoring_contract_for_run.\n"
                "6. If intent is still missing, call light_elicitation and ask only those questions.\n"
                "7. Call finalize_authoring_contract.\n"
                "8. Stop and ask the human to confirm the finalized contract.\n"
                "9. Call authoring_execution_plan to reason about the build, then call build_execution_plan.\n"
                "10. Stop and ask the human to confirm the execution plan.\n"
                "11. Only after confirmation, call generate_workbook_from_run.\n"
                "12. Finish by summarizing the run id, key artifacts, final workbook path, validation, and analysis.\n\n"
                f"Human brief:\n{brief}\n\n"
                f"Datasource path: {datasource_path}\n"
                f"Run output root: {output_dir}"
            ),
        }
    ]


@server.prompt(
    name="dashboard_brief_to_contract",
    title="Dashboard Brief To Contract",
    description="Turn a human brief plus schema summary into a strict cwtwb contract draft.",
)
def dashboard_brief_to_contract(
    brief: str,
    schema_summary_json: str,
) -> list[dict[str, str]]:
    """Convert a human brief plus schema context into a contract draft prompt."""

    template = json.loads(read_dashboard_authoring_contract())
    schema_summary = json.loads(schema_summary_json)
    profile_index = read_profiles_index()

    return [
        {
            "role": "user",
            "content": (
                "Draft a cwtwb dashboard authoring contract as strict JSON only.\n\n"
                "Rules:\n"
                "- Output valid JSON only.\n"
                "- Follow the template shape exactly.\n"
                "- Use only fields present in the schema summary.\n"
                "- Keep workbook_template blank unless the human explicitly asks for one.\n"
                "- Prefer simple, supported worksheet ideas over speculative complexity.\n"
                "- Do not continue to execution; this prompt is only for draft thinking.\n\n"
                f"Contract template:\n{json.dumps(template, indent=2, ensure_ascii=False)}\n\n"
                f"Known dataset profiles:\n{profile_index}\n\n"
                f"Schema summary:\n{json.dumps(schema_summary, indent=2, ensure_ascii=False)}\n\n"
                f"Human brief:\n{brief}"
            ),
        }
    ]


@server.prompt(
    name="light_elicitation",
    title="Light Elicitation",
    description="Ask only the missing high-value follow-up questions from a contract review artifact.",
)
def light_elicitation(contract_review_json: str) -> list[dict[str, str]]:
    """Generate concise follow-up questions from a persisted contract review."""

    review = json.loads(contract_review_json)
    normalized_contract = json.dumps(
        review.get("normalized_contract", {}),
        indent=2,
        ensure_ascii=False,
    )

    if review.get("valid"):
        content = (
            "The reviewed contract is already valid.\n"
            "Respond with exactly: No clarification needed.\n\n"
            f"Review summary: {review.get('summary', '')}\n"
            f"Normalized contract:\n{normalized_contract}"
        )
    else:
        question_block = "\n".join(
            f"- {question}" for question in review.get("clarification_questions", [])
        )
        content = (
            "Ask the user only the minimum necessary follow-up questions.\n"
            "Rules:\n"
            "- Ask at most 3 questions.\n"
            "- Keep them short and business-oriented.\n"
            "- Do not ask about fields that already exist in the schema summary.\n"
            "- Preserve the current analytical direction.\n"
            "- Stop after asking; do not continue to generation.\n\n"
            f"Review summary: {review.get('summary', '')}\n"
            f"Detected profile: {review.get('detected_profile') or '(none)'}\n"
            f"Suggested clarification questions:\n{question_block}\n\n"
            f"Normalized contract:\n{normalized_contract}"
        )

    return [{"role": "user", "content": content}]


@server.prompt(
    name="authoring_execution_plan",
    title="Authoring Execution Plan",
    description="Produce a concise build-oriented MCP execution plan from a finalized contract.",
)
def authoring_execution_plan(contract_final_json: str) -> list[dict[str, str]]:
    """Generate an execution-oriented MCP plan from a finalized contract."""

    contract_final = json.loads(contract_final_json)

    return [
        {
            "role": "user",
            "content": (
                "Create a concise MCP execution plan for cwtwb.\n"
                "Rules:\n"
                "- Use the finalized contract as the source of truth.\n"
                "- Assume schema confirmation has already happened.\n"
                "- Describe the likely tool sequence, but stop before execution.\n"
                "- Mention the final human confirmation gate before generate_workbook_from_run.\n"
                "- Keep the reasoning aligned to supported workbook tools.\n\n"
                f"Final contract:\n{json.dumps(contract_final, indent=2, ensure_ascii=False)}"
            ),
        }
    ]
