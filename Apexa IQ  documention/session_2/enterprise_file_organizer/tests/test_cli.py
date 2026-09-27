"""
Unit and integration tests for CLI interface and end-to-end execution.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from organizer.config_loader import ConfigLoader
from organizer.models import ExecutionReport
from organizer.organizer import FileOrganizer
from main import generate_config, print_summary


def test_generate_config_cli(tmp_path: Path):
    """Verify --generate-config writes valid default JSON config."""
    target_cfg = tmp_path / "generated_rules.json"
    generate_config(target_cfg)

    assert target_cfg.exists()
    loaded = ConfigLoader.load_config(target_cfg)
    assert "categories" in loaded
    assert "rules" in loaded


def test_print_summary_format(capsys, tmp_path: Path):
    """Verify summary table structure and formatting."""
    log_file = tmp_path / "organizer.log"
    report = ExecutionReport(
        total_scanned=10,
        total_organized=8,
        duplicates_found=2,
        skipped=1,
        errors=1,
        category_counts={"Documents": 5, "Images": 3},
        execution_time_seconds=1.23,
    )

    print_summary(report, log_file)
    captured = capsys.readouterr().out

    assert "ORGANIZATION SUMMARY" in captured
    assert "Files scanned       : 10" in captured
    assert "Files organized     : 8" in captured
    assert "Duplicates found    : 2" in captured
    assert "Documents           : 5" in captured
    assert "Images              : 3" in captured
    assert "Execution time      : 1.23 seconds" in captured


def test_end_to_end_organizer_run(tmp_path: Path):
    """
    End-to-end integration test:
    Creates an unorganized folder with invoices, photos, and duplicate files,
    runs FileOrganizer, verifies categorized folder creation and duplicate detection.
    """
    source_dir = tmp_path / "Downloads"
    target_dir = tmp_path / "Organized"
    history_dir = tmp_path / "history"
    source_dir.mkdir()

    # Create test files
    (source_dir / "invoice_100.pdf").write_text("invoice text", encoding="utf-8")
    (source_dir / "photo.jpg").write_text("photo data", encoding="utf-8")
    (source_dir / "photo_duplicate.jpg").write_text("photo data", encoding="utf-8")
    (source_dir / "script.py").write_text("print('hello')", encoding="utf-8")

    # Load default rules
    default_cfg = ConfigLoader.load_default_config()
    rules = ConfigLoader.parse_rules(default_cfg["rules"])
    categories = default_cfg["categories"]

    organizer = FileOrganizer(
        source_dir=source_dir,
        target_dir=target_dir,
        rules=rules,
        custom_categories=categories,
        dry_run=False,
        history_dir=history_dir,
    )

    report = organizer.run()

    assert report.total_scanned == 4
    assert report.total_organized == 4
    assert report.duplicates_found == 1

    # Check organized paths
    assert (target_dir / "Finance" / "Invoices" / "invoice_100.pdf").exists()
    assert (target_dir / "Images" / "photo.jpg").exists()
    assert (target_dir / "Code" / "script.py").exists()

    # Check history journal was written
    history_files = list(history_dir.glob("history_*.jsonl"))
    assert len(history_files) == 1
