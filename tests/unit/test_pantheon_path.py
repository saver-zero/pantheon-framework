"""Tests for the PantheonPath protection proxy class.

This module contains unit tests that verify PantheonPath acts as a protection
proxy around pathlib.Path, providing path manipulation while preventing I/O
operations to enforce architectural boundaries.
"""

from pathlib import Path

# This import will fail initially - that's expected for TDD
from pantheon.path import PantheonPath


class TestPantheonPathCreation:
    """Test PantheonPath can be created from various path inputs."""

    def test_pantheon_path_can_be_created_from_string(self) -> None:
        """PantheonPath should be creatable from string path."""
        path = PantheonPath("test/path")
        assert path is not None
        assert isinstance(path, PantheonPath)

    def test_pantheon_path_rejects_path_object_input(self) -> None:
        """PantheonPath should reject pathlib.Path objects per T015."""
        import pytest

        pathlib_path = Path("test/path")
        with pytest.raises(ValueError, match="All path segments must be strings"):
            PantheonPath(pathlib_path)

    def test_pantheon_path_can_be_created_from_segments(self) -> None:
        """PantheonPath should be creatable from path segments."""
        path = PantheonPath("test", "sub", "file.txt")
        assert path is not None
        assert isinstance(path, PantheonPath)


class TestPantheonPathT015Constraints:
    """Test PantheonPath enforces T015 constraints for security boundaries."""

    def test_rejects_absolute_unix_paths(self) -> None:
        """PantheonPath should reject absolute Unix-style paths per T015."""
        from pathlib import Path

        import pytest

        # Only test if we're on a Unix-like system where / is absolute
        if Path("/").is_absolute():
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath("/absolute/path")
        else:
            # On Windows, test with UNC path which is always absolute
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath("//server/share/path")

    def test_rejects_absolute_windows_paths(self) -> None:
        """PantheonPath should reject absolute Windows paths per T015."""
        import platform

        import pytest

        # On Windows, this will be rejected; on Unix, it's a relative path
        if platform.system() == "Windows":
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath("C:\\Windows\\System32")
        else:
            # On Unix systems, Windows paths are treated as relative paths
            # So we test Unix absolute paths instead
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath("/usr/bin")

    def test_rejects_empty_arguments(self) -> None:
        """PantheonPath should require at least one path segment per T015."""
        import pytest

        with pytest.raises(ValueError, match="requires at least one path segment"):
            PantheonPath()

    def test_rejects_mixed_type_arguments(self) -> None:
        """PantheonPath should reject mixed string/non-string arguments per T015."""
        import pytest

        with pytest.raises(ValueError, match="All path segments must be strings"):
            PantheonPath("test", 123, "file.txt")

    def test_rejects_integer_arguments(self) -> None:
        """PantheonPath should reject integer arguments per T015."""
        import pytest

        with pytest.raises(ValueError, match="All path segments must be strings"):
            PantheonPath(123)

    def test_accepts_relative_paths(self) -> None:
        """PantheonPath should accept relative paths per T015."""
        # These should all work
        path1 = PantheonPath("relative/path")
        path2 = PantheonPath("test", "sub", "file.txt")
        path3 = PantheonPath("single-segment")

        assert isinstance(path1, PantheonPath)
        assert isinstance(path2, PantheonPath)
        assert isinstance(path3, PantheonPath)

        # All should be relative
        assert not path1.is_absolute()
        assert not path2.is_absolute()
        assert not path3.is_absolute()


class TestPantheonPathProperties:
    """Test PantheonPath exposes safe path properties."""

    def setup_method(self) -> None:
        """Set up PantheonPath instance for testing."""
        self.path = PantheonPath("test", "sub", "file.txt")

    def test_name_property_exists(self) -> None:
        """PantheonPath should expose name property."""
        assert hasattr(self.path, "name")
        assert self.path.name == "file.txt"

    def test_stem_property_exists(self) -> None:
        """PantheonPath should expose stem property."""
        assert hasattr(self.path, "stem")
        assert self.path.stem == "file"

    def test_suffix_property_exists(self) -> None:
        """PantheonPath should expose suffix property."""
        assert hasattr(self.path, "suffix")
        assert self.path.suffix == ".txt"

    def test_parent_property_exists(self) -> None:
        """PantheonPath should expose parent property."""
        assert hasattr(self.path, "parent")
        parent = self.path.parent
        assert isinstance(parent, PantheonPath)
        assert str(parent).endswith("sub")

    def test_parts_property_exists(self) -> None:
        """PantheonPath should expose parts property."""
        assert hasattr(self.path, "parts")
        parts = self.path.parts
        assert isinstance(parts, tuple)
        assert "test" in parts
        assert "sub" in parts
        assert "file.txt" in parts


class TestPantheonPathMethods:
    """Test PantheonPath exposes safe path manipulation methods."""

    def setup_method(self) -> None:
        """Set up PantheonPath instance for testing."""
        self.path = PantheonPath("test", "sub")

    def test_joinpath_method_exists(self) -> None:
        """PantheonPath should have joinpath method."""
        assert hasattr(self.path, "joinpath")
        assert callable(self.path.joinpath)

        new_path = self.path.joinpath("file.txt")
        assert isinstance(new_path, PantheonPath)
        assert str(new_path).endswith("file.txt")

    def test_with_suffix_method_exists(self) -> None:
        """PantheonPath should have with_suffix method."""
        file_path = PantheonPath("test", "file.txt")
        assert hasattr(file_path, "with_suffix")
        assert callable(file_path.with_suffix)

        new_path = file_path.with_suffix(".py")
        assert isinstance(new_path, PantheonPath)
        assert str(new_path).endswith(".py")

    def test_relative_to_method_exists(self) -> None:
        """PantheonPath should have relative_to method."""
        assert hasattr(self.path, "relative_to")
        assert callable(self.path.relative_to)

    def test_is_absolute_method_exists(self) -> None:
        """PantheonPath should have is_absolute method."""
        assert hasattr(self.path, "is_absolute")
        assert callable(self.path.is_absolute)

        result = self.path.is_absolute()
        assert isinstance(result, bool)


class TestPantheonPathIORestrictions:
    """Test PantheonPath prevents I/O operations to enforce boundaries."""

    def setup_method(self) -> None:
        """Set up PantheonPath instance for testing."""
        self.path = PantheonPath("test", "file.txt")

    def test_open_method_does_not_exist(self) -> None:
        """PantheonPath should not have open() method."""
        assert not hasattr(self.path, "open")

    def test_read_text_method_does_not_exist(self) -> None:
        """PantheonPath should not have read_text() method."""
        assert not hasattr(self.path, "read_text")

    def test_write_text_method_does_not_exist(self) -> None:
        """PantheonPath should not have write_text() method."""
        assert not hasattr(self.path, "write_text")

    def test_read_bytes_method_does_not_exist(self) -> None:
        """PantheonPath should not have read_bytes() method."""
        assert not hasattr(self.path, "read_bytes")

    def test_write_bytes_method_does_not_exist(self) -> None:
        """PantheonPath should not have write_bytes() method."""
        assert not hasattr(self.path, "write_bytes")

    def test_mkdir_method_does_not_exist(self) -> None:
        """PantheonPath should not have mkdir() method."""
        assert not hasattr(self.path, "mkdir")

    def test_rmdir_method_does_not_exist(self) -> None:
        """PantheonPath should not have rmdir() method."""
        assert not hasattr(self.path, "rmdir")

    def test_unlink_method_does_not_exist(self) -> None:
        """PantheonPath should not have unlink() method."""
        assert not hasattr(self.path, "unlink")

    def test_exists_method_does_not_exist(self) -> None:
        """PantheonPath should not have exists() method."""
        assert not hasattr(self.path, "exists")

    def test_iterdir_method_does_not_exist(self) -> None:
        """PantheonPath should not have iterdir() method."""
        assert not hasattr(self.path, "iterdir")


class TestPantheonPathValueObjectSemantics:
    """Test PantheonPath behaves as an immutable value object."""

    def test_equality_comparison_works(self) -> None:
        """PantheonPath should support equality comparison."""
        path1 = PantheonPath("test", "file.txt")
        path2 = PantheonPath("test", "file.txt")
        path3 = PantheonPath("other", "file.txt")

        assert path1 == path2
        assert path1 != path3
        assert path2 != path3

    def test_hash_works_for_sets_and_dicts(self) -> None:
        """PantheonPath should be hashable for use in sets and as dict keys."""
        path1 = PantheonPath("test", "file.txt")
        path2 = PantheonPath("test", "file.txt")
        path3 = PantheonPath("other", "file.txt")

        # Test in sets
        path_set = {path1, path2, path3}
        assert len(path_set) == 2  # path1 and path2 are equal

        # Test as dict keys
        path_dict = {path1: "value1", path3: "value2"}
        assert len(path_dict) == 2
        assert path_dict[path2] == "value1"  # path2 equals path1

    def test_string_representation_works(self) -> None:
        """PantheonPath should have string representation."""
        path = PantheonPath("test", "file.txt")
        str_repr = str(path)
        assert isinstance(str_repr, str)
        assert "test" in str_repr
        assert "file.txt" in str_repr

    def test_repr_representation_works(self) -> None:
        """PantheonPath should have repr representation."""
        path = PantheonPath("test", "file.txt")
        repr_str = repr(path)
        assert isinstance(repr_str, str)
        assert "PantheonPath" in repr_str


class TestPantheonPathUnwrapAccess:
    """Test PantheonPath provides controlled access to underlying Path."""

    def setup_method(self) -> None:
        """Set up PantheonPath instance for testing."""
        self.path = PantheonPath("test", "file.txt")

    def test_unwrap_method_exists(self) -> None:
        """PantheonPath should have method to access underlying Path."""
        # This could be _unwrap() or get_underlying_path() - check for either
        has_unwrap = hasattr(self.path, "_unwrap") or hasattr(
            self.path, "get_underlying_path"
        )
        assert has_unwrap, "PantheonPath should have unwrap method for Workspace access"

    def test_unwrap_returns_pathlib_path(self) -> None:
        """Unwrap method should return actual pathlib.Path object."""
        if hasattr(self.path, "_unwrap"):
            underlying = self.path._unwrap()
        else:
            underlying = self.path.get_underlying_path()

        assert isinstance(underlying, Path)
        assert str(underlying).endswith("file.txt")
