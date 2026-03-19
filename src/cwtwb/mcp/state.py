"""Mutable workbook state for the MCP server — single active editor singleton.

The MCP server is stateful: it holds one TWBEditor instance at a time.
All tools that need to read or mutate the workbook call get_editor(), which
raises RuntimeError if no workbook has been opened yet.

State transitions:
  (none)  →  set_editor(editor)   [create_workbook / open_workbook]
          →  get_editor()         [any subsequent tool call]
          →  set_editor(editor)   [create_workbook / open_workbook again resets]

There is no "close workbook" operation — saving the file is the final step.
The state is process-local and resets when the MCP server process restarts.
"""

from __future__ import annotations

from typing import Optional

from ..twb_editor import TWBEditor

_editor: Optional[TWBEditor] = None


def get_editor() -> TWBEditor:
    """Get the current editor instance, raising if none exists."""

    if _editor is None:
        raise RuntimeError("No active workbook. Call create_workbook or open_workbook first.")
    return _editor


def set_editor(editor: TWBEditor) -> None:
    """Replace the current editor instance."""

    global _editor
    _editor = editor
