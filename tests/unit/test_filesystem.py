"""Unit tests for FileSystem I/O abstraction interface.

This test module defines the fundamental behavior expected from the FileSystem
component. The tests use mocks to verify that FileSystem properly wraps
standard library I/O operations without performing actual file system access.

These tests are designed to fail with NotImplementedError since FileSystem
contains only interface definitions. They serve as behavioral contracts for
Phase 2 TDD implementation.
"""

from pathlib import Path

from pantheon.filesystem import FileSystem


class TestFileSystem:
    """Test cases for FileSystem I/O abstraction behavior."""

    def test_read_text_success_with_temp_file(self, tmp_path):
        """Test that read_text successfully reads content from a real file."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content, encoding="utf-8")

        # Act
        result = filesystem.read_text(test_file)

        # Assert
        assert result == test_content

    def test_read_text_with_string_path(self, tmp_path):
        """Test that read_text accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content, encoding="utf-8")

        # Act
        result = filesystem.read_text(str(test_file))

        # Assert
        assert result == test_content

    def test_read_text_file_not_found_error(self):
        """Test that read_text raises FileNotFoundError for non-existent file."""
        # Arrange
        filesystem = FileSystem()
        non_existent_path = Path("/non/existent/file.txt")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            filesystem.read_text(non_existent_path)

    def test_read_text_with_custom_encoding(self, tmp_path):
        """Test that read_text respects encoding parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_content = "Test content with encoding"
        test_file.write_text(test_content, encoding="utf-8")

        # Act
        result = filesystem.read_text(test_file, encoding="utf-8")

        # Assert
        assert result == test_content

    def test_write_text_creates_file_with_content(self, tmp_path):
        """Test that write_text creates file with correct content."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "output.txt"
        test_content = "Content to write"

        # Act
        filesystem.write_text(test_file, test_content)

        # Assert
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_write_text_with_string_path(self, tmp_path):
        """Test that write_text accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "output.txt"
        test_content = "String path content"

        # Act
        filesystem.write_text(str(test_file), test_content)

        # Assert
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_write_text_parent_directory_missing_error(self):
        """Test that write_text raises FileNotFoundError when parent directory missing."""
        # Arrange
        filesystem = FileSystem()
        non_existent_parent = Path("/non/existent/dir/file.txt")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            filesystem.write_text(non_existent_parent, "content")

    def test_write_text_with_custom_encoding(self, tmp_path):
        """Test that write_text respects encoding parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "encoded.txt"
        test_content = "Encoded content"

        # Act
        filesystem.write_text(test_file, test_content, encoding="utf-8")

        # Assert
        assert test_file.read_text(encoding="utf-8") == test_content

    def test_exists_returns_true_for_existing_file(self, tmp_path):
        """Test that exists returns True for existing file."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "existing.txt"
        test_file.write_text("content")

        # Act
        result = filesystem.exists(test_file)

        # Assert
        assert result is True

    def test_exists_returns_true_for_existing_directory(self, tmp_path):
        """Test that exists returns True for existing directory."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()

        # Act
        result = filesystem.exists(test_dir)

        # Assert
        assert result is True

    def test_exists_returns_false_for_non_existent_path(self):
        """Test that exists returns False for non-existent path."""
        # Arrange
        filesystem = FileSystem()
        non_existent_path = Path("/non/existent/path")

        # Act
        result = filesystem.exists(non_existent_path)

        # Assert
        assert result is False

    def test_exists_handles_string_path(self, tmp_path):
        """Test that exists accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act
        result = filesystem.exists(str(test_file))

        # Assert
        assert result is True

    def test_mkdir_creates_simple_directory(self, tmp_path):
        """Test that mkdir creates directory successfully."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "new_dir"

        # Act
        filesystem.mkdir(test_dir)

        # Assert
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_mkdir_with_parents_creates_nested_directories(self, tmp_path):
        """Test that mkdir with parents=True creates nested directories."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "parent" / "child"

        # Act
        filesystem.mkdir(test_dir, parents=True)

        # Assert
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert test_dir.parent.exists()

    def test_mkdir_with_exist_ok_doesnt_raise_on_existing(self, tmp_path):
        """Test that mkdir with exist_ok=True doesn't raise on existing directory."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()

        # Act
        filesystem.mkdir(test_dir, exist_ok=True)

        # Assert - No exception should be raised
        assert test_dir.exists()

    def test_mkdir_raises_file_exists_error_when_exist_ok_false(self, tmp_path):
        """Test that mkdir raises FileExistsError when exist_ok=False and dir exists."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()

        # Act & Assert
        import pytest

        with pytest.raises(FileExistsError):
            filesystem.mkdir(test_dir, exist_ok=False)

    def test_mkdir_with_string_path(self, tmp_path):
        """Test that mkdir accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "string_dir"

        # Act
        filesystem.mkdir(str(test_dir))

        # Assert
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_iterdir_returns_directory_contents(self, tmp_path):
        """Test that iterdir returns Path objects for directory contents."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        (test_dir / "subdir").mkdir()

        # Act
        contents = list(filesystem.iterdir(test_dir))

        # Assert
        assert len(contents) == 3
        content_names = {path.name for path in contents}
        assert content_names == {"file1.txt", "file2.txt", "subdir"}
        assert all(isinstance(path, Path) for path in contents)

    def test_iterdir_with_string_path(self, tmp_path):
        """Test that iterdir accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "test_file.txt").write_text("content")

        # Act
        contents = list(filesystem.iterdir(str(test_dir)))

        # Assert
        assert len(contents) == 1
        assert contents[0].name == "test_file.txt"

    def test_iterdir_raises_file_not_found_error(self):
        """Test that iterdir raises FileNotFoundError for non-existent directory."""
        # Arrange
        filesystem = FileSystem()
        non_existent_dir = Path("/non/existent/directory")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            list(filesystem.iterdir(non_existent_dir))

    def test_iterdir_raises_not_a_directory_error(self, tmp_path):
        """Test that iterdir raises NotADirectoryError when path is a file."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act & Assert
        import pytest

        with pytest.raises(NotADirectoryError):
            list(filesystem.iterdir(test_file))

    def test_iterdir_returns_empty_iterator_for_empty_directory(self, tmp_path):
        """Test that iterdir returns empty iterator for empty directory."""
        # Arrange
        filesystem = FileSystem()
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()

        # Act
        contents = list(filesystem.iterdir(empty_dir))

        # Assert
        assert len(contents) == 0

    def test_rmdir_removes_empty_directory(self, tmp_path):
        """Test that rmdir removes empty directory successfully."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "empty_dir"
        test_dir.mkdir()

        # Act
        filesystem.rmdir(test_dir)

        # Assert
        assert not test_dir.exists()

    def test_rmdir_with_string_path(self, tmp_path):
        """Test that rmdir accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "empty_dir"
        test_dir.mkdir()

        # Act
        filesystem.rmdir(str(test_dir))

        # Assert
        assert not test_dir.exists()

    def test_rmdir_raises_file_not_found_error(self):
        """Test that rmdir raises FileNotFoundError for non-existent directory."""
        # Arrange
        filesystem = FileSystem()
        non_existent_dir = Path("/non/existent/directory")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            filesystem.rmdir(non_existent_dir)

    def test_rmdir_raises_os_error_for_non_empty_directory(self, tmp_path):
        """Test that rmdir raises OSError when directory is not empty."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "non_empty_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        # Act & Assert
        import pytest

        with pytest.raises(OSError):
            filesystem.rmdir(test_dir)

    def test_unlink_removes_file_successfully(self, tmp_path):
        """Test that unlink removes file successfully."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act
        filesystem.unlink(test_file)

        # Assert
        assert not test_file.exists()

    def test_unlink_with_string_path(self, tmp_path):
        """Test that unlink accepts string path parameter."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act
        filesystem.unlink(str(test_file))

        # Assert
        assert not test_file.exists()

    def test_unlink_with_missing_ok_true_ignores_missing_file(self):
        """Test that unlink with missing_ok=True ignores missing files."""
        # Arrange
        filesystem = FileSystem()
        non_existent_file = Path("/non/existent/file.txt")

        # Act - Should not raise exception
        filesystem.unlink(non_existent_file, missing_ok=True)

        # Assert - No exception should be raised

    def test_unlink_raises_file_not_found_error_when_missing_ok_false(self):
        """Test that unlink raises FileNotFoundError when missing_ok=False."""
        # Arrange
        filesystem = FileSystem()
        non_existent_file = Path("/non/existent/file.txt")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            filesystem.unlink(non_existent_file, missing_ok=False)

    def test_unlink_raises_is_a_directory_error_for_directory(self, tmp_path):
        """Test that unlink raises IsADirectoryError for directory paths."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Act & Assert
        import pytest

        # On Windows, pathlib raises PermissionError instead of IsADirectoryError
        # Both are acceptable as they indicate the operation failed on a directory
        with pytest.raises((IsADirectoryError, PermissionError)):
            filesystem.unlink(test_dir)

    # Edge case tests for path parameter type handling
    def test_all_methods_handle_path_objects(self, tmp_path):
        """Test all methods correctly handle Path objects."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "path_test.txt"
        test_dir = tmp_path / "path_dir"

        # Act & Assert - All should work with Path objects
        filesystem.write_text(test_file, "content")
        assert filesystem.read_text(test_file) == "content"
        assert filesystem.exists(test_file) is True

        filesystem.mkdir(test_dir)
        assert filesystem.exists(test_dir) is True

        contents = list(filesystem.iterdir(tmp_path))
        assert len(contents) >= 2

        filesystem.rmdir(test_dir)
        filesystem.unlink(test_file)

    def test_all_methods_handle_string_paths(self, tmp_path):
        """Test all methods correctly handle string paths."""
        # Arrange
        filesystem = FileSystem()
        test_file = str(tmp_path / "string_test.txt")
        test_dir = str(tmp_path / "string_dir")

        # Act & Assert - All should work with string paths
        filesystem.write_text(test_file, "content")
        assert filesystem.read_text(test_file) == "content"
        assert filesystem.exists(test_file) is True

        filesystem.mkdir(test_dir)
        assert filesystem.exists(test_dir) is True

        contents = list(filesystem.iterdir(str(tmp_path)))
        assert len(contents) >= 2

        filesystem.rmdir(test_dir)
        filesystem.unlink(test_file)

    def test_glob_returns_matching_files_in_directory(self, tmp_path):
        """Test that glob successfully returns list of Path objects matching pattern in existing directory."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "glob_test"
        test_dir.mkdir()
        (test_dir / "file1.md").write_text("content1")
        (test_dir / "file2.md").write_text("content2")
        (test_dir / "file3.txt").write_text("content3")
        (test_dir / "subdir").mkdir()

        # Act
        result = filesystem.glob(test_dir, "*.md")

        # Assert
        assert len(result) == 2
        result_names = {path.name for path in result}
        assert result_names == {"file1.md", "file2.md"}
        assert all(isinstance(path, Path) for path in result)

    def test_glob_accepts_both_path_and_string_parameters(self, tmp_path):
        """Test that glob method accepts both Path objects and string paths for directory parameter."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "string_test"
        test_dir.mkdir()
        (test_dir / "test1.py").write_text("code1")
        (test_dir / "test2.py").write_text("code2")

        # Act - Test with Path object
        result_path = filesystem.glob(test_dir, "*.py")
        # Act - Test with string
        result_string = filesystem.glob(str(test_dir), "*.py")

        # Assert - Both should return identical results
        assert len(result_path) == 2
        assert len(result_string) == 2
        assert {p.name for p in result_path} == {p.name for p in result_string}

    def test_glob_returns_empty_list_when_no_files_match_pattern(self, tmp_path):
        """Test that glob method returns empty list when no files match the pattern in valid directory."""
        # Arrange
        filesystem = FileSystem()
        test_dir = tmp_path / "empty_match"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")

        # Act
        result = filesystem.glob(test_dir, "*.md")

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_glob_raises_file_not_found_error_for_non_existent_directory(self):
        """Test that glob method raises FileNotFoundError for non-existent directory."""
        # Arrange
        filesystem = FileSystem()
        non_existent_dir = Path("/non/existent/directory")

        # Act & Assert
        import pytest

        with pytest.raises(FileNotFoundError):
            filesystem.glob(non_existent_dir, "*.txt")

    def test_glob_raises_not_a_directory_error_when_path_is_file(self, tmp_path):
        """Test that glob method raises NotADirectoryError when path points to a file instead of directory."""
        # Arrange
        filesystem = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act & Assert
        import pytest

        with pytest.raises(NotADirectoryError):
            filesystem.glob(test_file, "*.txt")

    def test_filesystem_as_mockable_dependency_integration(self):
        """Integration test demonstrating FileSystem as mockable dependency for higher-level components."""
        from unittest.mock import Mock

        # Arrange - Create mock FileSystem
        mock_filesystem = Mock(spec=FileSystem)
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = "mocked content"
        mock_filesystem.iterdir.return_value = iter(
            [Path("file1.txt"), Path("file2.txt")]
        )

        # This simulates how PantheonWorkspace would use FileSystem
        class MockWorkspace:
            def __init__(self, filesystem: FileSystem):
                self.filesystem = filesystem

            def check_project_exists(self, path: Path) -> bool:
                return self.filesystem.exists(path)

            def load_config(self, config_path: Path) -> str:
                return self.filesystem.read_text(config_path)

            def list_files(self, directory: Path) -> list[Path]:
                return list(self.filesystem.iterdir(directory))

        # Act - Use mock FileSystem in higher-level component
        workspace = MockWorkspace(mock_filesystem)

        project_exists = workspace.check_project_exists(Path("/project"))
        config_content = workspace.load_config(Path("/config.yaml"))
        files = workspace.list_files(Path("/directory"))

        # Assert - Verify mock was used correctly
        assert project_exists is True
        assert config_content == "mocked content"
        assert len(files) == 2
        assert files[0].name == "file1.txt"

        # Verify mock interactions
        mock_filesystem.exists.assert_called_once_with(Path("/project"))
        mock_filesystem.read_text.assert_called_once_with(Path("/config.yaml"))
        mock_filesystem.iterdir.assert_called_once_with(Path("/directory"))

        # This test serves as documentation - FileSystem interface specifies Path | str only
        # PantheonPath interaction is handled at the PantheonWorkspace level
        # No actual test implementation needed as type hints enforce this
