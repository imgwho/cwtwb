"""MCP tools for workbook validation via Tableau Cloud upload."""

from __future__ import annotations

from pathlib import Path

from .app import server


@server.tool()
def upload_workbook(
    twb_path: str,
    data_path: str | None = None,
    name: str | None = None,
    overwrite: bool = True,
) -> dict:
    """Upload a .twb/.twbx to Tableau Cloud to validate it.

    Upload success means the workbook structure is valid and Tableau Cloud
    can parse it. Use this after saving a generated workbook to verify
    correctness.

    Args:
        twb_path: Path to .twb or .twbx file.
        data_path: Optional data file (.xlsx/.xls/.hyper) to package.
        name: Workbook name on Tableau Cloud (defaults to filename stem).
        overwrite: Whether to overwrite existing workbook with same name.

    Returns:
        {success, workbook_id, workbook_url, views, twbx_path, twbx_size_kb, error}
    """
    from ..validate.uploader import TableauUploader

    uploader = TableauUploader()
    result = uploader.upload(twb_path, data_path, name, overwrite)
    return {
        "success": result.success,
        "workbook_id": result.workbook_id,
        "workbook_url": result.workbook_url,
        "views": result.views,
        "twbx_path": result.twbx_path,
        "twbx_size_kb": round(result.twbx_size_kb, 1),
        "error": result.error,
    }


@server.tool()
def screenshot_workbook(
    workbook_id: str,
    output_dir: str = "output/validation",
    view_index: int = 0,
    view_name: str | None = None,
) -> dict:
    """Screenshot a published workbook's view for human review.

    Use after upload_workbook to capture a visual snapshot. The screenshot
    is saved locally for human inspection.

    Args:
        workbook_id: The workbook ID returned by upload_workbook.
        output_dir: Directory to save screenshot (default: output/validation).
        view_index: Index of the view to screenshot (default: 0).
        view_name: Name of the view to screenshot (overrides view_index).

    Returns:
        {success, path, view_name, view_id, size_kb, error}
    """
    from ..validate.uploader import TableauUploader

    uploader = TableauUploader()
    result = uploader.screenshot(workbook_id, output_dir, view_index, view_name)
    return {
        "success": result.success,
        "path": result.path,
        "view_name": result.view_name,
        "view_id": result.view_id,
        "size_kb": round(result.size_kb, 1),
        "error": result.error,
    }
