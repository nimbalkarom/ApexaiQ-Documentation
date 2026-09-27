"""
mover.py
========
Safe file movement engine with collision resolution and transactional recording.
Prioritizes data integrity:
- Never silently overwrites files
- Checks hashes on collisions to detect duplicates
- Auto-renames files with collision counters (e.g. report_1.pdf)
- Validates path security and directory containment
- Simulates complete preview in dry-run mode
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from organizer.exceptions import ConflictError, SafeMoveError, SecurityError
from organizer.models import ConflictStrategy, FileInfo, OperationRecord
from organizer.utils import calculate_sha256, is_subpath

logger = logging.getLogger("EnterpriseOrganizer.Mover")


class SafeMover:
    """
    Safely transfers files from source to destination according to conflict strategies.
    Guarantees that files are never overwritten without explicit verification,
    and supports dry-run previewing without modifying the filesystem.
    """

    def __init__(
        self,
        target_root: Path,
        conflict_strategy: ConflictStrategy = ConflictStrategy.RENAME_AUTO,
        dry_run: bool = False,
    ):
        self.target_root = Path(target_root).resolve()
        self.conflict_strategy = conflict_strategy
        self.dry_run = dry_run

    def resolve_destination(self, file_info: FileInfo, planned_subpath: str) -> Tuple[Path, str]:
        """
        Determine the exact target path for a file, handling potential collisions.
        Returns:
            Tuple[Path, str]: (resolved_destination_path, collision_status)
        """
        dest_dir = (self.target_root / planned_subpath).resolve()

        # Security check: Ensure destination does not escape target root
        if not is_subpath(dest_dir, self.target_root):
            raise SecurityError(
                f"Security Violation: Target directory '{dest_dir}' escapes target root '{self.target_root}'"
            )

        candidate = dest_dir / file_info.name

        # If candidate does not exist, safe to use directly
        if not candidate.exists():
            return candidate, "none"

        # Case 1: Source and destination are already the same physical file
        if candidate.resolve() == file_info.path.resolve():
            return candidate, "identical_path"

        # Case 2: Destination already has a file with the same name - check hashes
        is_identical_content = False
        try:
            if not file_info.file_hash:
                file_info.file_hash = calculate_sha256(file_info.path)
            dest_hash = calculate_sha256(candidate)
            if file_info.file_hash == dest_hash:
                is_identical_content = True
        except (PermissionError, OSError) as err:
            logger.warning("Could not compare hashes for collision '%s': %s", candidate, err)

        if is_identical_content:
            logger.info(
                "Collision detected for '%s', but file content is identical to existing destination.",
                file_info.name,
            )
            if self.conflict_strategy in (ConflictStrategy.SKIP, ConflictStrategy.OVERWRITE_IDENTICAL):
                return candidate, "identical_content"

        if self.conflict_strategy == ConflictStrategy.SKIP:
            return candidate, "conflict_skip"

        # Auto-Rename Strategy: Append _1, _2, etc. until an unused filename is found
        stem = file_info.path.stem
        suffix = file_info.path.suffix
        counter = 1
        renamed_candidate = dest_dir / f"{stem}_{counter}{suffix}"
        while renamed_candidate.exists():
            if renamed_candidate.resolve() == file_info.path.resolve():
                return renamed_candidate, "identical_path"
            counter += 1
            renamed_candidate = dest_dir / f"{stem}_{counter}{suffix}"

        logger.info("Resolved collision for '%s' -> '%s'", file_info.name, renamed_candidate.name)
        return renamed_candidate, "renamed"

    def move_file(self, file_info: FileInfo, target_path: Path, collision_status: str = "none") -> OperationRecord:
        """
        Execute file move or record planned move in dry-run mode.
        Ensures atomic-style checks before moving.
        """
        source_path = file_info.path.resolve()
        resolved_target = target_path.resolve()
        timestamp = datetime.now().isoformat()

        # Pre-flight check: Source file must exist
        if not source_path.exists():
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="move",
                status="error",
                error=f"Source file does not exist: {source_path}",
            )

        if not source_path.is_file():
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="move",
                status="error",
                error=f"Source is not a regular file: {source_path}",
            )

        # Pre-flight check: Identical source and target
        if source_path == resolved_target:
            logger.info("Source and target are identical (%s). Skipping move.", source_path)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="skip",
                status="identical_skipped",
                file_size=file_info.size,
                file_hash=file_info.file_hash,
            )

        # Pre-flight check: Identical content skip
        if collision_status == "identical_content" and self.conflict_strategy in (
            ConflictStrategy.SKIP,
            ConflictStrategy.OVERWRITE_IDENTICAL,
        ):
            logger.info("File '%s' already exists at destination with matching hash. Skipping.", file_info.name)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="skip",
                status="identical_skipped",
                file_size=file_info.size,
                file_hash=file_info.file_hash,
            )

        if collision_status == "conflict_skip":
            logger.info("Destination occupied for '%s' and strategy is SKIP. Skipping.", file_info.name)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="skip",
                status="conflict_skipped",
                file_size=file_info.size,
                file_hash=file_info.file_hash,
            )

        # Dry-run Preview
        if self.dry_run:
            logger.info("[DRY RUN] Would move: %s -> %s", source_path, target_path)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="dry_run_move",
                status="preview",
                file_size=file_info.size,
                file_hash=file_info.file_hash,
            )

        # Real Execution
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(target_path))
            logger.info("Successfully moved: %s -> %s", source_path, target_path)

            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="move",
                status="success",
                file_size=file_info.size,
                file_hash=file_info.file_hash,
            )
        except PermissionError as perm_err:
            logger.error("Permission denied moving %s -> %s: %s", source_path, target_path, perm_err)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="move",
                status="error",
                error=f"PermissionError: {perm_err}",
            )
        except OSError as os_err:
            logger.error("OS error moving %s -> %s: %s", source_path, target_path, os_err)
            return OperationRecord(
                source=str(source_path),
                destination=str(target_path),
                timestamp=timestamp,
                operation="move",
                status="error",
                error=f"OSError: {os_err}",
            )

    @staticmethod
    def format_preview(records: List[OperationRecord]) -> str:
        """
        Format planned operations into a clean preview string.
        """
        lines = [
            "========================================",
            "          DRY RUN PREVIEW",
            "========================================",
            f"Total planned operations: {len(records)}",
            "----------------------------------------",
        ]

        for rec in records:
            source_p = Path(rec.source)
            dest_p = Path(rec.destination)
            lines.append(f"{source_p.name}")
            lines.append(f"    {source_p}")
            lines.append("    ->")
            lines.append(f"    {dest_p}")
            lines.append("")

        lines.append("========================================")
        return "\n".join(lines)
