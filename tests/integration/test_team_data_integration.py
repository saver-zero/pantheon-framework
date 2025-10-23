"""Integration tests for team-data functionality using real filesystem."""

from pathlib import Path
import tempfile

import pytest
import yaml

from pantheon.artifact_engine import ArtifactEngine
from pantheon.filesystem import FileSystem
from pantheon.process_handler import ProcessHandler
from pantheon.rae_engine import RaeEngine
from pantheon.workspace import PantheonWorkspace


class TestTeamDataIntegration:
    """Integration tests for team-data operations with real filesystem."""

    def setup_test_project(
        self, temp_dir: Path
    ) -> tuple[Path, PantheonWorkspace, ProcessHandler]:
        """Set up a test project with team structure."""
        # Create project structure
        project_config = temp_dir / ".pantheon_project"
        project_config.write_text(
            "active_team: test-team\nartifacts_root: pantheon-artifacts"
        )

        teams_dir = temp_dir / "pantheon-teams" / "test-team"
        teams_dir.mkdir(parents=True)

        agents_dir = teams_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test-actor.md").write_text(
            "# Test Actor\nA test actor for integration tests."
        )

        artifacts_dir = temp_dir / "pantheon-artifacts"
        artifacts_dir.mkdir()

        # Create components
        filesystem = FileSystem()
        workspace = PantheonWorkspace(temp_dir, "pantheon-artifacts", filesystem)
        artifact_engine = ArtifactEngine(workspace)
        rae_engine = RaeEngine(workspace, artifact_engine)
        process_handler = ProcessHandler(workspace, artifact_engine, rae_engine)

        return temp_dir, workspace, process_handler

    def test_team_data_full_workflow(self):
        """Test complete team-data workflow with real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            project_dir, workspace, process_handler = self.setup_test_project(temp_dir)

            # Test 1: Initially no team-data.yaml
            with pytest.raises(FileNotFoundError):
                workspace.get_team_data()

            # Test 2: Create new team-data.yaml with set operation
            workspace.set_team_data(
                {"agents.pantheon": "Intelligent orchestrator", "foo": "bar"}, []
            )

            # Verify file was created
            team_data_path = (
                project_dir / "pantheon-teams" / "test-team" / "team-data.yaml"
            )
            assert team_data_path.exists()

            # Test 3: Read back the data using ProcessHandler (with rendering)
            result = process_handler.get_team_data("test-actor")
            data = yaml.safe_load(result)
            assert data["agents"]["pantheon"] == "Intelligent orchestrator"
            assert data["foo"] == "bar"

            # Test 4: Get filtered data using ProcessHandler
            agents_result = process_handler.get_team_data("test-actor", "agents")
            agents_data = yaml.safe_load(agents_result)
            assert agents_data["pantheon"] == "Intelligent orchestrator"

            # Test 5: Get nested value directly using ProcessHandler
            pantheon_result = process_handler.get_team_data(
                "test-actor", "agents.pantheon"
            )
            assert pantheon_result == "Intelligent orchestrator"

            # Test 6: Update existing data and delete a key
            workspace.set_team_data(
                {"agents.architect": "Technical foundations", "new_key": "new_value"},
                ["foo"],
            )

            # Test 7: Verify updates using ProcessHandler
            final_result = process_handler.get_team_data("test-actor")
            final_data = yaml.safe_load(final_result)
            assert (
                final_data["agents"]["pantheon"] == "Intelligent orchestrator"
            )  # Preserved
            assert final_data["agents"]["architect"] == "Technical foundations"  # Added
            assert final_data["new_key"] == "new_value"  # Added
            assert "foo" not in final_data  # Deleted

    def test_team_data_deep_merge_preservation(self):
        """Test that deep merge preserves existing nested structures."""
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            project_dir, workspace, process_handler = self.setup_test_project(temp_dir)

            # Create initial data structure
            initial_data = {
                "agents": {
                    "pantheon": "Orchestrator",
                    "architect": "Technical foundations",
                },
                "metrics": {"count": "10", "last_update": "2025-09-20"},
                "config": {"debug": "true"},
            }

            # Write initial data directly to file
            team_data_path = (
                project_dir / "pantheon-teams" / "test-team" / "team-data.yaml"
            )
            team_data_path.write_text(yaml.dump(initial_data))

            # Update with new nested data
            workspace.set_team_data(
                {
                    "agents.backend": "Backend specialist",
                    "metrics.new_metric": "15",
                    "config.log_level": "DEBUG",
                },
                ["metrics.count"],
            )

            # Verify deep merge worked correctly
            result = workspace.get_team_data()
            final_data = yaml.safe_load(result)

            # Check agents section (added new agent, preserved existing)
            assert final_data["agents"]["pantheon"] == "Orchestrator"
            assert final_data["agents"]["architect"] == "Technical foundations"
            assert final_data["agents"]["backend"] == "Backend specialist"

            # Check metrics section (added new metric, deleted count, preserved last_update)
            assert "count" not in final_data["metrics"]
            assert final_data["metrics"]["last_update"] == "2025-09-20"
            assert final_data["metrics"]["new_metric"] == 15

            # Check config section (added new config, preserved existing)
            assert final_data["config"]["debug"] == "true"
            assert final_data["config"]["log_level"] == "DEBUG"

    def test_team_data_error_handling(self):
        """Test error handling with real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            project_dir, workspace, process_handler = self.setup_test_project(temp_dir)

            # Test invalid YAML handling - workspace.get_team_data() returns raw content
            # ProcessHandler raises ValueError when parsing invalid YAML
            team_data_path = (
                project_dir / "pantheon-teams" / "test-team" / "team-data.yaml"
            )
            team_data_path.write_text("invalid: yaml: content: [unclosed")

            with pytest.raises(ValueError, match="Invalid YAML"):
                process_handler.get_team_data("test-actor")

            with pytest.raises(ValueError, match="Invalid YAML"):
                workspace.set_team_data({"key": "value"}, [])

    def test_type_coercion_integration(self):
        """Test type coercion with real filesystem operations."""
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            project_dir, workspace, process_handler = self.setup_test_project(temp_dir)

            # Test setting various typed values
            workspace.set_team_data(
                {
                    "agents.pantheon": "Intelligent orchestrator",  # string
                    "metrics.count": "15",  # → int
                    "metrics.success_rate": "87.5",  # → float
                    "config.debug": "true",  # → bool
                    "config.enabled": "false",  # → bool
                    "version": "1.2.3",  # → string (ambiguous)
                    "tags": "backend-specialist",  # → string
                    "negative_number": "-42",  # → int
                    "negative_float": "-3.14",  # → float
                },
                [],
            )

            # Read back and verify types were preserved correctly
            team_data_path = (
                project_dir / "pantheon-teams" / "test-team" / "team-data.yaml"
            )
            assert team_data_path.exists()

            # Read the actual YAML file
            with open(team_data_path) as f:
                yaml_content = f.read()
                data = yaml.safe_load(yaml_content)

            # Verify types
            assert isinstance(data["agents"]["pantheon"], str)
            assert data["agents"]["pantheon"] == "Intelligent orchestrator"

            assert isinstance(data["metrics"]["count"], int)
            assert data["metrics"]["count"] == 15

            assert isinstance(data["metrics"]["success_rate"], float)
            assert data["metrics"]["success_rate"] == 87.5

            assert isinstance(data["config"]["debug"], bool)
            assert data["config"]["debug"] is True

            assert isinstance(data["config"]["enabled"], bool)
            assert data["config"]["enabled"] is False

            assert isinstance(data["version"], str)
            assert data["version"] == "1.2.3"

            assert isinstance(data["tags"], str)
            assert data["tags"] == "backend-specialist"

            assert isinstance(data["negative_number"], int)
            assert data["negative_number"] == -42

            assert isinstance(data["negative_float"], float)
            assert data["negative_float"] == -3.14

            # Verify the YAML file looks correct
            print("Generated YAML with type coercion:")
            print("=" * 40)
            print(yaml_content)
            print("=" * 40)

            # Verify YAML syntax is correct (no quotes around numbers/booleans)
            assert "count: 15" in yaml_content  # int without quotes
            assert "success_rate: 87.5" in yaml_content  # float without quotes
            assert "debug: true" in yaml_content  # bool without quotes
            assert "enabled: false" in yaml_content  # bool without quotes
            assert "version: 1.2.3" in yaml_content  # string without quotes (safe)

            # Test reading back with process_handler (which handles rendering and filtering)
            result_all = process_handler.get_team_data("test-actor")
            result_metrics = process_handler.get_team_data("test-actor", "metrics")
            result_count = process_handler.get_team_data("test-actor", "metrics.count")

            # Verify process_handler returns correct formats
            assert "count: 15" in result_all  # Numbers without quotes
            assert "debug: true" in result_all  # Booleans without quotes
            assert "count: 15" in result_metrics  # Filtered section
            assert (
                result_count.strip() == "15"
            )  # Single value as string (strip newline)
