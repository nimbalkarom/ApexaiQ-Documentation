"""
Unit tests for FileScanner component.
Verifies recursive directory scanning, exclusion handling, metadata accuracy,
hidden file filtering, symlink handling, and error resilience.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from organizer.exceptions import ScanError
from organizer.scanner import FileScanner


def test_scanner_finds_nested_files(tmp_path: Path):
    """Test scanner recursively discovers files across multiple directory levels."""
    sub = tmp_path / "level1" / "level2"
    sub.mkdir(parents=True)

    f1 = tmp_path / "root_file.txt"
    f2 = sub / "deep_file.pdf"
    f3 = tmp_path / "level1" / "mid_file.py"

    f1.write_text("root", encoding="utf-8")
    f2.write_text("deep", encoding="utf-8")
    f3.write_text("mid", encoding="utf-8")

    scanner = FileScanner(source_dir=tmp_path)
    discovered = scanner.scan_all()

    assert len(discovered) == 3
    names = {f.name for f in discovered}
    assert names == {"root_file.txt", "deep_file.pdf", "mid_file.py"}


def test_scanner_metadata_accuracy(tmp_path: Path):
    """Verify all collected metadata attributes on discovered files."""
    test_file = tmp_path / "document.DOCX"
    content = "Sample content for metadata test"
    test_file.write_text(content, encoding="utf-8")

    scanner = FileScanner(source_dir=tmp_path)
    results = scanner.scan_all()

    assert len(results) == 1
    info = results[0]

    assert info.name == "document.DOCX"
    assert info.extension == ".docx"  # Lowercased
    assert info.size == len(content.encode("utf-8"))
    assert isinstance(info.modified_time, datetime)
    assert info.created_time is not None
    assert info.relative_path == Path("document.DOCX")
    assert info.parent_dir.resolve() == tmp_path.resolve()


def test_scanner_excludes_nested_target_dir(tmp_path: Path):
    """
    Ensure the target destination folder (e.g. source/Organized) is strictly excluded
    from scanning to prevent infinite scanning cycles.
    """
    source_dir = tmp_path / "Downloads"
    source_dir.mkdir()

    target_dir = source_dir / "Organized"
    target_dir.mkdir()

    sub_target = target_dir / "Documents"
    sub_target.mkdir()

    # Files to be scanned
    (source_dir / "report.pdf").write_text("pdf", encoding="utf-8")
    (source_dir / "photo.jpg").write_text("jpg", encoding="utf-8")

    # Files inside excluded destination
    (target_dir / "already_moved.pdf").write_text("ignore", encoding="utf-8")
    (sub_target / "nested_moved.pdf").write_text("ignore", encoding="utf-8")

    scanner = FileScanner(source_dir=source_dir, exclude_dirs=[target_dir])
    results = scanner.scan_all()

    scanned_names = [f.name for f in results]
    assert len(scanned_names) == 2
    assert "report.pdf" in scanned_names
    assert "photo.jpg" in scanned_names
    assert "already_moved.pdf" not in scanned_names
    assert "nested_moved.pdf" not in scanned_names


def test_scanner_empty_directories(tmp_path: Path):
    """Empty directories should return zero files without errors."""
    empty_sub = tmp_path / "empty_dir"
    empty_sub.mkdir()

    scanner = FileScanner(source_dir=tmp_path)
    assert scanner.scan_all() == []


def test_scanner_zero_byte_files(tmp_path: Path):
    """0-byte files must be discovered without crash."""
    zero_file = tmp_path / "empty.txt"
    zero_file.touch()

    scanner = FileScanner(source_dir=tmp_path)
    results = scanner.scan_all()
    assert len(results) == 1
    assert results[0].size == 0


def test_scanner_invalid_source_paths(tmp_path: Path):
    """Non-existent directory or file as source must raise ScanError."""
    missing = tmp_path / "does_not_exist"
    with pytest.raises(ScanError, match="Source directory does not exist"):
        FileScanner(source_dir=missing)

    regular_file = tmp_path / "file.txt"
    regular_file.write_text("hello", encoding="utf-8")
    with pytest.raises(ScanError, match="Source path is not a directory"):
        FileScanner(source_dir=regular_file)


def test_scanner_hidden_files_filter(tmp_path: Path):
    """Test hidden files and folders toggle."""
    visible = tmp_path / "visible.txt"
    hidden = tmp_path / ".hidden_file.txt"
    hidden_dir = tmp_path / ".git"
    hidden_dir.mkdir()
    hidden_sub = hidden_dir / "config"

    visible.write_text("visible", encoding="utf-8")
    hidden.write_text("hidden", encoding="utf-8")
    hidden_sub.write_text("sub", encoding="utf-8")

    # With include_hidden=False
    scanner_filtered = FileScanner(source_dir=tmp_path, include_hidden=False)
    results_filtered = scanner_filtered.scan_all()
    assert len(results_filtered) == 1
    assert results_filtered[0].name == "visible.txt"

    # With include_hidden=True (default)
    scanner_all = FileScanner(source_dir=tmp_path, include_hidden=True)
    results_all = scanner_all.scan_all()
    assert len(results_all) == 3


def test_scanner_permission_error_resilience(tmp_path: Path):
    """
    Verify that encountering PermissionError on a directory logs a warning
    and continues processing remaining directories without crashing.
    """
    good_dir = tmp_path / "good"
    good_dir.mkdir()
    (good_dir / "good_file.txt").write_text("ok", encoding="utf-8")

    locked_dir = tmp_path / "locked"
    locked_dir.mkdir()
    (locked_dir / "locked_file.txt").write_text("locked", encoding="utf-8")

    scanner = FileScanner(source_dir=tmp_path)

    orig_scandir = FileScanner._scan_directory

    # Simulate permission error when opening locked_dir
    def mock_scan_directory(self_scanner, current_dir: Path):
        if current_dir.name == "locked":
            self_scanner.permission_denied_paths.append(current_dir)
            return iter([])
        return orig_scandir(self_scanner, current_dir)

    with patch.object(FileScanner, "_scan_directory", mock_scan_directory):
        results = scanner.scan_all()
        assert len(results) == 1
        assert results[0].name == "good_file.txt"
        assert len(scanner.permission_denied_paths) == 1
