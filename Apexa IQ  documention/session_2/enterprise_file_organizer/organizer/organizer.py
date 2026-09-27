"""
organizer.py
============
Main orchestrator for Enterprise File Organizer.
Coordinates scanning, classification, rule evaluation, duplicate detection,
safe file moving, preview generation, and operation history recording.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from organizer.classifier import FileClassifier
from organizer.config_loader import ConfigLoader
from organizer.duplicate import DuplicateDetector
from organizer.exceptions import OrganizerError
from organizer.models import (
    ConflictStrategy,
    DuplicateGroup,
    ExecutionReport,
    FileInfo,
    OperationRecord,
    Rule,
)
from organizer.mover import SafeMover
from organizer.rules import RuleEngine
from organizer.scanner import FileScanner

logger = logging.getLogger("EnterpriseOrganizer.Core")


class FileOrganizer:
    """
    High-level coordinator executing end-to-end file organization.
    """

    def __init__(
        self,
        source_dir: Path,
        target_dir: Path,
        rules: Optional[List[Rule]] = None,
        custom_categories: Optional[Dict[str, List[str]]] = None,
        conflict_strategy: ConflictStrategy = ConflictStrategy.RENAME_AUTO,
        dry_run: bool = False,
        history_dir: Optional[Path] = None,
    ):
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.rules = rules or []
        self.conflict_strategy = conflict_strategy
        self.dry_run = dry_run
        self.history_dir = Path(history_dir or (Path.cwd() / "history")).resolve()

        self.classifier = FileClassifier(custom_categories)
        self.rule_engine = RuleEngine(self.rules, self.classifier)
        self.duplicate_detector = DuplicateDetector()
        self.mover = SafeMover(
            target_root=self.target_dir,
            conflict_strategy=self.conflict_strategy,
            dry_run=self.dry_run,
        )

        # Scanner automatically excludes target directory to prevent infinite cycles
        self.scanner = FileScanner(
            source_dir=self.source_dir,
            exclude_dirs=[self.target_dir],
        )

        self.last_records: List[OperationRecord] = []
        self.last_report: Optional[ExecutionReport] = None

    def run(self) -> ExecutionReport:
        """
        Execute full organization workflow:
        1. Scan and register files.
        2. Detect duplicates without deleting.
        3. Match rules deterministically.
        4. Move or simulate movement safely.
        5. Record history journal if live.
        """
        start_time = time.time()
        report = ExecutionReport()
        records: List[OperationRecord] = []

        logger.info(
            "Starting organization from '%s' to '%s' (Dry-run: %s)",
            self.source_dir,
            self.target_dir,
            self.dry_run,
        )

        # 1. Scan files
        files: List[FileInfo] = []
        for file_info in self.scanner.scan():
            report.total_scanned += 1
            self.duplicate_detector.register(file_info)
            files.append(file_info)

        # 2. Analyze duplicates
        duplicate_groups = self.duplicate_detector.analyze()
        report.duplicates_found = sum(len(g.duplicates) for g in duplicate_groups)

        # 3. Apply rules and plan movement
        for file_info in files:
            try:
                dest_subpath, rule_name = self.rule_engine.evaluate(file_info)
                file_info.planned_destination = Path(dest_subpath)
                file_info.matched_rule = rule_name

                # Category metrics
                cat = file_info.category or self.classifier.classify_filename(file_info.name)
                report.category_counts[cat] = report.category_counts.get(cat, 0) + 1

                # Resolve collision & destination
                target_path, collision_status = self.mover.resolve_destination(file_info, dest_subpath)

                # Move or preview
                op_record = self.mover.move_file(file_info, target_path, collision_status)
                records.append(op_record)

                if op_record.status in ("success", "preview"):
                    report.total_organized += 1
                elif op_record.status in ("identical_skipped", "conflict_skipped", "skip"):
                    report.skipped += 1
                elif op_record.status == "error":
                    report.errors += 1
                    if op_record.error:
                        report.error_messages.append(op_record.error)
            except Exception as err:
                report.errors += 1
                err_msg = f"Error processing file {file_info.path}: {err}"
                report.error_messages.append(err_msg)
                logger.error(err_msg)

        report.execution_time_seconds = round(time.time() - start_time, 2)
        self.last_records = records
        self.last_report = report

        # 4. Save history journal if live operations executed
        if not self.dry_run and records:
            self._save_history(records)

        return report

    def get_dry_run_preview(self) -> str:
        """Return formatted preview text if dry_run was executed."""
        return SafeMover.format_preview(self.last_records)

    def _save_history(self, records: List[OperationRecord]) -> Path:
        """Save executed operations to a timestamped JSON Lines journal."""
        self.history_dir.mkdir(parents=True, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_dir / f"history_{timestamp_str}.jsonl"

        with open(history_file, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec.to_dict()) + "\n")

        logger.info("Saved operation history to %s", history_file)
        return history_file
