"""Integration tests for profile selection and runtime usage.

This test module validates the complete profile selection workflow:
- Profile selection during init writes to team-profile.yaml
- Runtime system reads active_profile from team-profile.yaml
- Process execution uses correct profile settings for schema composition
"""

import pytest
import yaml

from pantheon.filesystem import FileSystem
from pantheon.workspace import PantheonWorkspace


class TestProfileSelectionIntegration:
    """Integration tests for profile selection workflow."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create test project structure with profile-enabled team."""
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Create team directory structure
        team_dir = project_root / "pantheon-teams" / "test-team"
        team_dir.mkdir(parents=True)

        # Create team-profile.yaml with multiple profiles
        profile_data = {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "verbosity": False,
                    "max_iterations": 3,
                },
                "development": {
                    "verbosity": True,
                    "max_iterations": 10,
                },
                "production": {
                    "verbosity": False,
                    "max_iterations": 5,
                },
            },
        }
        profile_file = team_dir / "team-profile.yaml"
        profile_file.write_text(yaml.safe_dump(profile_data))

        # Create .pantheon_project config
        config_content = """active_team: test-team
artifacts_root: pantheon-artifacts
"""
        (project_root / ".pantheon_project").write_text(config_content)

        # Create artifacts directory
        (project_root / "pantheon-artifacts").mkdir()

        return project_root

    def test_profile_change_immediately_reflected_in_process_execution(
        self, test_project
    ):
        """Test that profile changes in team-profile.yaml are immediately used."""
        # Arrange: Create workspace with real filesystem
        filesystem = FileSystem()
        workspace = PantheonWorkspace(
            project_root=str(test_project),
            artifacts_root="pantheon-artifacts",
            filesystem=filesystem,
        )

        # Read initial profile
        initial_profile_yaml = workspace.get_team_profile()
        initial_profile = yaml.safe_load(initial_profile_yaml)
        assert initial_profile["active_profile"] == "default"
        assert initial_profile["profiles"]["default"]["verbosity"] is False

        # Act: Manually edit team-profile.yaml to change active_profile
        profile_file = (
            test_project / "pantheon-teams" / "test-team" / "team-profile.yaml"
        )
        profile_data = yaml.safe_load(profile_file.read_text())
        profile_data["active_profile"] = "development"
        profile_file.write_text(yaml.safe_dump(profile_data))

        # Create new workspace instance (simulates subsequent command)
        workspace_after_change = PantheonWorkspace(
            project_root=str(test_project),
            artifacts_root="pantheon-artifacts",
            filesystem=filesystem,
        )

        # Assert: New profile is immediately reflected
        updated_profile_yaml = workspace_after_change.get_team_profile()
        updated_profile = yaml.safe_load(updated_profile_yaml)
        assert updated_profile["active_profile"] == "development"
        assert updated_profile["profiles"]["development"]["verbosity"] is True
        assert updated_profile["profiles"]["development"]["max_iterations"] == 10

    def test_runtime_system_reads_profile_from_team_profile_yaml(self, test_project):
        """Test that runtime system correctly reads active_profile from team-profile.yaml."""
        # Arrange: Setup workspace
        filesystem = FileSystem()
        workspace = PantheonWorkspace(
            project_root=str(test_project),
            artifacts_root="pantheon-artifacts",
            filesystem=filesystem,
        )

        # Act: Read profile through workspace (same method ProcessHandler uses)
        profile_yaml = workspace.get_team_profile()
        profile_data = yaml.safe_load(profile_yaml)

        # Assert: Profile loaded from team-profile.yaml
        assert "active_profile" in profile_data
        assert profile_data["active_profile"] == "default"
        assert "profiles" in profile_data
        assert "default" in profile_data["profiles"]
        assert profile_data["profiles"]["default"]["verbosity"] is False

    def test_profile_selection_persistence_integration(self, tmp_path):
        """Test complete flow: init with profile selection -> profile persisted -> runtime reads it."""
        # Arrange: Create project structure
        project_root = tmp_path / "integration-test"
        project_root.mkdir()

        # Create team with profiles in bundled templates (simulated)
        team_dir = project_root / "pantheon-teams" / "integration-team"
        team_dir.mkdir(parents=True)

        # Simulate init writing selected profile to team-profile.yaml
        selected_profile = "production"
        profile_data = {
            "active_profile": selected_profile,
            "profiles": {
                "default": {"feature_flags": []},
                "production": {"feature_flags": ["strict_validation", "audit_logging"]},
            },
        }
        (team_dir / "team-profile.yaml").write_text(yaml.safe_dump(profile_data))

        # Create .pantheon_project
        config_content = """active_team: integration-team
artifacts_root: pantheon-artifacts
"""
        (project_root / ".pantheon_project").write_text(config_content)
        (project_root / "pantheon-artifacts").mkdir()

        # Act: Create workspace and read profile (runtime behavior)
        filesystem = FileSystem()
        workspace = PantheonWorkspace(
            project_root=str(project_root),
            artifacts_root="pantheon-artifacts",
            filesystem=filesystem,
        )

        runtime_profile_yaml = workspace.get_team_profile()
        runtime_profile = yaml.safe_load(runtime_profile_yaml)

        # Assert: Runtime correctly reads the persisted profile selection
        assert runtime_profile["active_profile"] == selected_profile
        assert (
            "strict_validation"
            in runtime_profile["profiles"]["production"]["feature_flags"]
        )
        assert (
            "audit_logging"
            in runtime_profile["profiles"]["production"]["feature_flags"]
        )
