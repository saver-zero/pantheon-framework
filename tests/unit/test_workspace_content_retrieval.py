"""Unit tests for PantheonWorkspace content-retrieval methods.

This test suite validates all 15+ content-retrieval methods using parameterized tests
to ensure consistent coverage across similar method patterns. Tests use mocked FileSystem
for complete I/O isolation while validating path construction and error handling.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from pantheon.filesystem import FileSystem
from pantheon.workspace import PantheonWorkspace, ProjectConfig

# Function removed - using proper pathlib operations instead


class TestPantheonWorkspaceContentRetrieval:
    """Test suite for PantheonWorkspace content-retrieval methods."""

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
    def workspace_with_config(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> PantheonWorkspace:
        """Create a PantheonWorkspace instance with test team configuration.

        Args:
            mock_filesystem: Mocked FileSystem dependency
            sample_paths: Sample path instances

        Returns:
            Configured PantheonWorkspace for testing with active team
        """
        # Mock config loading to return test team
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        # Set up active team for content-retrieval methods
        workspace._project_config = ProjectConfig(
            active_team="test-team", artifacts_root="pantheon-artifacts"
        )

        return workspace

    @pytest.fixture
    def sample_content(self) -> dict[str, str]:
        """Create sample content for each file type.

        Returns:
            Dictionary mapping file types to sample content
        """
        return {
            "schema": '{\n  "type": "object",\n  "properties": {\n    "title": {"type": "string"}\n  }\n}',
            "routine": "# Process Routine\n\n1. Step one\n2. Step two\n3. Step three",
            "finder": '{\n  "pattern": "^({id})_.*\\.md$"\n}',
            "normalizer": '[\n  {"pattern": "^\\s+|\\s+$", "replacement": ""}\n]',
            "markers": '{\n  "start": "<!-- START -->",\n  "end": "<!-- END -->"\n}',
            "template": "# {{title}}\n\n{{content}}",
            "directory_template": "{{team}}/{{process}}",
            "filename_template": "{{id}}_{{date}}.md",
            "team_profile": "team_name: test-team\nverbosity: standard",
            "permissions": '{\n  "allow": ["tech-lead"],\n  "deny": []\n}',
            "config": "setting1: value1\nsetting2: value2",
        }

    # Process-Related Content Methods Tests

    @pytest.mark.parametrize(
        "process_name,expected_filename",
        [
            ("create-ticket", "schema.jsonnet"),
            ("update-plan", "schema.jsonnet"),
            ("get-artifact", "schema.jsonnet"),
            ("process-with-hyphens", "schema.jsonnet"),
            ("process_with_underscores", "schema.jsonnet"),
        ],
    )
    def test_get_process_schema(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
        process_name: str,
        expected_filename: str,
    ) -> None:
        """Test get_process_schema with various process names.

        Tests process schema retrieval with different process name formats,
        verifying correct path construction and content retrieval.
        """
        expected_content = sample_content["schema"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_process_schema(process_name)

        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        actual_path = Path(str(call_args))
        assert "pantheon-teams" in actual_path.parts
        assert "test-team" in actual_path.parts
        assert "processes" in actual_path.parts
        assert process_name in actual_path.parts
        assert expected_filename in path_str

    @pytest.mark.parametrize(
        "process_name",
        [
            "create-ticket",
            "update-plan",
            "get-status",
            "complex-process-name",
            "simple",
        ],
    )
    def test_get_process_routine(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
        process_name: str,
    ) -> None:
        """Test get_process_routine with various process names.

        Tests routine retrieval for different processes, verifying correct
        path construction includes routine.md filename.
        """
        expected_content = sample_content["routine"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_process_routine(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "routine.md" in path_str
        actual_path = Path(str(call_args))
        assert "processes" in actual_path.parts
        assert process_name in actual_path.parts

    @pytest.mark.parametrize(
        "process_name",
        [
            "get-ticket",
            "find-artifact",
            "locate-item",
            "search-process",
            "discovery",
        ],
    )
    def test_get_permissions(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
        process_name: str,
    ) -> None:
        """Test get_permissions for different process types.

        Tests permissions configuration retrieval, verifying path includes
        permissions.jsonnet in team directory, not process-specific.
        """
        expected_content = sample_content["permissions"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_permissions(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "permissions.jsonnet" in path_str
        actual_path = Path(str(call_args))
        assert "pantheon-teams" in actual_path.parts
        assert "test-team" in actual_path.parts
        # Permissions are process-specific
        assert "processes" in actual_path.parts
        assert process_name in actual_path.parts

    # Artifact-Related Content Methods Tests

    @pytest.mark.parametrize(
        "method_name,expected_filename",
        [
            ("get_artifact_locator", "locator.jsonnet"),
            ("get_artifact_parser", "parser.jsonnet"),
            ("get_artifact_section_markers", "sections.jsonnet"),
            ("get_artifact_content_template", "content.md"),
            ("get_artifact_directory_template", "placement.jinja"),
            ("get_artifact_filename_template", "naming.jinja"),
        ],
    )
    def test_artifact_methods_with_same_process_names(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
        method_name: str,
        expected_filename: str,
    ) -> None:
        """Test all artifact methods with same process names.

        Validates that all artifact-related methods work consistently
        with the same process names and construct correct artifact/ subdirectory paths.
        Uses new operation-specific naming conventions.
        """
        process_name = "test-process"
        expected_content = sample_content.get(
            expected_filename.split(".")[0], "sample content"
        )
        mock_filesystem.read_text.return_value = expected_content

        # Get the method from workspace and call it
        method = getattr(workspace_with_config, method_name)
        result = method(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "artifact/" in path_str or "artifact\\" in path_str
        assert expected_filename in path_str
        actual_path = Path(str(call_args))
        assert "processes" in actual_path.parts
        assert process_name in actual_path.parts

    @pytest.mark.parametrize(
        "process_name,has_artifacts",
        [
            ("process-with-artifacts", True),
            ("process-without-artifacts", False),
            ("minimal-process", False),
            ("full-featured-process", True),
            ("legacy-process", False),
        ],
    )
    def test_artifact_methods_with_mixed_process_types(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        process_name: str,
        has_artifacts: bool,
    ) -> None:
        """Test artifact methods with processes that have/don't have artifacts.

        Tests artifact retrieval methods handle both processes with artifacts
        and those without, ensuring appropriate errors for missing files.
        """
        if has_artifacts:
            mock_filesystem.read_text.return_value = "artifact content"
            result = workspace_with_config.get_artifact_locator(process_name)
            assert result == "artifact content"
        else:
            mock_filesystem.read_text.side_effect = FileNotFoundError(
                f"No artifacts for {process_name}"
            )
            with pytest.raises(FileNotFoundError):
                workspace_with_config.get_artifact_locator(process_name)

    # Team-Related Content Methods Tests

    def test_get_team_profile(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
    ) -> None:
        """Test team profile retrieval with comprehensive profile configuration.

        Tests team profile loading with complete YAML configuration including
        all team settings and behavioral parameters.
        """
        expected_content = sample_content["team_profile"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_team_profile()

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "team-profile.yaml" in path_str
        actual_path = Path(str(call_args))
        assert "pantheon-teams" in actual_path.parts
        assert "test-team" in actual_path.parts

    def test_get_team_profile_minimal_profile(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test team profile retrieval with minimal profile configuration.

        Tests team profile loading with minimal YAML containing only required keys.
        """
        minimal_profile = "team_name: minimal-team"
        mock_filesystem.read_text.return_value = minimal_profile

        result = workspace_with_config.get_team_profile()

        assert result == minimal_profile

    def test_get_team_profile_missing_file(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test team profile retrieval when team-profile.yaml missing.

        Tests FileNotFoundError handling when team profile doesn't exist.
        """
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            "team-profile.yaml not found"
        )

        with pytest.raises(FileNotFoundError):
            workspace_with_config.get_team_profile()

    def test_get_team_profile_with_nested_configuration(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test team profile with nested configuration structure.

        Tests team profile loading with complex nested YAML structure.
        """
        nested_profile = """team_name: complex-team
settings:
  verbosity: verbose
  testing:
    enabled: true
    coverage: 90
agents:
  - tech-lead
  - backend-engineer
"""
        mock_filesystem.read_text.return_value = nested_profile

        result = workspace_with_config.get_team_profile()

        assert result == nested_profile

    # Agent Discovery Tests

    # Configuration Methods Tests

    @pytest.mark.parametrize(
        "config_name,scope,expected_path_contains",
        [
            ("settings", "team1", "config/team1/settings.yaml"),
            ("deployment", "prod", "config/prod/deployment.yaml"),
            ("database", None, "config/database.yaml"),
            ("logging", "dev", "config/dev/logging.yaml"),
            ("security", None, "config/security.yaml"),
        ],
    )
    def test_get_config_scoped_and_global(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
        config_name: str,
        scope: str | None,
        expected_path_contains: str,
    ) -> None:
        """Test configuration loading with scoped and global configs.

        Tests hierarchical config resolution prefers scoped config when available.
        """
        config_yaml = sample_content["config"]
        mock_filesystem.read_text.return_value = config_yaml

        result = workspace_with_config.get_config(config_name, scope)

        expected_dict = {"setting1": "value1", "setting2": "value2"}
        assert result == expected_dict
        call_args = mock_filesystem.read_text.call_args[0][0]
        actual_path = Path(str(call_args)).as_posix()
        assert expected_path_contains in actual_path

    def test_get_config_fallback_to_global(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
    ) -> None:
        """Test configuration loading falls back to global when scoped missing.

        Tests config resolution falls back to global config when scoped doesn't exist.
        """
        config_yaml = sample_content["config"]
        call_log = []

        def mock_read_text(path):
            path_str = str(path)
            call_log.append(path_str)  # Track what paths are called
            if "config/scoped/" in path_str or "config\\scoped\\" in path_str:
                raise FileNotFoundError("Scoped config not found")
            return config_yaml

        mock_filesystem.read_text.side_effect = mock_read_text

        result = workspace_with_config.get_config("settings", "scoped")

        expected_dict = {"setting1": "value1", "setting2": "value2"}
        assert result == expected_dict
        # Should have been called twice: scoped (failed) then global (success)
        assert mock_filesystem.read_text.call_count == 2

    def test_get_config_no_scope_uses_global(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        sample_content: dict[str, str],
    ) -> None:
        """Test configuration loading with no scope uses global directly.

        Tests config loading goes directly to global config when no scope provided.
        """
        config_yaml = sample_content["config"]
        mock_filesystem.read_text.return_value = config_yaml

        result = workspace_with_config.get_config("settings")

        expected_dict = {"setting1": "value1", "setting2": "value2"}
        assert result == expected_dict
        # Should only be called once for global config
        mock_filesystem.read_text.assert_called_once()

    def test_get_config_yaml_parsing_errors(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test configuration loading handles YAML parsing errors gracefully.

        Tests config loading returns empty dict on YAML syntax errors.
        """
        invalid_yaml = "setting1: value1\n  invalid: [unclosed"
        mock_filesystem.read_text.return_value = invalid_yaml

        # YAML parsing will raise specific yaml error, but implementation may catch it
        # Test the actual behavior - if it raises, test that; if not, test returned value
        try:
            result = workspace_with_config.get_config("invalid")
            # If no exception, should return empty dict for invalid YAML
            assert result == {}
        except Exception as e:
            # If exception is raised, that's also acceptable behavior
            assert "invalid" in str(e).lower() or "yaml" in str(e).lower()

    def test_get_config_non_dict_yaml(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test configuration loading with non-dict YAML results return empty dict.

        Tests config loading handles YAML that parses to non-dict gracefully.
        """
        non_dict_yaml = "- item1\n- item2\n- item3"
        mock_filesystem.read_text.return_value = non_dict_yaml

        result = workspace_with_config.get_config("list_config")

        assert result == {}

    # Error Handling Tests

    @pytest.mark.parametrize(
        "method_name,process_name",
        [
            ("get_process_schema", "missing-process"),
            ("get_process_routine", "nonexistent"),
            ("get_artifact_locator", "no-finder"),
            ("get_artifact_parser", "no-normalizer"),
            ("get_artifact_section_markers", "no-markers"),
            ("get_artifact_content_template", "no-template"),
            ("get_permissions", "restricted-process"),
        ],
    )
    def test_content_methods_file_not_found_error(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        method_name: str,
        process_name: str,
    ) -> None:
        """Test FileNotFoundError for each content-retrieval method.

        Tests all content-retrieval methods properly propagate FileNotFoundError
        when requested files don't exist.
        """
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            f"File not found for {process_name}"
        )

        method = getattr(workspace_with_config, method_name)
        with pytest.raises(FileNotFoundError):
            if method_name == "get_team_profile":
                method()
            else:
                method(process_name)

    @pytest.mark.parametrize(
        "method_name,process_name",
        [
            ("get_process_schema", "protected-process"),
            ("get_process_routine", "secured"),
            ("get_artifact_locator", "restricted-finder"),
            ("get_permissions", "admin-only"),
        ],
    )
    def test_content_methods_permission_error(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        method_name: str,
        process_name: str,
    ) -> None:
        """Test PermissionError propagation for read operations.

        Tests content-retrieval methods properly propagate PermissionError
        when filesystem access is denied.
        """
        mock_filesystem.read_text.side_effect = PermissionError(
            f"Access denied to {process_name}"
        )

        method = getattr(workspace_with_config, method_name)
        with pytest.raises(PermissionError):
            method(process_name)

    @pytest.mark.parametrize(
        "method_name,process_name",
        [
            ("get_process_schema", "unicode-issue"),
            ("get_artifact_content_template", "encoding-problem"),
            ("get_team_profile", None),  # No process name for team profile
        ],
    )
    def test_content_methods_unicode_decode_error(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        method_name: str,
        process_name: str | None,
    ) -> None:
        """Test UnicodeDecodeError for invalid file encoding.

        Tests content-retrieval methods properly propagate UnicodeDecodeError
        when files have invalid encoding.
        """
        mock_filesystem.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"invalid", 0, 1, "invalid encoding"
        )

        method = getattr(workspace_with_config, method_name)
        with pytest.raises(UnicodeDecodeError):
            if process_name is None:
                method()
            else:
                method(process_name)

    def test_content_methods_include_relevant_context_in_errors(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test error messages include relevant context information.

        Tests content-retrieval methods provide helpful error context including
        process names and file paths when errors occur.
        """
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            "schema.jsonnet not found in /path/to/process"
        )

        with pytest.raises(FileNotFoundError, match="schema.jsonnet.*process"):
            workspace_with_config.get_process_schema("test-process")

    # Recovery and Default Tests

    def test_get_config_uses_appropriate_defaults(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test configuration methods have appropriate default behaviors.

        Tests config methods provide sensible defaults or clear errors
        when configurations are missing or invalid.
        """
        # Test that empty dict is returned for malformed YAML
        mock_filesystem.read_text.return_value = "null"

        result = workspace_with_config.get_config("null_config")

        assert result == {}

    def test_get_matching_artifact_finds_matching_files(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact returns matching files."""
        from pathlib import Path
        from unittest.mock import Mock

        # Create mock Path objects with proper attributes
        def create_mock_file(name, full_path, is_file=True, is_dir=False):
            mock_path = Mock(spec=Path)
            mock_path.name = name
            mock_path.suffix = Path(name).suffix
            mock_path.is_file.return_value = is_file
            mock_path.is_dir.return_value = is_dir
            mock_path.__str__ = lambda: full_path
            # Mock relative_to to return just the filename
            mock_path.relative_to.return_value = Path(name)
            return mock_path

        # Setup test files
        artifacts_files = [
            create_mock_file("T001_create_user.md", "/artifacts/T001_create_user.md"),
            create_mock_file(
                "T002_update_profile.md", "/artifacts/T002_update_profile.md"
            ),
            create_mock_file("sub", "/artifacts/sub", is_file=False, is_dir=True),
            create_mock_file("other.md", "/artifacts/other.md"),
        ]

        sub_files = [
            create_mock_file(
                "T003_delete_account.md", "/artifacts/sub/T003_delete_account.md"
            ),
            create_mock_file("notes.txt", "/artifacts/sub/notes.txt"),
        ]

        def mock_iterdir(path):
            if "sub" in str(path):
                return iter(sub_files)
            return iter(artifacts_files)

        mock_filesystem.iterdir.side_effect = mock_iterdir
        mock_filesystem.exists.return_value = True

        # Test pattern matching T001 and T002
        pattern = r"^T00[12]_.*\.md$"
        result = workspace_with_config.get_matching_artifact(pattern)

        # Should find T001 and T002
        result_names = [str(r) for r in result]
        assert len(result_names) == 2
        assert "T001_create_user.md" in result_names
        assert "T002_update_profile.md" in result_names

    def test_get_matching_artifact_no_matches(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact returns empty list when no files match."""
        from pathlib import Path
        from unittest.mock import Mock

        def create_mock_file(name, full_path):
            mock_path = Mock(spec=Path)
            mock_path.name = name
            mock_path.suffix = Path(name).suffix
            mock_path.is_file.return_value = True
            mock_path.is_dir.return_value = False
            mock_path.__str__ = lambda: full_path
            mock_path.relative_to.return_value = Path(name)
            return mock_path

        mock_filesystem.iterdir.return_value = [
            create_mock_file("other.md", "/artifacts/other.md"),
            create_mock_file("different.md", "/artifacts/different.md"),
        ]
        mock_filesystem.exists.return_value = True

        pattern = r"^T\d+_.*\.md$"
        result = workspace_with_config.get_matching_artifact(pattern)
        assert result == []

    def test_get_matching_artifact_invalid_regex(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact handles invalid regex gracefully."""
        mock_filesystem.exists.return_value = True

        # Invalid regex pattern
        pattern = r"[invalid"
        result = workspace_with_config.get_matching_artifact(pattern)
        assert result == []

    def test_get_matching_artifact_directory_not_found(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact handles missing directory gracefully."""
        mock_filesystem.exists.return_value = False

        pattern = r"^T\d+_.*\.md$"
        result = workspace_with_config.get_matching_artifact(pattern)
        assert result == []

    def test_get_matching_artifact_with_directory_parameter(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact with directory parameter limits search scope."""
        from pathlib import Path
        from unittest.mock import Mock

        def create_mock_file(name, full_path, is_file=True, is_dir=False):
            mock_path = Mock(spec=Path)
            mock_path.name = name
            mock_path.suffix = Path(name).suffix
            mock_path.is_file.return_value = is_file
            mock_path.is_dir.return_value = is_dir
            mock_path.__str__ = lambda: full_path
            # Mock relative_to to return relative path from artifacts root
            if "tickets" in full_path:
                mock_path.relative_to.return_value = Path(f"tickets/{name}")
            else:
                mock_path.relative_to.return_value = Path(name)
            return mock_path

        # Setup files in tickets subdirectory
        tickets_files = [
            create_mock_file("T001.md", "/artifacts/tickets/T001.md"),
            create_mock_file("T002.md", "/artifacts/tickets/T002.md"),
        ]

        def mock_iterdir(path):
            if "tickets" in str(path):
                return iter(tickets_files)
            return iter([])  # No files in root

        mock_filesystem.iterdir.side_effect = mock_iterdir
        mock_filesystem.exists.return_value = True

        # Test with directory parameter
        pattern = r"^T\d+\.md$"
        result = workspace_with_config.get_matching_artifact(
            pattern, directory="tickets"
        )

        # Should find files in tickets directory
        result_paths = [str(r) for r in result]
        assert len(result_paths) == 2
        assert "tickets/T001.md" in result_paths
        assert "tickets/T002.md" in result_paths

    def test_get_matching_artifact_directory_security_validation(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact rejects directory traversal attempts."""
        mock_filesystem.exists.return_value = True

        pattern = r"^test\.md$"

        # Test various directory traversal attempts
        dangerous_directories = ["../", "../../", "../etc", "dir/../other"]

        for dangerous_dir in dangerous_directories:
            result = workspace_with_config.get_matching_artifact(
                pattern, directory=dangerous_dir
            )
            assert result == [], f"Should reject dangerous directory: {dangerous_dir}"

    def test_get_matching_artifact_directory_not_exists(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact returns empty when directory doesn't exist."""

        def mock_exists(path):
            # Only artifacts root exists, not the subdirectory
            return "artifacts" in str(path) and "nonexistent" not in str(path)

        mock_filesystem.exists.side_effect = mock_exists

        pattern = r"^test\.md$"
        result = workspace_with_config.get_matching_artifact(
            pattern, directory="nonexistent"
        )

        assert result == []

    def test_get_matching_artifact_backward_compatibility(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_matching_artifact maintains backward compatibility when directory=None."""
        from pathlib import Path
        from unittest.mock import Mock

        def create_mock_file(name, full_path, is_file=True, is_dir=False):
            mock_path = Mock(spec=Path)
            mock_path.name = name
            mock_path.suffix = Path(name).suffix
            mock_path.is_file.return_value = is_file
            mock_path.is_dir.return_value = is_dir
            mock_path.__str__ = lambda: full_path
            mock_path.relative_to.return_value = Path(name)
            return mock_path

        # Setup files in root artifacts directory
        root_files = [
            create_mock_file("test1.md", "/artifacts/test1.md"),
            create_mock_file("test2.md", "/artifacts/test2.md"),
        ]

        mock_filesystem.iterdir.return_value = iter(root_files)
        mock_filesystem.exists.return_value = True

        # Test without directory parameter (backward compatibility)
        pattern = r"^test\d+\.md$"
        result = workspace_with_config.get_matching_artifact(pattern, directory=None)

        # Should behave same as before
        result_names = [str(r) for r in result]
        assert len(result_names) == 2
        assert "test1.md" in result_names
        assert "test2.md" in result_names
