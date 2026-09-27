"""
models.py
=========
Data models, enums, and dataclasses representing files, rules, operations,
and execution summaries for Enterprise File Organizer.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from organizer.utils import format_size


class Category(str, Enum):
    """Standard predefined categories."""
    DOCUMENTS = "Documents"
    IMAGES = "Images"
    VIDEOS = "Videos"
    AUDIO = "Audio"
    ARCHIVES = "Archives"
    CODE = "Code"
    DATA = "Data"
    SPREADSHEETS = "Spreadsheets"
    PRESENTATIONS = "Presentations"
    TEXT = "Text"
    EXECUTABLES = "Executables"
    OTHERS = "Others"


class RuleType(str, Enum):
    """Enumeration of rule types supported by the rule engine."""
    REGEX = "regex"
    FILENAME = "filename"
    EXTENSION = "extension"
    SIZE = "size"
    DATE = "date"
    DEFAULT = "default"


class ConflictStrategy(str, Enum):
    """Strategies for handling filename conflicts at the target directory."""
    RENAME_AUTO = "rename_auto"                  # Appends _1, _2, etc.
    SKIP = "skip"                                # Leaves source intact and skips
    OVERWRITE_IDENTICAL = "overwrite_identical"  # Replaces only if hashes are identical


@dataclass
class FileInfo:
    """
    Encapsulates all collected metadata for a discovered file.
    Follows enterprise-grade standards for filesystem representations.
    """
    path: Path
    name: str
    extension: str
    size: int
    modified_time: datetime
    created_time: Optional[datetime] = None
    relative_path: Optional[Path] = None
    parent_dir: Optional[Path] = None
    file_hash: Optional[str] = None
    category: Optional[str] = None
    planned_destination: Optional[Path] = None
    matched_rule: Optional[str] = None

    @property
    def destination(self) -> Optional[Path]:
        """Convenience alias for planned_destination."""
        return self.planned_destination

    @destination.setter
    def destination(self, value: Optional[Path]) -> None:
        self.planned_destination = value

    @property
    def is_symlink(self) -> bool:
        """Check if file is a symbolic link."""
        try:
            return self.path.is_symlink()
        except OSError:
            return False

    @property
    def human_size(self) -> str:
        """Human-readable size format (e.g. '1.45 MB')."""
        return format_size(self.size)

    @property
    def formatted_mtime(self) -> str:
        """ISO-formatted modification time."""
        return self.modified_time.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata to dictionary."""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "human_size": self.human_size,
            "modified_time": self.modified_time.isoformat(),
            "created_time": self.created_time.isoformat() if self.created_time else None,
            "relative_path": str(self.relative_path) if self.relative_path else None,
            "parent_dir": str(self.parent_dir) if self.parent_dir else None,
            "file_hash": self.file_hash,
            "category": self.category,
            "destination": str(self.planned_destination) if self.planned_destination else None,
            "matched_rule": self.matched_rule,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileInfo":
        """Reconstruct FileInfo from dictionary."""
        return cls(
            path=Path(data["path"]),
            name=data["name"],
            extension=data["extension"],
            size=data["size"],
            modified_time=datetime.fromisoformat(data["modified_time"]),
            created_time=datetime.fromisoformat(data["created_time"]) if data.get("created_time") else None,
            relative_path=Path(data["relative_path"]) if data.get("relative_path") else None,
            parent_dir=Path(data["parent_dir"]) if data.get("parent_dir") else None,
            file_hash=data.get("file_hash"),
            category=data.get("category"),
            planned_destination=Path(data["destination"]) if data.get("destination") else None,
            matched_rule=data.get("matched_rule"),
        )


@dataclass
class Rule:
    """
    Represents an organization rule with criteria and destination.
    """
    name: str
    rule_type: RuleType
    destination: str
    pattern: Optional[str] = None
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None
    modified_within_days: Optional[int] = None
    modified_older_than_days: Optional[int] = None
    case_sensitive: bool = False
    priority: int = 0


@dataclass
class DuplicateGroup:
    """
    Represents a group of duplicate files sharing identical size and hash.
    """
    file_hash: str
    size: int
    original: Path
    duplicates: List[Path] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        """Total number of copies including original."""
        return 1 + len(self.duplicates)

    @property
    def wasted_bytes(self) -> int:
        """Total storage consumed by redundant duplicates."""
        return self.size * len(self.duplicates)

    @property
    def human_wasted_size(self) -> str:
        """Human-readable representation of wasted space."""
        return format_size(self.wasted_bytes)


@dataclass
class OperationRecord:
    """
    Represents a single recorded file operation for history and rollback tracking.
    """
    source: str
    destination: str
    timestamp: str
    operation: str = "move"
    status: str = "success"
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "source": self.source,
            "destination": self.destination,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "status": self.status,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationRecord":
        """Reconstruct record from dictionary."""
        return cls(
            source=data["source"],
            destination=data["destination"],
            timestamp=data["timestamp"],
            operation=data.get("operation", "move"),
            status=data.get("status", "success"),
            file_hash=data.get("file_hash"),
            file_size=data.get("file_size"),
            error=data.get("error"),
        )


@dataclass
class ExecutionReport:
    """
    Summary metrics collected during execution.
    """
    total_scanned: int = 0
    total_organized: int = 0
    duplicates_found: int = 0
    skipped: int = 0
    errors: int = 0
    category_counts: Dict[str, int] = field(default_factory=dict)
    execution_time_seconds: float = 0.0
    error_messages: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage of processed files."""
        total_attempted = self.total_organized + self.errors
        if total_attempted == 0:
            return 100.0
        return round((self.total_organized / total_attempted) * 100.0, 1)
