"""Unit tests for team-data functionality in CLI, ProcessHandler, and Workspace."""

from unittest.mock import Mock

import pytest
import yaml

from pantheon.cli import CLI
from pantheon.process_handler import ProcessHandler
from pantheon.workspace import PantheonWorkspace


class TestWorkspaceTeamData:
    """Test team-data I/O operations in Workspace class."""

    def test_get_team_data_returns_raw_content(self, tmp_path):
        """Test Workspace returns raw file content without processing."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        raw_content = "agents:\n  pantheon: {{ pantheon_actor }}\nmetrics:\n  count: 15"
        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = raw_content

        # Act
        result = workspace.get_team_data()

        # Assert - Workspace just returns raw content, no template rendering
        assert result == raw_content
        # read_text is called at least once for team-data.yaml (may also be called for .pantheon_project)
        assert mock_filesystem.read_text.call_count >= 1

    def test_get_team_data_nonexistent_file(self, tmp_path):
        """Test error handling when team-data.yaml doesn't exist."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        mock_filesystem.exists.return_value = False

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="team-data.yaml not found"):
            workspace.get_team_data()


class TestProcessHandlerTeamData:
    """Test team-data orchestration in ProcessHandler class."""

    def test_get_team_data_full_file(self, tmp_path):
        """Test getting entire team-data.yaml with template rendering."""
        # Arrange
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        process_handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, mock_rae_engine
        )

        test_data = {
            "agents": {
                "pantheon": "Intelligent orchestrator",
                "architect": "Technical foundations",
            },
            "metadata": {"last_accessed_by": "test-actor"},
        }
        raw_content = "agents:\n  pantheon: Intelligent orchestrator\n  architect: Technical foundations\nmetadata:\n  last_accessed_by: {{ pantheon_actor }}"
        rendered_content = yaml.dump(test_data, default_flow_style=False)

        mock_workspace.get_team_data.return_value = raw_content
        mock_workspace.get_team_profile.side_effect = FileNotFoundError()
        mock_artifact_engine.render_template.return_value = rendered_content
        mock_artifact_engine._generate_timestamp.return_value = "2025-09-29"
        mock_artifact_engine._generate_datestamp.return_value = "2025-09-29"

        # Act
        result = process_handler.get_team_data("test-actor")

        # Assert
        data = yaml.safe_load(result)
        assert data["agents"]["pantheon"] == "Intelligent orchestrator"
        assert data["metadata"]["last_accessed_by"] == "test-actor"
        mock_artifact_engine.render_template.assert_called_once()

    def test_get_team_data_filtered_by_key(self, tmp_path):
        """Test getting filtered team-data by key."""
        # Arrange
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        process_handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, mock_rae_engine
        )

        test_data = {
            "agents": {
                "pantheon": "Intelligent orchestrator",
                "architect": "Technical foundations",
            },
            "metrics": {"count": "15"},
        }
        raw_content = yaml.dump(test_data, default_flow_style=False)
        rendered_content = raw_content

        mock_workspace.get_team_data.return_value = raw_content
        mock_workspace.get_team_profile.side_effect = FileNotFoundError()
        mock_workspace._get_nested_value.return_value = test_data["agents"]
        mock_artifact_engine.render_template.return_value = rendered_content
        mock_artifact_engine._generate_timestamp.return_value = "2025-09-29"
        mock_artifact_engine._generate_datestamp.return_value = "2025-09-29"

        # Act
        result = process_handler.get_team_data("test-actor", "agents")

        # Assert
        data = yaml.safe_load(result)
        assert "pantheon" in data
        assert "architect" in data
        assert "metrics" not in result

    def test_get_team_data_nested_key(self, tmp_path):
        """Test getting nested value using dot notation."""
        # Arrange
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        process_handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, mock_rae_engine
        )

        test_data = {
            "agents": {
                "pantheon": "Intelligent orchestrator",
                "architect": "Technical foundations",
            }
        }
        raw_content = yaml.dump(test_data, default_flow_style=False)

        mock_workspace.get_team_data.return_value = raw_content
        mock_workspace.get_team_profile.side_effect = FileNotFoundError()
        mock_workspace._get_nested_value.return_value = "Intelligent orchestrator"
        mock_artifact_engine.render_template.return_value = raw_content
        mock_artifact_engine._generate_timestamp.return_value = "2025-09-29"
        mock_artifact_engine._generate_datestamp.return_value = "2025-09-29"

        # Act
        result = process_handler.get_team_data("test-actor", "agents.pantheon")

        # Assert
        assert result == "Intelligent orchestrator"

    def test_get_team_data_nonexistent_key(self, tmp_path):
        """Test behavior when requested key doesn't exist."""
        # Arrange
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()

        process_handler = ProcessHandler(
            mock_workspace, mock_artifact_engine, mock_rae_engine
        )

        test_data = {"agents": {"pantheon": "Orchestrator"}}
        raw_content = yaml.dump(test_data, default_flow_style=False)

        mock_workspace.get_team_data.return_value = raw_content
        mock_workspace.get_team_profile.side_effect = FileNotFoundError()
        mock_workspace._get_nested_value.side_effect = KeyError("nonexistent")
        mock_artifact_engine.render_template.return_value = raw_content
        mock_artifact_engine._generate_timestamp.return_value = "2025-09-29"
        mock_artifact_engine._generate_datestamp.return_value = "2025-09-29"

        # Act
        result = process_handler.get_team_data("test-actor", "nonexistent")

        # Assert
        assert result == ""

    def test_set_team_data_new_file(self, tmp_path):
        """Test creating new team-data.yaml file."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        mock_filesystem.exists.return_value = False  # File doesn't exist

        updates = {"agents.pantheon": "Orchestrator", "foo": "bar"}
        deletes = []

        # Act
        workspace.set_team_data(updates, deletes)

        # Assert
        mock_filesystem.write_text.assert_called_once()
        call_args = mock_filesystem.write_text.call_args
        written_content = call_args[0][1]

        # Parse written YAML to verify structure
        written_data = yaml.safe_load(written_content)
        assert written_data["agents"]["pantheon"] == "Orchestrator"
        assert written_data["foo"] == "bar"

    def test_set_team_data_update_existing(self, tmp_path):
        """Test updating existing team-data.yaml file."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        existing_data = {
            "agents": {"architect": "Technical foundations"},
            "old_key": "old_value",
        }
        existing_content = yaml.dump(existing_data, default_flow_style=False)

        mock_filesystem.exists.return_value = True
        mock_filesystem.read_text.return_value = existing_content

        updates = {"agents.pantheon": "Orchestrator", "new_key": "new_value"}
        deletes = ["old_key"]

        # Act
        workspace.set_team_data(updates, deletes)

        # Assert
        mock_filesystem.write_text.assert_called_once()
        call_args = mock_filesystem.write_text.call_args
        written_content = call_args[0][1]

        # Parse written YAML to verify structure
        written_data = yaml.safe_load(written_content)
        assert (
            written_data["agents"]["architect"] == "Technical foundations"
        )  # Preserved
        assert written_data["agents"]["pantheon"] == "Orchestrator"  # Added
        assert written_data["new_key"] == "new_value"  # Added
        assert "old_key" not in written_data  # Deleted

    def test_parse_dot_notation(self, tmp_path):
        """Test parsing dot notation into nested dictionary."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act
        result = workspace._parse_dot_notation("agents.backend", "Backend dev")

        # Assert
        expected = {"agents": {"backend": "Backend dev"}}
        assert result == expected

    def test_parse_dot_notation_single_key(self, tmp_path):
        """Test parsing single key (no dots)."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act
        result = workspace._parse_dot_notation("foo", "bar")

        # Assert
        expected = {"foo": "bar"}
        assert result == expected

    def test_deep_merge(self, tmp_path):
        """Test deep merge functionality."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        base = {"agents": {"architect": "Technical foundations"}, "existing": "value"}
        update = {"agents": {"pantheon": "Orchestrator"}, "new": "value"}

        # Act
        result = workspace._deep_merge(base, update)

        # Assert
        expected = {
            "agents": {
                "architect": "Technical foundations",
                "pantheon": "Orchestrator",
            },
            "existing": "value",
            "new": "value",
        }
        assert result == expected

    def test_delete_nested_key(self, tmp_path):
        """Test deleting nested key using dot notation."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        data = {
            "agents": {
                "pantheon": "Orchestrator",
                "architect": "Technical foundations",
            },
            "other": "value",
        }

        # Act
        workspace._delete_nested_key(data, "agents.pantheon")

        # Assert
        expected = {"agents": {"architect": "Technical foundations"}, "other": "value"}
        assert data == expected

    def test_delete_nested_key_nonexistent(self, tmp_path):
        """Test deleting non-existent key doesn't cause errors."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        data = {"agents": {"architect": "Technical foundations"}}
        original_data = data.copy()

        # Act
        workspace._delete_nested_key(data, "agents.nonexistent")
        workspace._delete_nested_key(data, "nonexistent.key")

        # Assert - data should be unchanged
        assert data == original_data


class TestCLITeamData:
    """Test team-data CLI commands."""

    def test_get_team_data_cli(self):
        """Test get team-data CLI command delegates to ProcessHandler."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )
        mock_process_handler.get_team_data.return_value = (
            "agents:\n  pantheon: Orchestrator"
        )

        # Act
        result = cli.get_team_data("test-actor", "agents")

        # Assert
        mock_process_handler.get_team_data.assert_called_once_with(
            "test-actor", "agents"
        )
        assert result == "agents:\n  pantheon: Orchestrator"

    def test_set_team_data_cli(self):
        """Test set team-data CLI command."""
        # Arrange
        mock_workspace = Mock()
        mock_process_handler = Mock()
        mock_rae_engine = Mock()
        mock_filesystem = Mock()

        cli = CLI(
            mock_workspace, mock_process_handler, mock_rae_engine, mock_filesystem
        )

        updates = {"agents.pantheon": "Orchestrator"}
        deletes = ["old_key"]

        # Act
        result = cli.set_team_data("test-actor", updates, deletes)

        # Assert
        mock_workspace.set_team_data.assert_called_once_with(updates, deletes)
        assert "2 operations completed" in result

    def test_set_team_data_values_with_spaces(self, tmp_path):
        """Test setting values with spaces works correctly."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        mock_filesystem.exists.return_value = False  # New file

        # Act - Test values with spaces like shell would pass them
        updates = {
            "agents.pantheon": "Intelligent orchestrator with spaces",
            "description": "This is a longer description with multiple words",
        }
        workspace.set_team_data(updates, [])

        # Assert
        mock_filesystem.write_text.assert_called_once()
        call_args = mock_filesystem.write_text.call_args
        written_content = call_args[0][1]

        # Parse written YAML to verify spaces preserved
        written_data = yaml.safe_load(written_content)
        assert (
            written_data["agents"]["pantheon"] == "Intelligent orchestrator with spaces"
        )
        assert (
            written_data["description"]
            == "This is a longer description with multiple words"
        )

    def test_type_coercion_booleans(self, tmp_path):
        """Test boolean type coercion."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act & Assert
        assert workspace._coerce_value_type("true") is True
        assert workspace._coerce_value_type("True") is True
        assert workspace._coerce_value_type("TRUE") is True
        assert workspace._coerce_value_type("false") is False
        assert workspace._coerce_value_type("False") is False
        assert workspace._coerce_value_type("FALSE") is False

    def test_type_coercion_integers(self, tmp_path):
        """Test integer type coercion."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act & Assert
        assert workspace._coerce_value_type("15") == 15
        assert workspace._coerce_value_type("0") == 0
        assert workspace._coerce_value_type("-5") == -5
        assert workspace._coerce_value_type("007") == 7  # Leading zeros stripped

    def test_type_coercion_floats(self, tmp_path):
        """Test float type coercion."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act & Assert
        assert workspace._coerce_value_type("87.5") == 87.5
        assert workspace._coerce_value_type("0.0") == 0.0
        assert workspace._coerce_value_type("-12.34") == -12.34
        assert workspace._coerce_value_type("3.14159") == 3.14159

    def test_type_coercion_strings_preserved(self, tmp_path):
        """Test strings that should remain strings."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)

        # Act & Assert - these should remain strings
        assert workspace._coerce_value_type("hello") == "hello"
        assert workspace._coerce_value_type("backend-engineer") == "backend-engineer"
        assert workspace._coerce_value_type("1.2.3") == "1.2.3"  # Multiple dots
        assert workspace._coerce_value_type("v1.0") == "v1.0"  # Mixed alphanumeric
        assert workspace._coerce_value_type("true!") == "true!"  # Not pure boolean
        assert workspace._coerce_value_type("15px") == "15px"  # Not pure number
        assert workspace._coerce_value_type("3.14.15") == "3.14.15"  # Multiple dots

    def test_set_team_data_with_type_coercion(self, tmp_path):
        """Test complete workflow with type coercion."""
        # Arrange
        mock_filesystem = Mock()
        workspace = PantheonWorkspace(tmp_path, "pantheon-artifacts", mock_filesystem)
        workspace._project_config = {"active_team": "test-team"}

        mock_filesystem.exists.return_value = False  # New file

        # Act - Mix of different types
        updates = {
            "agents.pantheon": "Intelligent orchestrator",  # String
            "metrics.count": "15",  # → int
            "metrics.percentage": "87.5",  # → float
            "config.debug": "true",  # → bool
            "config.enabled": "false",  # → bool
            "version": "1.2.3",  # → string (multiple dots)
        }
        workspace.set_team_data(updates, [])

        # Assert
        mock_filesystem.write_text.assert_called_once()
        call_args = mock_filesystem.write_text.call_args
        written_content = call_args[0][1]

        # Parse and verify types
        written_data = yaml.safe_load(written_content)
        assert written_data["agents"]["pantheon"] == "Intelligent orchestrator"
        assert written_data["metrics"]["count"] == 15  # int
        assert written_data["metrics"]["percentage"] == 87.5  # float
        assert written_data["config"]["debug"] is True  # bool
        assert written_data["config"]["enabled"] is False  # bool
        assert written_data["version"] == "1.2.3"  # string
