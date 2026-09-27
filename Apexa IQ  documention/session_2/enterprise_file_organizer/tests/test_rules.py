"""
Unit tests for deterministic RuleEngine, covering:
- Rule type precedence & explicit priority
- Regex matching (case sensitivity, relative paths, syntax errors)
- Filename pattern matching
- Extension-specific matching
- File size thresholds (min, max, bounded ranges)
- Date thresholds (recent vs old archives, timezone awareness)
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from organizer.classifier import FileClassifier
from organizer.exceptions import RuleError
from organizer.models import FileInfo, Rule, RuleType
from organizer.rules import RuleEngine


def test_rule_priority_pipeline(tmp_path: Path):
    """
    Verify strict precedence:
    Regex (1) > Filename (2) > Extension (3) > Size (4) > Date (5) > Default (6)
    """
    classifier = FileClassifier()

    # Rule set with overlapping criteria
    rules = [
        Rule(name="Date Rule", rule_type=RuleType.DATE, modified_within_days=100, destination="Dest/Date"),
        Rule(name="Size Rule", rule_type=RuleType.SIZE, min_size_bytes=100, destination="Dest/Size"),
        Rule(name="Extension Rule", rule_type=RuleType.EXTENSION, pattern=".pdf", destination="Dest/Extension"),
        Rule(name="Filename Rule", rule_type=RuleType.FILENAME, pattern="invoice", destination="Dest/Filename"),
        Rule(name="Regex Rule", rule_type=RuleType.REGEX, pattern=r"^invoice_\d+\.pdf$", destination="Dest/Regex"),
    ]

    engine = RuleEngine(rules, classifier)

    file_info = FileInfo(
        path=tmp_path / "invoice_101.pdf",
        name="invoice_101.pdf",
        extension=".pdf",
        size=1024 * 1024,  # 1MB
        modified_time=datetime.now(),
    )

    dest, matched = engine.evaluate(file_info)
    # Regex rule must take precedence
    assert matched == "Regex Rule"
    assert dest == "Dest/Regex"


def test_filename_beats_extension_and_size(tmp_path: Path):
    """Filename rule should be evaluated before Extension and Size rules."""
    rules = [
        Rule(name="Size Rule", rule_type=RuleType.SIZE, min_size_bytes=50, destination="Dest/Size"),
        Rule(name="Ext Rule", rule_type=RuleType.EXTENSION, pattern=".pdf", destination="Dest/Ext"),
        Rule(name="Assignment Rule", rule_type=RuleType.FILENAME, pattern="assignment", destination="Dest/Assignment"),
    ]
    engine = RuleEngine(rules, FileClassifier())

    file_info = FileInfo(
        path=tmp_path / "math_assignment_1.pdf",
        name="math_assignment_1.pdf",
        extension=".pdf",
        size=500,
        modified_time=datetime.now(),
    )

    dest, matched = engine.evaluate(file_info)
    assert matched == "Assignment Rule"
    assert dest == "Dest/Assignment"


def test_regex_case_sensitivity(tmp_path: Path):
    """Verify case sensitivity flag on regex rules."""
    rules = [
        Rule(
            name="Strict Regex",
            rule_type=RuleType.REGEX,
            pattern=r"^REPORT_\d+\.PDF$",
            destination="Upper/Reports",
            case_sensitive=True,
        )
    ]
    engine = RuleEngine(rules, FileClassifier())

    upper_file = FileInfo(
        path=tmp_path / "REPORT_1.PDF",
        name="REPORT_1.PDF",
        extension=".pdf",
        size=10,
        modified_time=datetime.now(),
    )
    lower_file = FileInfo(
        path=tmp_path / "report_1.pdf",
        name="report_1.pdf",
        extension=".pdf",
        size=10,
        modified_time=datetime.now(),
    )

    dest_u, match_u = engine.evaluate(upper_file)
    assert match_u == "Strict Regex"

    dest_l, match_l = engine.evaluate(lower_file)
    assert match_l.startswith("DefaultCategory")


def test_regex_relative_path_matching(tmp_path: Path):
    """Regex can match against directory hierarchy in relative path."""
    rules = [
        Rule(
            name="Subproject Regex",
            rule_type=RuleType.REGEX,
            pattern=r"^projects/web/.*",
            destination="WebProjects",
        )
    ]
    engine = RuleEngine(rules, FileClassifier())

    info = FileInfo(
        path=tmp_path / "projects" / "web" / "index.html",
        name="index.html",
        extension=".html",
        size=100,
        modified_time=datetime.now(),
        relative_path=Path("projects/web/index.html"),
    )

    dest, matched = engine.evaluate(info)
    assert matched == "Subproject Regex"
    assert dest == "WebProjects"


def test_invalid_regex_raises_rule_error():
    """Uncompilable regex pattern should raise RuleError."""
    rules = [Rule(name="Bad", rule_type=RuleType.REGEX, pattern="[unclosed-regex", destination="Dest")]
    with pytest.raises(RuleError, match="Failed to compile regex"):
        RuleEngine(rules, FileClassifier())


def test_file_size_rules(tmp_path: Path):
    """Verify min_size, max_size, and bounded size range rules."""
    rules = [
        Rule(name="Large Files", rule_type=RuleType.SIZE, min_size_bytes=1024 * 1024 * 100, destination="Large"),  # > 100MB
        Rule(name="Medium Files", rule_type=RuleType.SIZE, min_size_bytes=1024 * 1024, max_size_bytes=1024 * 1024 * 10, destination="Medium"),  # 1MB - 10MB
        Rule(name="Tiny Files", rule_type=RuleType.SIZE, max_size_bytes=1024, destination="Tiny"),  # < 1KB
    ]
    engine = RuleEngine(rules, FileClassifier())

    large_file = FileInfo(path=tmp_path / "video.mp4", name="video.mp4", extension=".mp4", size=200 * 1024 * 1024, modified_time=datetime.now())
    med_file = FileInfo(path=tmp_path / "audio.mp3", name="audio.mp3", extension=".mp3", size=5 * 1024 * 1024, modified_time=datetime.now())
    tiny_file = FileInfo(path=tmp_path / "note.txt", name="note.txt", extension=".txt", size=500, modified_time=datetime.now())
    unmatched_file = FileInfo(path=tmp_path / "photo.jpg", name="photo.jpg", extension=".jpg", size=50 * 1024 * 1024, modified_time=datetime.now())

    assert engine.evaluate(large_file) == ("Large", "Large Files")
    assert engine.evaluate(med_file) == ("Medium", "Medium Files")
    assert engine.evaluate(tiny_file) == ("Tiny", "Tiny Files")
    assert engine.evaluate(unmatched_file) == ("Images", "DefaultCategory:Images")


def test_date_rules(tmp_path: Path):
    """Verify modification date rules (recent vs historical archive)."""
    now = datetime.now()
    rules = [
        Rule(name="Recent 7 Days", rule_type=RuleType.DATE, modified_within_days=7, destination="Recent"),
        Rule(name="Old Archive", rule_type=RuleType.DATE, modified_older_than_days=365, destination="Archive/Historical"),
    ]
    engine = RuleEngine(rules, FileClassifier())

    recent_file = FileInfo(path=tmp_path / "f1.txt", name="f1.txt", extension=".txt", size=10, modified_time=now - timedelta(days=2))
    old_file = FileInfo(path=tmp_path / "f2.txt", name="f2.txt", extension=".txt", size=10, modified_time=now - timedelta(days=400))
    middle_file = FileInfo(path=tmp_path / "f3.txt", name="f3.txt", extension=".txt", size=10, modified_time=now - timedelta(days=30))

    assert engine.evaluate(recent_file) == ("Recent", "Recent 7 Days")
    assert engine.evaluate(old_file) == ("Archive/Historical", "Old Archive")
    assert engine.evaluate(middle_file) == ("Text", "DefaultCategory:Text")


def test_timezone_aware_date_rules(tmp_path: Path):
    """Ensure timezone-aware datetime works seamlessly without throwing TypeError."""
    now_utc = datetime.now(timezone.utc)
    rules = [Rule(name="UTC Recent", rule_type=RuleType.DATE, modified_within_days=5, destination="RecentUTC")]
    engine = RuleEngine(rules, FileClassifier())

    aware_file = FileInfo(
        path=tmp_path / "utc_file.txt",
        name="utc_file.txt",
        extension=".txt",
        size=10,
        modified_time=now_utc - timedelta(days=1),
    )
    dest, matched = engine.evaluate(aware_file)
    assert matched == "UTC Recent"
    assert dest == "RecentUTC"
