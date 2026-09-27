"""
scanner.py
==========
Recursive directory scanner with permission-error resilience, symbolic-link
loop detection, exclusion filtering, and metadata extraction.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional, Set, Tuple

from organizer.exceptions import ScanError
from organizer.models import FileInfo

logger = logging.getLogger("EnterpriseOrganizer.Scanner")


class FileScanner:
    """
    Recursively scans source directories and produces FileInfo metadata objects.
    Safely ignores excluded directories (such as destination directories inside source),
    handles permission errors gracefully without crashing, and tracks visited inodes
    to prevent symlink loops.
    """

    def __init__(
        self,
        source_dir: Path,
        exclude_dirs: Optional[List[Path]] = None,
        follow_symlinks: bool = False,
        include_hidden: bool = True,
    ):
        self.source_dir = Path(source_dir).resolve()
        self.exclude_dirs: Set[Path] = {Path(d).resolve() for d in (exclude_dirs or [])}
        self.follow_symlinks = follow_symlinks
        self.include_hidden = include_hidden

        self._visited_real_paths: Set[str] = set()
        self._visited_inodes: Set[Tuple[int, int]] = set()

        self.inaccessible_paths: List[Path] = []
        self.permission_denied_paths: List[Path] = []

        if not self.source_dir.exists():
            raise ScanError(f"Source directory does not exist: {self.source_dir}")
        if not self.source_dir.is_dir():
            raise ScanError(f"Source path is not a directory: {self.source_dir}")

    def scan(self) -> Generator[FileInfo, None, None]:
        """
        Recursively scan source directory and yield FileInfo objects for every discovered file.
        Resilient to PermissionError, FileNotFoundError, and OS-level access issues.
        """
        logger.info("Initiating recursive scan of: %s", self.source_dir)
        self._visited_real_paths.clear()
        self._visited_inodes.clear()
        self.inaccessible_paths.clear()
        self.permission_denied_paths.clear()

        yield from self._scan_directory(self.source_dir)
        logger.info(
            "Scan completed for %s (Inaccessible items: %d, Permission denied: %d)",
            self.source_dir,
            len(self.inaccessible_paths),
            len(self.permission_denied_paths),
        )

    def scan_all(self) -> List[FileInfo]:
        """Convenience method returning a list of all discovered FileInfo objects."""
        return list(self.scan())

    def _is_excluded(self, dir_path: Path) -> bool:
        """
        Check whether a directory matches or resides inside any excluded directory.
        Protects against infinite scanning loops if target directory is inside source.
        """
        resolved = dir_path.resolve()
        for exc in self.exclude_dirs:
            if resolved == exc or exc in resolved.parents:
                return True
        return False

    def _track_visited(self, dir_path: Path, stat_obj: Optional[os.stat_result] = None) -> bool:
        """
        Track visited directories using real canonical paths and (st_dev, st_ino) where available.
        Returns True if already visited (loop detected), False otherwise.
        """
        try:
            real_path = str(dir_path.resolve())
        except OSError:
            real_path = str(dir_path)

        if real_path in self._visited_real_paths:
            return True
        self._visited_real_paths.add(real_path)

        if stat_obj is not None and hasattr(stat_obj, "st_ino") and stat_obj.st_ino != 0:
            inode_key = (stat_obj.st_dev, stat_obj.st_ino)
            if inode_key in self._visited_inodes:
                return True
            self._visited_inodes.add(inode_key)

        return False

    def _scan_directory(self, current_dir: Path) -> Generator[FileInfo, None, None]:
        """Internal recursive generator with cycle detection and fault isolation."""
        try:
            dir_stat = current_dir.stat()
            if self._track_visited(current_dir, dir_stat):
                logger.debug("Skipping already visited directory (loop detected): %s", current_dir)
                return
        except PermissionError as perm_err:
            logger.warning("Permission denied checking directory stat: %s (%s)", current_dir, perm_err)
            self.permission_denied_paths.append(current_dir)
            return
        except OSError as os_err:
            logger.warning("OS error checking directory stat: %s (%s)", current_dir, os_err)
            self.inaccessible_paths.append(current_dir)
            return

        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    entry_name = entry.name

                    # Hidden file/folder filter
                    if not self.include_hidden and entry_name.startswith("."):
                        continue

                    entry_path = Path(entry.path)

                    try:
                        # Symlink check
                        if entry.is_symlink() and not self.follow_symlinks:
                            logger.debug("Skipping symlink (follow_symlinks=False): %s", entry_path)
                            continue

                        # Directory traversal
                        if entry.is_dir(follow_symlinks=self.follow_symlinks):
                            if self._is_excluded(entry_path):
                                logger.debug("Skipping excluded directory: %s", entry_path)
                                continue
                            yield from self._scan_directory(entry_path)

                        # File discovery
                        elif entry.is_file(follow_symlinks=self.follow_symlinks):
                            stat = entry.stat(follow_symlinks=self.follow_symlinks)
                            mod_time = datetime.fromtimestamp(stat.st_mtime)

                            # Determine creation/birth time
                            created_time = None
                            if hasattr(stat, "st_birthtime"):
                                created_time = datetime.fromtimestamp(stat.st_birthtime)
                            elif hasattr(stat, "st_ctime"):
                                created_time = datetime.fromtimestamp(stat.st_ctime)

                            rel_path = None
                            try:
                                rel_path = entry_path.relative_to(self.source_dir)
                            except ValueError:
                                rel_path = Path(entry_name)

                            yield FileInfo(
                                path=entry_path,
                                name=entry_name,
                                extension=entry_path.suffix.lower(),
                                size=stat.st_size,
                                modified_time=mod_time,
                                created_time=created_time,
                                relative_path=rel_path,
                                parent_dir=entry_path.parent,
                            )

                    except PermissionError as perm_err:
                        logger.warning("Permission denied accessing file/entry: %s (%s)", entry.path, perm_err)
                        self.permission_denied_paths.append(entry_path)
                    except OSError as os_err:
                        logger.warning("OS error accessing file/entry: %s (%s)", entry.path, os_err)
                        self.inaccessible_paths.append(entry_path)

        except PermissionError as perm_err:
            logger.warning("Permission denied opening directory: %s (%s)", current_dir, perm_err)
            self.permission_denied_paths.append(current_dir)
        except OSError as os_err:
            logger.warning("OS error opening directory: %s (%s)", current_dir, os_err)
            self.inaccessible_paths.append(current_dir)
