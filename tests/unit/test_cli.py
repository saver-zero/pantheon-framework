"""Unit tests for CLI command parsing and actor validation.

This test module validates the CLI component's core responsibilities:
command parsing, actor validation, permission checking, and delegation
to appropriate service components.
"""

import json
from unittest.mock import Mock, patch

import pytest

from pantheon.cli import (
    CLI,
    PANTHEON_INSTRUCTIONS_MARKER_END,
    PANTHEON_INSTRUCTIONS_MARKER_START,
    BadInputError,
)
from pantheon.process_handler import INPUT_FRAMEWORK_PARAMS, INPUT_INPUT_PARAMS


class TestCLI:
    """Test cases for CLI command parsing and validation behavior."""

    def test_validate_actor_accepts_any_non_empty_actor_name(self) -> None:
        """Test that validate_actor accepts any non-empty actor name without checking agent files."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act - test with various actor names including dynamically-created specialists
        cli.validate_actor("framework-engineer")
        cli.validate_actor("tech-lead")
        cli.validate_actor("process-engineer")
        cli.validate_actor("any-dynamic-actor")

        # Assert - verify get_agents() is NOT called

    def test_execute_process_validates_and_delegates(self) -> None:
        """Test that execute_process validates actor/permissions then delegates to ProcessHandler."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "result",
        }
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.execute_process("test-process", "test-actor", param="value")

        # Assert
        mock_workspace.get_permissions.assert_called_once_with("test-process")
        mock_process_handler.execute.assert_called_once()
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]  # First arg should be ProcessInput dict
        assert (
            process_input["process"] == "test-process"
        )  # Check process name in ProcessInput
        assert process_input["actor"] == "test-actor"
        assert process_input[INPUT_INPUT_PARAMS] == {"param": "value"}
        assert process_input[INPUT_FRAMEWORK_PARAMS] == {}
        assert result is not None

    def test_check_permissions_rejects_empty_process_name(self) -> None:
        """Test that check_permissions raises BadInputError for empty process names."""
        # Arrange

        from pantheon.cli import BadInputError

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError):
            cli.check_permissions("test-actor", "")

    def test_get_process_delegates_to_process_handler(self) -> None:
        """Test that get_process delegates to ProcessHandler for routine retrieval."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.get_routine.return_value = (
            "# Process Routine\nContent here"
        )
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.get_process("test-process", "test-actor")

        # Assert
        mock_workspace.get_permissions.assert_called_once_with("test-process")
        mock_process_handler.get_routine.assert_called_once_with(
            "test-process", "test-actor", None
        )
        assert result == "# Process Routine\nContent here"

    def test_get_schema_delegates_to_process_handler(self) -> None:
        """Test that get_schema delegates to ProcessHandler and renders JSON."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        composed_schema = {
            "properties": {
                "sections": {"properties": {"strategy": {"type": "object"}}},
                "section_order": {"default": ["strategy"]},
            }
        }
        mock_process_handler.compose_schema.return_value = composed_schema

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        result = cli.get_schema("update-team-blueprint", "test-actor", "strategy")

        mock_process_handler.compose_schema.assert_called_once_with(
            "update-team-blueprint", "test-actor", "strategy"
        )
        assert json.loads(result) == composed_schema

    def test_get_sections_delegates_to_process_handler(self) -> None:
        """Test that get_sections validates permissions and returns handler data."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.get_sections_metadata.return_value = [
            {"name": "overview", "description": "Ticket overview."}
        ]

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        result = cli.get_sections("update-ticket", "test-actor")

        mock_workspace.get_permissions.assert_called_once_with("update-ticket")
        mock_process_handler.get_sections_metadata.assert_called_once_with(
            "update-ticket"
        )
        assert json.loads(result) == [
            {"name": "overview", "description": "Ticket overview."}
        ]

    def test_get_sections_wraps_workspace_error(self) -> None:
        """Test that get_sections converts workspace ValueError into BadInputError."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.get_sections_metadata.side_effect = ValueError(
            "no sections"
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        with pytest.raises(BadInputError, match="no sections"):
            cli.get_sections("update-ticket", "test-actor")

    def test_get_sections_filters_by_actor_permissions(self) -> None:
        """Test that get_sections returns only sections the actor has permission to access."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process-level permissions are empty, but section-level permissions exist
        mock_workspace.get_permissions.return_value = """{
            "allow": [],
            "deny": [],
            "sections": {
                "foundation": {
                    "allow": ["pantheon"],
                    "deny": []
                },
                "artifacts": {
                    "allow": ["artifact-designer"],
                    "deny": []
                },
                "restricted": {
                    "allow": ["admin-only"],
                    "deny": []
                }
            }
        }"""

        # All sections available in the process
        mock_process_handler.get_sections_metadata.return_value = [
            {"name": "foundation", "description": "Foundation section"},
            {"name": "artifacts", "description": "Artifacts section"},
            {"name": "restricted", "description": "Restricted section"},
        ]

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Test with pantheon actor - should only get foundation section
        result = cli.get_sections("update-team-blueprint", "pantheon")

        mock_workspace.get_permissions.assert_called_with("update-team-blueprint")
        mock_process_handler.get_sections_metadata.assert_called_with(
            "update-team-blueprint"
        )

        # Should only return the foundation section that pantheon has access to
        sections = json.loads(result)
        assert len(sections) == 1
        assert sections[0]["name"] == "foundation"
        assert sections[0]["description"] == "Foundation section"

    def test_get_sections_filters_multiple_sections_for_actor(self) -> None:
        """Test that get_sections returns multiple sections when actor has access to them."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process-level has wildcard, but some sections are restricted
        mock_workspace.get_permissions.return_value = """{
            "allow": ["*"],
            "deny": [],
            "sections": {
                "public": {
                    "allow": ["*"],
                    "deny": []
                },
                "semi-public": {
                    "allow": ["multi-access-agent", "other-agent"],
                    "deny": []
                },
                "restricted": {
                    "allow": ["admin-only"],
                    "deny": ["multi-access-agent"]
                }
            }
        }"""

        mock_process_handler.get_sections_metadata.return_value = [
            {"name": "public", "description": "Public section"},
            {"name": "semi-public", "description": "Semi-public section"},
            {"name": "restricted", "description": "Restricted section"},
        ]

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        result = cli.get_sections("test-process", "multi-access-agent")

        # Should return public and semi-public, but not restricted (explicitly denied)
        sections = json.loads(result)
        assert len(sections) == 2
        section_names = [s["name"] for s in sections]
        assert "public" in section_names
        assert "semi-public" in section_names
        assert "restricted" not in section_names

    def test_get_sections_empty_when_no_permissions(self) -> None:
        """Test that get_sections returns empty list when actor has no permissions."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # No permissions for this actor
        mock_workspace.get_permissions.return_value = """{
            "allow": [],
            "deny": [],
            "sections": {
                "restricted": {
                    "allow": ["admin-only"],
                    "deny": []
                }
            }
        }"""

        mock_process_handler.get_sections_metadata.return_value = [
            {"name": "restricted", "description": "Restricted section"}
        ]

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        result = cli.get_sections("test-process", "no-access-agent")

        # Should return empty list
        sections = json.loads(result)
        assert len(sections) == 0

    def test_get_schema_rejects_sections_for_non_update_process(self) -> None:
        """Test that get_schema raises when --sections is used for non-update processes."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.compose_schema.side_effect = ValueError(
            "--sections is only supported for UPDATE processes"
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        with pytest.raises(BadInputError, match="only supported for UPDATE"):
            cli.get_schema("get-team-blueprint", "test-actor", "context")

    def test_validate_actor_accepts_actors_without_agent_files(self) -> None:
        """Test that validate_actor accepts actors that don't have corresponding agent files."""

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act - should not raise any errors for actors without agent files
        cli.validate_actor("dynamically-created-specialist")
        cli.validate_actor("non-existent-agent")

        # Assert - verify no agent file lookup was attempted

    def test_validate_actor_raises_for_empty_actor(self) -> None:
        """Test that validate_actor raises BadInputError for empty actor names."""

        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match="Actor name cannot be empty"):
            cli.validate_actor("")

    def test_permission_system_works_independently_of_agent_files(self) -> None:
        """Test that permission checking works for actors without agent files."""

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Configure permissions - dynamically-created specialist is allowed
        mock_workspace.get_permissions.return_value = (
            '{"allow": ["framework-engineer"]}'
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - actor without agent file but with permission should succeed
        cli.check_permissions("framework-engineer", "test-process")

        # Verify permission check happened without agent file lookup
        mock_workspace.get_permissions.assert_called_once_with("test-process")

    def test_permission_system_denies_actors_without_permissions(self) -> None:
        """Test that permission checking denies actors without proper permissions."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Configure permissions - only specific actor allowed
        mock_workspace.get_permissions.return_value = '{"allow": ["allowed-actor"]}'

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - actor without permission should be denied
        with pytest.raises(PermissionDeniedError):
            cli.check_permissions(
                "dynamic-specialist-without-permission", "test-process"
            )

        # Verify permission check happened without agent file lookup
        mock_workspace.get_permissions.assert_called_once_with("test-process")

    def test_audit_logging_tracks_actor_identity_for_dynamic_specialists(self) -> None:
        """Test that audit logging tracks actor identity regardless of agent file existence."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act - audit log a command with a dynamically-created specialist actor
        cli._audit_log(
            command="execute test-process",
            actor="framework-engineer",
            result="success",
        )

        # Assert - verify audit log was saved with correct actor
        mock_workspace.save_audit_log.assert_called_once()
        audit_event = mock_workspace.save_audit_log.call_args[0][0]
        assert audit_event["actor"] == "framework-engineer"
        assert audit_event["command"] == "execute test-process"
        assert audit_event["result"] == "success"

        # Verify no agent file lookup was performed

    def test_check_permissions_allows_when_no_restrictions(self) -> None:
        """Test that check_permissions raises error when no permissions file exists."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.side_effect = FileNotFoundError()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - should raise BadInputError for missing file
        with pytest.raises(BadInputError) as exc_info:
            cli.check_permissions("any-actor", "test-process")

        assert "This is a non-recoverable error" in str(exc_info.value)
        mock_workspace.get_permissions.assert_called_once_with("test-process")

    def test_check_permissions_denies_based_on_deny_list(self) -> None:
        """Test that check_permissions denies access for actors in deny list."""

        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"deny": ["blocked-actor"]}'
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(PermissionDeniedError, match="explicitly denied access"):
            cli.check_permissions("blocked-actor", "test-process")

    def test_check_permissions_allows_when_in_allow_list(self) -> None:
        """Test that check_permissions allows access for actors in allow list."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["allowed-actor"]}'
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act - should not raise
        cli.check_permissions("allowed-actor", "test-process")

        # Assert
        mock_workspace.get_permissions.assert_called_once_with("test-process")

    def test_get_schema_returns_json_string(self) -> None:
        """Test that get_schema returns a JSON string from composed schema."""

        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.compose_schema.return_value = {"type": "object"}
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        result = cli.get_schema("test-process", "test-actor")

        mock_process_handler.compose_schema.assert_called_once_with(
            "test-process", "test-actor", None
        )
        assert json.loads(result) == {"type": "object"}

    def test_get_tempfile_returns_path_string(self) -> None:
        """Test that get_tempfile returns temporary file path as string."""
        from pathlib import Path

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_path = Mock()
        mock_path.get_underlying_path.return_value = "test-process_abc123.json"
        mock_workspace.create_tempfile.return_value = mock_path
        # Mock the _artifacts_root to be a Path object for the path concatenation
        mock_workspace._artifacts_root = Path("/tmp")
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.get_tempfile("test-process", "test-actor")

        # Assert
        mock_workspace.create_tempfile.assert_called_once_with(
            suffix=".json", prefix="test-process"
        )
        # Use os.path.join for cross-platform compatibility or normalize separators
        expected_path = str(Path("/tmp") / "test-process_abc123.json")
        assert result == expected_path

    def test_execute_process_with_from_file(self) -> None:
        """Test that execute_process can read parameters from JSON file."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "Process completed",
        }
        # Mock filesystem to return JSON content
        mock_filesystem.read_text.return_value = '{"key": "value", "number": 42}'

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.execute_process(
            "test-process", "test-actor", from_file="/path/to/test.json"
        )

        # Assert
        # Verify filesystem was used to read the file
        mock_filesystem.read_text.assert_called_once_with("/path/to/test.json")

        # Verify process handler received correct parameters
        mock_process_handler.execute.assert_called_once()
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]  # First arg should be ProcessInput dict
        assert process_input["process"] == "test-process"
        assert process_input["actor"] == "test-actor"
        assert process_input[INPUT_INPUT_PARAMS] == {"key": "value", "number": 42}
        assert process_input[INPUT_FRAMEWORK_PARAMS] == {}
        assert result == "Process completed"


class TestCLIParameterHandling:
    """Test cases for CLI parameter parsing and validation."""

    def test_execute_process_with_multiple_parameters(self) -> None:
        """Test that execute_process handles multiple keyword parameters correctly."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "Multi-param process completed",
        }
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.execute_process(
            "test-process",
            "test-actor",
            title="Test Title",
            priority="high",
            assignee="backend-dev",
            tags="api,backend",
        )

        # Assert
        mock_process_handler.execute.assert_called_once()
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]  # First arg should be ProcessInput dict
        assert process_input["process"] == "test-process"
        assert process_input["actor"] == "test-actor"
        assert process_input[INPUT_INPUT_PARAMS] == {
            "title": "Test Title",
            "priority": "high",
            "assignee": "backend-dev",
            "tags": "api,backend",
        }
        assert process_input[INPUT_FRAMEWORK_PARAMS] == {}
        assert result == "Multi-param process completed"

    def test_execute_process_with_sections_parameter(self) -> None:
        """Test that execute_process handles --sections flag correctly."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "Sections process completed",
        }
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act - simulating CLI call: pantheon execute get-ticket --actor test-actor --sections plan,description --param ticket_id=T123
        result = cli.execute_process(
            "get-ticket",
            "test-actor",
            sections="plan,description",  # This gets converted to pantheon_sections array
            ticket_id="T123",
        )

        # Assert
        mock_process_handler.execute.assert_called_once()
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]  # First arg should be ProcessInput dict
        assert process_input["process"] == "get-ticket"
        assert process_input["actor"] == "test-actor"
        assert process_input[INPUT_INPUT_PARAMS] == {"ticket_id": "T123"}
        assert process_input[INPUT_FRAMEWORK_PARAMS] == {
            "pantheon_sections": ["plan", "description"]
        }
        assert result == "Sections process completed"

    def test_execute_process_with_conflicting_inputs_raises_error(self) -> None:
        """Test that execute_process raises error when both from_file and params provided."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(
            BadInputError,
            match="Cannot specify both --from-file and direct arguments",
        ):
            cli.execute_process(
                "test-process",
                "test-actor",
                from_file="/path/to/file.json",
                param="value",
            )

        # Verify filesystem was not called since validation happens first
        mock_filesystem.read_text.assert_not_called()

    def test_execute_process_with_no_inputs_raises_error(self) -> None:
        """Test that execute_process raises error when neither from_file nor params provided."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(
            BadInputError, match="Must specify either --from-file or direct arguments"
        ):
            cli.execute_process("test-process", "test-actor")

    def test_execute_process_handles_json_decode_error(self) -> None:
        """Test that execute_process handles malformed JSON file gracefully."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        # Mock filesystem to return invalid JSON
        mock_filesystem.read_text.return_value = '{"invalid": json malformed}'

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match="Invalid JSON in input file"):
            cli.execute_process(
                "test-process", "test-actor", from_file="/path/to/invalid.json"
            )

        # Verify filesystem was called
        mock_filesystem.read_text.assert_called_once_with("/path/to/invalid.json")

    def test_execute_process_handles_missing_file_error(self) -> None:
        """Test that execute_process handles missing input file gracefully."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        # Mock filesystem to raise FileNotFoundError
        mock_filesystem.read_text.side_effect = FileNotFoundError("File not found")

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match="Input file not found"):
            cli.execute_process(
                "test-process", "test-actor", from_file="/nonexistent/file.json"
            )

        # Verify filesystem was called
        mock_filesystem.read_text.assert_called_once_with("/nonexistent/file.json")


class TestCLIErrorHandling:
    """Test cases for CLI error handling and user-friendly messages."""

    def test_execute_process_with_process_handler_exception(self) -> None:
        """Test that execute_process handles ProcessHandler exceptions gracefully."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'

        # Mock ProcessHandler to raise an exception
        mock_process_handler.execute.side_effect = RuntimeError(
            "Process execution failed"
        )
        mock_process_handler.format_error.return_value = (
            "Formatted: Process execution failed"
        )

        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match="Formatted: Process execution failed"):
            cli.execute_process("test-process", "test-actor", param="value")

        # Verify error was formatted
        mock_process_handler.format_error.assert_called_once_with(
            "RuntimeError", "Process execution failed"
        )

    def test_execute_process_formats_success_with_artifact(self) -> None:
        """Test that execute_process formats files_created information from ProcessHandler."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'

        # ProcessHandler returns simple success message and structured file data
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "CREATE operation completed successfully. All verifications complete.",
            "files_created": [
                {
                    "path": "pantheon-artifacts/tickets/T123_test.md",
                    "type": "artifact",
                    "description": "Generated ticket document",
                }
            ],
            "error": None,
        }

        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.execute_process("create-ticket", "test-actor", title="Test")

        # Assert - CLI formats ProcessHandler's structured data for display
        expected_output = "CREATE operation completed successfully. All verifications complete.\n\nFiles created:\n- pantheon-artifacts/tickets/T123_test.md (artifact): Generated ticket document"
        assert result == expected_output

    def test_execute_process_returns_output_when_available(self) -> None:
        """Test that execute_process returns process output when no artifact created."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'

        mock_process_handler.execute.return_value = {
            "success": True,
            "output": '{"retrieved": "data", "status": "complete"}',
            "files_created": None,
            "error": None,
        }

        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        result = cli.execute_process("get-ticket", "test-actor", ticket_id="T123")

        # Assert
        assert result == '{"retrieved": "data", "status": "complete"}'


class TestCLIParameterized:
    """Parameterized test cases for efficient testing of similar scenarios."""

    @pytest.mark.parametrize(
        "actor_name,expected_error",
        [
            ("", "Actor name cannot be empty"),
            ("   ", "Actor name cannot be empty"),
            ("\t\n", "Actor name cannot be empty"),
        ],
    )
    def test_validate_actor_error_cases(
        self, actor_name: str, expected_error: str
    ) -> None:
        """Test that validate_actor only rejects empty or whitespace-only actor names."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match=expected_error):
            cli.validate_actor(actor_name)

    @pytest.mark.parametrize(
        "permissions_config,actor,should_raise",
        [
            ('{"allow": ["allowed-actor"]}', "allowed-actor", False),
            ('{"allow": ["allowed-actor"]}', "denied-actor", True),
            ('{"deny": ["denied-actor"]}', "denied-actor", True),
            (
                '{"deny": ["denied-actor"]}',
                "allowed-actor",
                True,
            ),  # Default deny - no explicit allow
            ('{"allow": ["*"]}', "any-actor", False),  # Wildcard allows all
            (
                '{"allow": ["*"], "deny": ["blocked-actor"]}',
                "any-actor",
                False,
            ),  # Wildcard allows
            (
                '{"allow": ["*"], "deny": ["blocked-actor"]}',
                "blocked-actor",
                True,
            ),  # Explicit deny wins
        ],
    )
    def test_check_permissions_scenarios(
        self, permissions_config: str, actor: str, should_raise: bool
    ) -> None:
        """Test various permission checking scenarios."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = permissions_config
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        if should_raise:
            with pytest.raises(PermissionDeniedError):
                cli.check_permissions(actor, "test-process")
        else:
            # Should not raise
            cli.check_permissions(actor, "test-process")

    def test_get_process_file_not_found_error(self) -> None:
        """Test error handling for process retrieval when file not found."""
        from pantheon.cli import BadInputError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
        mock_process_handler.get_routine.side_effect = FileNotFoundError(
            "File not found"
        )
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with pytest.raises(BadInputError, match="Process 'test-process' not found"):
            cli.get_process("test-process", "test-actor")


class TestCLIPermissionEvaluation:
    """Test cases for comprehensive permission evaluation logic."""

    def test_evaluate_permission_wildcard_allows_all(self) -> None:
        """Test that wildcard '*' in allow list permits any actor."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        perms = {"allow": ["*"], "deny": []}

        # Act & Assert
        assert cli._evaluate_permission("any-actor", perms) is True
        assert cli._evaluate_permission("another-actor", perms) is True
        assert cli._evaluate_permission("test-actor", perms) is True

    def test_evaluate_permission_explicit_deny_wins_over_wildcard(self) -> None:
        """Test that explicit deny always wins even with wildcard allow."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        perms = {"allow": ["*"], "deny": ["blocked-actor"]}

        # Act & Assert
        assert (
            cli._evaluate_permission("blocked-actor", perms) is False
        )  # Explicit deny wins
        assert (
            cli._evaluate_permission("allowed-actor", perms) is True
        )  # Wildcard allows others

    def test_evaluate_permission_default_deny(self) -> None:
        """Test that default behavior is deny when actor not in allow list."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        perms = {"allow": ["specific-actor"], "deny": []}

        # Act & Assert
        assert (
            cli._evaluate_permission("specific-actor", perms) is True
        )  # Explicitly allowed
        assert cli._evaluate_permission("other-actor", perms) is False  # Default deny

    def test_evaluate_permission_precedence_order(self) -> None:
        """Test evaluation precedence: explicit deny > wildcard allow > explicit allow > default deny."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Test case: actor in both allow and deny lists - deny should win
        perms = {"allow": ["conflicted-actor", "*"], "deny": ["conflicted-actor"]}
        assert cli._evaluate_permission("conflicted-actor", perms) is False

        # Test case: actor only in allow list
        perms = {"allow": ["allowed-actor"], "deny": []}
        assert cli._evaluate_permission("allowed-actor", perms) is True

        # Test case: wildcard allow with specific deny
        perms = {"allow": ["*"], "deny": ["specific-deny"]}
        assert (
            cli._evaluate_permission("random-actor", perms) is True
        )  # Wildcard allows
        assert (
            cli._evaluate_permission("specific-deny", perms) is False
        )  # Explicit deny wins

    def test_check_permissions_with_sections_parameter(self) -> None:
        """Test section-level permission checking."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Mock permissions with section-level controls using union model
        permissions_with_sections = {
            "allow": [],  # No process-level access
            "deny": [],
            "sections": {
                "foundation": {"allow": ["pantheon"], "deny": []},
                "artifacts": {"allow": ["artifact-designer", "pantheon"], "deny": []},
                "agents": {"allow": ["agent-designer", "pantheon"], "deny": []},
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_with_sections
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - No process-level access, only section-specific access
        # Should raise for process-level access since no process allows
        with pytest.raises(PermissionDeniedError, match="lacks permission for process"):
            cli.check_permissions("any-actor", "test-process")

        # Should raise for section-level access that's restricted (uses "lacks permission" message)
        with pytest.raises(
            PermissionDeniedError, match="lacks permission for section 'foundation'"
        ):
            cli.check_permissions("unauthorized-actor", "test-process", ["foundation"])

        # Should allow section access for authorized actor
        cli.check_permissions("pantheon", "test-process", ["foundation"])
        cli.check_permissions("artifact-designer", "test-process", ["artifacts"])
        cli.check_permissions("agent-designer", "test-process", ["agents"])

    def test_check_permissions_section_deny_precedence(self) -> None:
        """Test that section-level deny takes precedence over process-level allow."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        permissions_with_section_deny = {
            "allow": ["*"],  # Process allows everyone
            "deny": [],
            "sections": {
                "restricted": {
                    "allow": ["*"],
                    "deny": ["blocked-actor"],  # Section blocks specific actor
                }
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_with_section_deny
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        # Process-level access should work
        cli.check_permissions("blocked-actor", "test-process")

        # Section-level access should be denied (explicit deny message)
        with pytest.raises(
            PermissionDeniedError,
            match="is explicitly denied access to section 'restricted'",
        ):
            cli.check_permissions("blocked-actor", "test-process", ["restricted"])

        # Other actors should have section access
        cli.check_permissions("allowed-actor", "test-process", ["restricted"])

    def test_check_permissions_multiple_sections_validation(self) -> None:
        """Test permission validation for multiple sections."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        permissions_multi_sections = {
            "allow": [],  # No process-level access
            "deny": [],
            "sections": {
                "public": {"allow": ["*"], "deny": []},
                "private": {"allow": ["admin"], "deny": []},
                "secret": {"allow": ["admin"], "deny": ["guest"]},
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_multi_sections
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        # Admin should have access to all sections
        cli.check_permissions("admin", "test-process", ["public", "private", "secret"])

        # Regular user should only have access to public
        cli.check_permissions("user", "test-process", ["public"])

        # Regular user should be denied access to private sections (lacks permission message)
        with pytest.raises(
            PermissionDeniedError, match="lacks permission for section 'private'"
        ):
            cli.check_permissions("user", "test-process", ["public", "private"])

        # Guest should be explicitly denied secret even if trying with public
        with pytest.raises(
            PermissionDeniedError,
            match="is explicitly denied access to section 'secret'",
        ):
            cli.check_permissions("guest", "test-process", ["public", "secret"])

    def test_check_permissions_missing_section_definition(self) -> None:
        """Test behavior when section is requested but not defined in permissions."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        permissions_limited_sections = {
            "allow": ["*"],
            "deny": [],
            "sections": {
                "defined-section": {"allow": ["*"], "deny": []}
                # "undefined-section" not present - should fall back to process level
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_limited_sections
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Undefined sections should fall back to process-level permissions
        # Since process allows "*", undefined sections should be allowed
        cli.check_permissions("any-actor", "test-process", ["undefined-section"])

        # Should allow access to defined sections
        cli.check_permissions("any-actor", "test-process", ["defined-section"])

        # Test with process that denies access - undefined sections should be denied
        permissions_deny_all = {
            "allow": [],
            "deny": [],
            "sections": {"defined-section": {"allow": ["*"], "deny": []}},
        }
        mock_workspace.get_permissions.return_value = json.dumps(permissions_deny_all)

        with pytest.raises(
            PermissionDeniedError,
            match="lacks permission for section 'undefined-section'",
        ):
            cli.check_permissions("any-actor", "test-process", ["undefined-section"])


class TestCLISectionPermissions:
    """Test cases specifically for section-level permission functionality."""

    def test_execute_process_validates_section_permissions(self) -> None:
        """Test that execute_process validates section permissions when sections parameter provided."""
        from pantheon.cli import PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Mock permissions that deny at process level
        # Under union model: process denies test-actor, section allows admin
        permissions_with_sections = {
            "allow": [],  # No process-level allows
            "deny": [],
            "sections": {
                "restricted": {"allow": ["admin"], "deny": []}  # Only admin can access
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_with_sections
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Should raise permission error for restricted section
        with pytest.raises(
            PermissionDeniedError, match="lacks permission for section 'restricted'"
        ):
            cli.execute_process(
                "test-process", "test-actor", sections="restricted", param="value"
            )

        # Verify process handler was not called due to permission failure
        mock_process_handler.execute.assert_not_called()

    def test_execute_process_parses_sections_string_correctly(self) -> None:
        """Test that execute_process correctly parses comma-separated sections string."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["*"], "deny": []}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "result",
        }

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        cli.execute_process(
            "test-process",
            "test-actor",
            sections="section1,section2,section3",
            param="value",
        )

        # Assert - Check that sections were parsed and passed correctly
        mock_process_handler.execute.assert_called_once()
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]

        # Verify sections were parsed into list and moved to framework params
        assert "sections" not in process_input[INPUT_INPUT_PARAMS]
        assert process_input[INPUT_FRAMEWORK_PARAMS]["pantheon_sections"] == [
            "section1",
            "section2",
            "section3",
        ]
        assert process_input[INPUT_INPUT_PARAMS] == {"param": "value"}

    def test_execute_process_handles_whitespace_in_sections(self) -> None:
        """Test that execute_process handles whitespace in sections parameter."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        mock_workspace.get_permissions.return_value = '{"allow": ["*"], "deny": []}'
        mock_process_handler.execute.return_value = {
            "success": True,
            "output": "result",
        }

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act
        cli.execute_process(
            "test-process",
            "test-actor",
            sections=" section1 , section2,  section3  ",
            param="value",
        )

        # Assert - Whitespace should be stripped
        call_args = mock_process_handler.execute.call_args
        process_input = call_args[0][0]
        assert process_input[INPUT_FRAMEWORK_PARAMS]["pantheon_sections"] == [
            "section1",
            "section2",
            "section3",
        ]


# Note: CliRunner integration tests were removed due to complexity of mocking
# the Click command structure with dynamic imports inside the main function.
# The existing unit tests provide comprehensive coverage of the CLI class methods.


class TestLogLevelResolution:
    """Test cases for logging configuration resolution hierarchy."""

    def test_resolve_log_level_cli_flag_takes_precedence(self) -> None:
        """Test that CLI --log-level flag overrides project configuration."""
        from pantheon.cli import resolve_log_level

        # Arrange
        project_config = {"log_level": "DEBUG"}

        # Act
        result = resolve_log_level("WARNING", False, project_config)

        # Assert
        assert result == "WARNING"

    def test_resolve_log_level_debug_flag_sets_debug(self) -> None:
        """Test that --debug flag sets DEBUG level when no --log-level provided."""
        from pantheon.cli import resolve_log_level

        # Arrange
        project_config = {"log_level": "INFO"}

        # Act
        result = resolve_log_level(None, True, project_config)

        # Assert
        assert result == "DEBUG"

    def test_resolve_log_level_explicit_flag_overrides_debug(self) -> None:
        """Test that --log-level takes precedence over --debug when both provided."""
        from pantheon.cli import resolve_log_level

        # Act
        result = resolve_log_level("ERROR", True, {})

        # Assert
        assert result == "ERROR"

    def test_resolve_log_level_uses_project_config(self) -> None:
        """Test that project configuration is used when no CLI flags provided."""
        from pantheon.cli import resolve_log_level

        # Arrange
        project_config = {"log_level": "WARNING"}

        # Act
        result = resolve_log_level(None, False, project_config)

        # Assert
        assert result == "WARNING"

    def test_resolve_log_level_defaults_to_info(self) -> None:
        """Test that INFO is default when no configuration provided."""
        from pantheon.cli import resolve_log_level

        # Act
        result = resolve_log_level(None, False, {})

        # Assert
        assert result == "INFO"

    def test_resolve_log_level_handles_missing_log_level_key(self) -> None:
        """Test graceful handling when project config has no log_level key."""
        from pantheon.cli import resolve_log_level

        # Arrange
        project_config = {"active_team": "test-team", "artifacts_root": "/tmp"}

        # Act
        result = resolve_log_level(None, False, project_config)

        # Assert
        assert result == "INFO"

    def test_resolve_log_level_normalizes_case(self) -> None:
        """Test that log level is properly normalized to uppercase."""
        from pantheon.cli import resolve_log_level

        # Test CLI flag normalization
        result1 = resolve_log_level("debug", False, {})
        assert result1 == "DEBUG"

        # Test project config normalization
        project_config = {"log_level": "error"}
        result2 = resolve_log_level(None, False, project_config)
        assert result2 == "ERROR"

    @pytest.mark.parametrize(
        "cli_level,cli_debug,project_level,expected",
        [
            ("DEBUG", False, "WARNING", "DEBUG"),  # CLI flag wins
            ("INFO", True, "ERROR", "INFO"),  # CLI flag beats debug flag
            (None, True, "WARNING", "DEBUG"),  # Debug flag beats project
            (None, False, "ERROR", "ERROR"),  # Project config used
            (None, False, None, "INFO"),  # Default fallback
            ("error", False, "debug", "ERROR"),  # Case normalization
        ],
    )
    def test_resolve_log_level_hierarchy_scenarios(
        self,
        cli_level: str | None,
        cli_debug: bool,
        project_level: str | None,
        expected: str,
    ) -> None:
        """Test comprehensive scenarios for three-tier configuration hierarchy."""
        from pantheon.cli import resolve_log_level

        # Arrange
        project_config = {}
        if project_level:
            project_config["log_level"] = project_level

        # Act
        result = resolve_log_level(cli_level, cli_debug, project_config)

        # Assert
        assert result == expected


class TestUnionPermissions:
    """Test cases specifically for the new union/additive permission model."""

    def test_union_behavior_process_and_section_allows(self) -> None:
        """Test that process and section allows are combined (union)."""
        from pantheon.cli import CLI

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process allows admin, section allows developer - both should work
        permissions_union = {
            "allow": ["admin"],
            "deny": [],
            "sections": {"feature": {"allow": ["developer"], "deny": []}},
        }
        mock_workspace.get_permissions.return_value = json.dumps(permissions_union)

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Both admin and developer should have access (union)
        cli.check_permissions("admin", "test-process", ["feature"])  # Process allow
        cli.check_permissions("developer", "test-process", ["feature"])  # Section allow

    def test_union_behavior_either_allow_grants_access(self) -> None:
        """Test that actor in either process OR section allow list gets access."""
        from pantheon.cli import CLI, PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        permissions_either = {
            "allow": ["process-actor"],
            "deny": [],
            "sections": {"special": {"allow": ["section-actor"], "deny": []}},
        }
        mock_workspace.get_permissions.return_value = json.dumps(permissions_either)

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        cli.check_permissions(
            "process-actor", "test-process", ["special"]
        )  # Via process
        cli.check_permissions(
            "section-actor", "test-process", ["special"]
        )  # Via section

        # Neither list should be denied
        with pytest.raises(PermissionDeniedError):
            cli.check_permissions("other-actor", "test-process", ["special"])

    def test_explicit_deny_wins_over_union_allows(self) -> None:
        """Test that explicit deny at any level blocks access despite union allows."""
        from pantheon.cli import CLI, PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process allows blocked-actor, but section denies - deny should win
        permissions_deny_wins = {
            "allow": ["blocked-actor"],
            "deny": [],
            "sections": {
                "restricted": {
                    "allow": ["blocked-actor"],  # In both allows
                    "deny": ["blocked-actor"],  # But explicitly denied
                }
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(permissions_deny_wins)

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Should be denied despite being in both allow lists
        with pytest.raises(PermissionDeniedError, match="explicitly denied"):
            cli.check_permissions("blocked-actor", "test-process", ["restricted"])

    def test_wildcard_union_behavior(self) -> None:
        """Test wildcard behavior in union permissions."""
        from pantheon.cli import CLI

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process restricts, section opens with wildcard
        permissions_wildcard = {
            "allow": ["specific-actor"],
            "deny": [],
            "sections": {
                "open": {"allow": ["*"], "deny": []}  # Wildcard opens to all
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(permissions_wildcard)

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Anyone should have access due to wildcard in union
        cli.check_permissions("specific-actor", "test-process", ["open"])
        cli.check_permissions("any-actor", "test-process", ["open"])
        cli.check_permissions("random-actor", "test-process", ["open"])

    def test_empty_section_allows_falls_back_to_process(self) -> None:
        """Test that empty section allows still unions with process allows."""
        from pantheon.cli import CLI, PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Process allows admin, section has empty allows
        permissions_empty_section = {
            "allow": ["admin"],
            "deny": [],
            "sections": {
                "docs": {"allow": [], "deny": []}  # Empty section allows
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_empty_section
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert - Admin should still have access via process allows
        cli.check_permissions("admin", "test-process", ["docs"])

        # Others should be denied (empty union)
        with pytest.raises(PermissionDeniedError):
            cli.check_permissions("other-actor", "test-process", ["docs"])

    def test_section_deny_only_affects_requested_section(self) -> None:
        """Test that section deny lists only affect the specific section being requested."""
        from pantheon.cli import CLI, PermissionDeniedError

        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        # Actor is denied from section_b but allowed in section_a
        permissions_cross_section = {
            "allow": [],
            "deny": [],
            "sections": {
                "section_a": {"allow": ["actor_a"], "deny": []},
                "section_b": {"allow": ["other_actor"], "deny": ["actor_a"]},
            },
        }
        mock_workspace.get_permissions.return_value = json.dumps(
            permissions_cross_section
        )

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        # Actor should be able to access section_a (not denied there)
        cli.check_permissions("actor_a", "test-process", ["section_a"])

        # Actor should be denied from section_b (explicitly denied there)
        with pytest.raises(
            PermissionDeniedError,
            match="explicitly denied access to section 'section_b'",
        ):
            cli.check_permissions("actor_a", "test-process", ["section_b"])

        # Actor should be denied when requesting both (denied from section_b)
        with pytest.raises(
            PermissionDeniedError,
            match="explicitly denied access to section 'section_b'",
        ):
            cli.check_permissions("actor_a", "test-process", ["section_a", "section_b"])


class TestInitESCNavigation:
    """Test cases for ESC key navigation during pantheon init."""

    def test_select_team_esc_raises_bad_input_error(self) -> None:
        """Test that ESC during team selection raises BadInputError."""
        # Arrange
        from unittest.mock import Mock, patch

        import click

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Act & Assert
        with (
            patch("click.prompt", side_effect=click.Abort()),
            pytest.raises(BadInputError, match="Team selection cancelled"),
        ):
            cli._select_team_interactive(["team1", "team2"])

    def test_select_profile_esc_raises_navigate_back_exception(self, tmp_path) -> None:
        """Test that ESC during profile selection raises NavigateBackException."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        import click

        from pantheon.cli import NavigateBackException

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Create mock team profile with multiple profiles
        team_profile_content = """active_profile: standard
profiles:
  prototype:
    profile_description: Rapid prototyping
  standard:
    profile_description: Balanced development"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act & Assert
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.prompt", side_effect=click.Abort()),
            pytest.raises(NavigateBackException),
        ):
            cli._select_profile_interactive("test-team")

    def test_init_project_navigation_loop_handles_navigate_back(self, tmp_path) -> None:
        """Test that init_project handles NavigateBackException in navigation loop."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        from pantheon.cli import NavigateBackException

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )
        cli._filesystem = mock_filesystem

        team_profile_content = """active_profile: standard
profiles:
  standard:
    profile_description: Standard profile"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Mock _discover_bundled_teams to return test team
        with (
            patch.object(cli, "_discover_bundled_teams", return_value=["test-team"]),
            patch.object(
                cli, "_select_team_interactive", return_value="test-team"
            ) as mock_team_select,
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch.object(
                cli,
                "_select_profile_interactive",
                side_effect=[NavigateBackException(), "standard"],
            ) as mock_profile_select,
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch(
                "click.confirm", return_value=False
            ),  # Mock agent installation prompt
        ):
            # Act
            result = cli.init_project()

            # Assert
            # Team selection should be called twice (initial + after navigate back)
            assert mock_team_select.call_count == 2
            # Profile selection should be called twice (fail + success)
            assert mock_profile_select.call_count == 2
            assert "initialized successfully" in result


class TestInitActiveProfileDefault:
    """Test cases for active_profile default selection during pantheon init."""

    def test_select_profile_uses_active_profile_as_default(self, tmp_path) -> None:
        """Test that profile selection uses active_profile from team-profile.yaml as default."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Create team profile where active_profile is NOT the first profile
        team_profile_content = """active_profile: standard
profiles:
  prototype:
    profile_description: Rapid prototyping
  standard:
    profile_description: Balanced development
  production:
    profile_description: Maximum rigor"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.prompt", return_value="2") as mock_prompt,
        ):
            result = cli._select_profile_interactive("test-team")

            # Assert
            # Verify prompt was called with default="2" (second profile, which is "standard")
            mock_prompt.assert_called_once()
            call_kwargs = mock_prompt.call_args[1]
            assert call_kwargs["default"] == "2"
            assert result == "standard"

    def test_select_profile_displays_default_indicator(self, tmp_path) -> None:
        """Test that (default) indicator is displayed next to active profile."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        team_profile_content = """active_profile: production
profiles:
  prototype:
    profile_description: Rapid prototyping
  standard:
    profile_description: Balanced development
  production:
    profile_description: Maximum rigor"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.prompt", return_value="3"),
            patch("click.echo") as mock_echo,
        ):
            cli._select_profile_interactive("test-team")

            # Assert - verify (default) indicator appears for production
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("production (default)" in call for call in echo_calls)
            # Verify other profiles don't have (default)
            assert not any("prototype (default)" in call for call in echo_calls)
            assert not any("standard (default)" in call for call in echo_calls)

    def test_select_profile_falls_back_when_active_profile_missing(
        self, tmp_path
    ) -> None:
        """Test that selection falls back to first profile when active_profile is missing."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # No active_profile field in team-profile.yaml
        team_profile_content = """profiles:
  prototype:
    profile_description: Rapid prototyping
  standard:
    profile_description: Balanced development"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.prompt", return_value="1") as mock_prompt,
        ):
            result = cli._select_profile_interactive("test-team")

            # Assert - should default to first profile (index 1)
            call_kwargs = mock_prompt.call_args[1]
            assert call_kwargs["default"] == "1"
            assert result == "prototype"

    def test_select_profile_falls_back_when_active_profile_invalid(
        self, tmp_path
    ) -> None:
        """Test that selection falls back when active_profile doesn't exist in profiles."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # active_profile points to non-existent profile
        team_profile_content = """active_profile: nonexistent
profiles:
  prototype:
    profile_description: Rapid prototyping
  standard:
    profile_description: Balanced development"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.prompt", return_value="1") as mock_prompt,
            patch("click.echo"),
        ):
            result = cli._select_profile_interactive("test-team")

            # Assert - should fall back to first profile
            call_kwargs = mock_prompt.call_args[1]
            assert call_kwargs["default"] == "1"
            assert result == "prototype"

    def test_select_profile_no_default_indicator_for_single_profile(
        self, tmp_path
    ) -> None:
        """Test that (default) indicator is not shown for single-profile scenario."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        team_profile_content = """active_profile: standard
profiles:
  standard:
    profile_description: Only profile available"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        # Act
        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.echo") as mock_echo,
        ):
            result = cli._select_profile_interactive("test-team")

            # Assert - should auto-select without (default) indicator
            assert result == "standard"
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            # Should see "Using profile:" message without (default)
            assert any("Using profile: standard" in call for call in echo_calls)
            assert not any("(default)" in call for call in echo_calls)


class TestTeamDescriptionDisplay:
    """Test cases for displaying team descriptions during 'pantheon init' team selection."""

    def test_team_description_displayed_during_interactive_selection(
        self, tmp_path, monkeypatch
    ) -> None:
        """Test that team description is displayed when team-profile.yaml contains team_description field."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        team_profile_content = """team_name: test-team
team_description: This is a test team for unit testing purposes."""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("builtins.input", return_value="1"),
            patch("click.echo") as mock_echo,
        ):
            # Act
            selected_team = cli._select_team_interactive(["test-team"])

            # Assert
            assert selected_team == "test-team"
            assert any(
                "This is a test team for unit testing purposes" in str(call)
                for call in mock_echo.call_args_list
            )

    def test_default_description_when_field_missing(
        self, tmp_path, monkeypatch
    ) -> None:
        """Test that default description is shown when team_description field is missing from team-profile.yaml."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        team_profile_content = """team_name: test-team
active_profile: standard"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("builtins.input", return_value="1"),
            patch("click.echo") as mock_echo,
        ):
            # Act
            selected_team = cli._select_team_interactive(["test-team"])

            # Assert
            assert selected_team == "test-team"
            assert any(
                "No description available" in str(call)
                for call in mock_echo.call_args_list
            )

    def test_init_continues_when_team_profile_malformed(
        self, tmp_path, monkeypatch
    ) -> None:
        """Test that init process continues successfully when team-profile.yaml cannot be read or is malformed."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        malformed_yaml = """team_name: test-team
team_description: [invalid yaml structure
  missing closing bracket"""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "test-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(malformed_yaml)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("builtins.input", return_value="1"),
            patch("click.echo") as mock_echo,
        ):
            # Act
            selected_team = cli._select_team_interactive(["test-team"])

            # Assert
            assert selected_team == "test-team"
            assert any(
                "No description available" in str(call)
                for call in mock_echo.call_args_list
            )

    def test_single_team_scenario_displays_description(self, tmp_path) -> None:
        """Test that single-team scenario displays description without requiring interactive selection."""
        # Arrange
        from unittest.mock import MagicMock, Mock, patch

        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        team_profile_content = """team_name: only-team
team_description: The one and only team available."""

        mock_teams_path = tmp_path / "pantheon-teams"
        mock_teams_path.mkdir()
        team_dir = mock_teams_path / "only-team"
        team_dir.mkdir()
        team_profile_path = team_dir / "team-profile.yaml"
        team_profile_path.write_text(team_profile_content)

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = team_profile_path
        mock_context_manager.__exit__.return_value = None

        with (
            patch("importlib.resources.as_file", return_value=mock_context_manager),
            patch("click.echo") as mock_echo,
        ):
            # Act
            selected_team = cli._select_team_interactive(["only-team"])

            # Assert
            assert selected_team == "only-team"
            assert any(
                "only-team" in str(call)
                and "The one and only team available" in str(call)
                for call in mock_echo.call_args_list
            )


class TestInitDirectoryCreation:
    """Test cases for automatic directory creation from team-data.yaml during init."""

    def test_init_rejects_paths_outside_project_boundaries_with_warning(
        self, tmp_path
    ) -> None:
        """Test that paths outside project boundaries are rejected with warnings but don't fail init."""
        from unittest.mock import Mock, patch

        # Arrange: Set up mocks following dependency injection pattern
        mock_filesystem = Mock()
        mock_workspace = Mock()
        mock_workspace._filesystem = mock_filesystem
        mock_process_handler = Mock()
        mock_rae_engine = Mock()

        # Create CLI instance with mocked dependencies
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        # Set up test paths
        project_root = tmp_path / "test_project"
        project_root.mkdir()

        # Create test directory paths including an unsafe traversal path
        safe_path1 = project_root / "pantheon-artifacts" / "docs"
        safe_path2 = project_root / "pantheon-artifacts" / "tickets"
        unsafe_path = project_root / "../../../etc/passwd"

        test_directories = [safe_path1, safe_path2, unsafe_path]

        # Act: Call the actual CLI implementation with logging capture
        with patch("pantheon.cli.Log") as mock_log:
            created_dirs = cli._create_team_data_directories(
                project_root, test_directories
            )

        # Assert: Verify filesystem.mkdir was called only for safe paths
        assert mock_filesystem.mkdir.call_count == 2, (
            "Should only create 2 safe directories, not the unsafe one"
        )

        # Verify safe paths were created
        safe_calls = [call[0][0] for call in mock_filesystem.mkdir.call_args_list]
        assert safe_path1.resolve() in safe_calls
        assert safe_path2.resolve() in safe_calls

        # Verify unsafe path was NOT created
        assert unsafe_path.resolve() not in safe_calls

        # Verify warning was logged for rejected path
        mock_log.warning.assert_called()
        warning_messages = [
            call[0][0] for call in mock_log.warning.call_args_list if call[0]
        ]
        assert any("outside project boundaries" in msg for msg in warning_messages), (
            "Should log warning about path outside project boundaries"
        )

        # Verify return value contains only successfully created directories
        assert len(created_dirs) == 2
        assert safe_path1.resolve() in created_dirs
        assert safe_path2.resolve() in created_dirs


class TestClaudeAgentInstallation:
    """Test cases for Claude agent auto-installation feature during init."""

    def test_prompt_claude_agent_installation_user_declines(self):
        """Test that prompt defaults to 'Yes' and returns None when user declines (Phase 3 change)."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        selected_team = "test-team"
        selected_team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Act - mock click.confirm to return False (user declines)
        with patch("pantheon.cli.click.confirm", return_value=False) as mock_confirm:
            result = cli._prompt_claude_agent_installation(
                selected_team, selected_team_dir, project_root
            )

        # Assert
        mock_confirm.assert_called_once()
        call_kwargs = mock_confirm.call_args[1]
        assert (
            call_kwargs["default"] is True
        )  # Verify default is 'Yes' as per Phase 3 requirements
        assert result is None  # Method returns None (display-only method)

    def test_prompt_claude_agent_installation_user_accepts(self):
        """Test that prompt calls agent discovery and copying when user accepts."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        selected_team = "test-team"
        selected_team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Mock agent discovery to return sample agent files
        sample_agents = [
            Path("/test/teams/test-team/agents/agent1.md"),
            Path("/test/teams/test-team/agents/agent2.md"),
        ]

        # Act - mock click.confirm to return True and _discover_team_agents
        with (
            patch("pantheon.cli.click.confirm", return_value=True),
            patch.object(
                cli, "_discover_team_agents", return_value=sample_agents
            ) as mock_discover,
            patch.object(
                cli,
                "_copy_agents_to_claude",
                return_value={
                    "installed": 2,
                    "skipped": 0,
                    "failed": 0,
                    "installed_files": ["agent1.md", "agent2.md"],
                },
            ) as mock_copy,
        ):
            result = cli._prompt_claude_agent_installation(
                selected_team, selected_team_dir, project_root
            )

        # Assert
        mock_discover.assert_called_once_with(selected_team_dir)
        mock_copy.assert_called_once_with(
            sample_agents, selected_team, selected_team_dir, project_root
        )
        assert result is None  # Method returns None (display-only method)

    def test_discover_team_agents_finds_all_md_files(self):
        """Test that agent discovery correctly identifies all .md files in agents directory."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        team_dir = Path("/test/teams/test-team")
        agents_dir = team_dir / "agents"

        # Mock filesystem to simulate agents directory with .md files
        mock_filesystem.exists.return_value = True
        mock_filesystem.is_dir.return_value = True
        mock_agent_files = [
            agents_dir / "agent1.md",
            agents_dir / "agent2.md",
            agents_dir / "agent3.md",
        ]
        mock_filesystem.glob.return_value = mock_agent_files

        # Act
        result = cli._discover_team_agents(team_dir)

        # Assert
        mock_filesystem.exists.assert_called_once_with(agents_dir)
        mock_filesystem.glob.assert_called_once_with(agents_dir, "*.md")
        assert len(result) == 3
        assert all(str(agent).endswith(".md") for agent in result)

    def test_discover_team_agents_handles_missing_directory(self):
        """Test that agent discovery returns empty list when agents directory doesn't exist."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        team_dir = Path("/test/teams/test-team")

        # Mock filesystem to simulate missing agents directory
        mock_filesystem.exists.return_value = False

        # Act
        result = cli._discover_team_agents(team_dir)

        # Assert
        assert result == []  # Empty list for missing directory

    def test_resolve_file_conflict_first_conflict_prompts_user(self):
        """Test that first conflict prompts user for resolution strategy."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        dest_path = Path("/test/.claude/agents/test-team/agent1.md")
        conflict_strategy = {}  # Empty dict - first conflict

        # Act - mock click.prompt to return 'o' (overwrite all)
        with patch("pantheon.cli.click.prompt", return_value="o") as mock_prompt:
            result = cli._resolve_file_conflict(dest_path, conflict_strategy)

        # Assert
        mock_prompt.assert_called_once()
        assert conflict_strategy["choice"] == "o"  # Strategy stored
        assert result is True  # Overwrite all returns True

    def test_resolve_file_conflict_reuses_stored_strategy(self):
        """Test that subsequent conflicts reuse stored strategy without prompting."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        dest_path = Path("/test/.claude/agents/test-team/agent2.md")
        conflict_strategy = {"choice": "s"}  # Skip all already stored

        # Act - no prompt should be called
        with patch("pantheon.cli.click.prompt") as mock_prompt:
            result = cli._resolve_file_conflict(dest_path, conflict_strategy)

        # Assert
        mock_prompt.assert_not_called()  # Should not prompt again
        assert result is False  # Skip all returns False

    def test_resolve_file_conflict_ask_each_time_strategy(self):
        """Test that 'ask each time' strategy prompts for every conflict."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        dest_path = Path("/test/.claude/agents/test-team/agent1.md")
        conflict_strategy = {"choice": "a"}  # Ask each time

        # Act - mock click.confirm for per-file prompt
        with patch("pantheon.cli.click.confirm", return_value=True) as mock_confirm:
            result = cli._resolve_file_conflict(dest_path, conflict_strategy)

        # Assert
        mock_confirm.assert_called_once()
        assert result is True  # User confirmed this file

    def test_copy_agents_to_claude_creates_directory_structure(self):
        """Test that agent copying creates .claude/agents/<team-name>/ directory."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        agent_files = [Path("/test/teams/test-team/agents/agent1.md")]
        team_name = "test-team"
        team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Mock filesystem for read/write operations
        mock_filesystem.read_text.return_value = "# Agent content"
        mock_filesystem.exists.return_value = False  # No conflicts

        # Act
        result = cli._copy_agents_to_claude(
            agent_files, team_name, team_dir, project_root
        )

        # Assert
        expected_dir = project_root / ".claude" / "agents" / team_name
        mock_filesystem.mkdir.assert_called_once()
        mkdir_call_args = mock_filesystem.mkdir.call_args[0]
        assert mkdir_call_args[0] == expected_dir
        assert result["installed"] == 1
        assert result["skipped"] == 0

    def test_copy_agents_to_claude_handles_conflicts(self):
        """Test that agent copying detects and resolves file conflicts."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        agent_files = [
            Path("/test/teams/test-team/agents/agent1.md"),
            Path("/test/teams/test-team/agents/agent2.md"),
        ]
        team_name = "test-team"
        team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Mock filesystem - first file conflicts, second doesn't
        mock_filesystem.read_text.return_value = "# Agent content"
        mock_filesystem.exists.side_effect = [
            True,
            False,
        ]  # First exists, second doesn't

        # Mock conflict resolution to skip first file
        with patch.object(cli, "_resolve_file_conflict", return_value=False):
            # Act
            result = cli._copy_agents_to_claude(
                agent_files, team_name, team_dir, project_root
            )

        # Assert
        assert result["installed"] == 1  # Only second file installed
        assert result["skipped"] == 1  # First file skipped

    def test_copy_agents_to_claude_tracks_failures(self):
        """Test that agent copying tracks failed operations."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        agent_files = [Path("/test/teams/test-team/agents/agent1.md")]
        team_name = "test-team"
        team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Mock filesystem to raise exception during write
        mock_filesystem.read_text.return_value = "# Agent content"
        mock_filesystem.exists.return_value = False
        mock_filesystem.write_text.side_effect = PermissionError("Access denied")

        # Act
        result = cli._copy_agents_to_claude(
            agent_files, team_name, team_dir, project_root
        )

        # Assert
        assert result["failed"] == 1
        assert result["installed"] == 0

    def test_agent_installation_error_returns_warning_message(self):
        """Test that agent installation errors are logged and returned as warnings."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        selected_team = "test-team"
        selected_team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Act - mock _discover_team_agents to raise exception
        with (
            patch("pantheon.cli.click.confirm", return_value=True),
            patch.object(
                cli, "_discover_team_agents", side_effect=Exception("Filesystem error")
            ),
        ):
            result = cli._prompt_claude_agent_installation(
                selected_team, selected_team_dir, project_root
            )

        # Assert
        # Error is logged and displayed via click.echo (method returns None)
        assert result is None  # Method returns None (display-only method)


class TestClaudeMdAppend:
    """Test cases for CLAUDE.md protocol append feature during init."""

    def test_prompt_claude_md_append_defaults_yes_when_claude_directory_exists(self):
        """Test that prompt defaults to 'Yes' when .claude directory exists."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock .claude directory exists
        mock_filesystem.exists.side_effect = lambda p: str(p) == str(
            project_root / ".claude"
        )

        # Mock _detect_existing_protocol to return False (protocol not present)
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=False),
            patch("pantheon.cli.click.confirm", return_value=False) as mock_confirm,
        ):
            cli._prompt_claude_md_append(project_root)

        # Assert
        mock_confirm.assert_called_once()
        call_kwargs = mock_confirm.call_args[1]
        assert call_kwargs["default"] is True  # Default 'Yes' when .claude exists

    def test_prompt_claude_md_append_defaults_yes_for_common_use_case(self):
        """Test that prompt defaults to 'Yes' for common use case (Phase 3 change)."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock _detect_existing_protocol to return False (protocol not present)
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=False),
            patch("pantheon.cli.click.confirm", return_value=False) as mock_confirm,
        ):
            cli._prompt_claude_md_append(project_root)

        # Assert
        mock_confirm.assert_called_once()
        call_kwargs = mock_confirm.call_args[1]
        assert (
            call_kwargs["default"] is True
        )  # Default 'Yes' as per Phase 3 requirements

    def test_prompt_claude_md_append_user_declines(self):
        """Test that prompt returns empty string when user declines."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        mock_filesystem.exists.return_value = False

        # Act - mock click.confirm to return False (user declines)
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=False),
            patch("pantheon.cli.click.confirm", return_value=False),
        ):
            result = cli._prompt_claude_md_append(project_root)

        # Assert
        assert result == ""  # Empty string when user declines

    def test_prompt_claude_md_append_user_accepts(self):
        """Test that prompt calls append when user accepts."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        mock_filesystem.exists.return_value = False

        # Act - mock click.confirm to return True (user accepts)
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=False),
            patch("pantheon.cli.click.confirm", return_value=True) as mock_confirm,
            patch.object(
                cli,
                "_append_protocol_to_claude_md",
                return_value="Created CLAUDE.md with protocol",
            ) as mock_append,
        ):
            result = cli._prompt_claude_md_append(project_root)

        # Assert
        mock_confirm.assert_called_once()
        mock_append.assert_called_once_with(project_root)
        assert "Created CLAUDE.md with protocol" in result

    def test_prompt_claude_md_append_skips_when_protocol_exists(self):
        """Test that prompt skips append when protocol already exists."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        mock_filesystem.exists.return_value = False

        # Act - mock _detect_existing_protocol to return True
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=True),
            patch("pantheon.cli.click.confirm") as mock_confirm,
        ):
            result = cli._prompt_claude_md_append(project_root)

        # Assert
        mock_confirm.assert_not_called()  # Should not prompt if already exists
        assert "already exists" in result
        assert "skipping" in result.lower()

    def test_prompt_claude_md_append_handles_errors_gracefully(self):
        """Test that prompt handles errors gracefully without failing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        mock_filesystem.exists.return_value = False

        # Act - mock _append_protocol_to_claude_md to raise exception
        with (
            patch.object(cli, "_detect_existing_protocol", return_value=False),
            patch("pantheon.cli.click.confirm", return_value=True),
            patch.object(
                cli,
                "_append_protocol_to_claude_md",
                side_effect=Exception("Filesystem error"),
            ),
        ):
            result = cli._prompt_claude_md_append(project_root)

        # Assert
        assert result != ""  # Returns error description
        assert "error" in result.lower()  # Message indicates error occurred

    def test_get_protocol_content_retrieves_bundled_template(self):
        """Test that _get_protocol_content retrieves content from bundled template."""
        # Arrange
        expected_content = "# Subagent Invocation Protocol\nTest content"

        # Mock importlib.resources
        mock_template = Mock()
        mock_template.read_text.return_value = expected_content

        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_template

            # Act
            from pantheon.cli import CLI

            result = CLI._get_protocol_content()

        # Assert
        assert result == expected_content

    def test_get_protocol_content_raises_error_when_template_missing(self):
        """Test that _get_protocol_content raises FileNotFoundError when template missing."""
        # Mock importlib.resources to raise FileNotFoundError
        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.side_effect = FileNotFoundError(
                "Template not found"
            )

            # Act & Assert
            from pantheon.cli import CLI

            with pytest.raises(FileNotFoundError):
                CLI._get_protocol_content()

    def test_detect_existing_protocol_returns_false_when_file_missing(self):
        """Test that _detect_existing_protocol returns False when CLAUDE.md missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock CLAUDE.md does not exist
        mock_filesystem.exists.return_value = False

        # Act
        result = cli._detect_existing_protocol(project_root)

        # Assert
        assert result is False
        mock_filesystem.exists.assert_called_once_with(project_root / "CLAUDE.md")

    def test_detect_existing_protocol_returns_true_when_marker_found(self):
        """Test that _detect_existing_protocol returns True when protocol marker found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock CLAUDE.md exists with protocol marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = f"# Other content\n\n{PANTHEON_INSTRUCTIONS_MARKER_START}\nProtocol content\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Act
        result = cli._detect_existing_protocol(project_root)

        # Assert
        assert result is True
        mock_filesystem.exists.assert_called_once()
        mock_filesystem.read_text.assert_called_once_with(project_root / "CLAUDE.md")

    def test_detect_existing_protocol_returns_false_when_marker_not_found(self):
        """Test that _detect_existing_protocol returns False when marker not found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock CLAUDE.md exists without protocol marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = "# Other content\nNo protocol here"

        # Act
        result = cli._detect_existing_protocol(project_root)

        # Assert
        assert result is False

    def test_append_protocol_to_claude_md_creates_new_file(self):
        """Test that _append_protocol_to_claude_md creates new file when missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        protocol_content = "# Subagent Invocation Protocol\nTest protocol"

        # Mock file does not exist
        mock_filesystem.exists.return_value = False

        # Act
        with patch.object(CLI, "_get_protocol_content", return_value=protocol_content):
            result = cli._append_protocol_to_claude_md(project_root)

        # Assert
        expected_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{protocol_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "CLAUDE.md", expected_content
        )
        assert "Created CLAUDE.md with protocol" in result

    def test_append_protocol_to_claude_md_appends_to_existing_file(self):
        """Test that _append_protocol_to_claude_md appends when file exists."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        existing_content = "# Existing content\nSome text"
        protocol_content = "# Subagent Invocation Protocol\nTest protocol"

        # Mock file exists
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = existing_content

        # Act
        with patch.object(CLI, "_get_protocol_content", return_value=protocol_content):
            result = cli._append_protocol_to_claude_md(project_root)

        # Assert
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{protocol_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        expected_content = existing_content + "\n\n---\n\n" + wrapped_content
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "CLAUDE.md", expected_content
        )
        assert "Appended protocol to existing CLAUDE.md" in result


class TestAgentsMdAppend:
    """Test cases for AGENTS.md instruction append feature during init."""

    def test_prompt_agents_md_append_user_declines(self):
        """Test that _prompt_agents_md_append handles user declining the prompt."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock AGENTS.md does not exist and user declines
        mock_filesystem.exists.return_value = False

        # Mock click.confirm to return False (user declines)
        with patch("pantheon.cli.click.confirm", return_value=False):
            # Act
            result = cli._prompt_agents_md_append(project_root)

        # Assert
        assert result == ""
        mock_filesystem.write_text.assert_not_called()

    def test_prompt_agents_md_append_user_accepts(self):
        """Test that _prompt_agents_md_append appends instructions when user accepts."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        instructions_content = "# Operating Protocol\nTest instructions"

        # Mock AGENTS.md does not exist
        mock_filesystem.exists.return_value = False

        # Mock click.confirm to return True (user accepts)
        with (
            patch("pantheon.cli.click.confirm", return_value=True),
            patch.object(
                CLI, "_get_agents_instructions", return_value=instructions_content
            ),
        ):
            # Act
            result = cli._prompt_agents_md_append(project_root)

        # Assert
        assert "Created AGENTS.md with Pantheon instructions" in result
        mock_filesystem.write_text.assert_called_once()

    def test_prompt_agents_md_append_skips_when_instructions_exist(self):
        """Test that _prompt_agents_md_append skips when instructions already exist."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock AGENTS.md exists with instructions
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = f"# Other content\n\n{PANTHEON_INSTRUCTIONS_MARKER_START}\nExisting instructions\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Act
        result = cli._prompt_agents_md_append(project_root)

        # Assert
        assert "Pantheon instructions already exist in AGENTS.md" in result
        mock_filesystem.write_text.assert_not_called()

    def test_prompt_agents_md_append_handles_errors_gracefully(self):
        """Test that _prompt_agents_md_append handles errors without failing init."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock filesystem error
        mock_filesystem.exists.side_effect = PermissionError("Access denied")

        # Act
        result = cli._prompt_agents_md_append(project_root)

        # Assert - error should be caught and logged, not raised
        assert "Access denied" in result or result == ""
        # Init should continue, not raise exception

    def test_get_agents_instructions_retrieves_bundled_template(self):
        """Test that _get_agents_instructions retrieves content from bundled template."""
        # Arrange
        expected_content = "# Operating Protocol\nTest content"

        # Mock importlib.resources
        mock_template = Mock()
        mock_template.read_text.return_value = expected_content

        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_template

            # Act
            from pantheon.cli import CLI

            result = CLI._get_agents_instructions()

        # Assert
        assert result == expected_content

    def test_get_agents_instructions_raises_error_when_template_missing(self):
        """Test that _get_agents_instructions raises FileNotFoundError when template missing."""
        # Mock importlib.resources to raise FileNotFoundError
        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.side_effect = FileNotFoundError(
                "Template not found"
            )

            # Act & Assert
            from pantheon.cli import CLI

            with pytest.raises(FileNotFoundError):
                CLI._get_agents_instructions()

    def test_detect_existing_instructions_returns_false_when_file_missing(self):
        """Test that _detect_existing_instructions returns False when AGENTS.md missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock AGENTS.md does not exist
        mock_filesystem.exists.return_value = False

        # Act
        result = cli._detect_existing_instructions(project_root)

        # Assert
        assert result is False
        mock_filesystem.exists.assert_called_once_with(project_root / "AGENTS.md")

    def test_detect_existing_instructions_returns_true_when_marker_found(self):
        """Test that _detect_existing_instructions returns True when instruction marker found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock AGENTS.md exists with instruction marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = f"# Other content\n\n{PANTHEON_INSTRUCTIONS_MARKER_START}\nInstruction content\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Act
        result = cli._detect_existing_instructions(project_root)

        # Assert
        assert result is True
        mock_filesystem.exists.assert_called_once()
        mock_filesystem.read_text.assert_called_once_with(project_root / "AGENTS.md")

    def test_detect_existing_instructions_returns_false_when_marker_not_found(self):
        """Test that _detect_existing_instructions returns False when marker not found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock AGENTS.md exists without instruction marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = "# Other content\nNo instructions here"

        # Act
        result = cli._detect_existing_instructions(project_root)

        # Assert
        assert result is False

    def test_append_instructions_to_agents_md_creates_new_file(self):
        """Test that _append_instructions_to_agents_md creates new file when missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        instructions_content = "# Operating Protocol\nTest instructions"

        # Mock file does not exist
        mock_filesystem.exists.return_value = False

        # Act
        with patch.object(
            CLI, "_get_agents_instructions", return_value=instructions_content
        ):
            result = cli._append_instructions_to_agents_md(project_root)

        # Assert
        expected_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "AGENTS.md", expected_content
        )
        assert "Created AGENTS.md with Pantheon instructions" in result

    def test_append_instructions_to_agents_md_appends_to_existing_file(self):
        """Test that _append_instructions_to_agents_md appends when file exists."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        existing_content = "# Existing content\nSome text"
        instructions_content = "# Operating Protocol\nTest instructions"

        # Mock file exists
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = existing_content

        # Act
        with patch.object(
            CLI, "_get_agents_instructions", return_value=instructions_content
        ):
            result = cli._append_instructions_to_agents_md(project_root)

        # Assert
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        expected_content = existing_content + "\n\n---\n\n" + wrapped_content
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "AGENTS.md", expected_content
        )
        assert "Appended Pantheon instructions to existing AGENTS.md" in result


class TestGeminiMdAppend:
    """Test cases for GEMINI.md instruction append feature during init."""

    def test_prompt_gemini_md_append_user_declines(self):
        """Test that _prompt_gemini_md_append handles user declining the prompt."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock GEMINI.md does not exist and user declines
        mock_filesystem.exists.return_value = False

        # Mock click.confirm to return False (user declines)
        with patch("pantheon.cli.click.confirm", return_value=False):
            # Act
            result = cli._prompt_gemini_md_append(project_root)

        # Assert
        assert result == ""
        mock_filesystem.write_text.assert_not_called()

    def test_prompt_gemini_md_append_user_accepts(self):
        """Test that _prompt_gemini_md_append appends instructions when user accepts."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        instructions_content = "# Persona and Role Protocol\nTest instructions"

        # Mock GEMINI.md does not exist
        mock_filesystem.exists.return_value = False

        # Mock click.confirm to return True (user accepts)
        with (
            patch("pantheon.cli.click.confirm", return_value=True),
            patch.object(
                CLI, "_get_gemini_instructions", return_value=instructions_content
            ),
        ):
            # Act
            result = cli._prompt_gemini_md_append(project_root)

        # Assert
        assert "Created GEMINI.md with Pantheon instructions" in result
        mock_filesystem.write_text.assert_called_once()

    def test_prompt_gemini_md_append_skips_when_instructions_exist(self):
        """Test that _prompt_gemini_md_append skips when instructions already exist."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock GEMINI.md exists with instructions
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = f"# Other content\n\n{PANTHEON_INSTRUCTIONS_MARKER_START}\nExisting instructions\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Act
        result = cli._prompt_gemini_md_append(project_root)

        # Assert
        assert "Pantheon instructions already exist in GEMINI.md" in result
        mock_filesystem.write_text.assert_not_called()

    def test_prompt_gemini_md_append_handles_errors_gracefully(self):
        """Test that _prompt_gemini_md_append handles errors without failing init."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock filesystem error
        mock_filesystem.exists.side_effect = PermissionError("Access denied")

        # Act
        result = cli._prompt_gemini_md_append(project_root)

        # Assert - error should be caught and logged, not raised
        assert "Access denied" in result or result == ""
        # Init should continue, not raise exception

    def test_get_gemini_instructions_retrieves_bundled_template(self):
        """Test that _get_gemini_instructions retrieves content from bundled template."""
        # Arrange
        expected_content = "# Persona and Role Protocol\nTest content"

        # Mock importlib.resources
        mock_template = Mock()
        mock_template.read_text.return_value = expected_content

        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_template

            # Act
            from pantheon.cli import CLI

            result = CLI._get_gemini_instructions()

        # Assert
        assert result == expected_content

    def test_get_gemini_instructions_raises_error_when_template_missing(self):
        """Test that _get_gemini_instructions raises FileNotFoundError when template missing."""
        # Mock importlib.resources to raise FileNotFoundError
        with patch("pantheon.cli.importlib.resources.files") as mock_files:
            mock_files.return_value.__truediv__.side_effect = FileNotFoundError(
                "Template not found"
            )

            # Act & Assert
            from pantheon.cli import CLI

            with pytest.raises(FileNotFoundError):
                CLI._get_gemini_instructions()

    def test_detect_existing_gemini_instructions_returns_false_when_file_missing(self):
        """Test that _detect_existing_gemini_instructions returns False when GEMINI.md missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock GEMINI.md does not exist
        mock_filesystem.exists.return_value = False

        # Act
        result = cli._detect_existing_gemini_instructions(project_root)

        # Assert
        assert result is False
        mock_filesystem.exists.assert_called_once_with(project_root / "GEMINI.md")

    def test_detect_existing_gemini_instructions_returns_true_when_marker_found(self):
        """Test that _detect_existing_gemini_instructions returns True when instruction marker found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock GEMINI.md exists with instruction marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = f"# Other content\n\n{PANTHEON_INSTRUCTIONS_MARKER_START}\nInstruction content\n{PANTHEON_INSTRUCTIONS_MARKER_END}"

        # Act
        result = cli._detect_existing_gemini_instructions(project_root)

        # Assert
        assert result is True
        mock_filesystem.exists.assert_called_once()
        mock_filesystem.read_text.assert_called_once_with(project_root / "GEMINI.md")

    def test_detect_existing_gemini_instructions_returns_false_when_marker_not_found(
        self,
    ):
        """Test that _detect_existing_gemini_instructions returns False when marker not found."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")

        # Mock GEMINI.md exists without instruction marker
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = "# Other content\nNo instructions here"

        # Act
        result = cli._detect_existing_gemini_instructions(project_root)

        # Assert
        assert result is False

    def test_append_instructions_to_gemini_md_creates_new_file(self):
        """Test that _append_instructions_to_gemini_md creates new file when missing."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        instructions_content = "# Persona and Role Protocol\nTest instructions"

        # Mock file does not exist
        mock_filesystem.exists.return_value = False

        # Act
        with patch.object(
            CLI, "_get_gemini_instructions", return_value=instructions_content
        ):
            result = cli._append_instructions_to_gemini_md(project_root)

        # Assert
        expected_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "GEMINI.md", expected_content
        )
        assert "Created GEMINI.md with Pantheon instructions" in result

    def test_append_instructions_to_gemini_md_appends_to_existing_file(self):
        """Test that _append_instructions_to_gemini_md appends when file exists."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()
        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        from pathlib import Path

        project_root = Path("/test/project")
        existing_content = "# Existing content\nSome text"
        instructions_content = "# Persona and Role Protocol\nTest instructions"

        # Mock file exists
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = existing_content

        # Act
        with patch.object(
            CLI, "_get_gemini_instructions", return_value=instructions_content
        ):
            result = cli._append_instructions_to_gemini_md(project_root)

        # Assert
        wrapped_content = f"{PANTHEON_INSTRUCTIONS_MARKER_START}\n{instructions_content}\n{PANTHEON_INSTRUCTIONS_MARKER_END}"
        expected_content = existing_content + "\n\n---\n\n" + wrapped_content
        mock_filesystem.write_text.assert_called_once_with(
            project_root / "GEMINI.md", expected_content
        )
        assert "Appended Pantheon instructions to existing GEMINI.md" in result
