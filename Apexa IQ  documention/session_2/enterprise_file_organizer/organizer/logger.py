"""
logger.py
=========
Centralized logging system for Enterprise File Organizer.
Supports structured logging to file (logs/organizer.log) and console with
configurable verbosity.
"""

import logging
from pathlib import Path
from typing import Optional

DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
CONSOLE_FORMAT = "%(levelname)s: %(message)s"
VERBOSE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logger(
    name: str = "EnterpriseOrganizer",
    log_dir: Optional[Path] = None,
    verbose: bool = False,
) -> logging.Logger:
    """
    Initialize and return a configured logger instance.
    Logs to both console and a timestamped or rotating log file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter(VERBOSE_FORMAT if verbose else CONSOLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "organizer.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
