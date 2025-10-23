"""FileSystem abstraction interface for I/O operations.

This module provides the FileSystem class that abstracts all file system
I/O operations to enable dependency injection and testability throughout
the Pantheon Framework. The class serves as a concrete Port interface
following the Dependency Inversion Principle.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


class FileSystem:
    """Concrete I/O abstraction enabling dependency injection for testability.

    The FileSystem class wraps standard library I/O operations in a concrete
    class that can be mocked during testing. This follows the Dependency
    Inversion Principle where high-level components depend on abstractions
    rather than concrete implementations.

    This class serves as the single I/O boundary layer in the Pantheon Framework,
    providing a seam for dependency injection that enables complete test isolation
    for higher-level components like PantheonWorkspace. All methods delegate
    directly to pathlib.Path operations with proper exception propagation.

    Thread Safety:
        This class is thread-safe through stateless operations that rely on
        pathlib's inherent thread safety. No mutable instance state is maintained.

    Example Usage:
        # Real usage
        filesystem = FileSystem()
        content = filesystem.read_text(Path("config.yaml"))

        # Mock usage for testing
        mock_fs = Mock(spec=FileSystem)
        mock_fs.read_text.return_value = "mocked content"
        workspace = PantheonWorkspace(mock_fs)
    """

    def read_text(self, path: Path | str, encoding: str = "utf-8") -> str:
        """Read text content from a file.

        Args:
            path: Path to the file to read
            encoding: Text encoding to use (default: utf-8)

        Returns:
            Text content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If read access is denied
            UnicodeDecodeError: If encoding fails
        """
        path_obj = Path(path) if isinstance(path, str) else path
        return path_obj.read_text(encoding=encoding)

    def write_text(
        self, path: Path | str, content: str, encoding: str = "utf-8"
    ) -> None:
        """Write text content to a file.

        Args:
            path: Path to the file to write
            content: Text content to write
            encoding: Text encoding to use (default: utf-8)

        Raises:
            PermissionError: If write access is denied
            FileNotFoundError: If parent directory doesn't exist
            UnicodeEncodeError: If encoding fails
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.write_text(content, encoding=encoding)

    def append_text(
        self, path: Path | str, content: str, encoding: str = "utf-8"
    ) -> None:
        """Append text content to a file, creating it if it does not exist.

        Args:
            path: Path to the file to append to
            content: Text content to append
            encoding: Text encoding to use (default: utf-8)

        Raises:
            PermissionError: If write access is denied
            FileNotFoundError: If parent directory doesn't exist
            UnicodeEncodeError: If encoding fails
        """
        path_obj = Path(path) if isinstance(path, str) else path
        with path_obj.open("a", encoding=encoding) as f:
            f.write(content)

    def exists(self, path: Path | str) -> bool:
        """Check if a path exists.

        Args:
            path: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        path_obj = Path(path) if isinstance(path, str) else path
        return path_obj.exists()

    def mkdir(
        self, path: Path | str, parents: bool = False, exist_ok: bool = False
    ) -> None:
        """Create a directory.

        Args:
            path: Path to the directory to create
            parents: If True, create parent directories as needed
            exist_ok: If True, don't raise error if directory already exists

        Raises:
            FileExistsError: If directory exists and exist_ok is False
            FileNotFoundError: If parent directory doesn't exist and parents is False
            PermissionError: If creation permission is denied
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.mkdir(parents=parents, exist_ok=exist_ok)

    def rmdir(self, path: Path | str) -> None:
        """Remove an empty directory.

        Args:
            path: Path to the directory to remove

        Raises:
            FileNotFoundError: If the directory doesn't exist
            OSError: If the directory is not empty
            PermissionError: If removal permission is denied
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.rmdir()

    def unlink(self, path: Path | str, missing_ok: bool = False) -> None:
        """Remove a file.

        Args:
            path: Path to the file to remove
            missing_ok: If True, don't raise error if file doesn't exist

        Raises:
            FileNotFoundError: If file doesn't exist and missing_ok is False
            IsADirectoryError: If path points to a directory
            PermissionError: If removal permission is denied
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.unlink(missing_ok=missing_ok)

    def iterdir(self, path: Path | str) -> Iterator[Path]:
        """Iterate over directory contents.

        Args:
            path: Path to the directory to iterate

        Returns:
            Iterator yielding Path objects for directory contents

        Raises:
            FileNotFoundError: If the directory doesn't exist
            NotADirectoryError: If path is not a directory
            PermissionError: If read access is denied
        """
        path_obj = Path(path) if isinstance(path, str) else path
        return path_obj.iterdir()

    def glob(self, directory: Path | str, pattern: str) -> list[Path]:
        """Find all files matching a glob pattern in a directory.

        Args:
            directory: Path to the directory to search in
            pattern: Glob pattern to match files against (e.g., '*.md', 'test_*.py')

        Returns:
            List of Path objects matching the pattern

        Raises:
            FileNotFoundError: If the directory doesn't exist
            NotADirectoryError: If path is not a directory
            PermissionError: If read access is denied
        """
        path_obj = Path(directory) if isinstance(directory, str) else directory

        # Check if directory exists
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {path_obj}")

        # Check if path is a directory
        if not path_obj.is_dir():
            raise NotADirectoryError(f"Not a directory: {path_obj}")

        return list(path_obj.glob(pattern))

    def read_bundled_resource(
        self, package: str, resource_path: str, encoding: str = "utf-8"
    ) -> str:
        """Read text content from a bundled resource within the package.

        Args:
            package: Python package name containing the resource
            resource_path: Path to the resource relative to the package
            encoding: Text encoding to use (default: utf-8)

        Returns:
            Text content of the bundled resource

        Raises:
            FileNotFoundError: If the resource doesn't exist
            UnicodeDecodeError: If encoding fails
        """
        import importlib.resources

        with importlib.resources.as_file(
            importlib.resources.files(package) / resource_path
        ) as resource_file:
            return resource_file.read_text(encoding=encoding)
