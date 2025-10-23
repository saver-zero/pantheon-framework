"""Unit tests for PantheonWorkspace facade interface.

This test suite validates all PantheonWorkspace methods using mocks to avoid
actual I/O operations. Tests cover constructor validation, project discovery,
artifact management, convention-based path resolution, and security validation.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from pantheon.filesystem import FileSystem
from pantheon.path import PantheonPath
from pantheon.workspace import PantheonWorkspace, ProjectConfig, SecurityError

# Function removed - using proper pathlib operations instead


class TestPantheonWorkspace:
    """Test suite for PantheonWorkspace facade interface."""

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
            "project_root": "/test/project",
            "artifacts_root": "/test/project/pantheon-artifacts",
            "start_path": "/test/project/src",
            "marker_path": "/test/project/.pantheon_project",
            "artifact_path": "artifacts/test.txt",
            "config_file": "/test/project/config/settings.yaml",
        }

    @pytest.fixture
    def workspace(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> PantheonWorkspace:
        """Create a PantheonWorkspace instance with mocked dependencies.

        Args:
            mock_filesystem: Mocked FileSystem dependency
            sample_paths: Sample path instances

        Returns:
            Configured PantheonWorkspace for testing
        """
        # Mock config loading to return empty defaults
        mock_filesystem.exists.return_value = False

        return PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

    def test_workspace_init(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test PantheonWorkspace constructor accepts all required dependencies.

        Validates that the workspace correctly initializes with raw string paths
        from the outside world, converting them to internal PantheonPath representations.
        This tests the architectural boundary between outside world (str) and inside world (PantheonPath).
        """
        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        # Verify workspace initializes successfully - internal roots are not exposed
        assert isinstance(workspace, PantheonWorkspace)
        assert hasattr(workspace, "_project_root")
        assert hasattr(workspace, "_artifacts_root")
        assert hasattr(workspace, "_filesystem")
        assert workspace._filesystem is mock_filesystem

    def test_discover_project_root_found(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test project root discovery when marker file exists.

        Mocks FileSystem.exists() to simulate finding .pantheon_project marker
        and verifies correct project root identification.
        """

        # Mock marker file exists at project root
        def mock_exists(path: Path) -> bool:
            return str(path).endswith(".pantheon_project") and "project" in str(path)

        mock_filesystem.exists.side_effect = mock_exists

        result = PantheonWorkspace.discover_project_root(
            mock_filesystem, "/test/project/src"
        )

        assert result is not None
        assert "project" in result
        # Verify exists was called with marker path
        mock_filesystem.exists.assert_called()

    def test_discover_project_root_not_found(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test project root discovery when marker file doesn't exist.

        Mocks FileSystem.exists() to return False and verifies None is returned
        when no marker file is found in the directory tree.
        """
        # Mock no marker file found
        mock_filesystem.exists.return_value = False

        result = PantheonWorkspace.discover_project_root(
            mock_filesystem, "/test/project/src"
        )

        assert result is None
        mock_filesystem.exists.assert_called()

    def test_save_artifact(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving with path sandboxing and FileSystem interaction.

        Validates artifact saving with mocked FileSystem.write_text() and
        mkdir(), verifying sandboxing enforcement and proper I/O operations.
        """
        content = "Test artifact content"
        path = PantheonPath("test/artifact.txt")

        # Mock parent directory doesn't exist initially
        mock_filesystem.exists.return_value = False

        result = workspace.save_artifact(content, path)

        # Verify parent directory creation
        mock_filesystem.mkdir.assert_called_once()
        # Verify content writing
        mock_filesystem.write_text.assert_called_once()
        # Verify returned path includes output root
        assert "test" in str(result) and "artifact.txt" in str(result)

    def test_get_process_schema(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test process schema retrieval using content-retrieval method.

        Validates that get_process_schema correctly constructs the path
        and retrieves schema content from the active team's process directory.
        """
        expected_content = '{ "type": "object" }'
        process_name = "create-ticket"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = expected_content

        result = workspace.get_process_schema(process_name)

        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()
        # Verify the path construction includes team and process structure
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "pantheon-teams" in str(call_args)
        assert "test-team" in str(call_args)
        assert "processes" in str(call_args)
        assert "create-ticket" in str(call_args)
        assert "schema.jsonnet" in str(call_args)

    def test_get_resolved_content_semantic_uri(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test semantic URI resolution through get_resolved_content.

        Validates that get_resolved_content correctly parses semantic URIs
        and routes them to appropriate content-retrieval methods.
        """
        expected_content = '{ "pattern": "^({id})_.*\\\\.md$" }'

        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = expected_content

        result = workspace.get_resolved_content("artifact-locator://create-ticket")

        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()

    def test_get_resolved_content_invalid_scheme(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test get_resolved_content with unsupported URI scheme.

        Validates that unsupported schemes raise ValueError.
        """
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        with pytest.raises(ValueError, match="Unsupported URI scheme"):
            workspace.get_resolved_content("unknown-scheme://process-name")

    def test_parse_semantic_uri_with_sub_path(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test _parse_semantic_uri extracts sub-paths correctly.

        Validates that semantic URIs with sub-paths are parsed into
        scheme, process_name, sub_path, and parameters components.
        """
        # Arrange
        uri = "process-schema://update-guide/sections/core-principles"

        # Act
        scheme, process_name, sub_path, parameters = workspace._parse_semantic_uri(uri)

        # Assert
        assert scheme == "process-schema"
        assert process_name == "update-guide"
        assert sub_path == "sections/core-principles"
        assert parameters == {}

    def test_parse_semantic_uri_without_sub_path(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test _parse_semantic_uri handles URIs without sub-paths.

        Validates backward compatibility with existing semantic URI format.
        """
        # Arrange
        uri = "process-schema://create-ticket"

        # Act
        scheme, process_name, sub_path, parameters = workspace._parse_semantic_uri(uri)

        # Assert
        assert scheme == "process-schema"
        assert process_name == "create-ticket"
        assert sub_path is None
        assert parameters == {}

    def test_parse_semantic_uri_with_sub_path_and_parameters(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test _parse_semantic_uri handles sub-paths with query parameters.

        Validates that URIs with both sub-paths and parameters are correctly parsed.
        """
        # Arrange
        uri = "artifact-sections://get-ticket/custom-section?data=sections.plan"

        # Act
        scheme, process_name, sub_path, parameters = workspace._parse_semantic_uri(uri)

        # Assert
        assert scheme == "artifact-sections"
        assert process_name == "get-ticket"
        assert sub_path == "custom-section"
        assert parameters == {"data": "sections.plan"}

    def test_get_section_schema(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test get_section_schema retrieves section schemas correctly.

        Validates that section schemas are loaded from the conventional path
        and preprocessed to resolve imports.
        """
        # Arrange
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        expected_content = (
            '{"type": "object", "properties": {"name": {"type": "string"}}}'
        )
        mock_filesystem.read_text.return_value = expected_content

        # Act
        result = workspace.get_section_schema(
            "update-guide", "sections/core-principles"
        )

        # Assert
        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "update-guide" in str(call_args)
        assert "artifact" in str(call_args)
        assert "sections" in str(call_args)
        assert "core-principles.schema.jsonnet" in str(call_args)

    def test_get_section_schema_prevents_directory_traversal(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test get_section_schema validates section_path for security.

        Validates that directory traversal attempts are blocked to prevent
        unauthorized access to files outside the process artifact directory.
        """
        # Arrange
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Act & Assert
        with pytest.raises(ValueError, match="[Dd]irectory traversal"):
            workspace.get_section_schema("update-guide", "../../../etc/passwd")

        with pytest.raises(ValueError, match="[Aa]bsolute path"):
            workspace.get_section_schema("update-guide", "/absolute/path")

    def test_get_resolved_content_with_section_schema_uri(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test get_resolved_content routes section schema URIs correctly.

        Validates that process-schema:// URIs with sub-paths are routed
        to get_section_schema instead of get_process_schema.
        """
        # Arrange
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        expected_content = '{"type": "object", "required": ["principles"]}'
        mock_filesystem.read_text.return_value = expected_content

        # Act
        result = workspace.get_resolved_content(
            "process-schema://update-architecture-guide/sections/core-principles"
        )

        # Assert
        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "sections" in str(call_args)
        assert "core-principles.schema.jsonnet" in str(call_args)

    def test_preprocess_content_with_local_variable_imports(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test _preprocess_content handles local variable import assignments.

        Validates that import statements in the middle of lines (like Jsonnet
        local variable assignments) are correctly resolved.
        """
        # Arrange
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Content with local variable import
        content = 'local schema = import "process-schema://base-schema";\n\n{ properties: schema.properties }'
        base_path = Path(
            "/test/project/pantheon-teams/test-team/processes/test-process/schema.jsonnet"
        )

        # Mock the resolved import content
        resolved_import = '{ properties: { name: { type: "string" } } }'
        mock_filesystem.read_text.return_value = resolved_import

        # Act
        result = workspace._preprocess_content(content, base_path)

        # Assert - the import should be replaced with the resolved content inline
        assert "process-schema://base-schema" not in result
        assert 'local schema = { properties: { name: { type: "string" } } }' in result
        assert "{ properties: schema.properties }" in result

    def test_create_tempfile(self, workspace: PantheonWorkspace) -> None:
        """Test temporary file path creation within sandbox.

        Validates that create_tempfile() generates unique paths within
        the output root temp directory with optional prefix/suffix.
        """
        result = workspace.create_tempfile(suffix=".json", prefix="test_")

        assert "temp" in str(result)
        assert result.suffix == ".json"
        assert "test_" in str(result)

    def test_create_tempfile_no_options(self, workspace: PantheonWorkspace) -> None:
        """Test temporary file creation without prefix or suffix options."""
        result = workspace.create_tempfile()

        assert "temp" in str(result)
        # Should contain UUID-like string (check filename part only)
        import os

        filename = os.path.basename(str(result))
        assert len(filename) == 53  # YYYY-MM-DD_HH-MM + _ + UUID length

    def test_get_team_package_path(self, workspace: PantheonWorkspace) -> None:
        """Test team package path resolution following conventions.

        Validates correct path construction for team packages under
        the pantheon-teams directory structure.
        """
        team = "backend-team"

        result = workspace.get_team_package_path(team)

        from pathlib import Path

        actual_path = Path(str(result))
        assert "pantheon-teams" in actual_path.parts
        assert "backend-team" in actual_path.parts

    def test_get_artifact_normalizer(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact normalizer rules retrieval.

        Validates that get_artifact_normalizer correctly constructs the path
        and retrieves normalizer rules from the process artifact directory.
        Uses new RETRIEVE operation naming convention (parser.jsonnet).
        """
        expected_content = '[{"pattern": "^\\\\s+|\\\\s+$", "replacement": ""}]'
        process_name = "get-ticket"

        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = expected_content

        result = workspace.get_artifact_parser(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "artifact" in str(call_args) and "parser.jsonnet" in str(call_args)

    def test_get_process_routine(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test process routine retrieval.

        Validates that get_process_routine correctly constructs the path
        and retrieves routine markdown from the process directory.
        """
        expected_content = "# Process Routine\\n\\n1. Step one\\n2. Step two"
        process_name = "update-plan"

        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = expected_content

        result = workspace.get_process_routine(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "routine.md" in str(call_args)

    def test_get_config(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test configuration retrieval with YAML parsing.

        Validates that get_config correctly reads and parses YAML configuration
        files and returns them as dictionaries.
        """
        expected_config = {"key": "value", "nested": {"item": "test"}}
        config_yaml = "key: value\nnested:\n  item: test"

        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = config_yaml

        result = workspace.get_config("settings")

        assert result == expected_config
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "settings.yaml" in str(call_args)

    def test_validate_path_security_traversal_attack(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test security validation prevents directory traversal attacks.

        Validates that paths containing .. sequences are rejected
        with SecurityError and clear error message.
        """
        malicious_path = PantheonPath("../../../etc/passwd")

        with pytest.raises(SecurityError, match="Directory traversal not allowed"):
            workspace._validate_path_security(malicious_path)

    def test_validate_path_security_absolute_path_prevention(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test that PantheonPath construction prevents absolute paths per T015.

        This verifies that absolute paths cannot be created as PantheonPath objects,
        which is the T015 security constraint that prevents escaping sandbox boundaries.
        """
        import platform

        import pytest

        # T015 constraint: PantheonPath constructor should reject absolute paths
        # Use platform-appropriate absolute path
        if platform.system() == "Windows":
            absolute_path = "C:\\etc\\sensitive"
        else:
            absolute_path = "/etc/sensitive"

        with pytest.raises(ValueError, match="must represent a relative path"):
            PantheonPath(absolute_path)

        # Verify that relative paths still work fine
        safe_path = PantheonPath("safe", "relative", "path.txt")
        # This should not raise an exception
        workspace._validate_path_security(safe_path)

    def test_validate_path_security_safe_path(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test security validation allows safe relative paths.

        Validates that normal relative paths without traversal
        sequences are accepted without errors.
        """
        safe_path = PantheonPath("safe/relative/path.txt")

        # Should not raise any exception
        workspace._validate_path_security(safe_path)

    def test_load_project_config_with_valid_file(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test loading project configuration from valid .pantheon_project file.

        Validates that load_project_config correctly parses YAML and returns
        ProjectConfig with active_team and artifacts_root values.
        """
        config_yaml = """active_team: test-team
artifacts_root: test-artifacts"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_yaml

        result = PantheonWorkspace.load_project_config(
            mock_filesystem, sample_paths["project_root_str"]
        )

        assert isinstance(result, dict)
        assert result["active_team"] == "test-team"
        assert result["artifacts_root"] == "test-artifacts"
        mock_filesystem.read_text.assert_called_once()

    def test_load_project_config_with_missing_file(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test loading project configuration when .pantheon_project doesn't exist.

        Validates that load_project_config returns sensible defaults when
        the config file is missing.
        """
        mock_filesystem.exists.return_value = False

        result = PantheonWorkspace.load_project_config(
            mock_filesystem, sample_paths["project_root_str"]
        )

        assert isinstance(result, dict)
        assert result["active_team"] == ""
        assert result["artifacts_root"] == "pantheon-artifacts"
        mock_filesystem.read_text.assert_not_called()

    def test_workspace_init_with_project_config(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test workspace constructor loads and stores project configuration.

        Validates that the workspace correctly loads project config during
        initialization and stores it as _project_config.
        """
        config_yaml = """active_team: backend-team
artifacts_root: artifacts"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_yaml

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        assert hasattr(workspace, "_project_config")
        assert workspace._project_config["active_team"] == "backend-team"
        assert workspace._project_config["artifacts_root"] == "artifacts"

    def test_get_permissions(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test permissions configuration retrieval.

        Validates that get_permissions correctly reads permissions.jsonnet
        from the active team directory.
        """
        expected_content = '{"allow": ["tech-lead"], "deny": []}'
        process_name = "create-ticket"

        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }
        mock_filesystem.read_text.return_value = expected_content

        result = workspace.get_permissions(process_name)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "permissions.jsonnet" in str(call_args)

    def test_get_team_package_path_with_active_team(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test get_team_package_path uses active_team when team is None.

        Validates that omitting team parameter defaults to active_team
        from project configuration.
        """
        workspace._project_config = ProjectConfig(
            active_team="active-team", artifacts_root="pantheon-artifacts"
        )

        result = workspace.get_team_package_path()

        from pathlib import Path

        actual_path = Path(str(result))
        assert "pantheon-teams" in actual_path.parts
        assert "active-team" in actual_path.parts

    def test_get_active_team_root(self, workspace: PantheonWorkspace) -> None:
        """Test _get_active_team_root returns correct team directory path.

        Validates internal method for computing active team's sandbox path.
        """
        workspace._project_config = ProjectConfig(
            active_team="backend", artifacts_root="pantheon-artifacts"
        )

        result = workspace._get_active_team_root()

        from pathlib import Path

        actual_path = Path(str(result))
        assert "pantheon-teams" in actual_path.parts
        assert "backend" in actual_path.parts

    def test_get_active_team_root_no_team(self, workspace: PantheonWorkspace) -> None:
        """Test _get_active_team_root raises when no active_team configured.

        Validates that method raises clear error when active_team is not set.
        """
        workspace._project_config = ProjectConfig(
            active_team="", artifacts_root="pantheon-artifacts"
        )

        with pytest.raises(ValueError, match="No active_team configured"):
            workspace._get_active_team_root()

    # Phase 1 Comprehensive Tests - Constructor Tests

    def test_workspace_init_with_valid_config(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test PantheonWorkspace constructor with valid .pantheon_project config.

        Tests workspace initialization when .pantheon_project exists and contains
        all required fields, verifying proper config loading and initialization.
        """
        # Mock valid config file exists and contains required keys
        config_content = """
active_team: test-team
artifacts_root: custom-artifacts
"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        assert workspace._project_config["active_team"] == "test-team"
        assert workspace._project_config["artifacts_root"] == "custom-artifacts"
        mock_filesystem.read_text.assert_called_once()

    def test_workspace_init_with_missing_config(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test PantheonWorkspace constructor when .pantheon_project is missing.

        Tests workspace initialization falls back to defaults when config file doesn't exist.
        """
        # Mock config file doesn't exist
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        assert workspace._project_config["active_team"] == ""
        assert workspace._project_config["artifacts_root"] == "pantheon-artifacts"
        mock_filesystem.exists.assert_called_once()

    def test_workspace_init_with_malformed_config(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test PantheonWorkspace constructor with malformed YAML config.

        Tests workspace initialization falls back to defaults when config has YAML syntax errors.
        """
        # Mock malformed YAML content
        malformed_yaml = "active_team: test-team\n  invalid: [unclosed bracket"
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = malformed_yaml

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        # Should fall back to defaults on parse error
        assert workspace._project_config["active_team"] == ""
        assert workspace._project_config["artifacts_root"] == "pantheon-artifacts"

    def test_workspace_init_with_missing_active_team_key(
        self, mock_filesystem: Mock, sample_paths: dict[str, str]
    ) -> None:
        """Test PantheonWorkspace constructor with config missing active_team key.

        Tests workspace initialization uses defaults when config exists but lacks active_team.
        """
        # Mock config with missing active_team key
        config_content = "artifacts_root: custom-artifacts\n"
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        workspace = PantheonWorkspace(
            project_root=sample_paths["project_root_str"],
            artifacts_root=sample_paths["artifacts_root_str"],
            filesystem=mock_filesystem,
        )

        assert workspace._project_config["active_team"] == ""
        assert workspace._project_config["artifacts_root"] == "custom-artifacts"

    # Phase 1 Comprehensive Tests - Project Discovery Tests

    def test_discover_project_root_from_project_root(
        self, mock_filesystem: Mock
    ) -> None:
        """Test project discovery starting from project root directory itself.

        Tests discovery when starting path is already the project root containing marker.
        """
        project_root = "/test/project"

        def mock_exists(path: Path) -> bool:
            # Handle path normalization - on Windows, Path().resolve() converts paths
            expected_marker = str(Path(project_root).resolve() / ".pantheon_project")
            return str(path) == expected_marker

        mock_filesystem.exists.side_effect = mock_exists

        result = PantheonWorkspace.discover_project_root(mock_filesystem, project_root)

        assert result == str(Path(project_root).resolve())
        mock_filesystem.exists.assert_called()

    def test_discover_project_root_from_deep_nested_path(
        self, mock_filesystem: Mock
    ) -> None:
        """Test project discovery from 5+ levels deep subdirectory.

        Tests discovery traverses up the directory tree from deeply nested paths.
        """
        nested_path = "/test/project/src/components/ui/forms/input"
        project_root = "/test/project"

        def mock_exists(path: Path) -> bool:
            # Handle path normalization - on Windows, Path().resolve() converts paths
            expected_marker = str(Path(project_root).resolve() / ".pantheon_project")
            return str(path) == expected_marker

        mock_filesystem.exists.side_effect = mock_exists

        result = PantheonWorkspace.discover_project_root(mock_filesystem, nested_path)

        assert result == str(Path(project_root).resolve())
        # Should have called exists multiple times while traversing up
        assert mock_filesystem.exists.call_count > 1

    def test_discover_project_root_outside_any_project(
        self, mock_filesystem: Mock
    ) -> None:
        """Test project discovery from path outside any project.

        Tests discovery returns None when no marker file found in directory tree.
        """
        outside_path = "/home/user/documents/random"

        # Mock no marker file found anywhere
        mock_filesystem.exists.return_value = False

        result = PantheonWorkspace.discover_project_root(mock_filesystem, outside_path)

        assert result is None
        mock_filesystem.exists.assert_called()

    def test_discover_project_root_reaches_filesystem_root(
        self, mock_filesystem: Mock
    ) -> None:
        """Test project discovery when reaching filesystem root without finding marker.

        Tests discovery stops at filesystem root and returns None appropriately.
        """
        deep_path = "/very/deep/path/structure/that/has/no/project"

        # Mock no marker file found anywhere
        mock_filesystem.exists.return_value = False

        result = PantheonWorkspace.discover_project_root(mock_filesystem, deep_path)

        assert result is None
        # Should have called exists multiple times while traversing to root
        assert mock_filesystem.exists.call_count > 1

    # Phase 1 Comprehensive Tests - Save Artifact Tests

    def test_save_artifact_with_parent_directory_creation(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving creates parent directories when they don't exist.

        Tests save_artifact creates nested directory structure before writing file.
        """
        content = "Test content"
        artifact_path = PantheonPath("nested/deep/structure/artifact.txt")

        # Mock parent doesn't exist initially, then exists after mkdir
        mock_filesystem.exists.side_effect = [False, True]

        result = workspace.save_artifact(content, artifact_path)

        mock_filesystem.mkdir.assert_called_once()
        mock_filesystem.write_text.assert_called_once()
        from pathlib import Path

        assert Path(str(result)).as_posix() == "nested/deep/structure/artifact.txt"

    def test_save_artifact_overwrite_existing_file(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving overwrites existing file.

        Tests save_artifact properly overwrites existing artifact file.
        """
        content = "Updated content"
        artifact_path = PantheonPath("existing/artifact.txt")

        # Mock parent directory and file both exist
        mock_filesystem.exists.return_value = True

        result = workspace.save_artifact(content, artifact_path)

        # Should not try to create directory since it exists
        mock_filesystem.mkdir.assert_not_called()
        mock_filesystem.write_text.assert_called_once()
        from pathlib import Path

        assert Path(str(result)).as_posix() == "existing/artifact.txt"

    def test_save_artifact_permission_error(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving handles PermissionError from filesystem.

        Tests save_artifact propagates PermissionError when filesystem access denied.
        """
        content = "Test content"
        artifact_path = PantheonPath("protected/artifact.txt")

        mock_filesystem.exists.return_value = True
        mock_filesystem.write_text.side_effect = PermissionError("Access denied")

        with pytest.raises(PermissionError, match="Access denied"):
            workspace.save_artifact(content, artifact_path)

    def test_save_artifact_parent_creation_fails(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving handles parent directory creation failure.

        Tests save_artifact handles when parent directory creation fails.
        """
        content = "Test content"
        artifact_path = PantheonPath("failing/path/artifact.txt")

        mock_filesystem.exists.return_value = False
        mock_filesystem.mkdir.side_effect = OSError("Cannot create directory")

        with pytest.raises(OSError, match="Cannot create directory"):
            workspace.save_artifact(content, artifact_path)

    def test_save_artifact_returns_correct_relative_path(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test artifact saving returns correct relative path after save.

        Tests save_artifact returns the original relative path for external reference.
        """
        content = "Test content"
        artifact_path = PantheonPath("correct/relative/path.txt")

        mock_filesystem.exists.return_value = True

        result = workspace.save_artifact(content, artifact_path)

        assert result == artifact_path
        from pathlib import Path

        assert Path(str(result)).as_posix() == "correct/relative/path.txt"

    # Phase 1 Comprehensive Tests - Create Tempfile Tests

    # Removed redundant test - basic functionality covered elsewhere

    # Removed redundant test - basic functionality covered elsewhere

    def test_create_tempfile_with_both_prefix_and_suffix(
        self, workspace: PantheonWorkspace
    ) -> None:
        """Test temporary file creation with both prefix and suffix options.

        Tests create_tempfile generates path with both prefix and suffix.
        """
        result = workspace.create_tempfile(prefix="data_", suffix=".yaml")

        filename = result.name
        assert "_data_" in filename and filename.count("_") >= 2
        assert filename.endswith(".yaml")

        # Use pathlib for cross-platform path checking
        from pathlib import Path

        actual_path = Path(str(result))
        assert "temp" in actual_path.parts

    # Removed redundant test - covered by test_create_tempfile_no_options

    # Removed excessive test - UUID uniqueness is guaranteed by implementation

    # Removed redundant test - special characters covered by main tests

    # Removed redundant test - implementation detail not worth testing

    # Removed redundant test - security aspect covered by other tests

    # Phase 1 Comprehensive Tests - Load Project Config Tests

    def test_load_project_config_with_valid_yaml_all_keys(
        self, mock_filesystem: Mock
    ) -> None:
        """Test configuration loading with valid YAML containing all expected keys.

        Tests load_project_config parses valid YAML with all required configuration.
        """
        config_content = """
active_team: frontend
artifacts_root: custom-output
"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        result = PantheonWorkspace.load_project_config(mock_filesystem, "/test/project")

        assert result["active_team"] == "frontend"
        assert result["artifacts_root"] == "custom-output"

    def test_load_project_config_with_yaml_syntax_error(
        self, mock_filesystem: Mock
    ) -> None:
        """Test configuration loading handles YAML syntax errors gracefully.

        Tests load_project_config falls back to defaults on YAML parse errors.
        """
        invalid_yaml = "active_team: test\n  invalid: [unclosed"
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = invalid_yaml

        result = PantheonWorkspace.load_project_config(mock_filesystem, "/test/project")

        # Should fall back to defaults
        assert result["active_team"] == ""
        assert result["artifacts_root"] == "pantheon-artifacts"

    def test_load_project_config_missing_artifacts_root_uses_default(
        self, mock_filesystem: Mock
    ) -> None:
        """Test configuration loading uses default artifacts_root when missing.

        Tests load_project_config provides default value for missing artifacts_root key.
        """
        config_content = "active_team: backend"
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        result = PantheonWorkspace.load_project_config(mock_filesystem, "/test/project")

        assert result["active_team"] == "backend"
        assert result["artifacts_root"] == "pantheon-artifacts"  # Default value

    def test_load_project_config_ignores_extra_keys(
        self, mock_filesystem: Mock
    ) -> None:
        """Test configuration loading ignores unexpected extra keys.

        Tests load_project_config ignores unknown keys without causing errors.
        """
        config_content = """
active_team: test-team
artifacts_root: output
unknown_key: should_be_ignored
another_unknown: also_ignored
"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        result = PantheonWorkspace.load_project_config(mock_filesystem, "/test/project")

        assert result["active_team"] == "test-team"
        assert result["artifacts_root"] == "output"
        # Extra keys should be ignored, not cause errors

    def test_load_project_config_handles_non_string_active_team(
        self, mock_filesystem: Mock
    ) -> None:
        """Test configuration loading handles non-string values for active_team.

        Tests load_project_config handles type mismatches gracefully.
        """
        config_content = """
active_team: 12345
artifacts_root: output
"""
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = config_content

        result = PantheonWorkspace.load_project_config(mock_filesystem, "/test/project")

        # Should convert to string or handle appropriately
        assert result["artifacts_root"] == "output"

    def test_has_process_redirect_with_redirect_file(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test has_process_redirect returns True when redirect.md exists."""
        process_name = "get-plan"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Mock filesystem to indicate redirect.md exists
        mock_filesystem.exists.return_value = True

        result = workspace.has_process_redirect(process_name)

        assert result is True
        # Check that exists was called with redirect.md path (last call)
        last_call_args = mock_filesystem.exists.call_args[0][0]
        assert "redirect.md" in str(last_call_args)
        assert "get-plan" in str(last_call_args)

    def test_has_process_redirect_without_redirect_file(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test has_process_redirect returns False when redirect.md does not exist."""
        process_name = "create-ticket"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Reset mock to control return values specifically
        mock_filesystem.reset_mock()

        # Mock filesystem to indicate redirect.md does not exist
        mock_filesystem.exists.return_value = False

        result = workspace.has_process_redirect(process_name)

        assert result is False
        # Verify the path construction includes redirect.md
        call_args = mock_filesystem.exists.call_args[0][0]
        assert "redirect.md" in str(call_args)

    def test_has_process_redirect_with_nonexistent_process(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test has_process_redirect with non-existent process directory."""
        process_name = "nonexistent-process"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Reset mock to control return values specifically
        mock_filesystem.reset_mock()

        # Mock filesystem to indicate redirect.md does not exist
        mock_filesystem.exists.return_value = False

        result = workspace.has_process_redirect(process_name)

        assert result is False
        mock_filesystem.exists.assert_called_once()

    def test_get_process_redirect_successful_retrieval(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test get_process_redirect returns redirect URI when file exists."""
        process_name = "get-plan"
        expected_uri = "process://get-ticket?sections=plan"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Reset mock to control return values specifically
        mock_filesystem.reset_mock()

        # Mock filesystem to return redirect URI content
        mock_filesystem.read_text.return_value = (
            "  process://get-ticket?sections=plan  "
        )

        result = workspace.get_process_redirect(process_name)

        assert result == expected_uri
        mock_filesystem.read_text.assert_called_once()
        # Verify the path construction includes redirect.md
        call_args = mock_filesystem.read_text.call_args[0][0]
        assert "redirect.md" in str(call_args)
        assert "get-plan" in str(call_args)

    def test_get_process_redirect_file_not_found(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test get_process_redirect raises FileNotFoundError when file doesn't exist."""
        process_name = "create-ticket"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Reset mock to control return values specifically
        mock_filesystem.reset_mock()

        # Mock filesystem to raise FileNotFoundError
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            "redirect.md not found"
        )

        with pytest.raises(FileNotFoundError):
            workspace.get_process_redirect(process_name)

        mock_filesystem.read_text.assert_called_once()

    def test_get_process_redirect_empty_content(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test get_process_redirect handles empty redirect file."""
        process_name = "empty-redirect"

        # Set up active team
        workspace._project_config = {
            "active_team": "test-team",
            "artifacts_root": "artifacts",
        }

        # Reset mock to control return values specifically
        mock_filesystem.reset_mock()

        # Mock filesystem to return empty content
        mock_filesystem.read_text.return_value = "   "

        result = workspace.get_process_redirect(process_name)

        assert result == ""
        mock_filesystem.read_text.assert_called_once()


class TestRoutineTemplateRendering:
    """Test suite for Jinja template rendering in routine files."""

    @pytest.fixture
    def mock_filesystem(self) -> Mock:
        """Create a mock FileSystem for dependency injection."""
        return Mock(spec=FileSystem)

    @pytest.fixture
    def workspace(self, mock_filesystem: Mock) -> PantheonWorkspace:
        """Create a PantheonWorkspace instance with mocked dependencies."""
        # Mock config loading to return empty defaults
        mock_filesystem.exists.return_value = False

        return PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )

    @pytest.fixture
    def routine_template_content(self) -> str:
        """Sample routine template with Jinja variables."""
        return "# Routine: create-{{ artifact }}\n\n**Actor:** {{ pantheon_actor }}\n\nStep 1. Get schema for {{ artifact }}"

    def test_copy_default_create_routine_with_jinja_rendering(
        self,
        workspace: PantheonWorkspace,
        mock_filesystem: Mock,
        routine_template_content: str,
    ) -> None:
        """Test CREATE routine template renders Jinja variables with enhanced_parameters."""
        # Arrange: Mock filesystem to return template content
        target_path = PantheonPath("test", "create-ticket", "routine.md")
        enhanced_parameters = {"artifact": "ticket", "pantheon_actor": "ticket-agent"}

        # Configure mock filesystem to return template content
        mock_filesystem.read_bundled_resource.return_value = routine_template_content

        # Act: Copy routine with enhanced parameters
        result_path = workspace.copy_default_create_routine(
            target_path, enhanced_parameters
        )

        # Assert: Verify template was rendered
        assert result_path == target_path
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/create-process-routine.md"
        )
        mock_filesystem.write_text.assert_called_once()
        call_args = mock_filesystem.write_text.call_args
        rendered_content = call_args[0][1]

        # Verify Jinja variables were replaced
        assert "create-ticket" in rendered_content
        assert "ticket-agent" in rendered_content
        assert "{{ artifact }}" not in rendered_content
        assert "{{ pantheon_actor }}" not in rendered_content

    def test_copy_default_get_routine_with_jinja_rendering(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test GET routine template renders Jinja variables."""
        # Arrange: Setup template content
        template_content = (
            "# Routine: get-{{ artifact }}\n\nRetrieve {{ artifact }} by ID"
        )
        target_path = PantheonPath("test", "get-ticket", "routine.md")
        enhanced_parameters = {"artifact": "ticket"}

        # Configure mock filesystem to return template content
        mock_filesystem.read_bundled_resource.return_value = template_content

        # Act: Copy routine with enhanced parameters
        result_path = workspace.copy_default_get_routine(
            target_path, enhanced_parameters
        )

        # Assert: Verify template was rendered
        assert result_path == target_path
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/get-process-routine.md"
        )
        call_args = mock_filesystem.write_text.call_args
        rendered_content = call_args[0][1]
        assert "get-ticket" in rendered_content
        assert "{{ artifact }}" not in rendered_content

    def test_copy_default_update_routine_with_section_injection(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test UPDATE routine template renders both artifact and section variables."""
        # Arrange: Setup template with both artifact and section variables
        template_content = "# Routine: update-{{ artifact }}-{{ section }}\n\nUpdate {{ artifact }} {{ section }} section"
        target_path = PantheonPath("test", "update-ticket-plan", "routine.md")
        enhanced_parameters = {
            "artifact": "ticket",
            "section": "plan",
            "pantheon_actor": "planner-agent",
        }

        # Configure mock filesystem to return template content
        mock_filesystem.read_bundled_resource.return_value = template_content

        # Act: Copy routine with enhanced parameters including section
        result_path = workspace.copy_default_update_routine(
            target_path, enhanced_parameters
        )

        # Assert: Verify both artifact and section were rendered
        assert result_path == target_path
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/update-process-routine.md"
        )
        call_args = mock_filesystem.write_text.call_args
        rendered_content = call_args[0][1]
        assert "update-ticket-plan" in rendered_content
        assert "ticket plan section" in rendered_content
        assert "{{ artifact }}" not in rendered_content
        assert "{{ section }}" not in rendered_content

    def test_routine_template_rendering_fallback_on_error(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test routine falls back to raw template when Jinja rendering fails."""
        # Arrange: Setup template with invalid Jinja syntax
        invalid_template = "# Routine: {{ unclosed_variable }}\n\n{{ invalid"
        target_path = PantheonPath("test", "create-ticket", "routine.md")
        enhanced_parameters = {"artifact": "ticket"}

        # Configure mock filesystem to return invalid template content
        mock_filesystem.read_bundled_resource.return_value = invalid_template

        # Act: Copy routine with invalid template
        result_path = workspace.copy_default_create_routine(
            target_path, enhanced_parameters
        )

        # Assert: Should fall back to raw template content
        assert result_path == target_path
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/create-process-routine.md"
        )
        call_args = mock_filesystem.write_text.call_args
        rendered_content = call_args[0][1]
        # Should contain the raw template content, not rendered
        assert "{{ unclosed_variable }}" in rendered_content

    def test_routine_template_without_enhanced_parameters(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test routine uses raw template when no enhanced_parameters provided."""
        # Arrange: Setup template content
        template_content = "# Routine: create-{{ artifact }}\n\nGeneric routine"
        target_path = PantheonPath("test", "create-generic", "routine.md")

        # Configure mock filesystem to return template content
        mock_filesystem.read_bundled_resource.return_value = template_content

        # Act: Copy routine without enhanced parameters
        result_path = workspace.copy_default_create_routine(target_path, None)

        # Assert: Should use raw template content
        assert result_path == target_path
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/create-process-routine.md"
        )
        call_args = mock_filesystem.write_text.call_args
        rendered_content = call_args[0][1]
        assert (
            "{{ artifact }}" in rendered_content
        )  # Variables should remain unrendered

    def test_scaffold_create_process_passes_enhanced_parameters_to_routine(
        self, workspace: PantheonWorkspace, mock_filesystem: Mock
    ) -> None:
        """Test scaffold_create_process passes enhanced_parameters to routine copying."""
        # Arrange: Setup parameters
        bundle_root = PantheonPath("test-builds", "test-team", "processes")
        process_name = "create-ticket"
        enhanced_parameters = {"artifact": "ticket", "pantheon_actor": "test-actor"}

        # Configure mock filesystem to return template content
        template_content = "# Routine: create-{{ artifact }}"
        mock_filesystem.read_bundled_resource.return_value = template_content

        # Act: Call scaffold_create_process with enhanced_parameters
        paths = workspace.scaffold_create_process(
            bundle_root=bundle_root,
            process_name=process_name,
            content_md="test content",
            placement_jinja="test/",
            naming_jinja="{{ artifact }}.md",
            schema_jsonnet='{"type": "object"}',
            permissions_jsonnet=None,
            include_default_routine=True,
            enhanced_parameters=enhanced_parameters,
        )

        # Assert: Verify routine template was rendered with enhanced parameters
        assert len(paths) > 0
        mock_filesystem.read_bundled_resource.assert_called_once_with(
            "pantheon", "_templates/routines/create-process-routine.md"
        )

        # Find the routine.md write call
        routine_write_call = None
        for call in mock_filesystem.write_text.call_args_list:
            if "routine.md" in str(call[0][0]):
                routine_write_call = call
                break

        assert routine_write_call is not None
        rendered_content = routine_write_call[0][1]
        assert "create-ticket" in rendered_content
        assert "{{ artifact }}" not in rendered_content

    def test_get_artifact_template_environment_creates_proper_jinja_environment(self):
        """Test that get_artifact_template_environment creates Jinja environment with FileSystemLoader."""
        import jinja2

        mock_filesystem = Mock()
        workspace = PantheonWorkspace(
            "/test/project", "/test/artifacts", mock_filesystem
        )
        workspace._project_config = {"active_team": "test-team"}

        # Test creating template environment
        env = workspace.get_artifact_template_environment("test-process")

        # Verify it's a Jinja2 environment
        assert isinstance(env, jinja2.Environment)

        # Verify it has a FileSystemLoader
        assert isinstance(env.loader, jinja2.FileSystemLoader)

        # Verify the loader is configured with the correct path
        # The searchpath should include the process artifact directory
        expected_path_parts = ["test-team", "processes", "test-process", "artifact"]
        loader_path = str(env.loader.searchpath[0])
        for part in expected_path_parts:
            assert part in loader_path

        # Note: to_yaml filter is now added in _render_with_environment rather than here

        # Verify Jinja environment settings for Pantheon templates
        assert env.autoescape is False
        assert env.trim_blocks is False
        assert env.lstrip_blocks is True
        assert env.keep_trailing_newline is True

    def test_has_artifact_parser_returns_true_when_exists(self):
        """Test has_artifact_parser returns True when parser.jsonnet exists."""
        mock_filesystem = Mock()
        mock_filesystem.exists.return_value = True

        workspace = PantheonWorkspace(
            "/test/project", "/test/artifacts", mock_filesystem
        )
        workspace._project_config = {"active_team": "test-team"}

        # Reset mock to clear constructor calls
        mock_filesystem.exists.reset_mock()

        # Act: Check for parser.jsonnet
        result = workspace.has_artifact_parser("get-ticket")

        # Assert: Should return True and check correct path
        assert result is True
        mock_filesystem.exists.assert_called_once()
        call_args = mock_filesystem.exists.call_args[0][0]
        assert "test-team" in str(call_args)
        assert "get-ticket" in str(call_args)
        assert "parser.jsonnet" in str(call_args)

    def test_has_artifact_parser_returns_false_when_missing(self):
        """Test has_artifact_parser returns False when parser.jsonnet doesn't exist."""
        mock_filesystem = Mock()
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            "/test/project", "/test/artifacts", mock_filesystem
        )
        workspace._project_config = {"active_team": "test-team"}

        # Reset mock to clear constructor calls
        mock_filesystem.exists.reset_mock()

        # Act: Check for non-existent parser.jsonnet
        result = workspace.has_artifact_parser("get-architecture-guide")

        # Assert: Should return False
        assert result is False
        mock_filesystem.exists.assert_called_once()
        call_args = mock_filesystem.exists.call_args[0][0]
        assert "test-team" in str(call_args)
        assert "get-architecture-guide" in str(call_args)
        assert "parser.jsonnet" in str(call_args)
