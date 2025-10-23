"""Unit tests for PantheonWorkspace security and sandboxing validation.

This test suite validates active team sandboxing, directory traversal prevention,
and path security across all workspace operations. Tests cover the two-sandbox model
where source is isolated but artifacts are shared, following T015 security requirements.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from pantheon.filesystem import FileSystem
from pantheon.path import PantheonPath
from pantheon.workspace import PantheonWorkspace, ProjectConfig, SecurityError

# Function removed - using proper pathlib operations instead


class TestPantheonWorkspaceSecurity:
    """Test suite for PantheonWorkspace security and sandboxing validation."""

    @pytest.fixture
    def mock_filesystem(self) -> Mock:
        """Create a mock FileSystem for dependency injection.

        Returns:
            Mock FileSystem with spec to ensure proper interface usage
        """
        return Mock(spec=FileSystem)

    @pytest.fixture
    def sample_paths(self) -> dict[str, str]:
        """Create sample path instances for testing.

        Returns:
            Dictionary of named path instances for test scenarios
        """
        return {
            "project_root_str": "/test/project",
            "artifacts_root_str": "/test/project/pantheon-artifacts",
        }

    @pytest.fixture
    def workspace_team_a(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> PantheonWorkspace:
        """Create workspace configured for team-a.

        Args:
            mock_filesystem: Mocked FileSystem dependency
            sample_paths: Sample path instances

        Returns:
            PantheonWorkspace configured with team-a as active team
        """
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        workspace._project_config = ProjectConfig(
            active_team="team-a", artifacts_root="pantheon-artifacts"
        )

        return workspace

    @pytest.fixture
    def workspace_team_b(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> PantheonWorkspace:
        """Create workspace configured for team-b.

        Args:
            mock_filesystem: Mocked FileSystem dependency
            sample_paths: Sample path instances

        Returns:
            PantheonWorkspace configured with team-b as active team
        """
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        workspace._project_config = ProjectConfig(
            active_team="team-b", artifacts_root="pantheon-artifacts"
        )

        return workspace

    @pytest.fixture
    def malicious_paths(self) -> dict[str, str]:
        """Create malicious path examples for security testing.

        Returns:
            Dictionary mapping attack types to malicious path strings
        """
        return {
            "basic_traversal": "../../../etc/passwd",
            "windows_traversal": "..\\..\\..\\Windows\\System32\\config",
            "encoded_traversal": "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "double_encoded": "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "unicode_traversal": "..\u002e\u002f..\u002e\u002f..\u002e\u002fetc\u002fpasswd",
            "mixed_separators": "../..\\..\\etc/passwd",
            "multiple_traversal": "../../../../../../../../etc/passwd",
            "traversal_with_nulls": "../../../etc/passwd\x00.txt",
            "relative_absolute": "./../../etc/passwd",
            "current_dir_traversal": "./../../../etc/passwd",
        }

    @pytest.fixture
    def safe_relative_paths(self) -> list[str]:
        """Create safe relative path examples.

        Returns:
            List of safe relative paths that should be allowed
        """
        return [
            "safe/relative/path.txt",
            "documents/file.md",
            "nested/directory/structure/file.json",
            "simple-file.txt",
            "file_with_underscores.yaml",
            "file.with.dots.txt",
            "123-numeric-prefix.txt",
            "UPPERCASE_FILE.TXT",
            "mixed-Case_File.123",
        ]

    # Path Security Validation Tests

    @pytest.mark.parametrize(
        "attack_path",
        [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32",
            "../../../../../../../../etc/shadow",
            "../.ssh/id_rsa",
            "..\\..\\Windows\\System32\\config\\SAM",
        ],
    )
    def test_validate_path_security_blocks_directory_traversal(
        self, workspace_team_a: PantheonWorkspace, attack_path: str
    ) -> None:
        """Test _validate_path_security prevents directory traversal attacks.

        Tests various directory traversal sequences are blocked with SecurityError.
        """
        malicious_path = PantheonPath(attack_path)

        with pytest.raises(SecurityError, match="Directory traversal not allowed"):
            workspace_team_a._validate_path_security(malicious_path)

    def test_validate_path_security_prevents_absolute_paths_via_pantheon_path(
        self, workspace_team_a: PantheonWorkspace
    ) -> None:
        """Test PantheonPath construction prevents absolute paths per T015.

        Verifies that absolute paths cannot be created as PantheonPath objects,
        maintaining the T015 security constraint at the type level.
        """
        import os

        # Use one platform-appropriate absolute path
        absolute_path = "C:\\temp" if os.name == "nt" else "/tmp"

        with pytest.raises(ValueError, match="must represent a relative path"):
            PantheonPath(absolute_path)

    def test_validate_path_security_handles_encoded_traversal_attempts(
        self, workspace_team_a: PantheonWorkspace, malicious_paths: dict[str, str]
    ) -> None:
        """Test _validate_path_security catches URL-encoded traversal attempts.

        Tests URL-encoded directory traversal attempts are detected after decoding.
        Note: Unicode escapes in Python string literals are processed at parse time,
        so paths like "..\u002e\u002f" become ".../" (safe) not "../" (dangerous).
        """
        # URL-encoded paths that will be decoded and caught
        url_encoded_attacks = [
            malicious_paths["encoded_traversal"],  # %2e%2e%2f -> ../
            malicious_paths["double_encoded"],  # %252e%252e%252f -> ../
        ]

        for encoded_path in url_encoded_attacks:
            # These may fail at PantheonPath construction or validation
            try:
                malicious_path = PantheonPath(encoded_path)
                with pytest.raises(SecurityError):
                    workspace_team_a._validate_path_security(malicious_path)
            except ValueError:
                # If PantheonPath construction fails, that's also acceptable security
                pass

        # Unicode literals in Python strings are resolved at parse time, not runtime
        # "..\u002e\u002f" becomes ".../" which is safe (not directory traversal)
        unicode_path = malicious_paths["unicode_traversal"]  # Results in ".../.../..."
        safe_path = PantheonPath(unicode_path)  # Should not raise
        workspace_team_a._validate_path_security(safe_path)  # Should not raise

    def test_validate_path_security_blocks_embedded_nulls(
        self, workspace_team_a: PantheonWorkspace, malicious_paths: dict[str, str]
    ) -> None:
        """Test _validate_path_security handles paths with embedded nulls.

        Tests null byte injection attempts are handled appropriately.
        """
        null_attack = malicious_paths["traversal_with_nulls"]

        # May fail at construction or validation - both are acceptable
        try:
            malicious_path = PantheonPath(null_attack)
            with pytest.raises(SecurityError):
                workspace_team_a._validate_path_security(malicious_path)
        except (ValueError, TypeError):
            # If construction fails due to null bytes, that's acceptable security
            pass

    @pytest.mark.parametrize(
        "safe_path",
        [
            "safe/relative/path.txt",
            "documents/report.md",
            "nested/structure/file.json",
            "simple.txt",
        ],
    )
    def test_validate_path_security_allows_safe_relative_paths(
        self, workspace_team_a: PantheonWorkspace, safe_path: str
    ) -> None:
        """Test _validate_path_security allows safe relative paths.

        Tests normal relative paths without traversal sequences are accepted.
        """
        safe_pantheon_path = PantheonPath(safe_path)

        # Should not raise any exception
        workspace_team_a._validate_path_security(safe_pantheon_path)

    # Active Team Sandboxing Tests

    def test_active_team_cannot_read_other_team_process_files(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test team-a cannot read team-b process files.

        Tests active team isolation prevents accessing other team's source code.
        """
        # team-a workspace trying to access team-b processes should be impossible
        # through normal API since paths are constructed relative to active team

        # Verify that get_process_schema constructs paths within team-a
        mock_filesystem.read_text.return_value = "schema content"

        result = workspace_team_a.get_process_schema("some-process")

        assert result == "schema content"
        call_args = mock_filesystem.read_text.call_args[0][0]
        actual_path = Path(str(call_args))
        assert "pantheon-teams" in actual_path.parts
        assert "team-a" in actual_path.parts
        assert "team-b" not in actual_path.parts

    def test_active_team_can_only_access_own_processes(
        self,
        workspace_team_a: PantheonWorkspace,
        workspace_team_b: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test active team can only access processes in own team directory.

        Tests team boundary enforcement through path construction validation.
        """
        mock_filesystem.read_text.return_value = "team content"

        # Team A access
        result_a = workspace_team_a.get_process_schema("test-process")
        call_args_a = mock_filesystem.read_text.call_args[0][0]
        path_str_a = str(call_args_a)

        # Reset mock for Team B
        mock_filesystem.reset_mock()
        mock_filesystem.read_text.return_value = "team content"

        # Team B access
        result_b = workspace_team_b.get_process_schema("test-process")
        call_args_b = mock_filesystem.read_text.call_args[0][0]
        path_str_b = str(call_args_b)

        # Both get content but from their respective team directories
        assert result_a == "team content"
        assert result_b == "team content"
        actual_path_a = Path(str(call_args_a))
        assert "pantheon-teams" in actual_path_a.parts
        assert "team-a" in actual_path_a.parts
        actual_path_b = Path(str(call_args_b))
        assert "pantheon-teams" in actual_path_b.parts
        assert "team-b" in actual_path_b.parts
        assert path_str_a != path_str_b  # Different paths for different teams

    def test_shared_artifacts_root_accessible_to_all_teams(
        self,
        workspace_team_a: PantheonWorkspace,
        workspace_team_b: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test shared artifacts root is accessible to all teams.

        Tests the two-sandbox model where artifacts are shared across teams
        but source code is isolated.
        """
        artifact_path = PantheonPath("shared/output.txt")
        content = "shared artifact content"

        # Mock directory doesn't exist initially
        mock_filesystem.exists.return_value = True

        # Both teams should be able to save to artifacts root
        result_a = workspace_team_a.save_artifact(content, artifact_path)
        mock_filesystem.reset_mock()
        mock_filesystem.exists.return_value = True

        result_b = workspace_team_b.save_artifact(content, artifact_path)

        # Both should succeed and save to the same artifacts area
        assert Path(str(result_a)).as_posix() == "shared/output.txt"
        assert Path(str(result_b)).as_posix() == "shared/output.txt"

    def test_security_error_includes_clear_message_for_boundary_violations(
        self, workspace_team_a: PantheonWorkspace
    ) -> None:
        """Test SecurityError includes clear message for boundary violations.

        Tests security errors provide helpful context about what was blocked.
        """
        malicious_path = PantheonPath("../../../sensitive/file.txt")

        with pytest.raises(SecurityError) as exc_info:
            workspace_team_a._validate_path_security(malicious_path)

        error_message = str(exc_info.value)
        assert "Directory traversal not allowed" in error_message
        assert (
            "../" in error_message or "..\\" in error_message
        )  # Should include the problematic pattern

    def test_team_boundary_enforcement_in_content_retrieval_methods(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test boundary enforcement in all content-retrieval methods.

        Tests all content-retrieval methods construct paths within team boundaries.
        """
        mock_filesystem.read_text.return_value = "content"

        # Test multiple content methods
        content_methods = [
            ("get_process_schema", "test-process"),
            ("get_process_routine", "test-process"),
            ("get_artifact_locator", "test-process"),
            ("get_permissions", "test-process"),
        ]

        for method_name, process_name in content_methods:
            method = getattr(workspace_team_a, method_name)
            method(process_name)

            call_args = mock_filesystem.read_text.call_args[0][0]
            actual_path = Path(str(call_args))
            assert "pantheon-teams" in actual_path.parts
            assert "team-a" in actual_path.parts
            mock_filesystem.reset_mock()
            mock_filesystem.read_text.return_value = "content"

    # Save Artifact Security Tests

    def test_save_artifact_paths_cannot_escape_artifacts_root(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test save_artifact paths cannot escape artifacts_root sandbox.

        Tests artifact saving with traversal attempts raises SecurityError at workspace level.
        """
        # These should succeed at PantheonPath construction but fail at save_artifact
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\config",
            "../../../../sensitive.txt",
        ]

        content = "malicious content"

        for attack_path in traversal_attempts:
            # PantheonPath allows these (they're still relative paths)
            pantheon_path = PantheonPath(attack_path)
            # But workspace security validation rejects them
            with pytest.raises(SecurityError, match="Directory traversal not allowed"):
                workspace_team_a.save_artifact(content, pantheon_path)

    def test_save_artifact_rejects_absolute_paths_through_pantheon_path(
        self,
        workspace_team_a: PantheonWorkspace,
    ) -> None:
        """Test save_artifact rejects absolute paths via PantheonPath validation.

        Tests absolute paths are rejected at PantheonPath construction level.
        """
        import platform

        if platform.system() == "Windows":
            absolute_paths = [
                "C:\\etc\\passwd",
                "C:\\Windows\\System32\\config",
                "D:\\root\\.ssh\\id_rsa",
            ]
        else:
            absolute_paths = [
                "/etc/passwd",
                "/home/user/.ssh/id_rsa",
                "/var/log/system.log",
            ]

        for abs_path in absolute_paths:
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath(abs_path)

    def test_save_artifact_nested_directory_creation_stays_in_sandbox(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test save_artifact nested directory creation stays within sandbox.

        Tests deep directory creation remains within artifacts_root boundaries.
        """
        nested_path = PantheonPath("deep/nested/structure/artifact.txt")
        content = "nested content"

        # Mock parent doesn't exist initially
        mock_filesystem.exists.return_value = False

        result = workspace_team_a.save_artifact(content, nested_path)

        # Verify path stays relative and within sandbox
        assert str(result).replace("\\", "/") == "deep/nested/structure/artifact.txt"
        assert not str(result).startswith("/")  # Not absolute
        assert ".." not in str(result)  # No traversal

        # Verify mkdir was called for parent creation
        mock_filesystem.mkdir.assert_called_once()

    def test_save_artifact_handles_safe_paths_with_various_patterns(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
        safe_relative_paths: list[str],
    ) -> None:
        """Test save_artifact handles safe paths with various naming patterns.

        Tests artifact saving works correctly with various safe filename patterns.
        """
        content = "safe content"
        mock_filesystem.exists.return_value = True

        for safe_path_str in safe_relative_paths:
            safe_path = PantheonPath(safe_path_str)

            result = workspace_team_a.save_artifact(content, safe_path)

            assert str(result).replace("\\", "/") == safe_path_str
            assert not str(result).startswith("/")
            mock_filesystem.reset_mock()
            mock_filesystem.exists.return_value = True

    # PantheonPath Security Integration Tests

    def test_pantheon_path_rejects_absolute_paths_in_constructor(self) -> None:
        """Test PantheonPath rejects absolute paths at construction per T015.

        Tests the fundamental T015 security constraint implemented at type level.
        """
        import platform

        if platform.system() == "Windows":
            absolute_paths = [
                "C:\\absolute\\windows\\path",
                "\\\\network\\share\\path",
                "D:\\another\\absolute\\path",
            ]
        else:
            absolute_paths = [
                "/absolute/unix/path",
                "/etc/passwd",
                "/home/user/file",
            ]

        for abs_path in absolute_paths:
            with pytest.raises(ValueError, match="must represent a relative path"):
                PantheonPath(abs_path)

    def test_pantheon_path_allows_all_relative_paths(self) -> None:
        """Test PantheonPath allows all relative paths as intended.

        Tests relative paths of various formats are accepted by PantheonPath.
        """
        relative_paths = [
            "simple.txt",
            "relative/path.txt",
            "nested/deep/structure/file.json",
            "file-with-hyphens.txt",
            "file_with_underscores.yaml",
            "123-numeric-start.txt",
        ]

        for rel_path in relative_paths:
            # Should not raise any exception
            path = PantheonPath(rel_path)
            assert Path(str(path)).as_posix() == rel_path

    def test_pantheon_path_handles_edge_case_relative_paths(self) -> None:
        """Test PantheonPath handles suspicious but safe relative paths.

        Tests edge cases that might look suspicious but are actually safe relative paths.
        """
        edge_case_paths = [
            "file.txt",  # Simple file in current directory
            "a/b/c/d/e/f/g.txt",  # Very deep nesting (but relative)
            "file.with.many.dots.txt",  # Multiple dots in name
            "123",  # Numeric filename
            "ALLCAPS.TXT",  # All uppercase
        ]

        for edge_path in edge_case_paths:
            # Should not raise any exception
            path = PantheonPath(edge_path)
            assert Path(str(path)).as_posix() == edge_path

    def test_pantheon_path_error_message_clear_for_absolute_paths(self) -> None:
        """Test PantheonPath provides clear error messages for absolute paths.

        Tests error messages help users understand the security constraint.
        """
        import platform

        absolute_path = (
            "C:\\absolute\\path\\example"
            if platform.system() == "Windows"
            else "/absolute/path/example"
        )

        with pytest.raises(ValueError) as exc_info:
            PantheonPath(absolute_path)

        error_message = str(exc_info.value)
        assert "must represent a relative path" in error_message

    def test_workspace_can_safely_unwrap_pantheon_path(
        self,
        workspace_team_a: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test workspace can safely unwrap PantheonPath for filesystem operations.

        Tests workspace internal operations can safely use PantheonPath values
        knowing they are pre-validated as relative paths.
        """
        safe_path = PantheonPath("safe/relative/path.txt")
        content = "safe content"
        mock_filesystem.exists.return_value = True

        # Workspace should be able to unwrap and use the path safely
        result = workspace_team_a.save_artifact(content, safe_path)

        assert result == safe_path
        mock_filesystem.write_text.assert_called_once()

    # Cross-Process Reference Security Tests
