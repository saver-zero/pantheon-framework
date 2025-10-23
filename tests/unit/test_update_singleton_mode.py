"""Unit tests for UPDATE process singleton mode support.

This module tests that UPDATE processes can operate in singleton mode (without
artifact_id when parser.jsonnet is absent), matching the behavior already
implemented in GET processes. Tests verify that ProcessHandler delegates mode
detection to ArtifactEngine.find_artifact() rather than implementing separate
validation logic.
"""

from unittest.mock import Mock

import pytest

from pantheon.constants import (
    BUILTIN_ARTIFACT_ID,
    BUILTIN_PROCESS,
    PARAM_SECTIONS,
    RESULT_ERROR,
    RESULT_SUCCESS,
)
from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessHandler


class TestUpdateSingletonMode:
    """Test suite for UPDATE process singleton mode support."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_artifact_engine(self):
        """Create mock artifact engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_rae_engine(self):
        """Create mock RAE engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def handler(self, mock_workspace, mock_artifact_engine, mock_rae_engine):
        """Create ProcessHandler with mocked dependencies."""
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def mock_update_templates_base(self, mock_workspace):
        """Configure base mock template retrieval for UPDATE processes.

        Sets up common template mocks used across all UPDATE tests:
        - content.md returns FileNotFoundError (signals UPDATE not CREATE)
        - patch.md, locator.jsonnet, parser.jsonnet return minimal valid templates
        """
        mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError()
        mock_workspace.get_artifact_patch_template.return_value = "{{ new_content }}"
        mock_workspace.get_artifact_locator.return_value = "{}"
        mock_workspace.get_artifact_parser.return_value = "{}"
        return mock_workspace

    @pytest.fixture
    def mock_success_operations(self, mock_workspace, mock_artifact_engine):
        """Configure mocks for successful file operations.

        Sets up common mocks for template rendering and artifact saving
        used in success test cases.
        """
        mock_workspace.get_artifact_template_environment.return_value = Mock()
        mock_artifact_engine._create_template_context.return_value = {
            "new_content": "Updated content"
        }
        mock_artifact_engine.render_artifact_template.return_value = "Updated content"
        mock_workspace.save_artifact.return_value = "test/path.md"
        mock_workspace.summarize_created_files.return_value = ["test/path.md"]

    def test_update_whole_document_singleton_mode_success(
        self,
        handler,
        mock_workspace,
        mock_artifact_engine,
        mock_update_templates_base,
        mock_success_operations,
    ):
        """UPDATE processes in singleton mode (no parser.jsonnet) should find and update single artifact without artifact_id."""
        # Arrange: Configure mocks for singleton whole document UPDATE
        process_name = "update-singleton-doc"
        input_params = {"new_content": "Updated content"}
        framework_params = {
            BUILTIN_PROCESS: process_name,
            # Note: No BUILTIN_ARTIFACT_ID provided (singleton mode)
        }

        # Mock singleton mode detection - has_artifact_parser returns False
        mock_workspace.has_artifact_parser.return_value = False

        # Mock find_artifact to return valid path for singleton mode (called with None)
        artifact_path = PantheonPath("docs/singleton-doc.md")
        mock_artifact_engine.find_artifact.return_value = artifact_path

        # Act: Execute UPDATE process without artifact_id
        result = handler._execute_whole_document_update(
            process_name,
            input_params,
            framework_params,
            {"patch": "{{ new_content }}"},
        )

        # Assert: Process succeeds and find_artifact called with None
        assert result[RESULT_SUCCESS] is True
        mock_artifact_engine.find_artifact.assert_called_once_with(process_name, None)
        mock_workspace.save_artifact.assert_called_once()

    def test_update_sectioned_singleton_mode_success(
        self, handler, mock_workspace, mock_artifact_engine
    ):
        """UPDATE sectioned processes in singleton mode should find and update single artifact without artifact_id."""
        # Arrange: Configure mocks for singleton sectioned UPDATE
        process_name = "update-singleton-ticket"
        input_params = {"section_updates": {"plan": {"body": "Updated plan"}}}
        framework_params = {
            BUILTIN_PROCESS: process_name,
            PARAM_SECTIONS: ["plan"],
            # Note: No BUILTIN_ARTIFACT_ID provided (singleton mode)
        }

        # Mock template retrieval for UPDATE operation
        mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError()
        mock_workspace.get_artifact_patch_template.return_value = "{{ body }}"
        mock_workspace.get_artifact_locator.return_value = "{}"
        mock_workspace.get_artifact_parser.return_value = "{}"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"sections": {"plan": {"start": "<!-- START -->", "end": "<!-- END -->"}}}'
        )

        # Mock singleton mode detection - has_artifact_parser returns False
        mock_workspace.has_artifact_parser.return_value = False

        # Mock find_artifact to return valid path for singleton mode
        artifact_path = PantheonPath("tickets/singleton-ticket.md")
        mock_artifact_engine.find_artifact.return_value = artifact_path

        # Mock file reading and template rendering
        mock_workspace.read_artifact_file.return_value = (
            "<!-- START -->\nOld plan\n<!-- END -->"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()
        mock_artifact_engine._create_template_context.return_value = {
            "body": "Updated plan"
        }
        mock_artifact_engine.render_artifact_template.return_value = "Updated plan"
        mock_workspace.save_artifact.return_value = "tickets/singleton-ticket.md"
        mock_workspace.summarize_created_files.return_value = [
            "tickets/singleton-ticket.md"
        ]

        compiled_schema = {"properties": {"section_order": {"default": ["plan"]}}}

        # Act: Execute sectioned UPDATE process without artifact_id
        result = handler._execute_sectioned_update(
            process_name,
            input_params,
            framework_params,
            {"patch": "{{ body }}"},
            compiled_schema,
        )

        # Assert: Process succeeds and find_artifact called with None
        assert result[RESULT_SUCCESS] is True
        mock_artifact_engine.find_artifact.assert_called_once_with(process_name, None)
        mock_workspace.save_artifact.assert_called_once()

    def test_update_multi_artifact_mode_requires_artifact_id(
        self, handler, mock_workspace, mock_artifact_engine, mock_update_templates_base
    ):
        """UPDATE processes in multi-artifact mode (with parser.jsonnet) should fail when artifact_id is missing."""
        # Arrange: Configure mocks for multi-artifact mode UPDATE
        process_name = "update-multi-doc"
        input_params = {"new_content": "Updated content"}
        framework_params = {
            BUILTIN_PROCESS: process_name,
            # Note: No BUILTIN_ARTIFACT_ID provided but parser exists (multi-artifact mode)
        }

        # Mock multi-artifact mode detection - has_artifact_parser returns True
        mock_workspace.has_artifact_parser.return_value = True

        # Mock find_artifact to return None (ID required)
        mock_artifact_engine.find_artifact.return_value = None

        # Act: Execute UPDATE process without artifact_id in multi-artifact mode
        result = handler._execute_whole_document_update(
            process_name, input_params, framework_params, {"patch": "{{ new_content }}"}
        )

        # Assert: Process fails with error message (matches GET process behavior)
        assert result[RESULT_SUCCESS] is False
        assert "not found" in result[RESULT_ERROR].lower()
        mock_artifact_engine.find_artifact.assert_called_once_with(process_name, None)

    def test_update_singleton_mode_zero_artifacts_found(
        self, handler, mock_workspace, mock_artifact_engine, mock_update_templates_base
    ):
        """UPDATE processes in singleton mode should fail when no artifacts are found."""
        # Arrange: Configure mocks for singleton mode with no artifacts
        process_name = "update-singleton-doc"
        input_params = {"new_content": "Updated content"}
        framework_params = {
            BUILTIN_PROCESS: process_name,
        }

        # Mock singleton mode detection - has_artifact_parser returns False
        mock_workspace.has_artifact_parser.return_value = False

        # Mock find_artifact to return None (no artifact found)
        mock_artifact_engine.find_artifact.return_value = None

        # Act: Execute UPDATE process in singleton mode with no artifacts
        result = handler._execute_whole_document_update(
            process_name, input_params, framework_params, {"patch": "{{ new_content }}"}
        )

        # Assert: Process fails with error message
        assert result[RESULT_SUCCESS] is False
        assert "not found" in result[RESULT_ERROR].lower()
        mock_artifact_engine.find_artifact.assert_called_once_with(process_name, None)

    def test_update_singleton_mode_multiple_artifacts_found(
        self, handler, mock_workspace, mock_artifact_engine, mock_update_templates_base
    ):
        """UPDATE processes in singleton mode should fail when multiple artifacts are found."""
        # Arrange: Configure mocks for singleton mode with multiple artifacts
        process_name = "update-singleton-doc"
        input_params = {"new_content": "Updated content"}
        framework_params = {
            BUILTIN_PROCESS: process_name,
        }

        # Mock singleton mode detection - has_artifact_parser returns False
        mock_workspace.has_artifact_parser.return_value = False

        # Mock find_artifact to return None (ambiguous match - multiple found)
        # Note: find_artifact returns None when multiple artifacts match in singleton mode
        mock_artifact_engine.find_artifact.return_value = None

        # Act: Execute UPDATE process in singleton mode with multiple artifacts
        result = handler._execute_whole_document_update(
            process_name, input_params, framework_params, {"patch": "{{ new_content }}"}
        )

        # Assert: Process fails with error message
        assert result[RESULT_SUCCESS] is False
        assert "not found" in result[RESULT_ERROR].lower()
        mock_artifact_engine.find_artifact.assert_called_once_with(process_name, None)

    def test_update_multi_artifact_mode_backward_compatibility(
        self,
        handler,
        mock_workspace,
        mock_artifact_engine,
        mock_update_templates_base,
        mock_success_operations,
    ):
        """UPDATE processes in multi-artifact mode should continue working with artifact_id provided (backward compatibility)."""
        # Arrange: Configure mocks for multi-artifact mode with explicit ID
        process_name = "update-multi-doc"
        artifact_id = "T001"
        input_params = {"new_content": "Updated content"}
        framework_params = {
            BUILTIN_PROCESS: process_name,
            BUILTIN_ARTIFACT_ID: artifact_id,
        }

        # Mock multi-artifact mode detection
        mock_workspace.has_artifact_parser.return_value = True

        # Mock find_artifact to return valid path for explicit ID
        artifact_path = PantheonPath("tickets/T001_ticket.md")
        mock_artifact_engine.find_artifact.return_value = artifact_path

        # Act: Execute UPDATE process with explicit artifact_id
        result = handler._execute_whole_document_update(
            process_name, input_params, framework_params, {"patch": "{{ new_content }}"}
        )

        # Assert: Process succeeds and find_artifact called with explicit ID
        assert result[RESULT_SUCCESS] is True
        mock_artifact_engine.find_artifact.assert_called_once_with(
            process_name, artifact_id
        )
        mock_workspace.save_artifact.assert_called_once()
