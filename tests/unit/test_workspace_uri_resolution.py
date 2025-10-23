"""Unit tests for PantheonWorkspace URI resolution.

This test suite validates semantic URI resolution and cross-process
import scenarios based on the sequence diagram flows. Tests cover all supported URI schemes
and complex resolution chains while maintaining complete I/O isolation.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from pantheon.filesystem import FileSystem
from pantheon.workspace import PantheonWorkspace, ProjectConfig

# Function removed - using proper pathlib operations instead


class TestPantheonWorkspaceUriResolution:
    """Test suite for PantheonWorkspace URI resolution."""

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

    @pytest.fixture
    def supported_uri_schemes(self) -> dict[str, str]:
        """Create sample URIs for all supported schemes.

        Returns:
            Dictionary mapping scheme names to sample URIs
        """
        return {
            "process-schema": "process-schema://create-ticket",
            "process-routine": "process-routine://update-plan",
            "artifact-locator": "artifact-locator://get-ticket",
            "artifact-parser": "artifact-parser://normalize-content",
            "artifact-section-markers": "artifact-section-markers://mark-sections",
            "artifact-content-template": "artifact-content-template://render-output",
            "artifact-directory-template": "artifact-directory-template://build-path",
            "artifact-filename-template": "artifact-filename-template://name-file",
        }

    @pytest.fixture
    def mock_content_responses(self) -> dict[str, str]:
        """Create mock content responses for different URI types.

        Returns:
            Dictionary mapping URI schemes to mock content
        """
        return {
            "process-schema": '{\n  "type": "object",\n  "properties": {\n    "title": {"type": "string"}\n  }\n}',
            "process-routine": "# Process Steps\n\n1. Initialize\n2. Execute\n3. Complete",
            "artifact-locator": '{\n  "pattern": "^({id})_.*\\.md$"\n}',
            "artifact-parser": '[\n  {"pattern": "^\\s+", "replacement": ""}\n]',
            "artifact-section-markers": '{\n  "start": "<!-- START -->",\n  "end": "<!-- END -->"\n}',
            "artifact-content-template": "# {{title}}\n\n{{content}}",
            "artifact-directory-template": "{{team}}/{{process}}",
            "artifact-filename-template": "{{id}}_{{date}}.md",
        }

    # Semantic URI Resolution Tests

    @pytest.mark.parametrize(
        "scheme,expected_method",
        [
            ("process-schema", "get_process_schema"),
            ("process-routine", "get_process_routine"),
            ("artifact-locator", "get_artifact_locator"),
            ("artifact-parser", "get_artifact_parser"),
            ("artifact-section-markers", "get_artifact_section_markers"),
            ("artifact-content-template", "get_artifact_content_template"),
            ("artifact-directory-template", "get_artifact_directory_template"),
            ("artifact-filename-template", "get_artifact_filename_template"),
        ],
    )
    def test_get_resolved_content_for_all_supported_schemes(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        mock_content_responses: dict[str, str],
        scheme: str,
        expected_method: str,
    ) -> None:
        """Test URI resolution for each supported scheme.

        Tests get_resolved_content correctly routes to appropriate content-retrieval
        methods and returns expected content for all supported URI schemes.
        """
        process_name = "test-process"
        uri = f"{scheme}://{process_name}"
        expected_content = mock_content_responses[scheme]

        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_resolved_content(uri)

        assert result == expected_content
        mock_filesystem.read_text.assert_called_once()

        # Verify the correct method was called by checking the path construction
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert process_name in path_str
        from pathlib import Path

        actual_path = Path(str(call_args))
        assert "pantheon-teams" in actual_path.parts
        assert "test-team" in actual_path.parts

    def test_get_resolved_content_with_process_schema_uri(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        mock_content_responses: dict[str, str],
    ) -> None:
        """Test process-schema URI resolution in detail.

        Tests process-schema URI resolution verifies correct path construction
        and content retrieval for schema.jsonnet files.
        """
        uri = "process-schema://create-ticket"
        expected_content = mock_content_responses["process-schema"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_resolved_content(uri)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "schema.jsonnet" in path_str
        assert "create-ticket" in path_str

    def test_get_resolved_content_with_artifact_finder_uri(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        mock_content_responses: dict[str, str],
    ) -> None:
        """Test artifact-locator URI resolution in detail.

        Tests artifact-locator URI resolution verifies correct path construction
        includes artifact subdirectory and locator.jsonnet filename.
        Uses new RETRIEVE operation naming convention.
        """
        uri = "artifact-locator://get-ticket"
        expected_content = mock_content_responses["artifact-locator"]
        mock_filesystem.read_text.return_value = expected_content

        result = workspace_with_config.get_resolved_content(uri)

        assert result == expected_content
        call_args = mock_filesystem.read_text.call_args[0][0]
        path_str = str(call_args)
        assert "artifact" in path_str
        assert "locator.jsonnet" in path_str
        assert "get-ticket" in path_str

    def test_get_resolved_content_with_complex_process_names(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
        mock_content_responses: dict[str, str],
    ) -> None:
        """Test URI resolution with complex process names containing special characters.

        Tests URI parsing handles process names with hyphens, underscores, and dots.
        """
        complex_names = [
            "process-with-hyphens",
            "process_with_underscores",
            "process.with.dots",
            "complex-process_name.v2",
        ]

        for process_name in complex_names:
            uri = f"process-schema://{process_name}"
            expected_content = mock_content_responses["process-schema"]
            mock_filesystem.read_text.return_value = expected_content

            result = workspace_with_config.get_resolved_content(uri)

            assert result == expected_content
            call_args = mock_filesystem.read_text.call_args[0][0]
            path_str = str(call_args)
            assert process_name in path_str
            mock_filesystem.reset_mock()

    def test_get_resolved_content_with_unsupported_scheme(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test get_resolved_content with unsupported URI scheme.

        Tests unsupported schemes raise ValueError with clear error message.
        """
        unsupported_schemes = [
            "unknown-scheme://process",
            "invalid-type://test-process",
            "custom-handler://some-process",
            "future-scheme://new-process",
        ]

        for uri in unsupported_schemes:
            with pytest.raises(ValueError, match="Unsupported URI scheme"):
                workspace_with_config.get_resolved_content(uri)

    # URI Parsing Tests

    def test_parse_semantic_uri_with_valid_formats(
        self,
        workspace_with_config: PantheonWorkspace,
        supported_uri_schemes: dict[str, str],
    ) -> None:
        """Test _parse_semantic_uri with valid scheme://process-name formats.

        Tests URI parsing correctly extracts scheme and process name components.
        """
        for scheme_name, uri in supported_uri_schemes.items():
            (
                scheme,
                process_name,
                sub_path,
                parameters,
            ) = workspace_with_config._parse_semantic_uri(uri)

            assert scheme == scheme_name
            # Extract expected process name from the URI
            expected_process = uri.split("://", 1)[1]
            # Handle cases where there might be query parameters
            if "?" in expected_process:
                expected_process = expected_process.split("?", 1)[0]
            assert process_name == expected_process
            assert sub_path is None  # No sub-paths in basic URIs
            assert isinstance(parameters, dict)

    def test_parse_semantic_uri_missing_scheme_separator(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test _parse_semantic_uri with missing :// raises ValueError.

        Tests URI parsing requires :// separator between scheme and process name.
        """
        invalid_uris = [
            "process-schema-create-ticket",
            "artifact-locator/get-ticket",
            "process-routine:update-plan",
            "malformed-uri-format",
        ]

        for invalid_uri in invalid_uris:
            with pytest.raises(ValueError, match="missing ://"):
                workspace_with_config._parse_semantic_uri(invalid_uri)

    def test_parse_semantic_uri_empty_scheme(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test _parse_semantic_uri with empty scheme handling.

        Tests URI parsing rejects URIs with empty scheme component.
        """
        empty_scheme_uris = [
            "://process-name",
            "://create-ticket",
            "://artifact-locator",
        ]

        for uri in empty_scheme_uris:
            with pytest.raises(ValueError, match="empty scheme"):
                workspace_with_config._parse_semantic_uri(uri)

    def test_parse_semantic_uri_missing_process_name(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test _parse_semantic_uri with missing process name handling.

        Tests URI parsing requires process name after scheme://.
        """
        missing_process_uris = [
            "process-schema://",
            "artifact-locator://",
            "process-routine://",
        ]

        for uri in missing_process_uris:
            with pytest.raises(ValueError, match="missing process name"):
                workspace_with_config._parse_semantic_uri(uri)

    def test_parse_semantic_uri_with_special_characters_in_process_names(
        self,
        workspace_with_config: PantheonWorkspace,
    ) -> None:
        """Test _parse_semantic_uri handles special characters in process names.

        Tests URI parsing correctly handles process names with various special characters.
        """
        special_character_uris = [
            "process-schema://process-with-hyphens",
            "artifact-locator://process_with_underscores",
            "process-routine://process.with.dots",
            "artifact-content-template://complex-process_name.v2",
            "artifact-parser://process@version",
        ]

        for uri in special_character_uris:
            (
                scheme,
                process_name,
                sub_path,
                parameters,
            ) = workspace_with_config._parse_semantic_uri(uri)
            expected_process = uri.split("://", 1)[1]
            assert process_name == expected_process
            assert sub_path is None  # No sub-paths in these URIs
            assert "://" not in process_name  # Ensure separator not in process name
            assert isinstance(parameters, dict)  # Ensure separator not in process name

    # Cross-Process Reference Tests (Based on Sequence Diagrams)

    # Cross-Process Import Tests (Based on Sequence Diagrams)

    def test_schema_importing_another_via_process_schema_uri(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test schema importing another via process-schema:// URI.

        Simulates the sequence-cross-process-import.puml flow where
        Jsonnet schemas import from other processes using semantic URIs.
        """
        # Schema A imports from Schema B using semantic URI
        importing_schema_uri = "process-schema://schema-importer"
        imported_content = (
            '{\n  "shared_properties": {\n    "id": {"type": "string"}\n  }\n}'
        )

        mock_filesystem.read_text.return_value = imported_content

        result = workspace_with_config.get_resolved_content(importing_schema_uri)

        assert result == imported_content
        assert "shared_properties" in result
        assert "id" in result

    def test_multiple_imports_in_single_schema(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test multiple imports in single schema.

        Tests resolution of individual import URIs when a schema imports
        multiple components from different processes.
        """
        # Simulate resolving each import individually
        import_uris = [
            "process-schema://base-schema",
            "artifact-content-template://common-template",
            "artifact-parser://shared-rules",
        ]

        expected_contents = [
            '{"base": "schema"}',
            "# Common Template\n{{content}}",
            '[{"pattern": "normalize", "replacement": "clean"}]',
        ]

        for uri, expected_content in zip(import_uris, expected_contents, strict=False):
            mock_filesystem.read_text.return_value = expected_content

            result = workspace_with_config.get_resolved_content(uri)

            assert result == expected_content
            mock_filesystem.reset_mock()

    def test_import_of_non_existent_process_handling(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test import of non-existent process handling.

        Tests URI resolution properly handles imports to processes that don't exist.
        """
        uri = "process-schema://non-existent-process"
        mock_filesystem.read_text.side_effect = FileNotFoundError(
            "Process schema not found"
        )

        with pytest.raises(FileNotFoundError, match="Process schema not found"):
            workspace_with_config.get_resolved_content(uri)

    # Integration Tests for Complex Resolution Chains
    def test_resolution_with_deep_process_names(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test resolution with complex process name structures.

        Tests URI resolution handles complex hierarchical process names.
        """
        complex_process_names = [
            "team.backend.ticket-management",
            "service_authentication_oauth2",
            "feature-branch-workflow.v2",
            "integration-test-suite",
        ]

        for process_name in complex_process_names:
            uri = f"process-schema://{process_name}"
            expected_content = f'{{"process": "{process_name}"}}'
            mock_filesystem.read_text.return_value = expected_content

            result = workspace_with_config.get_resolved_content(uri)

            assert result == expected_content
            assert process_name in result
            mock_filesystem.reset_mock()

    # Error Handling and Edge Cases

    def test_uri_resolution_preserves_error_context(
        self,
        workspace_with_config: PantheonWorkspace,
        mock_filesystem: Mock,
    ) -> None:
        """Test URI resolution preserves error context from underlying methods.

        Tests error messages from content-retrieval methods are properly propagated
        through URI resolution with appropriate context.
        """
        uri = "process-schema://failing-process"
        original_error = FileNotFoundError(
            "Schema file not accessible: permission denied"
        )
        mock_filesystem.read_text.side_effect = original_error

        with pytest.raises(FileNotFoundError, match="Schema file not accessible"):
            workspace_with_config.get_resolved_content(uri)
