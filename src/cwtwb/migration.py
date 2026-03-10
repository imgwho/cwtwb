"""Workbook migration helpers for reusing TWB templates with a new datasource."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
from typing import Any

from lxml import etree
import xlrd

from .twb_analyzer import analyze_workbook


# Known bilingual field aliases used as a hint layer on top of automatic schema scanning.
FIELD_ALIAS_GROUPS: tuple[tuple[str, ...], ...] = (
    ("Row ID", "\u884c ID"),
    ("Order ID", "\u8ba2\u5355 ID"),
    ("Order Date", "\u8ba2\u5355\u65e5\u671f"),
    ("Ship Date", "\u53d1\u8d27\u65e5\u671f"),
    ("Ship Mode", "\u88c5\u8fd0\u6a21\u5f0f"),
    ("Customer ID", "\u5ba2\u6237 ID"),
    ("Customer Name", "\u5ba2\u6237\u540d\u79f0"),
    ("Segment", "\u7ec6\u5206"),
    ("Country/Region", "\u56fd\u5bb6/\u5730\u533a"),
    ("City", "\u57ce\u5e02"),
    ("State/Province", "\u7701/\u81ea\u6cbb\u533a"),
    ("Postal Code", "\u90ae\u653f\u7f16\u7801"),
    ("Region", "\u533a\u57df"),
    ("Product ID", "\u4ea7\u54c1 ID"),
    ("Category", "\u7c7b\u522b"),
    ("Sub-Category", "\u5b50\u7c7b\u522b"),
    ("Product Name", "\u4ea7\u54c1\u540d\u79f0"),
    ("Sales", "\u9500\u552e\u989d"),
    ("Quantity", "\u6570\u91cf"),
    ("Discount", "\u6298\u6263"),
    ("Profit", "\u5229\u6da6"),
)

_ALIAS_LOOKUP: dict[str, tuple[str, ...]] = {}
for _group in FIELD_ALIAS_GROUPS:
    for _name in _group:
        _ALIAS_LOOKUP["".join(ch for ch in _name.casefold() if ch.isalnum())] = _group


@dataclass
class MappingCandidate:
    source_field: str
    target_field: str
    confidence: float
    reason: str


@dataclass
class MigrationIssue:
    issue_type: str
    severity: str
    message: str
    worksheet: str | None = None
    calculation: str | None = None
    field: str | None = None


@dataclass
class MigrationPreview:
    template_file: str
    target_source: str
    source_datasource: str
    source_datasource_caption: str | None
    target_datasource: str
    target_datasource_caption: str | None
    scope: str
    worksheets_in_scope: list[str]
    dashboards_in_scope: list[str]
    used_datasources: list[str]
    source_schema: list[str]
    target_schema: list[str]
    candidate_field_mapping: list[MappingCandidate]
    calculation_rewrite_summary: dict[str, int]
    issues: list[MigrationIssue] = field(default_factory=list)
    removable_datasources: list[str] = field(default_factory=list)
    capability_summary: dict[str, Any] = field(default_factory=dict)

    @property
    def blocking_issue_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "blocking")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["blocking_issue_count"] = self.blocking_issue_count
        return payload


@dataclass
class WorkbookMigrationProfile:
    template_file: str
    scope: str
    datasources: list[dict[str, Any]]
    worksheets_in_scope: list[str]
    dashboards_in_scope: list[str]
    used_datasources: list[str]
    source_datasource: str
    source_datasource_caption: str | None
    source_schema: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_path(path: str | Path) -> str:
    return str(Path(path).resolve()).replace("\\", "/")


def _normalize_field_name(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def _read_excel_headers(path: str | Path) -> dict[str, Any]:
    workbook = xlrd.open_workbook(_normalize_path(path))
    sheet = workbook.sheet_by_index(0)
    headers = [str(value).strip() for value in sheet.row_values(0) if str(value).strip()]
    return {
        "sheet_name": sheet.name,
        "headers": headers,
    }


def _top_level_datasources(root: etree._Element) -> list[etree._Element]:
    datasources = root.find("datasources")
    if datasources is None:
        return []
    return datasources.findall("datasource")


def _get_datasource_fields(datasource: etree._Element) -> dict[str, str]:
    relation = datasource.find(".//relation")
    fields: dict[str, str] = {}
    if relation is None:
        return fields
    for col in relation.findall("columns/column"):
        raw_name = col.get("name")
        if raw_name:
            fields[raw_name] = f"[{raw_name}]"
    return fields


def _get_datasource_by_name(root: etree._Element, datasource_name: str) -> etree._Element | None:
    for ds in _top_level_datasources(root):
        if ds.get("name") == datasource_name:
            return ds
    return None


def _find_target_datasource(root: etree._Element, target_source: str | Path) -> etree._Element | None:
    target_name = Path(target_source).name.casefold()
    normalized_target = _normalize_path(target_source).casefold()
    for datasource in _top_level_datasources(root):
        for conn in datasource.findall(".//connection[@class='excel-direct']"):
            filename = (conn.get("filename") or "").replace("\\", "/")
            if Path(filename).name.casefold() == target_name or filename.casefold() == normalized_target:
                return datasource
    return None


def _collect_scope_worksheets(root: etree._Element, scope: str) -> list[etree._Element]:
    if scope != "workbook":
        raise ValueError(f"Unsupported migration scope: {scope}")
    worksheets = root.find("worksheets")
    if worksheets is None:
        return []
    return worksheets.findall("worksheet")


def _worksheet_datasource_names(worksheet: etree._Element) -> list[str]:
    seen: list[str] = []
    for dep in worksheet.findall(".//datasource-dependencies"):
        datasource_name = dep.get("datasource")
        if datasource_name and datasource_name not in seen:
            seen.append(datasource_name)
    return seen


def _find_source_datasource_name(root: etree._Element, target_datasource_name: str | None, scope: str) -> str:
    usage_count: dict[str, int] = {}
    for worksheet in _collect_scope_worksheets(root, scope):
        for datasource_name in _worksheet_datasource_names(worksheet):
            usage_count[datasource_name] = usage_count.get(datasource_name, 0) + 1

    ranked = sorted(
        (
            (name, count)
            for name, count in usage_count.items()
            if target_datasource_name is None or name != target_datasource_name
        ),
        key=lambda item: (-item[1], item[0]),
    )
    if not ranked:
        raise ValueError("Could not identify a source datasource to migrate from.")
    return ranked[0][0]


def _collect_dashboards_for_worksheets(root: etree._Element, worksheet_names: set[str]) -> list[str]:
    dashboards = root.find("dashboards")
    if dashboards is None:
        return []
    names: list[str] = []
    for dashboard in dashboards.findall("dashboard"):
        for zone in dashboard.findall(".//zone[@name]"):
            if zone.get("name") in worksheet_names:
                names.append(dashboard.get("name", ""))
                break
    return [name for name in names if name]


def inspect_target_schema(target_source: str | Path) -> dict[str, Any]:
    info = _read_excel_headers(target_source)
    info["target_source"] = _normalize_path(target_source)
    return info


def profile_twb_for_migration(
    file_path: str | Path,
    scope: str = "workbook",
    target_source: str | Path | None = None,
) -> WorkbookMigrationProfile:
    path = Path(file_path)
    root = etree.parse(str(path)).getroot()
    scope_worksheets = _collect_scope_worksheets(root, scope)
    worksheet_names = [worksheet.get("name", "") for worksheet in scope_worksheets]
    dashboards = _collect_dashboards_for_worksheets(root, set(worksheet_names))
    used_datasources = sorted(
        {
            datasource_name
            for worksheet in scope_worksheets
            for datasource_name in _worksheet_datasource_names(worksheet)
        }
    )

    target_datasource_name = None
    if target_source is not None:
        target_ds = _find_target_datasource(root, target_source)
        if target_ds is not None:
            target_datasource_name = target_ds.get("name")

    source_datasource_name = _find_source_datasource_name(root, target_datasource_name, scope)
    source_datasource = _get_datasource_by_name(root, source_datasource_name)
    if source_datasource is None:
        raise ValueError(f"Could not locate source datasource '{source_datasource_name}' in workbook.")

    datasources = []
    for datasource in _top_level_datasources(root):
        datasources.append(
            {
                "name": datasource.get("name"),
                "caption": datasource.get("caption"),
                "hasconnection": datasource.get("hasconnection"),
                "field_count": len(_get_datasource_fields(datasource)),
                "used_in_scope": datasource.get("name") in used_datasources,
            }
        )

    return WorkbookMigrationProfile(
        template_file=_normalize_path(path),
        scope=scope,
        datasources=datasources,
        worksheets_in_scope=worksheet_names,
        dashboards_in_scope=dashboards,
        used_datasources=used_datasources,
        source_datasource=source_datasource_name,
        source_datasource_caption=source_datasource.get("caption"),
        source_schema=list(_get_datasource_fields(source_datasource).keys()),
    )


def _find_match_candidates(source_field: str, target_fields: list[str]) -> tuple[list[str], str, float]:
    exact_matches = [target for target in target_fields if target == source_field]
    if len(exact_matches) == 1:
        return exact_matches, "exact field name match", 1.0

    normalized_source = _normalize_field_name(source_field)
    normalized_matches = [target for target in target_fields if _normalize_field_name(target) == normalized_source]
    if len(normalized_matches) == 1:
        return normalized_matches, "normalized field name match", 0.96

    alias_group = _ALIAS_LOOKUP.get(normalized_source)
    if alias_group is not None:
        alias_targets = [
            target
            for target in target_fields
            if _normalize_field_name(target) in {_normalize_field_name(alias) for alias in alias_group}
        ]
        if alias_targets:
            return alias_targets, "alias dictionary match", 0.9

    return [], "", 0.0


def propose_field_mapping(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    profile = profile_twb_for_migration(file_path, scope=scope, target_source=target_source)
    target_schema = inspect_target_schema(target_source)
    target_fields = target_schema["headers"]
    overrides = mapping_overrides or {}

    candidates: list[MappingCandidate] = []
    issues: list[MigrationIssue] = []
    for source_field in profile.source_schema:
        if source_field in overrides:
            target_field = overrides[source_field]
            if target_field in target_fields:
                candidates.append(
                    MappingCandidate(
                        source_field=source_field,
                        target_field=target_field,
                        confidence=1.0,
                        reason="override mapping",
                    )
                )
            else:
                issues.append(
                    MigrationIssue(
                        issue_type="unmapped",
                        severity="blocking",
                        message=(
                            f"Override target field '{target_field}' does not exist in target schema "
                            f"for source field '{source_field}'."
                        ),
                        field=source_field,
                    )
                )
            continue

        matches, reason, confidence = _find_match_candidates(source_field, target_fields)
        if len(matches) == 1:
            candidates.append(
                MappingCandidate(
                    source_field=source_field,
                    target_field=matches[0],
                    confidence=confidence,
                    reason=reason,
                )
            )
        elif len(matches) > 1:
            issues.append(
                MigrationIssue(
                    issue_type="ambiguous",
                    severity="blocking",
                    message=(
                        f"Source field '{source_field}' matched multiple target fields: "
                        f"{', '.join(matches)}."
                    ),
                    field=source_field,
                )
            )
        else:
            issues.append(
                MigrationIssue(
                    issue_type="unmapped",
                    severity="blocking",
                    message=f"Could not find a target field match for source field '{source_field}'.",
                    field=source_field,
                )
            )

    return {
        "template_file": profile.template_file,
        "target_source": target_schema["target_source"],
        "scope": scope,
        "source_datasource": profile.source_datasource,
        "source_schema": profile.source_schema,
        "target_schema": target_fields,
        "candidate_field_mapping": [asdict(candidate) for candidate in candidates],
        "issues": [asdict(issue) for issue in issues],
        "blocking_issue_count": sum(1 for issue in issues if issue.severity == "blocking"),
    }


def _calculation_summary(worksheets: list[etree._Element]) -> dict[str, int]:
    total_calcs = 0
    rewrite_candidates = 0
    for worksheet in worksheets:
        for dep in worksheet.findall(".//datasource-dependencies"):
            for col in dep.findall("column"):
                calc = col.find("calculation")
                if calc is None:
                    continue
                total_calcs += 1
                formula = calc.get("formula") or ""
                if "[" in formula and "]" in formula:
                    rewrite_candidates += 1
    return {
        "worksheet_count": len(worksheets),
        "calculation_columns": total_calcs,
        "formulas_requiring_field_rewrite": rewrite_candidates,
    }


def preview_twb_migration(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
) -> MigrationPreview:
    path = Path(file_path)
    root = etree.parse(str(path)).getroot()
    scope_worksheets = _collect_scope_worksheets(root, scope)
    worksheet_names = [worksheet.get("name", "") for worksheet in scope_worksheets]
    dashboards = _collect_dashboards_for_worksheets(root, set(worksheet_names))
    used_datasources = sorted(
        {
            datasource_name
            for worksheet in scope_worksheets
            for datasource_name in _worksheet_datasource_names(worksheet)
        }
    )

    target_datasource = _find_target_datasource(root, target_source)
    target_schema_info = inspect_target_schema(target_source)
    target_datasource_name = target_datasource.get("name", "") if target_datasource is not None else ""
    source_datasource_name = _find_source_datasource_name(root, target_datasource_name or None, scope)
    source_datasource = _get_datasource_by_name(root, source_datasource_name)
    if source_datasource is None:
        raise ValueError(f"Could not locate source datasource '{source_datasource_name}' in workbook.")

    mapping_payload = propose_field_mapping(
        file_path=file_path,
        target_source=target_source,
        scope=scope,
        mapping_overrides=mapping_overrides,
    )
    issues = [MigrationIssue(**issue) for issue in mapping_payload["issues"]]
    if target_datasource is None:
        issues.append(
            MigrationIssue(
                issue_type="target-datasource-missing",
                severity="blocking",
                message=(
                    "The target Excel file was scanned successfully, but no matching workbook datasource "
                    "points to it yet. Preview can continue, but apply requires an in-workbook target datasource."
                ),
            )
        )

    capability_report = analyze_workbook(path)
    return MigrationPreview(
        template_file=_normalize_path(path),
        target_source=_normalize_path(target_source),
        source_datasource=source_datasource_name,
        source_datasource_caption=source_datasource.get("caption"),
        target_datasource=target_datasource_name,
        target_datasource_caption=target_datasource.get("caption") if target_datasource is not None else None,
        scope=scope,
        worksheets_in_scope=worksheet_names,
        dashboards_in_scope=dashboards,
        used_datasources=used_datasources,
        source_schema=mapping_payload["source_schema"],
        target_schema=target_schema_info["headers"],
        candidate_field_mapping=[MappingCandidate(**candidate) for candidate in mapping_payload["candidate_field_mapping"]],
        calculation_rewrite_summary=_calculation_summary(scope_worksheets),
        issues=issues,
        removable_datasources=[source_datasource_name],
        capability_summary={
            "fit_level": capability_report.fit_level,
            "summary": capability_report.summary,
        },
    )


def _build_string_replacements(preview: MigrationPreview) -> dict[str, str]:
    if not preview.target_datasource:
        raise ValueError("Cannot build replacements without a target datasource already present in the workbook.")

    replacements = {
        preview.source_datasource: preview.target_datasource,
        f"[{preview.source_datasource}].": f"[{preview.target_datasource}].",
    }
    for candidate in preview.candidate_field_mapping:
        source_local = f"[{candidate.source_field}]"
        target_local = f"[{candidate.target_field}]"
        replacements[source_local] = target_local
        replacements[f":{candidate.source_field}:"] = f":{candidate.target_field}:"
    return replacements


def _replace_in_sections(root: etree._Element, replacements: dict[str, str]) -> None:
    ordered = sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True)
    for section_name in ("worksheets", "dashboards", "windows", "actions"):
        section = root.find(section_name)
        if section is None:
            continue
        for element in section.iter():
            for key, value in list(element.attrib.items()):
                updated = value
                for old, new in ordered:
                    if old in updated:
                        updated = updated.replace(old, new)
                if updated != value:
                    element.set(key, updated)
            if element.text:
                updated_text = element.text
                for old, new in ordered:
                    if old in updated_text:
                        updated_text = updated_text.replace(old, new)
                if updated_text != element.text:
                    element.text = updated_text


def apply_twb_migration(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    preview = preview_twb_migration(
        file_path=file_path,
        target_source=target_source,
        scope=scope,
        mapping_overrides=mapping_overrides,
    )
    if preview.blocking_issue_count:
        raise ValueError(
            f"Cannot apply migration while blocking issues remain ({preview.blocking_issue_count})."
        )

    path = Path(file_path)
    tree = etree.parse(str(path))
    root = tree.getroot()
    replacements = _build_string_replacements(preview)
    _replace_in_sections(root, replacements)

    if output_path is None:
        output_path = path.with_name(f"{path.stem} - migrated.twb")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_path), encoding="utf-8", xml_declaration=True)

    report_path = output_path.with_name("migration_report.json")
    mapping_path = output_path.with_name("field_mapping.json")

    report_payload = preview.to_dict()
    report_payload["output_summary"] = {
        "migrated_twb": _normalize_path(output_path),
        "report_json": _normalize_path(report_path),
        "mapping_json": _normalize_path(mapping_path),
    }
    report_payload["removable_datasources"] = preview.removable_datasources

    mapping_payload = {
        candidate.source_field: candidate.target_field
        for candidate in preview.candidate_field_mapping
    }
    report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    mapping_path.write_text(json.dumps(mapping_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return report_payload


def profile_twb_for_migration_json(
    file_path: str | Path,
    scope: str = "workbook",
    target_source: str | Path | None = None,
) -> str:
    profile = profile_twb_for_migration(file_path=file_path, scope=scope, target_source=target_source)
    return json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)


def propose_field_mapping_json(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
) -> str:
    payload = propose_field_mapping(
        file_path=file_path,
        target_source=target_source,
        scope=scope,
        mapping_overrides=mapping_overrides,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


def preview_twb_migration_json(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
) -> str:
    preview = preview_twb_migration(
        file_path=file_path,
        target_source=target_source,
        scope=scope,
        mapping_overrides=mapping_overrides,
    )
    return json.dumps(preview.to_dict(), ensure_ascii=False, indent=2)


def apply_twb_migration_json(
    file_path: str | Path,
    target_source: str | Path,
    scope: str = "workbook",
    mapping_overrides: dict[str, str] | None = None,
    output_path: str | Path | None = None,
) -> str:
    result = apply_twb_migration(
        file_path=file_path,
        target_source=target_source,
        scope=scope,
        mapping_overrides=mapping_overrides,
        output_path=output_path,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)
