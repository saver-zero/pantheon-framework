"""Integration tests demonstrating FileSystem dependency injection patterns.

This module contains integration tests that show how the FileSystem
abstraction enables dependency injection and mocking in realistic
scenarios throughout the Pantheon Framework.
"""

from pathlib import Path
from unittest.mock import Mock

from pantheon.filesystem import FileSystem
from pantheon.path import PantheonPath


class MockWorkspace:
    """Example component that accepts FileSystem via dependency injection."""

    def __init__(self, filesystem: FileSystem) -> None:
        """Initialize workspace with filesystem dependency.

        Args:
            filesystem: FileSystem instance for I/O operations
        """
        self.filesystem = filesystem

    def read_config(self, config_path: PantheonPath) -> str:
        """Read configuration from a path using injected filesystem.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration content as string
        """
        # Unwrap PantheonPath to get actual Path for filesystem operation
        actual_path = config_path._unwrap()
        return self.filesystem.read_text(actual_path)

    def save_output(self, output_path: PantheonPath, content: str) -> None:
        """Save output to a path using injected filesystem.

        Args:
            output_path: Path to save output
            content: Content to save
        """
        # Unwrap PantheonPath to get actual Path for filesystem operation
        actual_path = output_path._unwrap()
        self.filesystem.write_text(actual_path, content)

    def ensure_directory_exists(self, dir_path: PantheonPath) -> None:
        """Ensure directory exists using injected filesystem.

        Args:
            dir_path: Directory path to create if needed
        """
        actual_path = dir_path._unwrap()
        if not self.filesystem.exists(actual_path):
            self.filesystem.mkdir(actual_path, parents=True, exist_ok=True)


class TestFileSystemDependencyInjection:
    """Test FileSystem dependency injection patterns."""

    def test_filesystem_can_be_injected_into_component(self) -> None:
        """FileSystem should be injectable into components via constructor."""
        # Create real FileSystem instance
        filesystem = FileSystem()

        # Inject into component
        workspace = MockWorkspace(filesystem)

        # Verify injection worked
        assert workspace.filesystem is filesystem
        assert isinstance(workspace.filesystem, FileSystem)

    def test_mock_filesystem_can_be_injected(self) -> None:
        """Mock FileSystem should be injectable for testing."""
        # Create mock with FileSystem spec
        mock_filesystem = Mock(spec=FileSystem)

        # Inject mock into component
        workspace = MockWorkspace(mock_filesystem)

        # Verify mock injection worked
        assert workspace.filesystem is mock_filesystem
        assert hasattr(workspace.filesystem, "read_text")
        assert hasattr(workspace.filesystem, "write_text")

    def test_mock_filesystem_tracks_method_calls(self) -> None:
        """Mock FileSystem should track method calls for verification."""
        # Create mock and configure return values
        mock_filesystem = Mock(spec=FileSystem)
        mock_filesystem.read_text.return_value = "test config content"
        mock_filesystem.exists.return_value = True

        # Inject mock and use it
        workspace = MockWorkspace(mock_filesystem)
        config_path = PantheonPath("config", "app.yml")

        content = workspace.read_config(config_path)

        # Verify method was called with correct arguments
        mock_filesystem.read_text.assert_called_once_with(config_path._unwrap())
        assert content == "test config content"

    def test_mock_filesystem_can_verify_write_operations(self) -> None:
        """Mock FileSystem should track write operations for verification."""
        # Create mock
        mock_filesystem = Mock(spec=FileSystem)

        # Inject mock and perform write operation
        workspace = MockWorkspace(mock_filesystem)
        output_path = PantheonPath("output", "result.txt")
        test_content = "test output content"

        workspace.save_output(output_path, test_content)

        # Verify write was called with correct arguments
        mock_filesystem.write_text.assert_called_once_with(
            output_path._unwrap(), test_content
        )

    def test_mock_filesystem_can_simulate_directory_operations(self) -> None:
        """Mock FileSystem should support directory operation verification."""
        # Create mock and configure exists to return False (directory doesn't exist)
        mock_filesystem = Mock(spec=FileSystem)
        mock_filesystem.exists.return_value = False

        # Inject mock and ensure directory
        workspace = MockWorkspace(mock_filesystem)
        dir_path = PantheonPath("output", "subdirectory")

        workspace.ensure_directory_exists(dir_path)

        # Verify exists was checked and mkdir was called
        mock_filesystem.exists.assert_called_once_with(dir_path._unwrap())
        mock_filesystem.mkdir.assert_called_once_with(
            dir_path._unwrap(), parents=True, exist_ok=True
        )


class TestPantheonPathIOPrevention:
    """Test PantheonPath prevents I/O in computation layers."""

    def test_computation_layer_cannot_perform_io_with_pantheon_path(self) -> None:
        """Computation components receiving PantheonPath cannot perform I/O."""
        # Simulate an Artifact Engine that only receives PantheonPath
        path = PantheonPath("test", "file.txt")

        # Verify I/O operations are not available
        assert not hasattr(path, "open")
        assert not hasattr(path, "read_text")
        assert not hasattr(path, "write_text")
        assert not hasattr(path, "mkdir")
        assert not hasattr(path, "exists")

        # But path manipulation should still work
        assert hasattr(path, "name")
        assert hasattr(path, "parent")
        assert hasattr(path, "joinpath")
        assert path.name == "file.txt"

    def test_pantheon_path_enables_safe_path_computations(self) -> None:
        """PantheonPath should allow safe path computations without I/O risk."""
        # Artifact Engine can safely manipulate paths
        base_path = PantheonPath("project", "src")

        # Safe path manipulations that don't perform I/O
        python_file = base_path.joinpath("module.py")
        test_file = python_file.with_suffix(".test.py")

        # Verify computations worked
        assert isinstance(python_file, PantheonPath)
        assert isinstance(test_file, PantheonPath)
        assert str(python_file).endswith("module.py")
        assert str(test_file).endswith(".test.py")

        # But I/O operations are still unavailable
        assert not hasattr(python_file, "read_text")
        assert not hasattr(test_file, "write_text")


class TestArchitecturalBoundaryEnforcement:
    """Test the architectural boundary between computation and I/O."""

    def test_workspace_can_unwrap_pantheon_path_for_io(self) -> None:
        """Workspace component can unwrap PantheonPath to perform I/O."""
        pantheon_path = PantheonPath("test", "file.txt")

        # Workspace can unwrap to get pathlib.Path
        underlying_path = pantheon_path._unwrap()
        assert isinstance(underlying_path, Path)
        assert str(underlying_path).endswith("file.txt")

        # Alternative unwrap method
        underlying_path2 = pantheon_path.get_underlying_path()
        assert isinstance(underlying_path2, Path)
        assert underlying_path == underlying_path2

    def test_computation_layer_receives_pantheon_path_only(self) -> None:
        """Computation layers should only receive PantheonPath, not raw Path."""

        def artifact_engine_function(input_path: PantheonPath) -> PantheonPath:
            """Example Artifact Engine function that processes paths."""
            # Can only perform safe path operations
            return input_path.parent.joinpath("output.txt")

            # Cannot perform I/O operations
            # input_path.read_text()  # This would cause AttributeError
            # output_path.write_text("content")  # This would cause AttributeError

        # Test the function
        input_path = PantheonPath("project", "input.txt")
        result = artifact_engine_function(input_path)

        assert isinstance(result, PantheonPath)
        assert str(result).endswith("output.txt")

        # Verify I/O methods are still unavailable on result
        assert not hasattr(result, "read_text")
        assert not hasattr(result, "write_text")
