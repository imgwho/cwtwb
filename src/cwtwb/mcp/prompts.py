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
    """Guide the full datasource-first workflow with concise user-facing confirmation gates."""

    return [
        {
            "role": "user",
            "content": (
                "You are orchestrating a cwtwb MCP dashboard authoring run.\n"
                "The human interaction must stay natural-language, but your internal workflow must be datasource-first and gated.\n\n"
                "Required workflow:\n"
                "1. Call start_authoring_run with the datasource path, output_dir, and authoring_mode='agent_first'.\n"
                "2. Call intake_datasource_schema and summarize the resulting schema_summary artifact and its Markdown review file.\n"
                "3. Prefer interactive_stage_confirmation with stage='schema' right after the schema summary.\n"
                "4. If interactive_stage_confirmation returns chat_fallback, stop and ask the human to confirm the schema in chat, then call confirm_authoring_stage with stage='schema'. If the schema is rejected, do not draft the contract yet.\n"
                "5. Call build_analysis_brief to create the analysis scaffold. In agent_first mode, you must author 2-4 explicit dashboard directions yourself based on the schema and the human conversation.\n"
                "6. Show those candidate directions to the human in plain language and ask them to choose one before you proceed. Do not collapse to a single recommendation silently.\n"
                "7. Call finalize_analysis_brief with the full candidate set plus the human-chosen selected_direction_id.\n"
                "8. Prefer interactive_stage_confirmation with stage='analysis' after summarizing the chosen direction.\n"
                "9. If interactive_stage_confirmation returns chat_fallback, stop and ask the human to confirm the chosen direction in chat, then call confirm_authoring_stage with stage='analysis'. If the human rejects it, stay in the analysis phase and revise the options.\n"
                "10. Call dashboard_brief_to_contract to think about the draft shape, then call draft_authoring_contract.\n"
                "11. Call review_authoring_contract_for_run.\n"
                "12. If intent is still missing, call light_elicitation and ask only those questions.\n"
                "13. Call finalize_authoring_contract only after you have written an explicit executable contract spec: worksheet names, mark types, fields, filters, actions, and encodings.\n"
                "14. Summarize that finalized contract as a dashboard proposal focused on audience, business question, core KPI/charts, filters/interactions, and key calculated fields.\n"
                "15. Prefer interactive_stage_confirmation with stage='contract' after the dashboard proposal summary.\n"
                "16. If interactive_stage_confirmation returns chat_fallback, stop and ask the human to confirm the proposal in chat, then call confirm_authoring_stage with stage='contract'. If the human rejects it, stay in the contract phase.\n"
                "17. Call build_wireframe and summarize the ASCII wireframe and support/workaround notes from the Markdown review file.\n"
                "18. Call finalize_wireframe, even if the human keeps the default layout, and then prefer interactive_stage_confirmation with stage='wireframe'.\n"
                "19. If interactive_stage_confirmation returns chat_fallback, stop and ask the human to confirm the wireframe in chat, then call confirm_authoring_stage with stage='wireframe'. If the human rejects it, stay in the wireframe phase.\n"
                "20. Call authoring_execution_plan to reason about the build, then call build_execution_plan. Treat execution_plan.md as an internal read-only artifact and do not ask the human to approve it by default.\n"
                "21. Only after that internal planning step, call generate_workbook_from_run.\n"
                "22. Finish by summarizing the run id, key artifacts, final workbook path, validation, and analysis.\n\n"
                "Hard rules:\n"
                "- Prefer get_client_interaction_capabilities and interactive_stage_confirmation for the default human confirmation gates: schema, analysis, contract, and wireframe.\n"
                "- Use confirm_authoring_stage directly only after a real chat fallback answer or when replaying an already-explicit human decision.\n"
                "- The server requires a fresh interactive_stage_confirmation for the current artifact version before each confirm_authoring_stage call.\n"
                "- Keep schema summaries short: main sheet/table, measures, grouped dimensions, and one line about what the dashboard will use.\n"
                "- Keep contract summaries user-facing: who it is for, what it answers, the 4-6 key KPI/charts, filters/interactions, and any key calculated fields.\n"
                "- Keep wireframe summaries visual and plain-language. Avoid internal layout jargon such as weight, fixed_size, or layout-flow.\n"
                "- Do not ask the human to approve execution steps unless they explicitly ask to inspect the plan.\n"
                "- In agent_first mode, the server will not infer dashboard directions, audiences, KPIs, filters, or chart shapes from keywords. You must author those decisions explicitly.\n"
                "- In agent_first mode, analysis must present 2-4 candidate directions and the human must choose one before contract authoring begins.\n"
                "- If the human adds a new worksheet, KPI, or core interaction after contract confirmation, reopen `contract` instead of hiding the change in wireframe notes.\n"
                "- build_execution_plan validates that wireframe scope still matches the confirmed contract and will reject drift.\n"
                "- build_execution_plan will fail closed if the confirmed contract is not executable; do not rely on server-side defaults.\n"
                "- Never directly edit files under tmp/agentic_run/{run_id}/.\n"
                "- If any guided-run tool fails, stop immediately.\n"
                "- After a failure, call get_run_status(run_id), summarize last_error, and ask the human whether to reopen analysis, contract, wireframe, or execution_plan.\n"
                "- Do not switch to low-level workbook tools unless the human explicitly asks to leave guided mode.\n"
                "- Never promise an interaction as final if it only exists as a workaround in the wireframe review.\n\n"
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
                "- Make the contract executable: each worksheet should explicitly name its mark_type, dimensions/measures or kpi_fields, and any required encodings/actions.\n"
                "- Do not rely on the server to guess chart types, KPI lists, filters, or interaction targets from keywords.\n"
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
                "- Assume schema, contract, and wireframe confirmations have already happened. Analysis may exist internally without a separate human confirmation.\n"
                "- Describe the likely tool sequence, but stop before execution.\n"
                "- Treat execution_plan.md as an internal read-only artifact; upstream wireframe or contract changes should rebuild the plan instead of editing it.\n"
                "- Do not introduce a new human approval gate unless the human explicitly asks to inspect the execution plan.\n"
                "- Keep the reasoning aligned to supported workbook tools.\n\n"
                f"Final contract:\n{json.dumps(contract_final, indent=2, ensure_ascii=False)}"
            ),
        }
    ]
