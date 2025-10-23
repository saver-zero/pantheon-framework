"""Unit tests for ProcessHandler implementation behavior.

Tests verify ProcessHandler orchestration logic, process type determination,
input validation, and execution flows for both Read and Write processes.
All dependencies are mocked to ensure complete isolation and fast execution.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from pantheon.artifact_engine import ArtifactEngine
from pantheon.constants import PARAM_SECTIONS
from pantheon.path import PantheonPath
from pantheon.process_handler import (
    ERROR_PREFIX_FILE_NOT_FOUND,
    ERROR_PREFIX_INVALID_INPUT,
    ERROR_PREFIX_PERMISSION_DENIED,
    INPUT_ACTOR,
    INPUT_FRAMEWORK_PARAMS,
    INPUT_INPUT_PARAMS,
    INPUT_PROCESS,
    ProcessHandler,
)
from pantheon.rae_engine import RaeEngine
from pantheon.workspace import PantheonWorkspace
from tests.helpers.process_input import make_framework_params, make_process_input


class TestProcessHandlerImplementation:
    """Test suite for ProcessHandler implementation functionality."""

    def test_constructor_stores_dependencies(self):
        """Test constructor properly stores workspace, artifact engine, and rae engine dependencies."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)

        # Act
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Assert
        assert handler._workspace is mock_workspace
        assert handler._artifact_engine is mock_artifact_engine
        assert handler._rae_engine is mock_rae_engine

    def test_validate_input_with_valid_input(self):
        """Test validate_input returns True for properly structured ProcessInput."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        valid_input = make_process_input(
            "test-process",
            "test-actor",
            input_params={"key": "value"},
        )

        # Act
        result = handler.validate_input("test-process", valid_input)

        # Assert
        assert result is True

    def test_validate_input_with_missing_keys(self):
        """Test validate_input raises ValueError for missing required keys."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        invalid_input = {INPUT_PROCESS: "test-process"}  # Missing actor and parameters

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required keys"):
            handler.validate_input("test-process", invalid_input)

    def test_validate_input_with_empty_process_name(self):
        """Test validate_input raises ValueError for empty process name."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        invalid_input = {
            INPUT_PROCESS: "",
            INPUT_ACTOR: "test-actor",
            INPUT_INPUT_PARAMS: {},
            INPUT_FRAMEWORK_PARAMS: {},
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Process name must be a non-empty string"):
            handler.validate_input("test-process", invalid_input)

    def test_validate_input_with_invalid_parameters_type(self):
        """Test validate_input raises ValueError for non-dict parameters."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        invalid_input = {
            INPUT_PROCESS: "test-process",
            INPUT_ACTOR: "test-actor",
            INPUT_INPUT_PARAMS: "not-a-dict",
            INPUT_FRAMEWORK_PARAMS: {},
        }

        # Act & Assert
        with pytest.raises(ValueError, match="input_params must be a dictionary"):
            handler.validate_input("test-process", invalid_input)

    def test_determine_process_type_create_process_with_content_template(self):
        """Test determine_process_type returns 'create' when content template exists."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_workspace.get_process_routine.return_value = "routine content"
        mock_workspace.get_artifact_content_template.return_value = "template content"

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        # Act
        process_type, templates = handler.determine_process_type("create-ticket")

        # Assert
        assert process_type == "create"
        assert "content" in templates
        assert templates["content"] == "template content"
        mock_workspace.get_process_routine.assert_called_once_with("create-ticket")
        mock_workspace.get_artifact_content_template.assert_called_once_with(
            "create-ticket"
        )

    def test_determine_process_type_get_process_without_template(self):
        """Test determine_process_type returns 'get' when no templates exist."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_workspace.get_process_routine.return_value = "routine content"
        mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError(
            "Template not found"
        )
        mock_workspace.get_artifact_patch_template.side_effect = FileNotFoundError(
            "Patch not found"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        # Act
        process_type, templates = handler.determine_process_type("get-ticket")

        # Assert
        assert process_type == "get"
        assert templates == {}  # No templates loaded for RETRIEVE operation
        mock_workspace.get_process_routine.assert_called_once_with("get-ticket")
        mock_workspace.get_artifact_content_template.assert_called_once_with(
            "get-ticket"
        )
        mock_workspace.get_artifact_patch_template.assert_called_once_with("get-ticket")

    def test_determine_process_type_update_process_with_patch_template(self):
        """Test determine_process_type returns 'update' when patch template exists."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_workspace.get_process_routine.return_value = "routine content"
        mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError(
            "Content template not found"
        )
        mock_workspace.get_artifact_patch_template.return_value = (
            "patch template content"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        # Act
        process_type, templates = handler.determine_process_type("update-ticket")

        # Assert
        assert process_type == "update"
        assert "patch" in templates
        assert templates["patch"] == "patch template content"
        mock_workspace.get_process_routine.assert_called_once_with("update-ticket")
        mock_workspace.get_artifact_content_template.assert_called_once_with(
            "update-ticket"
        )
        mock_workspace.get_artifact_patch_template.assert_called_once_with(
            "update-ticket"
        )

    def test_determine_process_type_nonexistent_process(self):
        """Test determine_process_type raises FileNotFoundError for nonexistent process."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_workspace.get_process_routine.side_effect = FileNotFoundError(
            "Process not found"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Process not found"):
            handler.determine_process_type("nonexistent-process")

        mock_workspace.get_process_routine.assert_called_once_with(
            "nonexistent-process"
        )
        # Template check should not be called if process doesn't exist
        mock_workspace.get_artifact_content_template.assert_not_called()

    def test_execute_create_process_successful_flow(self):
        """Test execute_create_process coordinates all components successfully."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_content_template.return_value = "template content"
        mock_workspace.get_artifact_directory_template.return_value = (
            "directory template"
        )
        mock_workspace.get_artifact_filename_template.return_value = "filename template"
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.generate_artifact.return_value = (
            "content",
            PantheonPath("output.md"),
        )
        mock_workspace.save_artifact.return_value = PantheonPath("saved/output.md")
        mock_workspace.summarize_created_files.return_value = [
            {
                "path": "pantheon-artifacts/saved/output.md",
                "type": "artifact",
                "description": "Generated artifact",
            }
        ]

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test Ticket"}
        framework_params = make_framework_params("create-ticket", "tech-lead")

        templates = {"content": "template content"}
        result = handler.execute_create_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is True
        assert result["error"] is None
        assert result["files_created"] is not None
        assert len(result["files_created"]) > 0
        assert "completed successfully" in result["output"]
        assert "All verifications complete" in result["output"]

        # Verify method call sequence - compile_schema now receives full profile from framework_params
        mock_workspace.get_process_schema.assert_called_once_with("create-ticket")
        # Note: get_team_profile is called in _build_enhanced_parameters (in execute()), not here
        mock_artifact_engine.compile_schema.assert_called_once_with(
            "schema content",
            {},
            "create-ticket",  # Empty profile from make_framework_params
        )
        mock_artifact_engine.validate.assert_called_once_with(
            {"title": "Test Ticket"}, {"type": "object"}
        )

    def test_execute_create_process_validation_failure(self):
        """Test execute_create_process handles validation failure gracefully."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks for validation failure
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_content_template.return_value = "template content"
        mock_workspace.get_artifact_directory_template.return_value = (
            "directory template"
        )
        mock_workspace.get_artifact_filename_template.return_value = "filename template"
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}

        # Mock validation to raise detailed validation error (new behavior)
        detailed_error = "Schema validation failed:\n  - Field 'title': 'title' is a required property"
        mock_artifact_engine.validate.side_effect = ValueError(detailed_error)

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"invalid": "data"}
        framework_params = make_framework_params("create-ticket", "tech-lead")

        templates = {"content": "template content"}
        result = handler.execute_create_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Schema validation failed:" in result["error"]
        assert "title" in result["error"]

    def test_execute_get_process_successful_flow(self):
        """Test execute_get_process retrieves artifact sections successfully."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        test_path = PantheonPath("artifacts/ticket.md")
        mock_artifact_engine.find_artifact.return_value = test_path
        mock_artifact_engine.get_artifact_sections.return_value = {
            "title": "Test Ticket",
            "description": "Test description",
        }

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params: dict[str, Any] = {}
        framework_params = make_framework_params(
            "get-ticket",
            "backend-engineer",
            pantheon_artifact_id="T012",
            pantheon_sections=["title", "description"],
        )

        # Act
        result = handler.execute_get_process(input_params, framework_params)

        # Assert
        assert result["success"] is True
        assert result["error"] is None
        assert result["files_created"] is None

        import json

        parsed_output = json.loads(result["output"])
        assert parsed_output["title"] == "Test Ticket"
        assert parsed_output["description"] == "Test description"

        mock_artifact_engine.find_artifact.assert_called_once_with("get-ticket", "T012")
        mock_artifact_engine.get_artifact_sections.assert_called_once_with(
            "get-ticket", test_path, ["title", "description"]
        )

    def test_execute_get_process_artifact_not_found(self):
        """Test execute_get_process handles missing artifact gracefully."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_artifact_engine.find_artifact.return_value = None

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params: dict[str, Any] = {}
        framework_params = make_framework_params(
            "get-ticket",
            "backend-engineer",
            pantheon_artifact_id="NONEXISTENT",
        )

        result = handler.execute_get_process(input_params, framework_params)

        assert result["success"] is False
        assert "Artifact not found: NONEXISTENT" in result["error"]
        assert result["files_created"] is None

    def test_execute_get_process_json_output_format(self):
        """Test execute_get_process returns properly formatted JSON output."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        test_path = PantheonPath("artifacts/complex.md")
        mock_artifact_engine.find_artifact.return_value = test_path
        mock_artifact_engine.get_artifact_sections.return_value = {
            "title": "Complex Artifact",
            "tags": ["tag1", "tag2", "tag3"],
            "metadata": {"version": "1.2.3", "author": "test-user"},
            "count": 42,
        }

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params: dict[str, Any] = {}
        framework_params = make_framework_params(
            "get-artifact",
            "test-user",
            pantheon_artifact_id="COMPLEX001",
            pantheon_sections=["title", "tags", "metadata", "count"],
        )

        result = handler.execute_get_process(input_params, framework_params)

        assert result["success"] is True
        assert result["error"] is None

        import json

        parsed_output = json.loads(result["output"])
        assert parsed_output["title"] == "Complex Artifact"
        assert parsed_output["tags"] == ["tag1", "tag2", "tag3"]
        assert parsed_output["metadata"]["version"] == "1.2.3"
        assert parsed_output["count"] == 42
        assert "\n" in result["output"]

    def test_execute_main_method_routes_to_create_process(self):
        """Test main execute method routes to create process correctly."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Mock workspace paths for framework context
        mock_workspace._project_root = Path("/test/project")
        mock_workspace._artifacts_root = Path("/test/project/pantheon-artifacts")

        # Mock redirect check to return False so normal flow is followed
        mock_workspace.has_process_redirect.return_value = False

        # Mock determine_process_type to return 'create' by having content template exist
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_artifact_content_template.return_value = "template content"
        mock_workspace.get_artifact_directory_template.return_value = (
            "directory template"
        )
        mock_workspace.get_artifact_filename_template.return_value = "filename template"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.generate_artifact.return_value = (
            "content",
            PantheonPath("output.md"),
        )
        mock_workspace.save_artifact.return_value = PantheonPath("saved/output.md")
        mock_workspace.summarize_created_files.return_value = [
            {
                "path": "pantheon-artifacts/saved/output.md",
                "type": "artifact",
                "description": "Generated artifact",
            }
        ]

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        process_input = make_process_input(
            "create-ticket",
            "tech-lead",
            input_params={"title": "Test"},
        )

        # Act
        result = handler.execute(process_input)

        # Assert
        assert result["success"] is True
        assert result["files_created"] is not None
        assert len(result["files_created"]) > 0

    def test_execute_handles_exceptions_gracefully(self):
        """Test main execute method handles exceptions and formats errors."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_workspace._project_root = Path("/test/project")
        mock_workspace._artifacts_root = Path("/test/project/pantheon-artifacts")
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Mock redirect check to return False so normal flow is followed
        mock_workspace.has_process_redirect.return_value = False

        # Configure mock to raise exception
        mock_workspace.get_process_schema.side_effect = FileNotFoundError(
            "Process not found"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        process_input = make_process_input(
            "nonexistent-process",
            "test-actor",
        )

        # Act
        result = handler.execute(process_input)

        # Assert
        assert result["success"] is False
        assert "File not found: Process not found" in result["error"]
        assert result["files_created"] is None

    def test_format_error_handles_different_exception_types(self):
        """Test format_error provides appropriate messages for different exception types."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)
        mock_rae_engine = Mock(spec=RaeEngine)
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test different exception types
        test_cases = [
            (
                "FileNotFoundError",
                "File missing",
                f"{ERROR_PREFIX_FILE_NOT_FOUND}: File missing",
            ),
            (
                "PermissionError",
                "Access denied",
                f"{ERROR_PREFIX_PERMISSION_DENIED}: Access denied",
            ),
            (
                "ValueError",
                "Invalid value",
                f"{ERROR_PREFIX_INVALID_INPUT}: Invalid value",
            ),
            ("RuntimeError", "Runtime issue", "RuntimeError: Runtime issue"),
        ]

        # Act & Assert
        for error_type, context, expected_message in test_cases:
            result = handler.format_error(error_type, context)
            assert result == expected_message

    def test_execute_update_process_successful_flow(self):
        """Test execute_update_process coordinates all components successfully."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks for successful UPDATE flow
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"sections": {"plan": {"start": "## plan", "end": "## /plan"}}}'
        )
        mock_workspace.read_artifact_file.return_value = (
            "# Artifact\n## plan\nOld content\n## /plan\n# End"
        )
        mock_workspace.save_artifact.return_value = PantheonPath("updated/artifact.md")
        mock_workspace.summarize_created_files.return_value = [
            {
                "path": "pantheon-artifacts/updated/artifact.md",
                "type": "artifact",
                "description": "Updated artifact",
            }
        ]

        mock_artifact_engine.compile_schema.return_value = {
            "properties": {
                "sections": {"properties": {"plan": {"type": "object"}}},
                "section_order": {"default": ["plan"]},
            }
        }
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )
        mock_artifact_engine._create_template_context.return_value = {
            "sections": {"plan": {"content": "New updated content"}},
            "pantheon_sections": ["plan"],
        }
        mock_artifact_engine.render_artifact_template.return_value = (
            "New updated content"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"sections": {"plan": {"content": "New updated content"}}}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        framework_params[PARAM_SECTIONS] = ["plan"]
        templates = {
            "patch": (
                "{% for section_name in pantheon_sections %}\n"
                "{{ sections[section_name].content }}\n"
                "{% endfor %}"
            )
        }

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is True
        assert result["error"] is None
        assert result["files_created"] is not None
        assert len(result["files_created"]) > 0
        assert "completed successfully" in result["output"]
        assert "All verifications complete" in result["output"]

        # Verify method call sequence
        mock_workspace.get_process_schema.assert_called_once_with("update-ticket")
        # Note: get_team_profile is called in _build_enhanced_parameters (in execute()), not here
        mock_artifact_engine.compile_schema.assert_called_once_with(
            "schema content",
            {},
            "update-ticket",  # Empty profile from make_framework_params
        )
        mock_artifact_engine.validate.assert_called_once_with(
            {"sections": {"plan": {"content": "New updated content"}}},
            mock_artifact_engine.compile_schema.return_value,
        )
        mock_artifact_engine.find_artifact.assert_called_once_with(
            "update-ticket", "T001"
        )
        mock_workspace.read_artifact_file.assert_called_once()
        mock_workspace.save_artifact.assert_called_once()

    def test_execute_update_process_preserves_other_sections(self):
        """Test execute_update_process only replaces target section, preserving all other content."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks for successful UPDATE flow with multi-section content
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = '{"sections": {"description": {"start": "## description", "end": "## /description"}}}'

        # Multi-section artifact content - we're targeting 'description' section
        original_content = """# Ticket T001

## title
Original Title
## /title

## description
Old description content that should be replaced
## /description

## plan
- Step 1: Do something
- Step 2: Do something else
## /plan

## acceptance
- [ ] Verify requirement 1
- [ ] Verify requirement 2
## /acceptance

# End of ticket"""

        mock_workspace.read_artifact_file.return_value = original_content
        # Capture the content passed to save_artifact
        saved_content = None

        def capture_save_artifact(content, path):
            nonlocal saved_content
            saved_content = content
            return PantheonPath("updated/artifact.md")

        mock_workspace.save_artifact.side_effect = capture_save_artifact
        mock_workspace.summarize_created_files.return_value = [
            {
                "path": "pantheon-artifacts/updated/artifact.md",
                "type": "artifact",
                "description": "Updated artifact",
            }
        ]

        mock_artifact_engine.compile_schema.return_value = {
            "properties": {
                "sections": {"properties": {"description": {"type": "object"}}},
                "section_order": {"default": ["description", "plan"]},
            }
        }
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )
        mock_artifact_engine._create_template_context.return_value = {
            "sections": {
                "description": {
                    "content": "Updated description content from patch template"
                }
            },
            "pantheon_sections": ["description"],
        }
        # The rendered template content should include proper newlines for section formatting
        mock_artifact_engine.render_artifact_template.return_value = (
            "\nUpdated description content from patch template\n"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {
            "sections": {
                "description": {
                    "content": "Updated description content from patch template"
                }
            }
        }
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        framework_params[PARAM_SECTIONS] = ["description"]
        templates = {
            "patch": (
                "{% for section_name in pantheon_sections %}\n"
                "{{ sections[section_name].content }}\n"
                "{% endfor %}"
            )
        }

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is True
        assert result["error"] is None
        assert result["files_created"] is not None
        assert len(result["files_created"]) > 0
        assert "completed successfully" in result["output"]
        assert "All verifications complete" in result["output"]

        # Verify that only the description section was modified
        assert saved_content is not None, (
            "save_artifact should have been called with content"
        )

        # Check that title section is preserved exactly
        assert "## title\nOriginal Title\n## /title" in saved_content

        # Check that plan section is preserved exactly
        assert (
            "## plan\n- Step 1: Do something\n- Step 2: Do something else\n## /plan"
            in saved_content
        )

        # Check that acceptance section is preserved exactly
        assert (
            "## acceptance\n- [ ] Verify requirement 1\n- [ ] Verify requirement 2\n## /acceptance"
            in saved_content
        )

        # Check that description section was updated with proper formatting (accounting for how _replace_section_content works)
        # The method adds newlines before and after the new content for proper formatting
        assert (
            "## description\n\nUpdated description content from patch template\n\n## /description"
            in saved_content
        )

        # Check that header and footer are preserved
        assert saved_content.startswith("# Ticket T001")
        assert saved_content.endswith("# End of ticket")

        # Verify the old description content is completely gone
        assert "Old description content that should be replaced" not in saved_content

    def test_execute_update_process_validation_failure(self):
        """Test execute_update_process handles validation failure gracefully."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks for validation failure
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}

        # Mock validation to raise detailed validation error (new behavior)
        detailed_error = "Schema validation failed:\n  - Field 'description': 'description' is a required property"
        mock_artifact_engine.validate.side_effect = ValueError(detailed_error)

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"invalid": "data"}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        templates = {"patch": "template content"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Schema validation failed:" in result["error"]
        assert "description" in result["error"]

    def test_execute_update_process_missing_artifact_id(self):
        """Test execute_update_process handles missing artifact_id parameter in multi-artifact mode."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks for successful validation and template loading
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_target_section.return_value = '{"section": "plan"}'
        # Multi-artifact mode: has parser.jsonnet
        mock_workspace.has_artifact_parser.return_value = True
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        # find_artifact returns None because artifact_id is required but missing
        mock_artifact_engine.find_artifact.return_value = None

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test"}  # Missing artifact_id
        framework_params = make_framework_params("update-ticket", "tech-lead")
        templates = {"patch": "template content"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert: Error message matches GET process behavior (simpler message)
        assert result["success"] is False
        assert result["files_created"] is None
        assert "not found" in result["error"].lower()

    def test_execute_update_process_artifact_not_found(self):
        """Test execute_update_process handles artifact not found."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"sections": {"plan": {"start": "## plan", "end": "## /plan"}}}'
        )
        mock_artifact_engine.compile_schema.return_value = {
            "properties": {
                "sections": {"properties": {"plan": {"type": "object"}}},
                "section_order": {"default": ["plan"]},
            }
        }
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = None  # Artifact not found

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test"}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="NONEXISTENT",
        )
        templates = {"patch": "template content"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Artifact not found: NONEXISTENT" in result["error"]

    def test_execute_update_process_invalid_target_config(self):
        """Test execute_update_process handles invalid target configuration."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks with invalid target configuration
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '"not_an_object"'  # Invalid JSON
        )
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test"}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        templates = {"patch": "template content"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Invalid target configuration - expected JSON object" in result["error"]

    def test_execute_update_process_missing_section_field(self):
        """Test execute_update_process handles missing start/end fields in target config."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks with missing start/end fields
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"other": "field"}'  # Missing start and end
        )
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test"}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        templates = {"patch": "template content"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Invalid target configuration" in result["error"]

    def test_execute_update_process_patch_template_render_failure(self):
        """Test execute_update_process handles patch template rendering failure."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks with template rendering failure
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"sections": {"plan": {"start": "## plan", "end": "## /plan"}}}'
        )
        mock_artifact_engine.compile_schema.return_value = {
            "properties": {
                "sections": {"properties": {"plan": {"type": "object"}}},
                "section_order": {"default": ["plan"]},
            }
        }
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )
        mock_artifact_engine._create_template_context.return_value = {
            "sections": {"plan": {"content": "fail"}},
            "pantheon_sections": ["plan"],
        }
        mock_artifact_engine.render_artifact_template.side_effect = Exception(
            "Template error"
        )
        mock_workspace.get_artifact_template_environment.return_value = Mock()

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"sections": {"plan": {"content": "fail"}}}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        framework_params[PARAM_SECTIONS] = ["plan"]
        templates = {
            "patch": (
                "{% for section_name in pantheon_sections %}\n"
                "{{ sections[section_name].content }}\n"
                "{% endfor %}"
            )
        }

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Failed to update section 'plan'" in result["error"]

    def test_execute_update_process_section_not_found_in_artifact(self):
        """Test execute_update_process handles target section not found in artifact."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks with successful flow until section replacement
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = '{"sections": {"missing_section": {"start": "## missing_section", "end": "## /missing_section"}}}'
        mock_workspace.read_artifact_file.return_value = (
            "# Artifact\n## plan\nContent\n## /plan\n# End"  # No missing_section
        )
        mock_artifact_engine.compile_schema.return_value = {
            "properties": {
                "sections": {"properties": {"missing_section": {"type": "object"}}},
                "section_order": {"default": ["missing_section"]},
            }
        }
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )
        mock_artifact_engine._create_template_context.return_value = {
            "sections": {"missing_section": {"content": "New content"}},
            "pantheon_sections": ["missing_section"],
        }
        mock_artifact_engine.render_artifact_template.return_value = "New content"
        mock_workspace.get_artifact_template_environment.return_value = Mock()

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"sections": {"missing_section": {"content": "New content"}}}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        framework_params[PARAM_SECTIONS] = ["missing_section"]
        templates = {
            "patch": (
                "{% for section_name in pantheon_sections %}\n"
                "{{ sections[section_name].content }}\n"
                "{% endfor %}"
            )
        }

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Target section 'missing_section' not found" in result["error"]

    def test_execute_update_process_save_artifact_failure(self):
        """Test execute_update_process handles save artifact failure."""
        # Arrange
        mock_workspace = Mock(spec=PantheonWorkspace)
        mock_artifact_engine = Mock(spec=ArtifactEngine)

        # Configure mocks with save failure
        mock_workspace.get_process_schema.return_value = "schema content"
        mock_workspace.get_team_profile.return_value = (
            "active_profile: test\n"
            "profiles:\n"
            "  test:\n"
            "    priorities: ['high', 'medium', 'low']"
        )
        mock_workspace.get_artifact_locator.return_value = "locator template"
        mock_workspace.get_artifact_parser.return_value = "parser template"
        mock_workspace.get_artifact_target_section.return_value = (
            '{"start": "## plan", "end": "## /plan"}'
        )
        mock_workspace.read_artifact_file.return_value = (
            "# Artifact\n## plan\nOld content\n## /plan\n# End"
        )
        mock_workspace.save_artifact.side_effect = Exception("Save failed")
        mock_artifact_engine.compile_schema.return_value = {"type": "object"}
        mock_artifact_engine.validate.return_value = True
        mock_artifact_engine.find_artifact.return_value = PantheonPath(
            "artifacts/test.md"
        )
        mock_artifact_engine._create_template_context.return_value = {"title": "Test"}
        mock_artifact_engine.render_artifact_template.return_value = "New content"
        mock_workspace.get_artifact_template_environment.return_value = Mock()

        handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, Mock(spec=RaeEngine)
        )

        input_params = {"title": "Test"}
        framework_params = make_framework_params(
            "update-ticket",
            "tech-lead",
            pantheon_artifact_id="T001",
        )
        templates = {"patch": "{{ title }}"}

        # Act
        result = handler.execute_update_process(
            input_params, framework_params, templates
        )

        # Assert
        assert result["success"] is False
        assert result["files_created"] is None
        assert "Failed to save updated artifact" in result["error"]
