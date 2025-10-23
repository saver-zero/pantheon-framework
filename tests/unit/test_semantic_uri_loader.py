"""Unit tests for Semantic URI Loader for Jinja2 templates.

This test suite validates the custom Jinja2 loader that enables artifact-template://
semantic URIs in template include statements. Tests cover URI detection, delegation
to Workspace, error handling, and integration with Jinja2's loader protocol.
"""

from __future__ import annotations

from unittest.mock import Mock

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, TemplateNotFound
import pytest

from pantheon.artifact_engine import SemanticUriLoader
from pantheon.workspace import PantheonWorkspace


class TestSemanticUriLoader:
    """Test suite for SemanticUriLoader custom Jinja2 loader."""

    @pytest.fixture
    def mock_workspace(self) -> Mock:
        """Create a mock Workspace for dependency injection.

        Returns:
            Mock Workspace with spec to ensure proper interface usage
        """
        return Mock(spec=PantheonWorkspace)

    @pytest.fixture
    def semantic_uri_loader(self, mock_workspace: Mock) -> SemanticUriLoader:
        """Create a SemanticUriLoader instance with mocked workspace.

        Args:
            mock_workspace: Mocked Workspace dependency

        Returns:
            Configured SemanticUriLoader for testing
        """
        return SemanticUriLoader(mock_workspace)

    def test_loader_delegates_semantic_uris_to_workspace(
        self, semantic_uri_loader: SemanticUriLoader, mock_workspace: Mock
    ) -> None:
        """Test loader delegates artifact-template:// URIs to Workspace.

        Validates that SemanticUriLoader correctly identifies semantic URIs
        and routes them to workspace.get_resolved_content() for resolution.
        """
        # Arrange: Configure workspace mock to return section template content
        uri = "artifact-template://update-guide/sections/core-principles"
        expected_content = "# Core Principles\n\nGlass Box philosophy..."
        mock_workspace.get_resolved_content.return_value = expected_content

        # Act: Request template via Jinja2 loader protocol
        source, filename, uptodate_func = semantic_uri_loader.get_source(
            None,
            uri,  # environment parameter not used
        )

        # Assert: Verify delegation to workspace and correct return tuple
        assert source == expected_content
        assert filename == uri
        assert callable(uptodate_func)
        assert uptodate_func() is False  # Always reload for development
        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_loader_raises_template_not_found_for_regular_paths(
        self, semantic_uri_loader: SemanticUriLoader, mock_workspace: Mock
    ) -> None:
        """Test loader raises TemplateNotFound for non-semantic URIs.

        Validates that regular file paths are not handled by SemanticUriLoader,
        allowing fallback to FileSystemLoader in ChoiceLoader chain.
        """
        # Arrange: Regular file path (not semantic URI)
        regular_path = "templates/section.md"

        # Act & Assert: Verify TemplateNotFound raised for fallback
        with pytest.raises(TemplateNotFound):
            semantic_uri_loader.get_source(None, regular_path)

        # Verify workspace was not called for non-semantic paths
        mock_workspace.get_resolved_content.assert_not_called()

    def test_loader_converts_file_not_found_to_template_not_found(
        self, semantic_uri_loader: SemanticUriLoader, mock_workspace: Mock
    ) -> None:
        """Test loader converts FileNotFoundError to TemplateNotFound.

        Validates that when Workspace cannot resolve a URI, the FileNotFoundError
        is converted to Jinja2's TemplateNotFound for proper error handling.
        """
        # Arrange: Configure workspace to raise FileNotFoundError
        uri = "artifact-template://missing-process/sections/nonexistent"
        mock_workspace.get_resolved_content.side_effect = FileNotFoundError(
            f"Section template not found: {uri}"
        )

        # Act & Assert: Verify conversion to TemplateNotFound
        with pytest.raises(TemplateNotFound, match="Section template not found"):
            semantic_uri_loader.get_source(None, uri)

        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_loader_converts_value_error_to_template_not_found(
        self, semantic_uri_loader: SemanticUriLoader, mock_workspace: Mock
    ) -> None:
        """Test loader converts ValueError to TemplateNotFound.

        Validates that invalid URI formats result in TemplateNotFound
        with clear error messages for debugging.
        """
        # Arrange: Configure workspace to raise ValueError for invalid URI
        uri = "artifact-template://invalid-format"
        mock_workspace.get_resolved_content.side_effect = ValueError(
            "Missing sub_path: artifact-template requires sections/section-name format"
        )

        # Act & Assert: Verify conversion to TemplateNotFound with context
        with pytest.raises(TemplateNotFound, match="Missing sub_path"):
            semantic_uri_loader.get_source(None, uri)

        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_loader_handles_multiple_semantic_uri_schemes(
        self, semantic_uri_loader: SemanticUriLoader, mock_workspace: Mock
    ) -> None:
        """Test loader handles various semantic URI schemes correctly.

        Validates that SemanticUriLoader properly detects and delegates
        multiple types of semantic URIs beyond just artifact-template://.
        """
        # Test various semantic URI schemes
        test_uris = [
            "artifact-template://update-guide/sections/overview",
            "process-schema://create-ticket",
            "process-routine://update-plan",
        ]

        for uri in test_uris:
            # Arrange: Reset mock and configure response
            mock_workspace.reset_mock()
            mock_workspace.get_resolved_content.return_value = f"Content for {uri}"

            # Act: Request template
            source, filename, uptodate = semantic_uri_loader.get_source(None, uri)

            # Assert: Verify each URI type is delegated
            assert source == f"Content for {uri}"
            assert filename == uri
            mock_workspace.get_resolved_content.assert_called_once_with(uri)


class TestJinja2EnvironmentIntegration:
    """Test suite for Jinja2 environment integration with SemanticUriLoader."""

    @pytest.fixture
    def mock_workspace(self) -> Mock:
        """Create a mock Workspace for dependency injection."""
        return Mock(spec=PantheonWorkspace)

    def test_choice_loader_tries_semantic_uri_loader_first(
        self, mock_workspace: Mock, tmp_path
    ) -> None:
        """Test ChoiceLoader prioritizes SemanticUriLoader over FileSystemLoader.

        Validates that semantic URIs are resolved via SemanticUriLoader
        before attempting FileSystemLoader fallback.
        """
        # Arrange: Create Jinja2 environment with ChoiceLoader
        semantic_loader = SemanticUriLoader(mock_workspace)
        file_loader = FileSystemLoader(str(tmp_path))
        choice_loader = ChoiceLoader([semantic_loader, file_loader])
        env = Environment(loader=choice_loader)

        # Configure workspace to return section template
        uri = "artifact-template://update-guide/sections/core-principles"
        expected_content = "# Core Principles\n\nTransparency over opacity"
        mock_workspace.get_resolved_content.return_value = expected_content

        # Act: Render template with semantic URI include
        template_source = f"{{% include '{uri}' %}}"
        template = env.from_string(template_source)
        result = template.render()

        # Assert: Verify semantic URI was resolved via workspace
        assert result == expected_content
        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_choice_loader_falls_back_to_file_loader(
        self, mock_workspace: Mock, tmp_path
    ) -> None:
        """Test ChoiceLoader falls back to FileSystemLoader for regular paths.

        Validates that non-semantic paths are handled by FileSystemLoader
        when SemanticUriLoader raises TemplateNotFound.
        """
        # Arrange: Create actual template file
        template_file = tmp_path / "section.md"
        template_file.write_text("# Regular File Template")

        # Create Jinja2 environment with ChoiceLoader
        semantic_loader = SemanticUriLoader(mock_workspace)
        file_loader = FileSystemLoader(str(tmp_path))
        choice_loader = ChoiceLoader([semantic_loader, file_loader])
        env = Environment(loader=choice_loader)

        # Act: Include regular file path
        template_source = "{% include 'section.md' %}"
        template = env.from_string(template_source)
        result = template.render()

        # Assert: Verify file was loaded from filesystem
        assert result == "# Regular File Template"
        # Workspace should not be called for regular paths
        mock_workspace.get_resolved_content.assert_not_called()

    def test_jinja2_environment_renders_template_with_semantic_includes(
        self, mock_workspace: Mock
    ) -> None:
        """Test Jinja2 renders template containing semantic URI includes.

        Validates complete template rendering workflow with artifact-template://
        includes, demonstrating the integration between SemanticUriLoader and
        Jinja2's template resolution system.
        """
        # Arrange: Create environment with semantic loader
        semantic_loader = SemanticUriLoader(mock_workspace)
        env = Environment(loader=semantic_loader)

        # Configure workspace to return section templates
        mock_workspace.get_resolved_content.side_effect = lambda uri: {
            "artifact-template://update-guide/sections/overview": "## Overview\n\nThe Pantheon Framework...",
            "artifact-template://update-guide/sections/principles": "## Principles\n\nGlass Box philosophy...",
        }.get(uri, "")

        # Act: Render template with multiple semantic includes
        template_source = """# Architecture Guide

{% include 'artifact-template://update-guide/sections/overview' %}

{% include 'artifact-template://update-guide/sections/principles' %}
"""
        template = env.from_string(template_source)
        result = template.render()

        # Assert: Verify both includes were resolved and rendered
        assert "## Overview" in result
        assert "The Pantheon Framework..." in result
        assert "## Principles" in result
        assert "Glass Box philosophy..." in result
        assert mock_workspace.get_resolved_content.call_count == 2
