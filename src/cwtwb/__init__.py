"""cwtwb - Tableau Workbook (.twb) Generation MCP Server"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cwtwb")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

from .twb_editor import TWBEditor
from .field_registry import FieldRegistry
from .validator import TWBValidationError

__all__ = ["TWBEditor", "FieldRegistry", "TWBValidationError", "__version__"]
