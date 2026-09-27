"""
Unit tests for data models and metadata structures in models.py.
"""

from datetime import datetime
from pathlib import Path

from organizer.models import (
    Category,
    ConflictStrategy,
    DuplicateGroup,
    ExecutionReport,
    FileInfo,
    OperationRecord,
    Rule,
    RuleType,
)


def test_file_info_properties_and_serialization(tmp_path: Path):
    """Verify FileInfo attributes, properties, and dictionary round-trip."""
    file_path = tmp_path / "presentation.pptx"
    file_path.write_text("dummy", encoding="utf-8")
    now = datetime(2026, 9, 21, 10, 30, 0)

    info = FileInfo(
        path=file_path,
        name="presentation.pptx",
        extension=".pptx",
        size=1024 * 1024 * 5,  # 5 MB
        modified_time=now,
        created_time=now,
        relative_path=Path("presentation.pptx"),
        parent_dir=tmp_path,
        file_hash="mock_hash_123",
        category="Presentations",
    )

    # Property tests
    assert info.human_size == "5.00 MB"
    assert info.formatted_mtime == "2026-09-21 10:30:00"
    assert info.destination is None

    # Destination property setter
    target = Path("Presentations/presentation.pptx")
    info.destination = target
    assert info.destination == target
    assert info.planned_destination == target

    # Serialization round-trip
    info_dict = info.to_dict()
    assert info_dict["name"] == "presentation.pptx"
    assert info_dict["category"] == "Presentations"
    assert info_dict["destination"] == str(target)

    reconstructed = FileInfo.from_dict(info_dict)
    assert reconstructed.name == info.name
    assert reconstructed.size == info.size
    assert reconstructed.category == info.category
    assert reconstructed.destination == info.destination
    assert reconstructed.modified_time == info.modified_time


def test_category_enum():
    """Verify Category enum encompasses all core types."""
    assert Category.DOCUMENTS.value == "Documents"
    assert Category.IMAGES.value == "Images"
    assert Category.VIDEOS.value == "Videos"
    assert Category.CODE.value == "Code"
    assert Category.DATA.value == "Data"
    assert Category.SPREADSHEETS.value == "Spreadsheets"
    assert Category.PRESENTATIONS.value == "Presentations"
    assert Category.TEXT.value == "Text"
    assert Category.EXECUTABLES.value == "Executables"
    assert Category.OTHERS.value == "Others"


def test_duplicate_group_computations(tmp_path: Path):
    """Verify DuplicateGroup calculations for counts and wasted bytes."""
    orig = tmp_path / "file.pdf"
    d1 = tmp_path / "copy1.pdf"
    d2 = tmp_path / "copy2.pdf"

    group = DuplicateGroup(
        file_hash="abcdef",
        size=1024 * 1024,  # 1 MB
        original=orig,
        duplicates=[d1, d2],
    )

    assert group.total_count == 3
    assert group.wasted_bytes == 2 * 1024 * 1024
    assert group.human_wasted_size == "2.00 MB"


def test_operation_record_serialization():
    """Verify OperationRecord dictionary round-trip."""
    rec = OperationRecord(
        source="/source/path.txt",
        destination="/dest/path.txt",
        timestamp="2026-09-21T10:00:00",
        operation="move",
        status="success",
        file_size=500,
        file_hash="hashxyz",
    )

    data = rec.to_dict()
    reconstructed = OperationRecord.from_dict(data)
    assert reconstructed.source == rec.source
    assert reconstructed.destination == rec.destination
    assert reconstructed.file_hash == rec.file_hash


def test_execution_report_metrics():
    """Verify success rate computation in ExecutionReport."""
    report = ExecutionReport(
        total_scanned=10,
        total_organized=8,
        errors=2,
    )
    assert report.success_rate == 80.0

    empty_report = ExecutionReport()
    assert empty_report.success_rate == 100.0
