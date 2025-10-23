"""Unit tests for path security validation utilities."""

import pytest

from pantheon.path_security import (
    PathSecurityError,
    validate_directory_param,
    validate_import_path,
    validate_path_safety,
    validate_section_path,
)


class TestValidatePathSafety:
    """Tests for the core validate_path_safety function."""

    def test_allows_simple_relative_paths(self):
        """Simple relative paths should pass validation."""
        validate_path_safety("foo/bar.txt")
        validate_path_safety("agents/agent-name.md")
        validate_path_safety("processes/create-ticket/routine.md")

    def test_allows_paths_with_dots_in_filename(self):
        """Paths with dots in filenames (not ..) should pass."""
        validate_path_safety("file.name.with.dots.txt")
        validate_path_safety("foo/bar.baz.md")

    def test_rejects_directory_traversal_double_dot(self):
        """Paths with .. should be rejected."""
        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("../etc/passwd")

        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("foo/../bar")

        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("foo/bar/../../../etc/passwd")

    def test_rejects_url_encoded_traversal(self):
        """URL-encoded .. sequences should be rejected."""
        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("foo%2F..%2Fbar")

        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("%2E%2E/etc/passwd")

    def test_rejects_double_url_encoded_traversal(self):
        """Double URL-encoded .. sequences should be rejected."""
        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("%252E%252E/etc/passwd")

    def test_rejects_unix_absolute_paths(self):
        """Unix-style absolute paths should be rejected by default."""
        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("/etc/passwd")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("/root/.ssh/id_rsa")

    def test_rejects_windows_absolute_paths_colon_style(self):
        """Windows-style absolute paths with drive letters should be rejected."""
        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("C:\\Windows\\System32")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("D:\\secrets\\passwords.txt")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("C:/Windows/System32")

    def test_rejects_windows_absolute_paths_backslash_style(self):
        """Windows-style paths starting with backslash should be rejected."""
        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("\\Windows\\System32")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("\\\\network\\share")

    def test_allows_absolute_paths_when_explicitly_enabled(self):
        """Absolute paths should pass when allow_absolute=True."""
        validate_path_safety("/etc/passwd", allow_absolute=True)
        validate_path_safety("C:\\Windows\\System32", allow_absolute=True)
        validate_path_safety("\\\\network\\share", allow_absolute=True)

    def test_rejects_traversal_even_when_absolute_allowed(self):
        """Directory traversal should be rejected even with allow_absolute=True."""
        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("../etc/passwd", allow_absolute=True)

        with pytest.raises(PathSecurityError, match="Directory traversal"):
            validate_path_safety("/foo/../etc/passwd", allow_absolute=True)

    def test_rejects_empty_paths(self):
        """Empty paths should be rejected."""
        with pytest.raises(PathSecurityError, match="Empty"):
            validate_path_safety("")

    def test_custom_context_in_error_messages(self):
        """Error messages should include the custom context."""
        with pytest.raises(PathSecurityError, match="import path"):
            validate_path_safety("../bad", context="import path")

        with pytest.raises(PathSecurityError, match="section path"):
            validate_path_safety("/absolute", context="section path")

    def test_handles_path_with_trailing_slash(self):
        """Paths with trailing slashes should be validated correctly."""
        validate_path_safety("foo/bar/")
        validate_path_safety("processes/create-ticket/")

    def test_rejects_mixed_traversal_techniques(self):
        """Mixed traversal techniques should all be caught."""
        # Mix of .. and absolute paths
        with pytest.raises(PathSecurityError):
            validate_path_safety("C:/../Windows")

        # Mix of URL-encoded and regular
        with pytest.raises(PathSecurityError):
            validate_path_safety("foo/%2E%2E/bar")


class TestValidateSectionPath:
    """Tests for validate_section_path wrapper function."""

    def test_allows_valid_section_paths(self):
        """Valid section paths should pass."""
        validate_section_path("sections/core")
        validate_section_path("sections/implementation/details")
        validate_section_path("common/header")

    def test_rejects_traversal_in_section_path(self):
        """Section paths with traversal should be rejected."""
        with pytest.raises(ValueError, match="section path"):
            validate_section_path("../sections/core")

        with pytest.raises(ValueError, match="section path"):
            validate_section_path("sections/../../etc/passwd")

    def test_rejects_absolute_section_paths(self):
        """Absolute section paths should be rejected."""
        with pytest.raises(ValueError, match="section path"):
            validate_section_path("/etc/passwd")

        with pytest.raises(ValueError, match="section path"):
            validate_section_path("C:\\Windows\\System32")


class TestValidateImportPath:
    """Tests for validate_import_path wrapper function."""

    def test_allows_valid_import_paths(self):
        """Valid import paths should pass."""
        validate_import_path("common/header.md")
        validate_import_path("templates/base.jinja")
        validate_import_path("schemas/common.jsonnet")

    def test_rejects_traversal_in_import_path(self):
        """Import paths with traversal should be rejected."""
        with pytest.raises(PathSecurityError, match="import path"):
            validate_import_path("../../etc/passwd")

        with pytest.raises(PathSecurityError, match="import path"):
            validate_import_path("../secrets.txt")

    def test_rejects_absolute_import_paths(self):
        """Absolute import paths should be rejected."""
        with pytest.raises(PathSecurityError, match="import path"):
            validate_import_path("/etc/passwd")

        with pytest.raises(PathSecurityError, match="import path"):
            validate_import_path("C:\\secrets\\key.pem")


class TestValidateDirectoryParam:
    """Tests for validate_directory_param wrapper function."""

    def test_allows_valid_directory_params(self):
        """Valid directory parameters should pass."""
        validate_directory_param("tickets/backlog")
        validate_directory_param("agents")
        validate_directory_param("processes/create-ticket/artifact")

    def test_rejects_traversal_in_directory_param(self):
        """Directory params with traversal should be rejected."""
        with pytest.raises(PathSecurityError, match="directory parameter"):
            validate_directory_param("../../../etc")

        with pytest.raises(PathSecurityError, match="directory parameter"):
            validate_directory_param("tickets/../../../root")

    def test_rejects_absolute_directory_params(self):
        """Absolute directory parameters should be rejected."""
        with pytest.raises(PathSecurityError, match="directory parameter"):
            validate_directory_param("/root")

        with pytest.raises(PathSecurityError, match="directory parameter"):
            validate_directory_param("C:\\Windows")


class TestEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_single_dot_is_allowed(self):
        """Single dot (current directory) should be allowed."""
        validate_path_safety("./foo/bar.txt")
        validate_path_safety("foo/./bar.txt")

    def test_multiple_dots_in_filename_allowed(self):
        """Multiple dots in filename (not ..) should be allowed."""
        validate_path_safety("file...txt")
        validate_path_safety("foo.bar.baz.qux.md")

    def test_handles_unicode_normalization(self):
        """Unicode paths should be handled safely."""
        validate_path_safety("foo/\u0062ar.txt")  # Unicode 'b'
        validate_path_safety("processes/\u0063reate-ticket/routine.md")  # Unicode 'c'

    def test_rejects_null_byte_injection(self):
        """Null bytes in paths should be handled safely."""
        # Note: Python's pathlib might handle this, but we test it anyway
        # Some systems might interpret null bytes as path terminators
        validate_path_safety("foo\x00bar.txt")  # Should not crash

    def test_windows_drive_letter_case_insensitive(self):
        """Windows drive letters should be caught regardless of case."""
        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("c:\\windows")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("C:\\windows")

        with pytest.raises(PathSecurityError, match="Absolute paths"):
            validate_path_safety("d:\\data")
