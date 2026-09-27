"""
utils.py
========
General utility functions for filesystem operations, chunked hashing,
size formatting, and security validations.
"""

import hashlib
from pathlib import Path
from typing import Optional

from organizer.exceptions import SecurityError

CHUNK_SIZE = 64 * 1024  # 64 KB chunks for memory-safe hashing


def calculate_sha256(file_path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """
    Calculate SHA-256 hash of a file using chunks to avoid high memory consumption.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def format_size(bytes_val: int) -> str:
    """
    Convert raw byte count into human-readable representation (B, KB, MB, GB, TB).
    """
    if bytes_val < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    val = float(bytes_val)
    unit_idx = 0
    while val >= 1024.0 and unit_idx < len(units) - 1:
        val /= 1024.0
        unit_idx += 1
    return f"{val:.2f} {units[unit_idx]}" if unit_idx > 0 else f"{int(val)} B"


def parse_size_to_bytes(size_str: str) -> int:
    """
    Parse strings such as '10MB', '1.5GB', '500KB' into exact byte integers.
    Raises ValueError on invalid formats.
    """
    cleaned = size_str.strip().upper()
    multipliers = {
        "TB": 1024 ** 4,
        "GB": 1024 ** 3,
        "MB": 1024 ** 2,
        "KB": 1024,
        "B": 1,
    }
    for unit, mult in multipliers.items():
        if cleaned.endswith(unit):
            num_part = cleaned[:-len(unit)].strip()
            try:
                val = float(num_part)
                if val < 0:
                    raise ValueError(f"File size cannot be negative: {size_str}")
                return int(val * mult)
            except ValueError as err:
                raise ValueError(f"Invalid numeric size value '{num_part}' in '{size_str}'") from err

    # If no unit suffix, assume raw integer bytes
    try:
        val = int(cleaned)
        if val < 0:
            raise ValueError(f"File size cannot be negative: {size_str}")
        return val
    except ValueError as err:
        raise ValueError(f"Unrecognized size format or unit in '{size_str}'. Supported units: B, KB, MB, GB, TB.") from err


def sanitize_relative_path(rel_path: str) -> Path:
    """
    Verify that relative path does not escape using path traversal ('..').
    """
    path = Path(rel_path)
    if path.is_absolute() or ".." in path.parts:
        raise SecurityError(f"Unsafe path traversal detected in destination: {rel_path}")
    return path


def is_subpath(child: Path, parent: Path) -> bool:
    """
    Determine if child path is contained within parent path.
    """
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
