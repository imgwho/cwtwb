"""Regression coverage for the guided MCP authoring run workflow."""

from __future__ import annotations

import asyncio
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cwtwb.mcp.resources import (
    read_dashboard_authoring_contract,
    read_profiles_index,
    read_skill,
    read_skills_index,
)
from cwtwb.server import (
    build_execution_plan,
    confirm_authoring_stage,
    draft_authoring_contract,
    finalize_authoring_contract,
    generate_workbook_from_run,
    get_run_status,
    intake_datasource_schema,
    list_authoring_runs,
    resume_authoring_run,
    review_authoring_contract_for_run,
    server,
    start_authoring_run,
)

XLS_SOURCE = Path("templates/Sample - Superstore - simple.xls")
HYPER_SOURCE = Path("templates/dashboard/Sample _ Superstore.hyper")
RUN_ROOT = Path("tmp") / "authoring_run_tests"
GLOBAL_RUN_ROOT = Path("tmp") / "agentic_run"


@pytest.fixture(autouse=True)
def clean_authoring_runs():
    for root in (RUN_ROOT, GLOBAL_RUN_ROOT):
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)
    yield
    for root in (RUN_ROOT, GLOBAL_RUN_ROOT):
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)


def _start_run() -> dict:
    if not XLS_SOURCE.exists():
        pytest.skip("Sample Excel datasource not available")
    payload = json.loads(
        start_authoring_run(
            datasource_path=str(XLS_SOURCE),
            output_dir=str(RUN_ROOT),
        )
    )
    return payload


def _approve_schema(run_id: str) -> None:
    intake_payload = json.loads(intake_datasource_schema(run_id))
    schema_path = Path(intake_payload["artifact"])
    schema_summary = json.loads(schema_path.read_text(encoding="utf-8"))
    if not schema_summary.get("selected_primary_object") and schema_summary.get("sheets"):
        preferred = schema_summary["sheets"][0]["name"]
        intake_datasource_schema(run_id, preferred_sheet=preferred)
    confirm_authoring_stage(run_id, "schema", True, "Schema looks correct.")


def _finalize_contract(run_id: str) -> None:
    review_authoring_contract_for_run(run_id)
    finalize_authoring_contract(
        run_id,
        json.dumps(
            {
                "audience": "Sales leaders",
                "primary_question": "Which regions and categories are driving sales?",
                "require_interaction": True,
            },
            ensure_ascii=False,
        ),
    )
    confirm_authoring_stage(run_id, "contract", True, "Contract approved.")


class TestAuthoringResources:
    def test_contract_resource_contains_workbook_template(self):
        contract = json.loads(read_dashboard_authoring_contract())
        assert "workbook_template" in contract
        assert contract["dataset"] == ""

    def test_skills_index_includes_authoring_workflow(self):
        index_text = read_skills_index()
        assert "authoring_workflow" in index_text
        assert "dashboard_designer" in index_text

    def test_profiles_resources_expose_superstore_profile(self):
        index_text = read_profiles_index()
        assert "superstore" in index_text

    def test_authoring_workflow_skill_is_readable(self):
        skill_text = read_skill("authoring_workflow")
        assert "start_authoring_run" in skill_text
        assert "generate_workbook_from_run" in skill_text


class TestAuthoringPrompts:
    def test_guided_dashboard_authoring_prompt_is_registered(self):
        prompt = server._prompt_manager.get_prompt("guided_dashboard_authoring")
        assert prompt is not None

    def test_guided_dashboard_authoring_prompt_references_confirmation_gates(self):
        messages = asyncio.run(
            server._prompt_manager.render_prompt(
                "guided_dashboard_authoring",
                {
                    "brief": "Build an executive sales dashboard.",
                    "datasource_path": str(XLS_SOURCE),
                },
            )
        )
        text = messages[0].content.text
        assert "start_authoring_run" in text
        assert "confirm_authoring_stage" in text
        assert "stage='schema'" in text
        assert "stage='contract'" in text
        assert "stage='execution_plan'" in text
        assert "generate_workbook_from_run" in text

    def test_server_instructions_reference_all_guided_confirmation_calls(self):
        text = server.instructions
        assert "confirm_authoring_stage('schema')" in text
        assert "confirm_authoring_stage('contract')" in text
        assert "confirm_authoring_stage('execution_plan')" in text

    def test_dashboard_brief_to_contract_prompt_uses_schema_summary(self):
        schema_summary = {
            "datasource": {"path": str(XLS_SOURCE), "type": "excel"},
            "selected_primary_object": "Orders",
            "fields": [{"name": "Sales"}, {"name": "Region"}],
            "field_candidates": {"dimensions": ["Region"], "measures": ["Sales"], "date_fields": [], "geo_fields": []},
        }
        messages = asyncio.run(
            server._prompt_manager.render_prompt(
                "dashboard_brief_to_contract",
                {
                    "brief": "Build a sales dashboard for leaders.",
                    "schema_summary_json": json.dumps(schema_summary, ensure_ascii=False),
                },
            )
        )
        text = messages[0].content.text
        assert "Schema summary" in text
        assert "Use only fields present in the schema summary" in text

    def test_light_elicitation_uses_review_artifact(self):
        review_payload = {
            "valid": False,
            "summary": "Need clarification.",
            "clarification_questions": ["Who is the audience?"],
            "normalized_contract": {"goal": "Build a dashboard"},
            "detected_profile": "superstore",
        }
        messages = asyncio.run(
            server._prompt_manager.render_prompt(
                "light_elicitation",
                {"contract_review_json": json.dumps(review_payload, ensure_ascii=False)},
            )
        )
        text = messages[0].content.text
        assert "Ask the user only the minimum necessary follow-up questions" in text
        assert "Who is the audience?" in text

    def test_authoring_execution_plan_prompt_mentions_final_gate(self):
        messages = asyncio.run(
            server._prompt_manager.render_prompt(
                "authoring_execution_plan",
                {"contract_final_json": json.dumps({"dashboard": {"name": "Exec"}})},
            )
        )
        text = messages[0].content.text
        assert "final human confirmation gate" in text
        assert "Final contract" in text


class TestAuthoringRunLifecycle:
    def test_start_list_status_and_resume(self):
        run = _start_run()
        run_id = run["run_id"]

        listed = json.loads(list_authoring_runs(str(RUN_ROOT)))
        assert any(item["run_id"] == run_id for item in listed["runs"])

        status = json.loads(get_run_status(run_id))
        assert status["status"] == "initialized"
        assert status["datasource_path"].endswith("Sample - Superstore - simple.xls")

        resumed = json.loads(resume_authoring_run(run_id))
        assert resumed["run_id"] == run_id
        assert resumed["needs_attention"] is False

    def test_excel_schema_intake_creates_artifact(self):
        run = _start_run()
        run_id = run["run_id"]
        payload = json.loads(intake_datasource_schema(run_id))

        artifact = Path(payload["artifact"])
        assert artifact.exists()
        schema_summary = json.loads(artifact.read_text(encoding="utf-8"))
        assert schema_summary["datasource"]["type"] == "excel"
        assert schema_summary["fields"]
        assert "dimensions" in schema_summary["field_candidates"]

    def test_hyper_schema_intake_lists_tables(self):
        if not HYPER_SOURCE.exists():
            pytest.skip("Sample Hyper datasource not available")
        run = json.loads(
            start_authoring_run(
                datasource_path=str(HYPER_SOURCE),
                output_dir=str(RUN_ROOT),
            )
        )
        try:
            payload = json.loads(intake_datasource_schema(run["run_id"]))
        except RuntimeError as exc:
            pytest.skip(f"Hyper inspection unavailable in this environment: {exc}")
        schema_summary = json.loads(Path(payload["artifact"]).read_text(encoding="utf-8"))
        assert schema_summary["datasource"]["type"] == "hyper"
        assert schema_summary["tables"]
        assert schema_summary["selected_primary_object"]

    def test_contract_can_be_rewritten_after_rejection(self):
        run = _start_run()
        run_id = run["run_id"]
        _approve_schema(run_id)
        draft_authoring_contract(run_id, "Build a regional sales dashboard.")
        review_authoring_contract_for_run(run_id)
        finalize_authoring_contract(run_id)
        confirm_authoring_stage(run_id, "contract", False, "Please rewrite from scratch.")

        rewrite = json.loads(
            draft_authoring_contract(
                run_id,
                "Rewrite this as an executive profitability dashboard.",
                rewrite=True,
            )
        )
        assert rewrite["status"] == "contract_drafted"

    def test_draft_contract_prefers_explicit_audience_and_primary_question_labels(self):
        run = _start_run()
        run_id = run["run_id"]
        _approve_schema(run_id)

        draft = json.loads(
            draft_authoring_contract(
                run_id,
                (
                    "Build an executive sales performance dashboard for Matthew.\n"
                    "Audience: sales leaders\n"
                    "Primary question: Which regions and categories are driving sales and profit?\n"
                    "Please include interactive filtering from the top view into detail."
                ),
            )
        )
        contract = json.loads(Path(draft["artifact"]).read_text(encoding="utf-8"))
        assert contract["audience"] == "sales leaders"
        assert contract["primary_question"] == "Which regions and categories are driving sales and profit?"

    def test_execution_plan_prefers_regional_geo_and_primary_to_detail_action(self):
        run = _start_run()
        run_id = run["run_id"]
        _approve_schema(run_id)
        draft_authoring_contract(
            run_id,
            (
                "Build an executive sales performance dashboard for Matthew.\n"
                "Audience: sales leaders\n"
                "Primary question: Which regions, categories, and sub-categories are driving sales and profit?\n"
                "Please include interactive filtering from the top view into detail."
            ),
        )
        review_authoring_contract_for_run(run_id)
        finalize_authoring_contract(run_id)
        confirm_authoring_stage(run_id, "contract", True, "Contract approved.")

        plan = json.loads(build_execution_plan(run_id))
        payload = json.loads(Path(plan["artifact"]).read_text(encoding="utf-8"))
        primary_view_step = next(
            step
            for step in payload["steps"]
            if step["tool"] == "configure_chart"
            and step["args"].get("worksheet_name") == "Primary View"
        )
        assert primary_view_step["args"]["geographic_field"] == "Region"

        action_step = next(
            step for step in payload["steps"] if step["tool"] == "add_dashboard_action"
        )
        assert action_step["args"]["source_sheet"] == "Primary View"
        assert action_step["args"]["target_sheet"] == "Detail View"
        assert action_step["args"]["fields"] == ["Region"]

    def test_full_guided_run_generates_workbook_and_reports(self):
        run = _start_run()
        run_id = run["run_id"]

        _approve_schema(run_id)
        draft_authoring_contract(
            run_id,
            "Build an executive sales dashboard for sales leaders with interactive filtering.",
        )
        _finalize_contract(run_id)

        plan = json.loads(build_execution_plan(run_id))
        assert plan["status"] == "execution_planned"
        confirm_authoring_stage(run_id, "execution_plan", True, "Execution plan approved.")

        generated = json.loads(generate_workbook_from_run(run_id))
        workbook_path = Path(generated["final_workbook"])
        assert workbook_path.exists()
        assert generated["status"] == "analyzed"

        status = json.loads(get_run_status(run_id))
        assert status["status"] == "analyzed"
        assert any(name.startswith("validation_report.") for name in status["artifacts_present"])
        assert any(name.startswith("analysis_report.") for name in status["artifacts_present"])

        root = ET.parse(workbook_path).getroot()
        caption = root.find(".//worksheet[@name='Summary View']/layout-options/caption/formatted-text/run")
        assert caption is not None

    def test_generation_failure_sets_failed_status(self):
        run = _start_run()
        run_id = run["run_id"]

        _approve_schema(run_id)
        draft_authoring_contract(
            run_id,
            "Build an executive sales dashboard for sales leaders with interactive filtering.",
        )
        _finalize_contract(run_id)
        build_execution_plan(run_id)

        manifest = json.loads((RUN_ROOT / run_id / "manifest.json").read_text(encoding="utf-8"))
        plan_path = RUN_ROOT / run_id / manifest["artifacts"]["execution_plan"]["current"]
        plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
        plan_payload["steps"][1]["tool"] = "save_workbook"
        plan_path.write_text(json.dumps(plan_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        confirm_authoring_stage(run_id, "execution_plan", True, "Approve the broken plan for failure coverage.")
        with pytest.raises(RuntimeError):
            generate_workbook_from_run(run_id)

        failed_status = json.loads(get_run_status(run_id))
        assert failed_status["status"] == "workbook_generation_failed"
        assert failed_status["last_error"]["step_tool"] == "save_workbook"
