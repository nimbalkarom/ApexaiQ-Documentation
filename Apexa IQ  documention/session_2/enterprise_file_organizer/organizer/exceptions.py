"""
exceptions.py
=============
Custom exception hierarchy for Enterprise File Organizer.
Provides granular error handling for scanning, classification, movement,
configuration, and rollback operations.
"""


class OrganizerError(Exception):
    """Base exception for all Enterprise File Organizer errors."""
    pass


class ConfigurationError(OrganizerError):
    """Raised when configuration validation or loading fails."""
    pass


class ScanError(OrganizerError):
    """Raised when file scanning encounters an unrecoverable condition."""
    pass


class RuleError(OrganizerError):
    """Raised when rule evaluation or regex compilation fails."""
    pass


class ConflictError(OrganizerError):
    """Raised when a filename conflict cannot be safely resolved."""
    pass


class SafeMoveError(OrganizerError):
    """Raised when safe file movement operation fails or aborts for safety."""
    pass


class RollbackError(OrganizerError):
    """Raised when rollback of a past operation fails."""
    pass


class SecurityError(OrganizerError):
    """Raised when path traversal or unsafe filesystem operations are detected."""
    pass
