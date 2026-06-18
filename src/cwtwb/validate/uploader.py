"""Upload .twb to Tableau Cloud for validation, with optional screenshot."""

from __future__ import annotations

import os
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UploadResult:
    """Result of uploading a workbook to Tableau Cloud."""

    success: bool
    workbook_id: str | None = None
    workbook_url: str | None = None
    views: list[str] = field(default_factory=list)
    twbx_path: str | None = None
    twbx_size_kb: float = 0.0
    error: str | None = None


@dataclass
class ScreenshotResult:
    """Result of screenshotting a published workbook view."""

    success: bool
    path: str | None = None
    view_name: str | None = None
    view_id: str | None = None
    size_kb: float = 0.0
    error: str | None = None


def _load_dotenv(env_path: Path) -> dict[str, str]:
    """Load a .env file into a dict without overriding existing env vars."""
    result: dict[str, str] = {}
    if not env_path.exists():
        return result
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                result[key] = value
    return result


def _get_config() -> dict[str, str]:
    """Load Tableau config from env vars, falling back to .env file.

    Priority: env vars > project .env > home .env
    """
    from ..config import PROJECT_ROOT

    env_file = PROJECT_ROOT / ".env"
    dotenv = _load_dotenv(env_file)

    def _get(key: str, default: str = "") -> str:
        return os.environ.get(key) or dotenv.get(key, default)

    return {
        "server": _get("TABLEAU_SERVER", "https://10ax.online.tableau.com"),
        "site": _get("TABLEAU_SITE", ""),
        "pat_name": _get("TABLEAU_PAT_NAME", ""),
        "pat_secret": _get("TABLEAU_PAT_SECRET", ""),
        "project_id": _get("TABLEAU_PROJECT_ID", ""),
    }


def _package_twbx(
    twb_path: Path,
    data_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Package .twb + optional data file into .twbx (ZIP archive)."""
    assert twb_path.exists(), f"TWB not found: {twb_path}"

    with open(twb_path, "r", encoding="utf-8") as f:
        twb_content = f.read()

    data_filename = None
    if data_path:
        assert data_path.exists(), f"Data file not found: {data_path}"
        data_filename = data_path.name

        # Rewrite absolute paths to relative filename
        twb_content = twb_content.replace(data_path.as_posix(), data_filename)
        twb_content = twb_content.replace(str(data_path.resolve()), data_filename)

    if output_path:
        twbx_path = Path(output_path)
        twbx_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        twbx_path = twb_path.with_suffix(".twbx")

    with zipfile.ZipFile(twbx_path, "w", zipfile.ZIP_DEFLATED) as zf:
        twb_name = twb_path.stem + ".twb"
        zf.writestr(twb_name, twb_content.encode("utf-8"))
        if data_path:
            zf.write(data_path, arcname=data_filename)

    return twbx_path


class TableauUploader:
    """Upload .twb to Tableau Cloud for validation, with optional screenshot."""

    def __init__(
        self,
        server: str | None = None,
        site: str | None = None,
        pat_name: str | None = None,
        pat_secret: str | None = None,
        project_id: str | None = None,
    ) -> None:
        cfg = _get_config()
        self.server_url = server or cfg["server"]
        self.site = site or cfg["site"]
        self.pat_name = pat_name or cfg["pat_name"]
        self.pat_secret = pat_secret or cfg["pat_secret"]
        self.project_id = project_id or cfg["project_id"]
        self._server = None
        self._auth = None
        self._is_signed_in = False

    def _ensure_client(self):
        """Lazy import and init of tableauserverclient."""
        if self._server is not None:
            return
        try:
            import tableauserverclient as TSC
        except ImportError:
            raise ImportError(
                "tableauserverclient is required for validation. "
                "Install it with: pip install 'cwtwb[validate]'"
            )
        self._TSC = TSC
        self._server = TSC.Server(self.server_url, use_server_version=True)
        self._server.add_http_options({"verify": False})
        self._auth = TSC.PersonalAccessTokenAuth(
            self.pat_name, self.pat_secret, self.site
        )

    def _check_config(self) -> str | None:
        """Return error message if config is incomplete, else None."""
        if not self.pat_secret:
            return (
                "Tableau PAT not configured. "
                "Create .env from .env.example and fill in your credentials, "
                "or set TABLEAU_PAT_SECRET environment variable."
            )
        if not self.pat_name:
            return "TABLEAU_PAT_NAME is not set."
        if not self.project_id:
            return "TABLEAU_PROJECT_ID is not set."
        return None

    def sign_in(self):
        """Authenticate with Tableau Cloud."""
        self._ensure_client()
        if not self._is_signed_in:
            self._server.auth.sign_in(self._auth)
            self._is_signed_in = True

    def sign_out(self):
        """Sign out from Tableau Cloud."""
        if self._is_signed_in and self._server:
            self._server.auth.sign_out()
            self._is_signed_in = False

    def upload(
        self,
        twb_path: str | Path,
        data_path: str | Path | None = None,
        name: str | None = None,
        overwrite: bool = True,
    ) -> UploadResult:
        """Package .twbx and upload to Tableau Cloud.

        Upload success = workbook structure is valid.
        """
        err = self._check_config()
        if err:
            return UploadResult(success=False, error=err)

        try:
            twb_path = Path(twb_path)
            data_path = Path(data_path) if data_path else None

            # Package
            if twb_path.suffix.lower() == ".twbx":
                twbx_path = twb_path
            else:
                twbx_path = _package_twbx(twb_path, data_path)

            # Upload
            self.sign_in()
            TSC = self._TSC
            wb_name = name or twb_path.stem

            new_workbook = TSC.WorkbookItem(
                name=wb_name, project_id=self.project_id
            )
            mode = (
                TSC.Server.PublishMode.Overwrite
                if overwrite
                else TSC.Server.PublishMode.CreateNew
            )
            published = self._server.workbooks.publish(
                new_workbook, str(twbx_path), mode
            )
            self._server.workbooks.populate_views(published)

            return UploadResult(
                success=True,
                workbook_id=published.id,
                workbook_url=f"{self.server_url}/#/site/{self.site}/workbooks/{published.id}",
                views=[v.name for v in published.views],
                twbx_path=str(twbx_path),
                twbx_size_kb=twbx_path.stat().st_size / 1024,
            )
        except Exception as e:
            return UploadResult(success=False, error=str(e))
        finally:
            self.sign_out()

    def screenshot(
        self,
        workbook_id: str,
        output_dir: str | Path = "output/validation",
        view_index: int = 0,
        view_name: str | None = None,
        resolution: str = "high",
    ) -> ScreenshotResult:
        """Screenshot a published workbook view. Requires prior upload."""
        err = self._check_config()
        if err:
            return ScreenshotResult(success=False, error=err)

        try:
            self.sign_in()
            TSC = self._TSC

            wb = self._server.workbooks.get_by_id(workbook_id)
            self._server.workbooks.populate_views(wb)

            if not wb.views:
                return ScreenshotResult(
                    success=False, error=f"No views found for workbook {workbook_id}"
                )

            target = None
            if view_name:
                for v in wb.views:
                    if v.name.lower() == view_name.lower():
                        target = v
                        break
                if not target:
                    available = [v.name for v in wb.views]
                    return ScreenshotResult(
                        success=False,
                        error=f"View '{view_name}' not found. Available: {available}",
                    )
            else:
                if view_index >= len(wb.views):
                    return ScreenshotResult(
                        success=False,
                        error=f"view_index={view_index} out of range (total: {len(wb.views)})",
                    )
                target = wb.views[view_index]

            image_req = TSC.ImageRequestOptions(imageresolution=resolution)
            self._server.views.populate_image(target, image_req)

            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            safe_name = target.name.replace(" ", "_")
            filename = f"{wb.name}_{safe_name}.png"
            out_path = out_dir / filename

            with open(out_path, "wb") as f:
                f.write(target.image)

            return ScreenshotResult(
                success=True,
                path=str(out_path),
                view_name=target.name,
                view_id=target.id,
                size_kb=out_path.stat().st_size / 1024,
            )
        except Exception as e:
            return ScreenshotResult(success=False, error=str(e))
        finally:
            self.sign_out()

    def __enter__(self):
        self.sign_in()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sign_out()
