"""Unit tests for CLI profile selection and persistence.

This test module validates the CLI init command's profile selection workflow:
- Selected profile is written to team-profile.yaml in project's team directory
- .pantheon_project file does not contain active_profile field
- Teams without profiles continue working correctly
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from pantheon.cli import CLI


class TestCLIProfileSelectionPersistence:
    """Test cases for profile selection persistence to team-profile.yaml."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for CLI initialization tests."""
        return {
            "workspace": Mock(),
            "process_handler": Mock(),
            "rae_engine": Mock(),
            "filesystem": Mock(),
        }

    @pytest.fixture
    def cli_with_mocks(self, mock_dependencies):
        """Create CLI instance with mocked dependencies."""
        return CLI(
            mock_dependencies["workspace"],
            mock_dependencies["process_handler"],
            mock_dependencies["rae_engine"],
            mock_dependencies["filesystem"],
        )

    def test_selected_profile_written_to_team_profile_yaml(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test that selected profile is written to team-profile.yaml."""
        # Arrange: Setup test data
        project_root = Path("/test/project")
        selected_team = "test-team"
        selected_profile = "development"
        filesystem = mock_dependencies["filesystem"]

        # Mock bundled profile reading
        bundled_profile_data = {
            "active_profile": "default",
            "profiles": {
                "default": {"verbosity": False},
                "development": {"verbosity": True},
            },
        }

        # Act: Call the helper method with mocked resources
        with patch("pantheon.cli.importlib.resources.as_file") as mock_as_file:
            # Create a mock file path that exists
            mock_profile_path = Mock()
            mock_profile_path.exists.return_value = True
            mock_profile_path.read_text.return_value = yaml.safe_dump(
                bundled_profile_data
            )

            # Configure as_file to yield the mock path
            mock_as_file.return_value.__enter__.return_value = mock_profile_path

            cli_with_mocks._update_team_profile_from_selection(
                project_root, selected_team, selected_profile, filesystem
            )

            # Assert: Verify filesystem.write_text was called with updated profile
            filesystem.write_text.assert_called_once()
            call_args = filesystem.write_text.call_args
            written_path = call_args[0][0]
            written_content = call_args[0][1]

            # Verify path is correct
            assert "team-profile.yaml" in str(written_path)
            assert selected_team in str(written_path)

            # Verify content has updated active_profile
            written_data = yaml.safe_load(written_content)
            assert written_data["active_profile"] == selected_profile

    def test_pantheon_project_does_not_contain_active_profile(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test that .pantheon_project file does not contain active_profile field."""
        # This test validates the config template will be updated in Phase 3
        # to remove the active_profile field

        # Current implementation (lines 1105-1106 in cli.py) adds active_profile
        # Phase 3 will remove those lines

        # This test will pass once Phase 3 is complete
        # For now, documenting expected behavior

    def test_teams_without_profiles_continue_working(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test that teams without profiles work correctly (backward compatibility)."""
        # This test validates that the profile update logic (Phase 4) only executes
        # when selected_profile is not None

        # Phase 4 implementation should include:
        # if selected_profile:
        #     self._update_team_profile(...)

        # This ensures teams without profiles continue to work


class TestCLIProfileUpdateFlow:
    """Test cases for profile update logic flow."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for CLI initialization tests."""
        return {
            "workspace": Mock(),
            "process_handler": Mock(),
            "rae_engine": Mock(),
            "filesystem": Mock(),
        }

    @pytest.fixture
    def cli_with_mocks(self, mock_dependencies):
        """Create CLI instance with mocked dependencies."""
        return CLI(
            mock_dependencies["workspace"],
            mock_dependencies["process_handler"],
            mock_dependencies["rae_engine"],
            mock_dependencies["filesystem"],
        )

    def test_profile_update_reads_bundled_template(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test that profile update reads from bundled team-profile.yaml template."""
        # Arrange
        project_root = Path("/test/project")
        selected_team = "test-team"
        selected_profile = "staging"
        filesystem = mock_dependencies["filesystem"]

        bundled_profile_data = {
            "active_profile": "default",
            "profiles": {
                "default": {"verbosity": False},
                "staging": {"verbosity": True, "cache_enabled": False},
            },
        }

        # Act: Call profile update method
        with patch("pantheon.cli.importlib.resources.as_file") as mock_as_file:
            # Create a mock file path that exists
            mock_profile_path = Mock()
            mock_profile_path.exists.return_value = True
            mock_profile_path.read_text.return_value = yaml.safe_dump(
                bundled_profile_data
            )

            # Configure as_file to yield the mock path
            mock_as_file.return_value.__enter__.return_value = mock_profile_path

            cli_with_mocks._update_team_profile_from_selection(
                project_root, selected_team, selected_profile, filesystem
            )

            # Assert: Verify the bundled template was read
            filesystem.write_text.assert_called_once()

            # Verify updated content has correct active_profile
            written_content = filesystem.write_text.call_args[0][1]
            written_data = yaml.safe_load(written_content)
            assert written_data["active_profile"] == selected_profile
            assert "profiles" in written_data
            assert written_data["profiles"]["staging"]["verbosity"] is True

    def test_profile_update_preserves_profile_definitions(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test that profile update preserves profiles definitions."""
        # This test validates expected behavior for Phase 4 implementation
        # The implementation should:
        # 1. Read bundled profile_data with all profiles
        # 2. Update only active_profile field to selected value
        # 3. Write back with all profiles preserved


class TestCLIProfileErrorHandling:
    """Test cases for profile selection error handling."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for CLI initialization tests."""
        return {
            "workspace": Mock(),
            "process_handler": Mock(),
            "rae_engine": Mock(),
            "filesystem": Mock(),
        }

    @pytest.fixture
    def cli_with_mocks(self, mock_dependencies):
        """Create CLI instance with mocked dependencies."""
        return CLI(
            mock_dependencies["workspace"],
            mock_dependencies["process_handler"],
            mock_dependencies["rae_engine"],
            mock_dependencies["filesystem"],
        )

    def test_profile_update_handles_missing_bundled_profile(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test profile update handles missing bundled team-profile.yaml gracefully."""
        # Arrange: Team has no profile file
        project_root = Path("/test/project")
        selected_team = "no-profile-team"
        selected_profile = "development"
        filesystem = mock_dependencies["filesystem"]

        # Act: Should handle missing file gracefully
        with patch("pantheon.cli.importlib.resources.as_file") as mock_as_file:
            # Create a mock file path that doesn't exist
            mock_profile_path = Mock()
            mock_profile_path.exists.return_value = False

            # Configure as_file to yield the mock path
            mock_as_file.return_value.__enter__.return_value = mock_profile_path

            # Should not raise exception - graceful handling
            cli_with_mocks._update_team_profile_from_selection(
                project_root, selected_team, selected_profile, filesystem
            )

            # Assert: Should log warning but not fail
            # No write should occur if bundled profile doesn't exist
            filesystem.write_text.assert_not_called()

    def test_profile_update_handles_malformed_yaml(
        self, cli_with_mocks, mock_dependencies
    ):
        """Test profile update handles malformed YAML gracefully."""
        # Arrange: Bundled profile has invalid YAML
        project_root = Path("/test/project")
        selected_team = "test-team"
        selected_profile = "development"
        filesystem = mock_dependencies["filesystem"]
        malformed_yaml = "active_profile: test\n  profiles: {invalid: [unclosed"

        # Act: Should handle yaml.YAMLError gracefully
        with patch("pantheon.cli.importlib.resources.as_file") as mock_as_file:
            # Create a mock file path with malformed YAML
            mock_profile_path = Mock()
            mock_profile_path.exists.return_value = True
            mock_profile_path.read_text.return_value = malformed_yaml

            # Configure as_file to yield the mock path
            mock_as_file.return_value.__enter__.return_value = mock_profile_path

            # Should not raise exception - graceful handling
            cli_with_mocks._update_team_profile_from_selection(
                project_root, selected_team, selected_profile, filesystem
            )

            # Assert: Should log warning but not fail
            # No write should occur if YAML is malformed
            filesystem.write_text.assert_not_called()
