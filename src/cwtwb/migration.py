"""Workbook migration helpers for reusing TWB templates with a new datasource."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
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
    source_excel_profile: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ColumnProfile:
    field: str
    index: int
    kind: str
    pattern: str
    blank_ratio: float
    distinct_ratio: float
    sample_values: list[str]

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


def _strip_table_brackets(table_name: str | None) -> str | None:
    if not table_name:
        return None
    cleaned = table_name.strip()
    cleaned = cleaned.replace("[", "").replace("]", "")
    if "." in cleaned:
        cleaned = cleaned.split(".")[-1]
    if cleaned.endswith("$"):
        cleaned = cleaned[:-1]
    return cleaned or None


def _find_excel_connection_filename(datasource: etree._Element) -> str | None:
    connection = datasource.find(".//connection[@class='excel-direct']")
    if connection is None:
        return None
    filename = connection.get("filename")
    if not filename:
        return None
    return filename.replace("\\", "/")


def _find_relation_sheet_name(datasource: etree._Element) -> str | None:
    relation = datasource.find(".//relation")
    if relation is None:
        return None
    return _strip_table_brackets(relation.get("table") or relation.get("name"))


def _open_excel_sheet(path: str | Path, sheet_name: str | None = None):
    workbook = xlrd.open_workbook(_normalize_path(path))
    if sheet_name:
        for worksheet in workbook.sheets():
            if worksheet.name == sheet_name:
                return workbook, worksheet
    return workbook, workbook.sheet_by_index(0)


def _infer_value_kind(values: list[Any]) -> str:
    non_blank = [value for value in values if value not in ("", None)]
    if not non_blank:
        return "empty"
    if all(isinstance(value, (int, float)) for value in non_blank):
        numeric = [float(value) for value in non_blank]
        if all(value.is_integer() for value in numeric):
            if numeric and min(numeric) >= 30000 and max(numeric) <= 60000:
                return "date_serial"
            return "integer"
        return "real"
    return "text"


def _infer_value_pattern(kind: str, values: list[Any], distinct_ratio: float, blank_ratio: float) -> str:
    if blank_ratio >= 0.8:
        return "blank-heavy"
    non_blank = [value for value in values if value not in ("", None)]
    if kind == "date_serial":
        return "date"
    if kind == "integer":
        numeric = [float(value) for value in non_blank]
        if numeric and distinct_ratio >= 0.95 and numeric == sorted(numeric):
            return "integer-counter"
        if numeric and min(numeric) >= 0 and max(numeric) <= 20:
            return "small-integer"
        return "integer"
    if kind == "real":
        numeric = [float(value) for value in non_blank]
        if numeric and min(numeric) >= 0 and max(numeric) <= 1.0:
            return "fraction"
        if any(value < 0 for value in numeric):
            return "signed-measure"
        return "positive-measure"
    if kind == "text":
        text_values = [str(value).strip() for value in non_blank]
        if text_values and all(any(ch.isdigit() for ch in value) for value in text_values[: min(10, len(text_values))]):
            return "id-code"
        if distinct_ratio <= 0.1:
            return "text-low-cardinality"
        if distinct_ratio >= 0.9:
            return "text-high-cardinality"
        return "text"
    return kind


def _build_column_profiles(headers: list[str], rows: list[list[Any]], max_samples: int = 50) -> dict[str, ColumnProfile]:
    profiles: dict[str, ColumnProfile] = {}
    if not headers:
        return profiles
    sample_rows = rows[:max_samples]
    row_count = max(len(sample_rows), 1)
    for index, field in enumerate(headers):
        values = [row[index] if index < len(row) else "" for row in sample_rows]
        non_blank = [value for value in values if value not in ("", None)]
        distinct_ratio = len({str(value) for value in non_blank}) / max(len(non_blank), 1)
        blank_ratio = 1 - (len(non_blank) / row_count)
        kind = _infer_value_kind(values)
        pattern = _infer_value_pattern(kind, values, distinct_ratio, blank_ratio)
        sample_values = [str(value) for value in non_blank[:5]]
        profiles[field] = ColumnProfile(
            field=field,
            index=index,
            kind=kind,
            pattern=pattern,
            blank_ratio=round(blank_ratio, 4),
            distinct_ratio=round(distinct_ratio, 4),
            sample_values=sample_values,
        )
    return profiles


def _read_excel_profiles(path: str | Path, sheet_name: str | None = None) -> dict[str, Any]:
    workbook, sheet = _open_excel_sheet(path, sheet_name)
    headers = [str(value).strip() for value in sheet.row_values(0) if str(value).strip()]
    rows = [sheet.row_values(row_index) for row_index in range(1, min(sheet.nrows, 151))]
    profiles = _build_column_profiles(headers, rows)
    return {
        "path": _normalize_path(path),
        "sheet_name": sheet.name,
        "headers": headers,
        "row_count": max(sheet.nrows - 1, 0),
        "profiles": {field: profile.to_dict() for field, profile in profiles.items()},
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
    info = _read_excel_profiles(target_source)
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

    source_fields = list(_get_datasource_fields(source_datasource).keys())
    source_excel_profile = None
    source_excel_filename = _find_excel_connection_filename(source_datasource)
    if source_excel_filename:
        source_excel_profile = _read_excel_profiles(
            source_excel_filename,
            _find_relation_sheet_name(source_datasource),
        )

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
        source_schema=source_fields,
        source_excel_profile=source_excel_profile,
    )


def _profile_from_dict(field: str, payload: dict[str, Any]) -> ColumnProfile:
    return ColumnProfile(
        field=field,
        index=int(payload["index"]),
        kind=str(payload["kind"]),
        pattern=str(payload["pattern"]),
        blank_ratio=float(payload["blank_ratio"]),
        distinct_ratio=float(payload["distinct_ratio"]),
        sample_values=list(payload.get("sample_values", [])),
    )


def _score_field_match(source_field: str, target_field: str, source_profile: ColumnProfile, target_profile: ColumnProfile) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if source_field == target_field:
        score += 1.0
        reasons.append("exact field name match")
    else:
        normalized_source = _normalize_field_name(source_field)
        normalized_target = _normalize_field_name(target_field)
        if normalized_source == normalized_target:
            score += 0.92
            reasons.append("normalized field name match")
        else:
            alias_group = _ALIAS_LOOKUP.get(normalized_source)
            if alias_group and normalized_target in {_normalize_field_name(alias) for alias in alias_group}:
                score += 1.15
                reasons.append("alias hint match")

    if source_profile.kind == target_profile.kind:
        score += 0.28
        reasons.append(f"same kind: {source_profile.kind}")

    if source_profile.pattern == target_profile.pattern:
        score += 0.24
        reasons.append(f"same pattern: {source_profile.pattern}")

    distinct_gap = abs(source_profile.distinct_ratio - target_profile.distinct_ratio)
    if distinct_gap <= 0.2:
        score += 0.12 * (1 - (distinct_gap / 0.2))
        reasons.append("similar distinct ratio")

    blank_gap = abs(source_profile.blank_ratio - target_profile.blank_ratio)
    if blank_gap <= 0.2:
        score += 0.08 * (1 - (blank_gap / 0.2))
        reasons.append("similar blank ratio")

    position_gap = abs(source_profile.index - target_profile.index)
    if position_gap == 0:
        score += 0.14
        reasons.append("same column position")
    elif position_gap == 1:
        score += 0.08
        reasons.append("adjacent column position")

    confidence = round(min(score / 1.78, 1.0), 3)
    return confidence, reasons


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
    source_profiles_payload = (profile.source_excel_profile or {}).get("profiles", {})
    target_profiles_payload = target_schema.get("profiles", {})

    source_profiles = {
        field: _profile_from_dict(field, payload)
        for field, payload in source_profiles_payload.items()
        if field in profile.source_schema
    }
    target_profiles = {
        field: _profile_from_dict(field, payload)
        for field, payload in target_profiles_payload.items()
    }

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

        source_profile = source_profiles.get(source_field)
        ranked: list[tuple[float, str, list[str]]] = []
        if source_profile is not None:
            for target_field in target_fields:
                target_profile = target_profiles.get(target_field)
                if target_profile is None:
                    continue
                confidence, reasons = _score_field_match(
                    source_field,
                    target_field,
                    source_profile,
                    target_profile,
                )
                ranked.append((confidence, target_field, reasons))
        ranked.sort(key=lambda item: (-item[0], item[1]))

        if ranked and ranked[0][0] >= 0.6 and (len(ranked) == 1 or ranked[0][0] - ranked[1][0] >= 0.08):
            best_confidence, best_target, best_reasons = ranked[0]
            candidates.append(
                MappingCandidate(
                    source_field=source_field,
                    target_field=best_target,
                    confidence=best_confidence,
                    reason=", ".join(best_reasons[:3]) or "profile similarity match",
                )
            )
        elif ranked and ranked[0][0] >= 0.6:
            issues.append(
                MigrationIssue(
                    issue_type="ambiguous",
                    severity="blocking",
                    message=(
                        f"Source field '{source_field}' has multiple close target matches: "
                        f"{ranked[0][1]} ({ranked[0][0]}), {ranked[1][1]} ({ranked[1][0]})."
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
        "source_excel_profile": profile.source_excel_profile,
        "target_excel_profile": {
            "path": target_schema["path"],
            "sheet_name": target_schema["sheet_name"],
            "row_count": target_schema["row_count"],
        },
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
