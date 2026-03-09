"""Advanced chart example with optional Hyper connection switching.

This example stays in the advanced support tier. It demonstrates chart patterns
such as Scatterplot, Heatmap, Tree Map, and Bubble Chart without implying that
recipe-level charts are part of the default SDK promise.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwtwb import TWBEditor


ADVENT_BUNDLE_DIR = (
    Path("templates")
    / "viz"
    / "Tableau Advent Calendar.twb \u4e2a\u6587\u4ef6"
    / "Data"
    / "Tableau Advent Calendar"
)
PREFERRED_HYPER_FILE = "Sample - EU Superstore.hyper"
PREFERRED_HYPER_TABLE = "Extract"


def _find_sample_hyper(project_root: Path) -> tuple[Path, str] | None:
    """Prefer the Advent Calendar Superstore extract over unrelated bundle files."""
    bundle_dir = project_root / ADVENT_BUNDLE_DIR
    if not bundle_dir.exists():
        return None

    preferred = bundle_dir / PREFERRED_HYPER_FILE
    if preferred.exists():
        return preferred, PREFERRED_HYPER_TABLE

    candidates = sorted(bundle_dir.glob("*.hyper"))
    if not candidates:
        return None
    return candidates[0], PREFERRED_HYPER_TABLE


def main():
    project_root = Path(__file__).parent.parent
    template_path = project_root / "templates" / "twb" / "superstore.twb"
    output_path = project_root / "output" / "hyper_and_new_charts.twb"

    print("Initializing Editor...")
    editor = TWBEditor(str(template_path) if template_path.exists() else None)

    hyper_info = _find_sample_hyper(project_root)
    if hyper_info is not None:
        hyper_path, table_name = hyper_info
        print(f"Switching to Hyper extract: {hyper_path.name}")
        editor.set_hyper_connection(str(hyper_path), table_name=table_name)
    else:
        print("Hyper extract not found. Continuing with the template datasource.")

    print("Generating Scatterplot...")
    editor.add_worksheet("Scatterplot Example")
    editor.configure_chart(
        "Scatterplot Example",
        mark_type="Scatterplot",
        columns=["SUM(Sales)"],
        rows=["SUM(Profit)"],
        color="Category",
        detail="Customer Name",
    )

    print("Generating Heatmap...")
    editor.add_worksheet("Heatmap Example")
    editor.configure_chart(
        "Heatmap Example",
        mark_type="Heatmap",
        columns=["Sub-Category"],
        rows=["Region"],
        color="SUM(Sales)",
        label="SUM(Sales)",
    )

    print("Generating Tree Map...")
    editor.add_worksheet("Tree Map Example")
    editor.configure_chart(
        "Tree Map Example",
        mark_type="Tree Map",
        size="SUM(Sales)",
        color="SUM(Profit)",
        label="Sub-Category",
    )

    print("Generating Bubble Chart...")
    editor.add_worksheet("Bubble Chart Example")
    editor.configure_chart(
        "Bubble Chart Example",
        mark_type="Bubble Chart",
        size="SUM(Sales)",
        color="Category",
        label="Category",
    )

    print("Creating Dashboard...")
    editor.add_dashboard(
        dashboard_name="New Advanced Charts Overview",
        worksheet_names=[
            "Scatterplot Example",
            "Heatmap Example",
            "Tree Map Example",
            "Bubble Chart Example",
        ],
        layout="grid-2x2",
    )

    output_path.parent.mkdir(exist_ok=True)
    editor.save(str(output_path))
    print(f"Successfully generated visualization to: {output_path}")
    print("You can open this .twb file with Tableau Desktop to verify the results.")


if __name__ == "__main__":
    main()
