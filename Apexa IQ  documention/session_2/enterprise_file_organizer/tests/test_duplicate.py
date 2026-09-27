"""
Unit tests for two-tier DuplicateDetector component.
"""

from datetime import datetime
from pathlib import Path

from organizer.duplicate import DuplicateDetector
from organizer.models import FileInfo


def test_duplicate_detection_pipeline(tmp_path: Path):
    """Verify duplicate detection correctly identifies original vs duplicate files."""
    f1 = tmp_path / "resume.pdf"
    f2 = tmp_path / "resume_copy.pdf"
    f3 = tmp_path / "unique.txt"

    content_pdf = "Resume content 2026"
    f1.write_text(content_pdf, encoding="utf-8")
    f2.write_text(content_pdf, encoding="utf-8")
    f3.write_text("Unique text", encoding="utf-8")

    info1 = FileInfo(path=f1, name=f1.name, extension=".pdf", size=f1.stat().st_size, modified_time=datetime.now())
    info2 = FileInfo(path=f2, name=f2.name, extension=".pdf", size=f2.stat().st_size, modified_time=datetime.now())
    info3 = FileInfo(path=f3, name=f3.name, extension=".txt", size=f3.stat().st_size, modified_time=datetime.now())

    detector = DuplicateDetector()
    detector.register(info1)
    detector.register(info2)
    detector.register(info3)

    groups = detector.analyze()
    assert len(groups) == 1
    assert detector.get_duplicate_count() == 1
    assert detector.get_total_wasted_space() == f1.stat().st_size
    assert detector.is_duplicate(f2)
    assert not detector.is_duplicate(f1)
    assert detector.get_original_for(f2) == f1

    # Files must not be deleted or modified
    assert f1.exists()
    assert f2.exists()
    assert f3.exists()

    report_text = detector.format_report()
    assert "DUPLICATE FILES REPORT" in report_text
    assert "resume.pdf" in report_text
    assert "resume_copy.pdf" in report_text


def test_unique_sizes_skip_hashing(tmp_path: Path):
    """Files with unique sizes should not have duplicates."""
    f1 = tmp_path / "small.txt"
    f2 = tmp_path / "large.txt"

    f1.write_text("a", encoding="utf-8")
    f2.write_text("abcdefghij", encoding="utf-8")

    info1 = FileInfo(path=f1, name=f1.name, extension=".txt", size=f1.stat().st_size, modified_time=datetime.now())
    info2 = FileInfo(path=f2, name=f2.name, extension=".txt", size=f2.stat().st_size, modified_time=datetime.now())

    detector = DuplicateDetector()
    detector.register(info1)
    detector.register(info2)

    groups = detector.analyze()
    assert len(groups) == 0
    assert detector.get_duplicate_count() == 0
    assert "No duplicate files detected." in detector.format_report()


def test_zero_byte_files_duplicates(tmp_path: Path):
    """0-byte files should be identified as duplicate group."""
    z1 = tmp_path / "empty1.txt"
    z2 = tmp_path / "empty2.txt"
    z1.touch()
    z2.touch()

    info1 = FileInfo(path=z1, name=z1.name, extension=".txt", size=0, modified_time=datetime.now())
    info2 = FileInfo(path=z2, name=z2.name, extension=".txt", size=0, modified_time=datetime.now())

    detector = DuplicateDetector()
    detector.register(info1)
    detector.register(info2)

    groups = detector.analyze()
    assert len(groups) == 1
    assert groups[0].size == 0
    assert detector.get_duplicate_count() == 1
