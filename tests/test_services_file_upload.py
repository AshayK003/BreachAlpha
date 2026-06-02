"""Tests for services/file_upload.py — file upload validation and handling."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

from breachalpha.services.file_upload import (
    validate_upload_extension,
    cleanup_upload,
)
from breachalpha.core.constants import ALLOWED_UPLOAD_EXTENSIONS
from breachalpha.core.exceptions import UnsupportedFileTypeError


class TestValidateUploadExtension:
    def test_csv_accepted(self):
        assert validate_upload_extension("data.csv") == ".csv"

    def test_xlsx_accepted(self):
        assert validate_upload_extension("data.xlsx") == ".xlsx"

    def test_xls_accepted(self):
        assert validate_upload_extension("data.xls") == ".xls"

    def test_tsv_accepted(self):
        assert validate_upload_extension("data.tsv") == ".tsv"

    def test_json_rejected(self):
        with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
            validate_upload_extension("data.json")

    def test_exe_rejected(self):
        with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
            validate_upload_extension("malware.exe")

    def test_none_filename(self):
        with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
            validate_upload_extension(None)

    def test_empty_string(self):
        with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
            validate_upload_extension("")

    def test_no_extension(self):
        with pytest.raises(UnsupportedFileTypeError, match="Unsupported file type"):
            validate_upload_extension("README")

    def test_case_insensitive(self):
        assert validate_upload_extension("DATA.CSV") == ".csv"
        assert validate_upload_extension("Data.XLSX") == ".xlsx"


class TestCleanupUpload:
    def test_cleanup_removes_file(self, tmp_path):
        f = tmp_path / "test.csv"
        f.write_text("data")
        assert f.exists()
        cleanup_upload(f)
        assert not f.exists()

    def test_cleanup_none_is_safe(self):
        cleanup_upload(None)

    def test_cleanup_nonexistent_is_safe(self, tmp_path):
        cleanup_upload(tmp_path / "nonexistent.csv")
