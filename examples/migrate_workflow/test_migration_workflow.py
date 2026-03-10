from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from cwtwb import migrate_twb_guided  # noqa: E402


EXAMPLE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = EXAMPLE_DIR / "5 KPI Design Ideas (2).twb"
TARGET_SOURCE = next(path for path in EXAMPLE_DIR.glob("*.xls") if "Superstore" not in path.name)
OUTPUT_PATH = EXAMPLE_DIR / "5 KPI Design Ideas (2) - migrated to target.twb"


def _approve_warning_bundle(payload: dict) -> dict[str, str]:
    bundle = payload.get("warning_review_bundle", {})
    return {
        item["source_field"]: item["suggested_target_field"]
        for item in bundle.get("fields_requiring_review", [])
    }


def run_example() -> dict:
    result = migrate_twb_guided(
        TEMPLATE_PATH,
        TARGET_SOURCE,
        output_path=OUTPUT_PATH,
    )
    if result["workflow_status"] == "needs_review":
        result = migrate_twb_guided(
            TEMPLATE_PATH,
            TARGET_SOURCE,
            output_path=OUTPUT_PATH,
            mapping_overrides=_approve_warning_bundle(result),
        )

    assert result["workflow_status"] == "applied"
    assert result["blocking_issue_count"] == 0

    root = ET.parse(OUTPUT_PATH).getroot()
    dashboard = root.find(".//dashboards/dashboard[@name='KPI Board']")
    assert dashboard is not None

    target_filename = str(TARGET_SOURCE.resolve()).replace("\\", "/")
    filenames = {
        conn.get("filename")
        for conn in root.findall(".//connection[@class='excel-direct']")
        if conn.get("filename")
    }
    assert target_filename in filenames
    return result


if __name__ == "__main__":
    payload = run_example()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\nMigrated workbook: {OUTPUT_PATH}")
