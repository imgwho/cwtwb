"""Shared configuration constants for cwtwb.

This module provides path constants and configuration used across
the cwtwb package. Extracted to avoid circular imports between
twb_editor.py and server.py.
"""

from pathlib import Path
import uuid


def _generate_uuid() -> str:
    """Generate an uppercase UUID string: {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}."""
    return "{" + str(uuid.uuid4()).upper() + "}"

# Directory containing reference files (templates, XLS data, function definitions)
REFERENCES_DIR = Path(__file__).parent / "references"

# Path to the default Superstore template
DEFAULT_TEMPLATE = REFERENCES_DIR / "empty_template.twb"

# Path to the Tableau functions JSON
TABLEAU_FUNCTIONS_JSON = REFERENCES_DIR / "tableau_all_functions.json"
