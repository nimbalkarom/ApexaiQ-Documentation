"""
main.py
=======
Command-Line Interface and Interactive Entry Point for Enterprise File Organizer.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

from organizer import __version__
from organizer.config_loader import ConfigLoader
from organizer.exceptions import ConfigurationError, OrganizerError, SecurityError
from organizer.logger import setup_logger
from organizer.models import ConflictStrategy
from organizer.organizer import FileOrganizer
from organizer.rollback import RollbackManager


def print_banner() -> None:
    """Display program header banner."""
    print("========================================")
    print("       ENTERPRISE FILE ORGANIZER        ")
    print(f"                v{__version__}                 ")
    print("========================================")


def print_summary(report, log_path: Path) -> None:
    """Print the exact organization summary as specified."""
    print("\n========================================")
    print("          ORGANIZATION SUMMARY          ")
    print("========================================")
    print(f"Files scanned       : {report.total_scanned}")
    print(f"Files organized     : {report.total_organized}")
    print(f"Duplicates found    : {report.duplicates_found}")
    print(f"Skipped             : {report.skipped}")
    print(f"Errors              : {report.errors}")
    print("")

    if report.category_counts:
        for cat, count in sorted(report.category_counts.items(), key=lambda x: -x[1]):
            print(f"{cat:<20}: {count}")
        print("")

    print(f"Execution time      : {report.execution_time_seconds:.2f} seconds")
    print(f"\nLog:\n{log_path}")
    print("========================================\n")


def generate_config(target_path: Path) -> None:
    """Generate default configuration template at target location."""
    default_cfg = Path(__file__).parent / "config" / "default_rules.json"
    if not default_cfg.exists():
        print(f"Error: Base default configuration file missing at {default_cfg}")
        sys.exit(1)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(default_cfg, "r", encoding="utf-8") as src, open(target_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    print(f"Successfully generated default configuration file at: {target_path}")


def clean_path_string(val: Optional[str]) -> Optional[Path]:
    """Strip surrounding quotes and whitespace from path input."""
    if not val:
        return None
    cleaned = val.strip().strip('"\'').strip()
    return Path(cleaned) if cleaned else None


def interactive_mode(log_path: Path) -> None:
    """Interactive wizard guiding the user through organization or rollback."""
    print_banner()
    print("\nSource directory:")
    raw_source = input("> ").strip()
    source_path = clean_path_string(raw_source)
    if not source_path:
        print("Source directory cannot be empty.")
        return

    print("\nDestination directory:")
    raw_target = input("> ").strip()
    target_path = clean_path_string(raw_target)
    if not target_path:
        print("Destination directory cannot be empty.")
        return

    print("\nConfiguration file (press Enter for default):")
    raw_config = input("> ").strip()
    config_path = clean_path_string(raw_config)

    print("\nMode:")
    print("1. Dry Run (Preview only)")
    print("2. Organize (Perform moves)")
    print("3. Rollback")
    mode_choice = input("> ").strip()

    if mode_choice == "1":
        run_organizer(
            source=source_path,
            target=target_path,
            config_path=config_path,
            dry_run=True,
            log_path=log_path,
        )
    elif mode_choice == "2":
        # Pre-scan count for confirmation prompt
        cfg_file = config_path or (Path(__file__).parent / "config" / "default_rules.json")
        try:
            config_data = ConfigLoader.load_config(cfg_file)
            rules = ConfigLoader.parse_rules(config_data.get("rules", []))
            categories = config_data.get("categories", {})
        except Exception as err:
            print(f"Configuration Error: {err}")
            return

        organizer = FileOrganizer(
            source_dir=source_path,
            target_dir=target_path,
            rules=rules,
            custom_categories=categories,
            dry_run=True,
        )
        preview_report = organizer.run()

        confirm = input(f"\nProceed with organizing {preview_report.total_scanned} files? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Operation aborted by user.")
            return

        run_organizer(
            source=source_path,
            target=target_path,
            config_path=config_path,
            dry_run=False,
            log_path=log_path,
        )
    elif mode_choice == "3":
        run_rollback(dry_run=False)
    else:
        print("Invalid selection. Aborted.")


def run_organizer(
    source: Path,
    target: Path,
    config_path: Optional[Path],
    dry_run: bool,
    log_path: Path,
) -> None:
    """Execute organization pipeline."""
    cfg_file = config_path or (Path(__file__).parent / "config" / "default_rules.json")
    try:
        config_data = ConfigLoader.load_config(cfg_file)
        rules = ConfigLoader.parse_rules(config_data.get("rules", []))
        categories = config_data.get("categories", {})
        strategy_str = config_data.get("conflict_strategy", "rename_auto")
        conflict_strategy = ConflictStrategy(strategy_str)
    except Exception as err:
        print(f"Error loading configuration from {cfg_file}: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        organizer = FileOrganizer(
            source_dir=source,
            target_dir=target,
            rules=rules,
            custom_categories=categories,
            conflict_strategy=conflict_strategy,
            dry_run=dry_run,
        )
    except Exception as err:
        print(f"Initialization Error: {err}", file=sys.stderr)
        sys.exit(1)

    report = organizer.run()

    if dry_run:
        print("\n" + organizer.get_dry_run_preview())

    # If duplicates were detected, display duplicate summary
    if report.duplicates_found > 0:
        print("\n" + organizer.duplicate_detector.format_report())

    print_summary(report, log_path)


def run_rollback(dry_run: bool) -> None:
    """Execute rollback on the most recent history journal."""
    history_dir = Path(__file__).parent / "history"
    manager = RollbackManager(history_dir)
    latest = manager.get_latest_history_file()
    if not latest:
        print("No operation history found to roll back.")
        return

    print(f"Latest operation journal: {latest.name}")
    if not dry_run:
        confirm = input(f"Proceed with rollback of operations from {latest.name}? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Rollback aborted by user.")
            return

    results = manager.execute_rollback(latest, dry_run=dry_run)
    print("\n" + manager.format_summary(results))


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Enterprise File Organizer: Safe, automated, multi-criteria file classification and organization."
    )
    parser.add_argument("source", nargs="?", help="Source directory containing unorganized files")
    parser.add_argument("target", nargs="?", help="Target directory where organized folders will be created")
    parser.add_argument("--dry-run", action="store_true", help="Preview planned operations without modifying filesystem")
    parser.add_argument("--verbose", "-v", action="store_true", help="Display verbose debug logs in console")
    parser.add_argument("--config", "-c", type=Path, help="Path to custom JSON configuration rules file")
    parser.add_argument("--generate-config", type=Path, help="Generate default configuration template at specified path")
    parser.add_argument("--rollback", action="store_true", help="Reverse the most recent organization operation")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive interactive console wizard")

    args = parser.parse_args()

    log_dir = Path(__file__).parent / "logs"
    log_file = log_dir / "organizer.log"
    setup_logger(log_dir=log_dir, verbose=args.verbose)

    try:
        if args.generate_config:
            generate_config(args.generate_config)
            return

        if args.rollback:
            run_rollback(dry_run=args.dry_run)
            return

        if args.interactive or (not args.source and not args.target):
            interactive_mode(log_path=log_file)
            return

        if not args.source or not args.target:
            parser.error("Both SOURCE and TARGET directories are required unless using --rollback or --interactive.")

        source_path = Path(args.source)
        target_path = Path(args.target)

        # In non-dry-run mode, require confirmation before moving real files
        if not args.dry_run:
            print_banner()
            print(f"Source Directory : {source_path.resolve()}")
            print(f"Target Directory : {target_path.resolve()}")
            confirm = input("\nProceed with file organization? [y/N]: ").strip().lower()
            if confirm != "y":
                print("Operation aborted by user.")
                sys.exit(0)

        run_organizer(
            source=source_path,
            target=target_path,
            config_path=args.config,
            dry_run=args.dry_run,
            log_path=log_file,
        )

    except (OrganizerError, SecurityError, ConfigurationError) as domain_err:
        print(f"\n[ERROR] Application encountered an error: {domain_err}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting safely.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
