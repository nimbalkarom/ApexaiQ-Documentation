"""
duplicate.py
============
Duplicate detection engine using two-tier comparison:
1. Exact file size matching (fast filter)
2. Chunked SHA-256 hash calculation (accurate verification)

Duplicate detection strictly reports duplicates and never automatically deletes user files.
"""

import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from organizer.models import DuplicateGroup, FileInfo
from organizer.utils import calculate_sha256, format_size

logger = logging.getLogger("EnterpriseOrganizer.Duplicate")


class DuplicateDetector:
    """
    Detects identical files using a two-tier size-and-hash strategy:
    1. Size-first comparison: skips hashing any file with a unique size.
    2. Chunked SHA-256 hashing: reads files in 64KB chunks to protect RAM.
    """

    def __init__(self):
        self._size_groups: Dict[int, List[FileInfo]] = defaultdict(list)
        self.duplicate_groups: List[DuplicateGroup] = []
        self._duplicate_to_original: Dict[Path, Path] = {}

    def register(self, file_info: FileInfo) -> None:
        """Register a file for duplicate analysis."""
        self._size_groups[file_info.size].append(file_info)

    def analyze(self) -> List[DuplicateGroup]:
        """
        Analyze registered files and identify duplicates.
        Calculates SHA-256 hashes only for files that share identical sizes.
        """
        self.duplicate_groups.clear()
        self._duplicate_to_original.clear()

        for size, files in self._size_groups.items():
            if len(files) < 2:
                continue  # Unique size; guaranteed not to have duplicates in this scan

            # Size match found: compute SHA-256 chunked hashes
            hash_buckets: Dict[str, List[FileInfo]] = defaultdict(list)
            for f in files:
                try:
                    if not f.file_hash:
                        f.file_hash = calculate_sha256(f.path)
                    hash_buckets[f.file_hash].append(f)
                except (PermissionError, OSError) as err:
                    logger.warning("Could not calculate hash for %s: %s", f.path, err)

            for f_hash, bucket in hash_buckets.items():
                if len(bucket) > 1:
                    # Sort files by path for deterministic original selection
                    sorted_bucket = sorted(bucket, key=lambda item: str(item.path))
                    original = sorted_bucket[0].path
                    duplicates = [item.path for item in sorted_bucket[1:]]

                    group = DuplicateGroup(
                        file_hash=f_hash,
                        size=size,
                        original=original,
                        duplicates=duplicates,
                    )
                    self.duplicate_groups.append(group)

                    for dup in duplicates:
                        self._duplicate_to_original[dup] = original

                    logger.info(
                        "Duplicate detected: Original '%s', %d duplicate(s) [Size: %s, SHA256: %s...]",
                        original.name,
                        len(duplicates),
                        format_size(size),
                        f_hash[:16],
                    )

        return self.duplicate_groups

    def get_duplicate_count(self) -> int:
        """Total number of duplicate files detected (excluding the original)."""
        return sum(len(g.duplicates) for g in self.duplicate_groups)

    def get_total_wasted_space(self) -> int:
        """Total redundant storage consumed by duplicate copies."""
        return sum(g.wasted_bytes for g in self.duplicate_groups)

    def is_duplicate(self, file_path: Path) -> bool:
        """Check if a specific path is identified as a duplicate."""
        return file_path in self._duplicate_to_original

    def get_original_for(self, file_path: Path) -> Optional[Path]:
        """Return the original file path for a detected duplicate, if any."""
        return self._duplicate_to_original.get(file_path)

    def format_report(self) -> str:
        """Return a formatted text summary of detected duplicates."""
        if not self.duplicate_groups:
            return "No duplicate files detected."

        lines = [
            "========================================",
            "        DUPLICATE FILES REPORT",
            "========================================",
            f"Total duplicate groups: {len(self.duplicate_groups)}",
            f"Redundant duplicate files: {self.get_duplicate_count()}",
            f"Wasted disk storage: {format_size(self.get_total_wasted_space())}",
            "----------------------------------------",
        ]

        for idx, group in enumerate(self.duplicate_groups, 1):
            lines.append(f"Group #{idx}:")
            lines.append(f"  Size   : {format_size(group.size)}")
            lines.append(f"  SHA256 : {group.file_hash}")
            lines.append(f"  Original: {group.original}")
            for dup in group.duplicates:
                lines.append(f"  Duplicate: {dup}")
            lines.append("")

        lines.append("========================================")
        return "\n".join(lines)
