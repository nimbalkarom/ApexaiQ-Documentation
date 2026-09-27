"""
rollback.py
===========
Rollback system for Enterprise File Organizer.
Parses operation history journals (.jsonl) and safely reverses file movements
in LIFO (Last-In, First-Out) order without overwriting existing files.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from organizer.exceptions import RollbackError
from organizer.models import OperationRecord

logger = logging.getLogger("EnterpriseOrganizer.Rollback")


class RollbackManager:
    """
    Manages loading and safely reversing file operations from history journals.
    """

    def __init__(self, history_dir: Path):
        self.history_dir = Path(history_dir).resolve()

    def list_history_files(self) -> List[Path]:
        """Return all available history journal files sorted newest first."""
        if not self.history_dir.exists():
            return []
        return sorted(self.history_dir.glob("history_*.jsonl"), reverse=True)

    def get_latest_history_file(self) -> Optional[Path]:
        """Find the most recent history .jsonl file."""
        files = self.list_history_files()
        return files[0] if files else None

    def load_records(self, history_file: Path) -> List[OperationRecord]:
        """Load operation records from a specific JSON Lines history file."""
        if not history_file.exists():
            raise RollbackError(f"History file not found: {history_file}")

        records: List[OperationRecord] = []
        with open(history_file, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        records.append(OperationRecord.from_dict(data))
                    except (json.JSONDecodeError, KeyError) as err:
                        logger.warning("Corrupt record in %s at line %d: %s", history_file.name, line_no, err)

        if not records:
            raise RollbackError(f"History file contains no valid operation records: {history_file}")

        return records

    def execute_rollback(
        self,
        history_file: Optional[Path] = None,
        dry_run: bool = False,
    ) -> List[OperationRecord]:
        """
        Roll back operations in reverse order (LIFO).
        Safe against data clobbering: will not overwrite files already at original positions.
        """
        target_file = history_file or self.get_latest_history_file()
        if not target_file:
            raise RollbackError("No operation history journal found to roll back.")

        records = self.load_records(target_file)
        rollback_results: List[OperationRecord] = []
        rollback_timestamp = datetime.now().isoformat()

        logger.info("Initiating rollback using journal: %s (Total records: %d)", target_file.name, len(records))

        # Reverse operations: from destination back to source
        for record in reversed(records):
            if record.operation != "move" or record.status != "success":
                logger.debug("Skipping non-move or failed record during rollback: %s", record)
                continue

            current_pos = Path(record.destination)
            original_pos = Path(record.source)

            # Check 1: Ensure the moved file is actually present at its organized location
            if not current_pos.exists():
                logger.warning("Rollback target file missing: %s. Skipping reverse.", current_pos)
                rollback_results.append(
                    OperationRecord(
                        source=str(current_pos),
                        destination=str(original_pos),
                        timestamp=rollback_timestamp,
                        operation="rollback",
                        status="skipped_missing",
                        error="File no longer exists at destination",
                        file_size=record.file_size,
                        file_hash=record.file_hash,
                    )
                )
                continue

            # Check 2: Prevent overwriting any newly created file at original position
            if original_pos.exists():
                logger.warning(
                    "Original location '%s' is occupied. Skipping rollback to prevent data loss.",
                    original_pos,
                )
                rollback_results.append(
                    OperationRecord(
                        source=str(current_pos),
                        destination=str(original_pos),
                        timestamp=rollback_timestamp,
                        operation="rollback",
                        status="skipped_conflict",
                        error="Original location occupied",
                        file_size=record.file_size,
                        file_hash=record.file_hash,
                    )
                )
                continue

            # Dry-run Simulation
            if dry_run:
                logger.info("[DRY RUN ROLLBACK] Would revert: %s -> %s", current_pos, original_pos)
                rollback_results.append(
                    OperationRecord(
                        source=str(current_pos),
                        destination=str(original_pos),
                        timestamp=rollback_timestamp,
                        operation="rollback_dry_run",
                        status="preview",
                        file_size=record.file_size,
                        file_hash=record.file_hash,
                    )
                )
                continue

            # Real Reversion
            try:
                original_pos.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current_pos), str(original_pos))
                logger.info("Reverted file: %s -> %s", current_pos, original_pos)
                rollback_results.append(
                    OperationRecord(
                        source=str(current_pos),
                        destination=str(original_pos),
                        timestamp=rollback_timestamp,
                        operation="rollback",
                        status="success",
                        file_size=record.file_size,
                        file_hash=record.file_hash,
                    )
                )
            except Exception as err:
                logger.error("Failed to revert %s -> %s: %s", current_pos, original_pos, err)
                rollback_results.append(
                    OperationRecord(
                        source=str(current_pos),
                        destination=str(original_pos),
                        timestamp=rollback_timestamp,
                        operation="rollback",
                        status="error",
                        error=str(err),
                        file_size=record.file_size,
                        file_hash=record.file_hash,
                    )
                )

        logger.info(
            "Rollback completed for journal '%s'. Reverted %d operations.",
            target_file.name,
            sum(1 for r in rollback_results if r.status == "success"),
        )
        return rollback_results

    @staticmethod
    def format_summary(results: List[OperationRecord]) -> str:
        """Format rollback results into a readable report."""
        total = len(results)
        succeeded = sum(1 for r in results if r.status in ("success", "preview"))
        skipped_missing = sum(1 for r in results if r.status == "skipped_missing")
        skipped_conflict = sum(1 for r in results if r.status == "skipped_conflict")
        errors = sum(1 for r in results if r.status == "error")

        lines = [
            "========================================",
            "           ROLLBACK SUMMARY",
            "========================================",
            f"Total operations in journal : {total}",
            f"Successfully reversed       : {succeeded}",
            f"Skipped (target missing)    : {skipped_missing}",
            f"Skipped (conflict safe-skip): {skipped_conflict}",
            f"Errors encountered          : {errors}",
            "========================================",
        ]
        return "\n".join(lines)
