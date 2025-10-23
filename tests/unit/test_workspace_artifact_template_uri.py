"""Unit tests for Workspace artifact-template:// URI resolution.

This test suite validates the extension of Workspace.get_resolved_content() to handle
artifact-template:// URIs for Jinja2 template includes. Tests cover URI parsing,
path construction, content retrieval, and error handling.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from pantheon.filesystem import FileSystem
from pantheon.workspace import PantheonWorkspace, ProjectConfig


class TestWorkspaceArtifactTemplateUri:
    """Test suite for Workspace artifact-template:// URI resolution."""

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

        # Set up active team for URI resolution
        workspace._project_config = ProjectConfig(
            active_team="test-team", artifacts_root="pantheon-artifacts"
        )

        return workspace

    def test_get_resolved_content_resolves_artifact_template_uri(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test artifact-template:// URI resolution via get_resolved_content.

        Validates that Workspace correctly routes artifact-template:// URIs
        to get_artifact_section_template() method and returns section content.
        """
        # Arrange: Configure filesystem to return section template
        uri = "artifact-template://update-architecture-guide/sections/core-principles"
        expected_content = "# Core Principles\n\n## Glass Box Philosophy\n\nTransparency over opacity..."
        mock_filesystem.read_text.return_value = expected_content

        # Act: Resolve URI via get_resolved_content
        result = workspace_with_config.get_resolved_content(uri)

        # Assert: Verify correct content returned and path construction
        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()

        # Verify path construction includes correct components
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "update-architecture-guide" in path_str
        assert "sections" in path_str
        assert "core-principles" in path_str
        assert path_str.endswith(".md")

    def test_get_resolved_content_requires_sub_path_for_artifact_template(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test artifact-template:// URIs require sub_path parameter.

        Validates that artifact-template:// URIs must include sub-path
        (sections/section-name) and raise ValueError if missing.
        """
        # Arrange: URI without sub-path
        uri_without_subpath = "artifact-template://update-guide"

        # Act & Assert: Verify ValueError raised with clear message
        with pytest.raises(
            ValueError,
            match="artifact-template:// URIs require sub-path.*sections/section-name",
        ):
            workspace_with_config.get_resolved_content(uri_without_subpath)

    def test_get_artifact_section_template_constructs_correct_path(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_artifact_section_template constructs conventional paths.

        Validates that method follows convention-over-configuration pattern:
        processes/{process-name}/artifact/{sub-path}.md
        """
        # Arrange: Configure filesystem response
        expected_content = "# Section Template Content"
        mock_filesystem.read_text.return_value = expected_content

        # Act: Call get_artifact_section_template directly
        result = workspace_with_config.get_artifact_section_template(
            "update-guide", "sections/core-principles"
        )

        # Assert: Verify content and path construction
        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)

        # Verify convention: processes/{process}/artifact/{sub_path}.md
        assert "processes" in path_str
        assert "update-guide" in path_str
        assert "artifact" in path_str
        assert (
            "sections" in path_str or "sections\\sections" in path_str
        )  # Handle double sections
        assert "core-principles.md" in path_str

    def test_get_artifact_section_template_appends_md_extension(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_artifact_section_template appends .md if not present.

        Validates that .md extension is automatically added to sub_path
        if not already present, following framework conventions.
        """
        # Arrange: Sub-path without .md extension
        expected_content = "# Template without extension"
        mock_filesystem.read_text.return_value = expected_content

        # Act: Call with sub-path lacking .md
        result = workspace_with_config.get_artifact_section_template(
            "update-guide", "sections/overview"
        )

        # Assert: Verify .md was appended
        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert path_str.endswith(".md")

    def test_get_artifact_section_template_preserves_existing_md_extension(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_artifact_section_template doesn't double-add .md extension.

        Validates that if sub_path already includes .md, it's not duplicated.
        """
        # Arrange: Sub-path with .md extension
        expected_content = "# Template with extension"
        mock_filesystem.read_text.return_value = expected_content

        # Act: Call with sub-path including .md
        result = workspace_with_config.get_artifact_section_template(
            "update-guide", "sections/principles.md"
        )

        # Assert: Verify .md not duplicated
        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert path_str.endswith(".md")
        assert not path_str.endswith(".md.md")

    def test_get_artifact_section_template_raises_file_not_found(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test get_artifact_section_template raises FileNotFoundError for missing templates.

        Validates that missing section templates result in clear FileNotFoundError
        with helpful context about which template was not found.
        """
        # Arrange: Configure filesystem to raise FileNotFoundError
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            "No such file or directory: 'sections/nonexistent.md'"
        )

        # Act & Assert: Verify FileNotFoundError propagated
        with pytest.raises(FileNotFoundError, match="sections/nonexistent.md"):
            workspace_with_config.get_artifact_section_template(
                "update-guide", "sections/nonexistent"
            )

    def test_artifact_template_uri_with_complex_section_paths(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test artifact-template:// URIs with nested section paths.

        Validates that complex sub-paths like sections/subsection/detail.md
        are correctly handled and mapped to filesystem paths.
        """
        # Arrange: Complex nested section path
        uri = "artifact-template://update-guide/sections/advanced/deployment.md"
        expected_content = "# Advanced Deployment"
        mock_filesystem.read_text.return_value = expected_content

        # Act: Resolve URI with nested path
        result = workspace_with_config.get_resolved_content(uri)

        # Assert: Verify correct resolution
        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "advanced" in path_str
        assert "deployment" in path_str

    def test_parse_semantic_uri_extracts_sub_path_from_artifact_template(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test _parse_semantic_uri extracts sub-path from artifact-template URIs.

        Validates that URI parsing correctly splits process name and sub-path
        for artifact-template:// URIs following process-name/sub-path format.
        """
        # Arrange: URI with sub-path
        uri = "artifact-template://update-guide/sections/core-principles"

        # Act: Parse URI
        scheme, process_name, sub_path, parameters = (
            workspace_with_config._parse_semantic_uri(uri)
        )

        # Assert: Verify correct parsing
        assert scheme == "artifact-template"
        assert process_name == "update-guide"
        assert sub_path == "sections/core-principles"
        assert isinstance(parameters, dict)

    def test_artifact_template_uri_with_multiple_processes(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test artifact-template:// URIs work for different processes.

        Validates that URI resolution works correctly across multiple
        processes, each with their own section templates.
        """
        # Test multiple processes
        test_cases = [
            (
                "artifact-template://create-architecture-guide/sections/overview",
                "# CREATE Overview",
            ),
            (
                "artifact-template://update-architecture-guide/sections/principles",
                "# UPDATE Principles",
            ),
            (
                "artifact-template://update-ticket/sections/technical-plan",
                "# Technical Plan",
            ),
        ]

        for uri, expected_content in test_cases:
            # Arrange: Reset mock and configure response
            mock_filesystem.reset_mock()
            mock_filesystem.read_text.return_value = expected_content

            # Act: Resolve URI
            result = workspace_with_config.get_resolved_content(uri)

            # Assert: Verify correct content
            assert result == expected_content
            mock_filesystem.read_text.assert_called_once()
