"""Tests for cwtwb.validate.uploader."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cwtwb.validate.uploader import (
    TableauUploader,
    UploadResult,
    ScreenshotResult,
    _load_dotenv,
    _package_twbx,
)


class TestLoadDotenv:
    """Tests for _load_dotenv helper."""

    def test_loads_valid_env(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TABLEAU_SERVER=https://example.com\n"
            "TABLEAU_PAT_SECRET=abc123\n"
            "# comment line\n"
            "\n"
            "TABLEAU_SITE=my-site\n"
        )
        result = _load_dotenv(env_file)
        assert result == {
            "TABLEAU_SERVER": "https://example.com",
            "TABLEAU_PAT_SECRET": "abc123",
            "TABLEAU_SITE": "my-site",
        }

    def test_missing_file_returns_empty(self, tmp_path):
        result = _load_dotenv(tmp_path / "nonexistent.env")
        assert result == {}

    def test_does_not_override_env_vars(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TABLEAU_SERVER", "https://override.com")
        env_file = tmp_path / ".env"
        env_file.write_text("TABLEAU_SERVER=https://default.com\n")
        result = _load_dotenv(env_file)
        # Should not include key that's already in env
        assert "TABLEAU_SERVER" not in result


class TestPackageTwbx:
    """Tests for _package_twbx helper."""

    def test_packages_twb_only(self, tmp_path):
        twb = tmp_path / "test.twb"
        twb.write_text(
            '<?xml version="1.0"?><workbook><datasources>'
            '<datasource><connection class="excel-direct" filename="data.xlsx" />'
            "</datasource></datasources></workbook>"
        )
        out = tmp_path / "out.twbx"
        result = _package_twbx(twb, output_path=out)
        assert result == out
        assert out.exists()

    def test_packages_twb_with_data(self, tmp_path):
        twb = tmp_path / "test.twb"
        twb.write_text(
            '<?xml version="1.0"?><workbook><datasources>'
            '<datasource><connection class="excel-direct" filename="data.xlsx" />'
            "</datasource></datasources></workbook>"
        )
        data = tmp_path / "data.xlsx"
        data.write_bytes(b"fake excel content")
        out = tmp_path / "out.twbx"
        result = _package_twbx(twb, data, out)
        assert result == out
        assert out.exists()

    def test_raises_on_missing_twb(self, tmp_path):
        with pytest.raises(AssertionError, match="TWB not found"):
            _package_twbx(tmp_path / "nonexistent.twb")

    def test_raises_on_missing_data(self, tmp_path):
        twb = tmp_path / "test.twb"
        twb.write_text("<workbook/>")
        with pytest.raises(AssertionError, match="Data file not found"):
            _package_twbx(twb, tmp_path / "missing.xlsx")


class TestTableauUploader:
    """Tests for TableauUploader class."""

    def test_check_config_missing_pat(self, monkeypatch):
        # Mock _get_config to return empty values
        monkeypatch.setattr(
            "cwtwb.validate.uploader._get_config",
            lambda: {"server": "", "site": "", "pat_name": "", "pat_secret": "", "project_id": ""}
        )
        uploader = TableauUploader(pat_secret="", pat_name="", project_id="")
        err = uploader._check_config()
        assert err is not None
        assert "PAT" in err

    def test_check_config_missing_project_id(self, monkeypatch):
        monkeypatch.setattr(
            "cwtwb.validate.uploader._get_config",
            lambda: {"server": "", "site": "", "pat_name": "name", "pat_secret": "secret", "project_id": ""}
        )
        uploader = TableauUploader(
            pat_secret="secret", pat_name="name", project_id=""
        )
        err = uploader._check_config()
        assert err is not None
        assert "PROJECT_ID" in err

    def test_check_config_valid(self):
        uploader = TableauUploader(
            pat_secret="secret", pat_name="name", project_id="proj-id"
        )
        err = uploader._check_config()
        assert err is None

    def test_upload_returns_error_when_not_configured(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "cwtwb.validate.uploader._get_config",
            lambda: {"server": "", "site": "", "pat_name": "", "pat_secret": "", "project_id": ""}
        )
        # Create a minimal .twb so it passes the file check
        twb = tmp_path / "test.twb"
        twb.write_text("<workbook/>")
        uploader = TableauUploader(pat_secret="")
        result = uploader.upload(str(twb))
        assert result.success is False
        assert result.error is not None
        assert "PAT" in result.error

    def test_screenshot_returns_error_when_not_configured(self, monkeypatch):
        monkeypatch.setattr(
            "cwtwb.validate.uploader._get_config",
            lambda: {"server": "", "site": "", "pat_name": "", "pat_secret": "", "project_id": ""}
        )
        uploader = TableauUploader(pat_secret="")
        result = uploader.screenshot("fake-id")
        assert result.success is False
        assert result.error is not None


class TestDataclasses:
    """Test result dataclasses have expected fields."""

    def test_upload_result_fields(self):
        r = UploadResult(success=True, workbook_id="abc", views=["Sheet 1"])
        assert r.success is True
        assert r.workbook_id == "abc"
        assert r.views == ["Sheet 1"]
        assert r.error is None

    def test_screenshot_result_fields(self):
        r = ScreenshotResult(success=True, path="/tmp/img.png", view_name="Sheet 1")
        assert r.success is True
        assert r.path == "/tmp/img.png"
        assert r.view_name == "Sheet 1"
        assert r.error is None
