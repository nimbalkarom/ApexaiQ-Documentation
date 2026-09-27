"""
Unit tests for RollbackManager component.
Verifies LIFO transaction reversal, conflict avoidance, missing file handling,
dry-run previewing, and error reporting.
"""

import json
from pathlib import Path
import pytest

from organizer.exceptions import RollbackError
from organizer.models import OperationRecord
from organizer.rollback import RollbackManager


def test_rollback_reverses_movement(tmp_path: Path):
    """Test standard single file rollback reverses file to original position."""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    src = tmp_path / "Downloads" / "report.pdf"
    dest = tmp_path / "Organized" / "Documents" / "report.pdf"

    dest.parent.mkdir(parents=True)
    dest.write_text("report content", encoding="utf-8")

    rec = OperationRecord(
        source=str(src),
        destination=str(dest),
        timestamp="2026-09-21T00:00:00",
        operation="move",
        status="success",
    )

    journal = history_dir / "history_20260921_000000.jsonl"
    journal.write_text(json.dumps(rec.to_dict()) + "\n", encoding="utf-8")

    manager = RollbackManager(history_dir)
    results = manager.execute_rollback(journal)

    assert len(results) == 1
    assert results[0].status == "success"
    assert src.exists()
    assert not dest.exists()
    assert src.read_text(encoding="utf-8") == "report content"


def test_rollback_lifo_order(tmp_path: Path):
    """Verify operations are reversed in strict LIFO (Last-In, First-Out) order."""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    src1 = tmp_path / "src1.txt"
    dest1 = tmp_path / "dest1.txt"
    src2 = tmp_path / "src2.txt"
    dest2 = tmp_path / "dest2.txt"

    dest1.write_text("data 1", encoding="utf-8")
    dest2.write_text("data 2", encoding="utf-8")

    journal = history_dir / "history_20260921_120000.jsonl"
    with open(journal, "w", encoding="utf-8") as f:
        f.write(json.dumps(OperationRecord(source=str(src1), destination=str(dest1), timestamp="t1").to_dict()) + "\n")
        f.write(json.dumps(OperationRecord(source=str(src2), destination=str(dest2), timestamp="t2").to_dict()) + "\n")

    manager = RollbackManager(history_dir)
    results = manager.execute_rollback(journal)

    # First reversed should be operation 2 (dest2 -> src2)
    assert len(results) == 2
    assert Path(results[0].destination) == src2
    assert Path(results[1].destination) == src1
    assert src1.exists()
    assert src2.exists()


def test_rollback_dry_run(tmp_path: Path):
    """Dry run rollback must not modify filesystem."""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    src = tmp_path / "orig.txt"
    dest = tmp_path / "organized.txt"
    dest.write_text("content", encoding="utf-8")

    journal = history_dir / "history_20260921_130000.jsonl"
    journal.write_text(
        json.dumps(OperationRecord(source=str(src), destination=str(dest), timestamp="t").to_dict()) + "\n",
        encoding="utf-8",
    )

    manager = RollbackManager(history_dir)
    results = manager.execute_rollback(journal, dry_run=True)

    assert len(results) == 1
    assert results[0].status == "preview"
    assert dest.exists()
    assert not src.exists()


def test_rollback_safeguards_occupied_original(tmp_path: Path):
    """If original position is occupied, rollback must skip to prevent overwriting."""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    src = tmp_path / "file.txt"
    dest = tmp_path / "organized_file.txt"

    dest.write_text("new content", encoding="utf-8")
    src.write_text("original position occupied by another file", encoding="utf-8")

    journal = history_dir / "history_20260921_140000.jsonl"
    journal.write_text(
        json.dumps(OperationRecord(source=str(src), destination=str(dest), timestamp="t").to_dict()) + "\n",
        encoding="utf-8",
    )

    manager = RollbackManager(history_dir)
    results = manager.execute_rollback(journal)

    assert len(results) == 1
    assert results[0].status == "skipped_conflict"
    assert dest.exists()
    assert src.read_text(encoding="utf-8") == "original position occupied by another file"


def test_rollback_missing_destination(tmp_path: Path):
    """If destination file was deleted or moved manually, rollback handles gracefully."""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    src = tmp_path / "file.txt"
    dest = tmp_path / "missing_at_dest.txt"  # Does not exist

    journal = history_dir / "history_20260921_150000.jsonl"
    journal.write_text(
        json.dumps(OperationRecord(source=str(src), destination=str(dest), timestamp="t").to_dict()) + "\n",
        encoding="utf-8",
    )

    manager = RollbackManager(history_dir)
    results = manager.execute_rollback(journal)

    assert len(results) == 1
    assert results[0].status == "skipped_missing"


def test_rollback_no_history_error(tmp_path: Path):
    """Empty history directory must raise RollbackError."""
    history_dir = tmp_path / "empty_history"
    manager = RollbackManager(history_dir)
    with pytest.raises(RollbackError, match="No operation history"):
        manager.execute_rollback()


def test_rollback_format_summary():
    """Verify rollback summary formatting."""
    records = [
        OperationRecord(source="s", destination="d", timestamp="t", status="success"),
        OperationRecord(source="s2", destination="d2", timestamp="t", status="skipped_conflict"),
    ]
    summary = RollbackManager.format_summary(records)
    assert "ROLLBACK SUMMARY" in summary
    assert "Successfully reversed       : 1" in summary
    assert "Skipped (conflict safe-skip): 1" in summary
