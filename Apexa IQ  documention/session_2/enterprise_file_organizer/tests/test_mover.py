"""
Unit tests for SafeMover component, conflict handling, and dry-run previewing.
"""

from datetime import datetime
from pathlib import Path
import pytest

from organizer.exceptions import SecurityError
from organizer.models import ConflictStrategy, FileInfo
from organizer.mover import SafeMover


def test_safe_mover_collision_rename(tmp_path: Path):
    """
    If a file exists at the destination with different content,
    it must NOT be overwritten. It should be renamed to name_1.ext.
    """
    target_root = tmp_path / "Organized"
    mover = SafeMover(target_root=target_root, conflict_strategy=ConflictStrategy.RENAME_AUTO)

    source_file = tmp_path / "report.pdf"
    source_file.write_text("content source 1", encoding="utf-8")

    # Simulate an existing different file at destination
    dest_dir = target_root / "Documents"
    dest_dir.mkdir(parents=True)
    existing_dest = dest_dir / "report.pdf"
    existing_dest.write_text("existing different content", encoding="utf-8")

    info = FileInfo(
        path=source_file,
        name=source_file.name,
        extension=".pdf",
        size=source_file.stat().st_size,
        modified_time=datetime.now(),
    )

    resolved, status = mover.resolve_destination(info, "Documents")
    assert status == "renamed"
    assert resolved.name == "report_1.pdf"

    record = mover.move_file(info, resolved, status)
    assert record.status == "success"
    assert resolved.exists()
    assert existing_dest.exists()  # Existing file preserved
    assert existing_dest.read_text(encoding="utf-8") == "existing different content"


def test_safe_mover_collision_identical_content(tmp_path: Path):
    """
    If a file exists at the destination with identical content (hash match),
    it should detect identical content and skip redundant movement.
    """
    target_root = tmp_path / "Organized"
    mover = SafeMover(target_root=target_root, conflict_strategy=ConflictStrategy.OVERWRITE_IDENTICAL)

    content = "Identical content across files"
    source_file = tmp_path / "document.pdf"
    source_file.write_text(content, encoding="utf-8")

    dest_dir = target_root / "Documents"
    dest_dir.mkdir(parents=True)
    existing_dest = dest_dir / "document.pdf"
    existing_dest.write_text(content, encoding="utf-8")

    info = FileInfo(
        path=source_file,
        name=source_file.name,
        extension=".pdf",
        size=source_file.stat().st_size,
        modified_time=datetime.now(),
    )

    resolved, status = mover.resolve_destination(info, "Documents")
    assert status == "identical_content"

    record = mover.move_file(info, resolved, status)
    assert record.status == "identical_skipped"
    assert source_file.exists()  # Source left untouched


def test_safe_mover_dry_run_preview(tmp_path: Path):
    """In dry-run mode, mover should not touch disk, and preview format should be valid."""
    target_root = tmp_path / "Organized"
    mover = SafeMover(target_root=target_root, dry_run=True)

    src = tmp_path / "image.png"
    src.write_text("png data", encoding="utf-8")

    info = FileInfo(
        path=src,
        name=src.name,
        extension=".png",
        size=src.stat().st_size,
        modified_time=datetime.now(),
    )

    resolved, status = mover.resolve_destination(info, "Images")
    record = mover.move_file(info, resolved, status)

    assert record.status == "preview"
    assert src.exists()
    assert not resolved.exists()

    preview_output = SafeMover.format_preview([record])
    assert "DRY RUN PREVIEW" in preview_output
    assert "image.png" in preview_output
    assert "->" in preview_output


def test_safe_mover_path_traversal_blocked(tmp_path: Path):
    """Attempting to resolve destination outside target root must raise SecurityError."""
    target_root = tmp_path / "Organized"
    mover = SafeMover(target_root=target_root)

    info = FileInfo(
        path=tmp_path / "file.txt",
        name="file.txt",
        extension=".txt",
        size=10,
        modified_time=datetime.now(),
    )

    with pytest.raises(SecurityError, match="escapes target root"):
        mover.resolve_destination(info, "../../escape_dir")


def test_safe_mover_source_missing(tmp_path: Path):
    """If source file vanishes before move, it should record error safely."""
    target_root = tmp_path / "Organized"
    mover = SafeMover(target_root=target_root)

    ghost_file = tmp_path / "ghost.txt"
    info = FileInfo(
        path=ghost_file,
        name=ghost_file.name,
        extension=".txt",
        size=10,
        modified_time=datetime.now(),
    )

    record = mover.move_file(info, target_root / "Text" / "ghost.txt")
    assert record.status == "error"
    assert "does not exist" in record.error
