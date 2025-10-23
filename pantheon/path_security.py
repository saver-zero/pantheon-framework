"""Path security validation utilities for Pantheon Framework.

Centralized security validation to prevent directory traversal attacks and
path manipulation attempts across all framework components.
"""

from pathlib import Path
import urllib.parse


class PathSecurityError(ValueError):
    """Raised when a path fails security validation."""


def validate_path_safety(
    path_str: str,
    allow_absolute: bool = False,
    context: str = "path",
) -> None:
    """Validate path for security to prevent directory traversal attacks.

    Comprehensive security validation that checks for:
    - Directory traversal sequences (..)
    - Absolute paths (Windows: C:\\, D:\\, etc. and Unix: /)
    - URL-encoded and Unicode-encoded traversal attempts
    - Leading/trailing slashes that could escape boundaries

    Args:
        path_str: The path string to validate
        allow_absolute: Whether to allow absolute paths (default: False)
        context: Description of where this path is used (for error messages)

    Raises:
        PathSecurityError: If path contains dangerous patterns

    Examples:
        >>> validate_path_safety("foo/bar.txt")  # OK
        >>> validate_path_safety("../etc/passwd")  # Raises
        >>> validate_path_safety("C:\\Windows\\System32\\config")  # Raises
        >>> validate_path_safety("/etc/passwd")  # Raises
        >>> validate_path_safety("foo%2F..%2Fbar")  # Raises (URL-encoded ..)
    """
    if not path_str:
        raise PathSecurityError(f"Empty {context} not allowed")

    # Decode URL-encoded sequences to catch encoded traversal attempts
    try:
        decoded_path = urllib.parse.unquote(path_str)
        # Double decode to catch double-encoded attempts
        double_decoded_path = urllib.parse.unquote(decoded_path)
    except Exception:
        # If decoding fails, continue with original path
        decoded_path = path_str
        double_decoded_path = path_str

    # Check for directory traversal in path components
    # We check the path components (parts) to avoid false positives with
    # filenames containing multiple dots like "file...txt"
    path_obj = Path(path_str)
    if ".." in path_obj.parts:
        raise PathSecurityError(
            f"Directory traversal not allowed in {context}: {path_str}"
        )

    # Also check decoded paths for traversal sequences
    decoded_obj = Path(decoded_path)
    double_decoded_obj = Path(double_decoded_path)

    if ".." in decoded_obj.parts or ".." in double_decoded_obj.parts:
        raise PathSecurityError(
            f"Directory traversal not allowed in {context}: {path_str}"
        )

    # Check for absolute paths (unless explicitly allowed)
    if not allow_absolute:
        # Check for Unix absolute paths (start with /)
        if path_str.startswith("/"):
            raise PathSecurityError(
                f"Absolute paths not allowed in {context}: {path_str}"
            )

        # Check for Windows absolute paths (C:\, D:\, etc.)
        if len(path_str) > 1 and path_str[1] == ":":
            raise PathSecurityError(
                f"Absolute paths not allowed in {context}: {path_str}"
            )

        # Also check using pathlib for cross-platform safety
        if path_obj.is_absolute():
            raise PathSecurityError(
                f"Absolute paths not allowed in {context}: {path_str}"
            )

    # Check for backslash at start (Windows-style absolute or escape attempt)
    if path_str.startswith("\\") and not allow_absolute:
        raise PathSecurityError(f"Absolute paths not allowed in {context}: {path_str}")


def validate_section_path(section_path: str) -> None:
    """Validate a section path for use in artifact templates.

    Ensures section paths are safe relative paths without traversal or
    absolute path components.

    Args:
        section_path: The section path to validate

    Raises:
        ValueError: If section path contains dangerous patterns

    Examples:
        >>> validate_section_path("sections/core")  # OK
        >>> validate_section_path("../sections/core")  # Raises
        >>> validate_section_path("/etc/passwd")  # Raises
    """
    try:
        validate_path_safety(section_path, allow_absolute=False, context="section path")
    except PathSecurityError as e:
        # Raise as ValueError for backward compatibility with existing error handlers
        raise ValueError(str(e)) from e


def validate_import_path(import_path: str) -> None:
    """Validate an import path for template or schema includes.

    Ensures import paths are safe relative paths without traversal or
    absolute path components.

    Args:
        import_path: The import path to validate

    Raises:
        PathSecurityError: If import path contains dangerous patterns

    Examples:
        >>> validate_import_path("common/header.md")  # OK
        >>> validate_import_path("../../etc/passwd")  # Raises
        >>> validate_import_path("C:\\Windows\\System32\\config")  # Raises
    """
    validate_path_safety(import_path, allow_absolute=False, context="import path")


def validate_directory_param(directory: str) -> None:
    """Validate a directory parameter for artifact operations.

    Ensures directory parameters are safe relative paths without traversal or
    absolute path components.

    Args:
        directory: The directory parameter to validate

    Raises:
        PathSecurityError: If directory contains dangerous patterns

    Examples:
        >>> validate_directory_param("tickets/backlog")  # OK
        >>> validate_directory_param("../../../etc")  # Raises
        >>> validate_directory_param("/root")  # Raises
    """
    validate_path_safety(directory, allow_absolute=False, context="directory parameter")
