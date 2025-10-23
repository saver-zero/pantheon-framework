"""PantheonPath protection proxy for enforcing architectural boundaries.

This module provides the PantheonPath class that wraps pathlib.Path while
deliberately omitting I/O methods to create compile-time guarantees that
the Artifact Engine cannot perform I/O operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PantheonPath:
    """Protection proxy that wraps pathlib.Path while preventing I/O operations.

    The PantheonPath class implements the Protection Proxy pattern by wrapping
    pathlib.Path and exposing only safe path manipulation methods. This creates
    a compile-time guarantee that components using PantheonPath cannot perform
    I/O operations, maintaining the architectural boundary between computation
    and I/O layers.

    This class behaves as an immutable value object with value-based equality,
    making it predictable when used as dictionary keys or in sets.

    Only authorized components like the Workspace can unwrap the underlying
    Path object to perform actual I/O operations.
    """

    def __init__(self, *args: str) -> None:
        """Create a PantheonPath from string path segments only.

        Per T015 requirements, PantheonPath can only be created from string
        segments and must represent a relative path to enforce security boundaries.

        Args:
            *args: Path segments as strings only

        Raises:
            ValueError: If path would be absolute or if non-string arguments provided

        Examples:
            PantheonPath("test", "sub", "file.txt")  # Valid
            PantheonPath("relative/path")            # Valid
        """
        if not args:
            raise ValueError("PantheonPath requires at least one path segment")

        # Ensure all arguments are strings (per T015 requirement)
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                raise ValueError(
                    f"All path segments must be strings, got {type(arg).__name__} at position {i}"
                )

        # Create the path and validate it's relative (per T015 requirement)
        self._path = Path(*args)

        if self._path.is_absolute():
            raise ValueError(
                f"PantheonPath must represent a relative path, got absolute path: {self._path}"
            )

    @property
    def name(self) -> str:
        """The final component of the path."""
        return self._path.name

    @property
    def stem(self) -> str:
        """The final component without its suffix."""
        return self._path.stem

    @property
    def suffix(self) -> str:
        """The file extension of the final component."""
        return self._path.suffix

    @property
    def parent(self) -> PantheonPath:
        """The logical parent of this path."""
        return PantheonPath(str(self._path.parent))

    @property
    def parts(self) -> tuple[str, ...]:
        """A tuple giving access to the path's various components."""
        return self._path.parts

    def joinpath(self, *args: str | PantheonPath) -> PantheonPath:
        """Combine this path with one or more other path components.

        Args:
            *args: Path components to join

        Returns:
            New PantheonPath with combined path
        """
        path_args = []
        for arg in args:
            if isinstance(arg, PantheonPath):
                path_args.append(str(arg._path))
            else:
                path_args.append(arg)

        return PantheonPath(str(self._path.joinpath(*path_args)))

    def with_suffix(self, suffix: str) -> PantheonPath:
        """Return a new path with the file suffix changed.

        Args:
            suffix: New file suffix

        Returns:
            New PantheonPath with changed suffix
        """
        return PantheonPath(str(self._path.with_suffix(suffix)))

    def relative_to(self, other: PantheonPath | str | Path) -> PantheonPath:
        """Return a version of this path relative to another path.

        Args:
            other: Base path to make this path relative to

        Returns:
            New PantheonPath representing the relative path
        """
        if isinstance(other, PantheonPath):
            other_path = other._path
        elif isinstance(other, str):
            other_path = Path(other)
        else:
            other_path = other

        return PantheonPath(str(self._path.relative_to(other_path)))

    def is_absolute(self) -> bool:
        """Return True if the path is absolute (starts from root).

        Returns:
            True if path is absolute, False otherwise
        """
        return self._path.is_absolute()

    def _unwrap(self) -> Path:
        """Return the underlying pathlib.Path object.

        WARNING: This method is intended for internal use by authorized
        components like the Workspace only. Using this method breaks the
        architectural boundary that PantheonPath is designed to enforce.

        Returns:
            The underlying pathlib.Path object
        """
        return self._path

    def get_underlying_path(self) -> Path:
        """Return the underlying pathlib.Path object (alias for _unwrap).

        WARNING: This method is intended for internal use by authorized
        components like the Workspace only. Using this method breaks the
        architectural boundary that PantheonPath is designed to enforce.

        Returns:
            The underlying pathlib.Path object
        """
        return self._unwrap()

    def __eq__(self, other: Any) -> bool:
        """Check equality based on the underlying path.

        Args:
            other: Object to compare with

        Returns:
            True if other is a PantheonPath with the same underlying path
        """
        if not isinstance(other, PantheonPath):
            return False
        return self._path == other._path

    def __hash__(self) -> int:
        """Return hash of the underlying path for use in sets and as dict keys.

        Returns:
            Hash value of the underlying path
        """
        return hash(self._path)

    def __str__(self) -> str:
        """Return string representation of the path.

        Returns:
            String representation of the underlying path using forward slashes
            for cross-platform consistency
        """
        return str(self._path).replace("\\", "/")

    def __repr__(self) -> str:
        """Return unambiguous string representation of the PantheonPath.

        Returns:
            String representation showing the class and path
        """
        return f"PantheonPath({str(self._path)!r})"
