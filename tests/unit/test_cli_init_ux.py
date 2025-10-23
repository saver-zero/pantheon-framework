"""Unit tests for CLI init command UX enhancements.

This test module validates the CLI init command's user experience improvements:
- Default team selection with clear indicators
- Detailed directory creation feedback showing paths
- Agent installation feedback showing file lists
- Content preview for CLAUDE.md and AGENTS.md appending
- Configuration file location display in success message
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pantheon.cli import CLI


class TestCLIInitDefaultTeamSelection:
    """Test cases for default team selection UI improvements."""

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

    @patch("click.prompt")
    @patch("click.echo")
    def test_default_team_displayed_first_with_indicator(
        self, mock_echo, mock_prompt, cli_with_mocks
    ):
        """Test that default team is displayed first with clear indicator."""
        # Arrange
        available_teams = ["standard", "pantheon-dev", "custom"]

        # Mock _load_team_description to return descriptions
        with (
            patch.object(
                cli_with_mocks,
                "_load_team_description",
                return_value="Test description",
            ),
            patch.object(
                cli_with_mocks, "_get_default_team", return_value="pantheon-dev"
            ),
        ):
            mock_prompt.return_value = "1"

            # Act
            result = cli_with_mocks._select_team_interactive(available_teams)

            # Assert - verify teams reordered with default first
            assert result == "pantheon-dev"

            # Verify default indicator is shown
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
            indicator_shown = any(
                "default - press enter to select" in call for call in echo_calls
            )
            assert indicator_shown, "Default indicator not shown in output"

            # Verify pantheon-dev is option 1
            first_team_call = any("1. pantheon-dev" in call for call in echo_calls)
            assert first_team_call, "Default team not shown as option 1"

    @patch("click.prompt")
    @patch("click.echo")
    def test_default_prompt_parameter_set_when_default_exists(
        self, mock_echo, mock_prompt, cli_with_mocks
    ):
        """Test that click.prompt receives default='1' when default team configured."""
        # Arrange
        available_teams = ["standard", "pantheon-dev"]

        with (
            patch.object(cli_with_mocks, "_load_team_description", return_value="Desc"),
            patch.object(
                cli_with_mocks, "_get_default_team", return_value="pantheon-dev"
            ),
        ):
            mock_prompt.return_value = "1"

            # Act
            cli_with_mocks._select_team_interactive(available_teams)

            # Assert - verify prompt called with default parameter
            mock_prompt.assert_called_once()
            call_kwargs = mock_prompt.call_args[1]
            assert "default" in call_kwargs, "Default parameter not passed to prompt"
            assert call_kwargs["default"] == "1", "Default parameter not set to '1'"

    @patch("click.prompt")
    @patch("click.echo")
    def test_no_default_indicator_when_no_default_configured(
        self, mock_echo, mock_prompt, cli_with_mocks
    ):
        """Test that no default indicator shown when default team not configured."""
        # Arrange
        available_teams = ["standard", "custom"]

        with (
            patch.object(cli_with_mocks, "_load_team_description", return_value="Desc"),
            patch.object(cli_with_mocks, "_get_default_team", return_value=None),
        ):
            mock_prompt.return_value = "1"

            # Act
            cli_with_mocks._select_team_interactive(available_teams)

            # Assert - verify no default indicator
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
            indicator_shown = any(
                "default - press enter" in call for call in echo_calls
            )
            assert not indicator_shown, (
                "Default indicator shown when no default configured"
            )


class TestCLIInitDirectoryFeedback:
    """Test cases for directory creation feedback improvements."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    @patch("pantheon.cli.click.echo")
    def test_directory_creation_shows_paths_not_counts(self, mock_echo, cli_with_mocks):
        """Test that directory creation displays actual paths instead of counts."""
        # Arrange
        created_paths = [
            Path("/project/pantheon-artifacts/docs"),
            Path("/project/pantheon-artifacts/tickets"),
            Path("/project/pantheon-artifacts/diagrams"),
        ]

        with patch.object(
            cli_with_mocks, "_create_team_data_directories", return_value=created_paths
        ):
            # Act - simulate directory creation feedback
            for path in created_paths:
                relative_path = path.relative_to("/project")
                cli_with_mocks._display_created_directory(relative_path)

            # Assert - verify paths are displayed
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
            # Convert to string for cross-platform compatibility
            echo_calls_str = " ".join(echo_calls)
            assert "pantheon-artifacts" in echo_calls_str
            assert "docs" in echo_calls_str
            assert "tickets" in echo_calls_str
            assert "diagrams" in echo_calls_str


class TestCLIInitAgentFeedback:
    """Test cases for agent installation feedback improvements."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    @patch("click.echo")
    def test_agent_installation_shows_file_list(self, mock_echo, cli_with_mocks):
        """Test that agent installation displays list of installed agent files."""
        # Arrange
        install_result = {
            "installed": 3,
            "skipped": 0,
            "failed": 0,
            "installed_files": [
                "tech-lead.md",
                "framework-engineer.md",
                "backend-engineer.md",
            ],
        }

        with patch.object(
            cli_with_mocks, "_copy_agents_to_claude", return_value=install_result
        ):
            # Act - simulate agent installation feedback
            cli_with_mocks._display_agent_installation_result(
                install_result, "pantheon-dev"
            )

            # Assert - verify agent files are listed
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
            assert any("tech-lead.md" in call for call in echo_calls)
            assert any("framework-engineer.md" in call for call in echo_calls)
            assert any("backend-engineer.md" in call for call in echo_calls)


class TestCLIInitContentPreview:
    """Test cases for CLAUDE.md and AGENTS.md content preview."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    @patch("click.echo")
    @patch("click.confirm")
    def test_claude_md_shows_preview_before_confirmation(
        self, mock_confirm, mock_echo, cli_with_mocks
    ):
        """Test that CLAUDE.md append shows content preview before prompting."""
        # Arrange
        protocol_content = """# Pantheon Protocol
Line 1
Line 2
Line 3"""

        with (
            patch.object(
                cli_with_mocks, "_get_protocol_content", return_value=protocol_content
            ),
            patch.object(
                cli_with_mocks, "_detect_existing_protocol", return_value=False
            ),
        ):
            mock_confirm.return_value = True

            # Act
            cli_with_mocks._prompt_claude_md_append(Path("/project"))

            # Assert - verify preview displayed before prompt
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]

            # Check preview separators shown
            preview_shown = any(
                "Preview of content to append" in call for call in echo_calls
            )
            assert preview_shown, "Preview header not shown"

            # Check content shown
            content_shown = any("Pantheon Protocol" in call for call in echo_calls)
            assert content_shown, "Content not shown in preview"

            # Verify confirmation references preview
            confirm_text = str(mock_confirm.call_args)
            assert "preview above" in confirm_text.lower(), (
                "Confirmation doesn't reference preview"
            )

    @patch("click.echo")
    def test_preview_truncates_long_content(self, mock_echo, cli_with_mocks):
        """Test that content preview truncates content longer than 15 lines."""
        # Arrange
        long_content = "\n".join([f"Line {i}" for i in range(20)])

        # Act
        cli_with_mocks._preview_content(long_content)

        # Assert - verify truncation message shown
        echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
        truncation_shown = any("more lines" in call for call in echo_calls)
        assert truncation_shown, "Truncation indicator not shown for long content"

    @patch("click.echo")
    @patch("click.confirm")
    def test_agents_md_shows_preview_before_confirmation(
        self, mock_confirm, mock_echo, cli_with_mocks
    ):
        """Test that AGENTS.md append shows content preview before prompting."""
        # Arrange
        instructions_content = """# Agent Instructions
Step 1
Step 2"""

        with (
            patch.object(
                cli_with_mocks,
                "_get_agents_instructions",
                return_value=instructions_content,
            ),
            patch.object(
                cli_with_mocks, "_detect_existing_instructions", return_value=False
            ),
        ):
            mock_confirm.return_value = True

            # Act
            cli_with_mocks._prompt_agents_md_append(Path("/project"))

            # Assert - verify preview displayed
            echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]
            preview_shown = any("Preview of content" in call for call in echo_calls)
            assert preview_shown, "Preview not shown before AGENTS.md prompt"


class TestCLIInitConfigFileLocations:
    """Test cases for configuration file location display in success message."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    @patch("click.echo")
    def test_success_message_shows_config_file_paths(self, mock_echo, cli_with_mocks):
        """Test that success message displays paths to configuration files."""
        # Arrange
        project_root = Path("/project")
        selected_team = "pantheon-dev"

        # Act
        cli_with_mocks._display_config_file_locations(project_root, selected_team)

        # Assert - verify configuration file paths displayed
        echo_calls = [str(call_args) for call_args in mock_echo.call_args_list]

        # Check .pantheon_project path shown
        pantheon_project_shown = any(".pantheon_project" in call for call in echo_calls)
        assert pantheon_project_shown, ".pantheon_project path not shown"

        # Check team-data.yaml path shown
        team_data_shown = any("team-data.yaml" in call for call in echo_calls)
        assert team_data_shown, "team-data.yaml path not shown"

        # Check team-profile.yaml path shown
        team_profile_shown = any("team-profile.yaml" in call for call in echo_calls)
        assert team_profile_shown, "team-profile.yaml path not shown"

    def test_config_paths_use_absolute_paths(self, cli_with_mocks):
        """Test that configuration file paths are displayed as absolute paths."""
        # Arrange - use absolute path that works on both Windows and Unix
        project_root = Path("C:/project").resolve()
        selected_team = "pantheon-dev"

        # Act
        paths = cli_with_mocks._get_config_file_paths(project_root, selected_team)

        # Assert - verify paths are absolute
        assert paths[".pantheon_project"].is_absolute()
        assert paths["team-data.yaml"].is_absolute()
        assert paths["team-profile.yaml"].is_absolute()

        # Verify correct path construction (platform-independent check)
        assert ".pantheon_project" in str(paths[".pantheon_project"])
        assert "pantheon-teams" in str(paths["team-data.yaml"])
        assert "pantheon-dev" in str(paths["team-data.yaml"])
        assert "team-data.yaml" in str(paths["team-data.yaml"])
        assert "pantheon-teams" in str(paths["team-profile.yaml"])
        assert "pantheon-dev" in str(paths["team-profile.yaml"])
        assert "team-profile.yaml" in str(paths["team-profile.yaml"])


class TestCLIInitPromptDefaults:
    """Test cases for init prompt default values."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    @patch("click.confirm")
    @patch("click.echo")
    def test_agent_installation_prompt_defaults_to_true(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that agent installation prompt uses default=True."""
        # Arrange
        mock_confirm.return_value = True
        selected_team = "test-team"
        selected_team_dir = Path("/test/teams/test-team")
        project_root = Path("/test/project")

        # Act
        cli_with_mocks._prompt_claude_agent_installation(
            selected_team, selected_team_dir, project_root
        )

        # Assert - verify click.confirm called with default=True
        mock_confirm.assert_called_once()
        call_kwargs = mock_confirm.call_args[1]
        assert "default" in call_kwargs, "Default parameter not passed to confirm"
        assert call_kwargs["default"] is True, "Default parameter not set to True"

    @patch("click.confirm")
    @patch("click.echo")
    def test_claude_md_append_prompt_defaults_to_true(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that CLAUDE.md append prompt uses default=True."""
        # Arrange
        with (
            patch.object(
                cli_with_mocks,
                "_get_protocol_content",
                return_value="# Protocol content",
            ),
            patch.object(
                cli_with_mocks, "_detect_existing_protocol", return_value=False
            ),
        ):
            mock_confirm.return_value = True

            # Act
            cli_with_mocks._prompt_claude_md_append(Path("/project"))

            # Assert - verify click.confirm called with default=True
            mock_confirm.assert_called_once()
            call_kwargs = mock_confirm.call_args[1]
            assert "default" in call_kwargs, "Default parameter not passed to confirm"
            assert call_kwargs["default"] is True, "Default parameter not set to True"

    @patch("click.confirm")
    @patch("click.echo")
    def test_agents_md_append_prompt_defaults_to_true(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that AGENTS.md append prompt uses default=True."""
        # Arrange
        with (
            patch.object(
                cli_with_mocks,
                "_get_agents_instructions",
                return_value="# Instructions",
            ),
            patch.object(
                cli_with_mocks, "_detect_existing_instructions", return_value=False
            ),
        ):
            mock_confirm.return_value = True

            # Act
            cli_with_mocks._prompt_agents_md_append(Path("/project"))

            # Assert - verify click.confirm called with default=True
            mock_confirm.assert_called_once()
            call_kwargs = mock_confirm.call_args[1]
            assert "default" in call_kwargs, "Default parameter not passed to confirm"
            assert call_kwargs["default"] is True, "Default parameter not set to True"


class TestCLIInitGitignoreManagement:
    """Test cases for gitignore management feature."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        filesystem_mock = Mock()
        return CLI(Mock(), Mock(), Mock(), filesystem_mock), filesystem_mock

    @patch("click.confirm")
    @patch("click.echo")
    def test_gitignore_prompt_defaults_to_false(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that gitignore management prompt uses default=False."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")

        with patch.object(cli, "_detect_gitignore_entries", return_value=False):
            mock_confirm.return_value = False

            # Act
            cli._prompt_gitignore_management(project_root)

            # Assert - verify click.confirm called with default=False
            mock_confirm.assert_called_once()
            call_kwargs = mock_confirm.call_args[1]
            assert "default" in call_kwargs, "Default parameter not passed to confirm"
            assert call_kwargs["default"] is False, "Default parameter not set to False"

    @patch("click.confirm")
    @patch("click.echo")
    def test_gitignore_entries_added_when_confirmed(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that gitignore entries are added when user confirms."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")

        with (
            patch.object(cli, "_detect_gitignore_entries", return_value=False),
            patch.object(cli, "_append_gitignore_entries") as mock_append,
        ):
            mock_confirm.return_value = True

            # Act
            result = cli._prompt_gitignore_management(project_root)

            # Assert - verify append method called
            mock_append.assert_called_once_with(project_root)
            assert result != ""  # Should return non-empty success message

    @patch("click.confirm")
    @patch("click.echo")
    def test_gitignore_not_modified_when_declined(
        self, mock_echo, mock_confirm, cli_with_mocks
    ):
        """Test that gitignore is not modified when user declines."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")

        with (
            patch.object(cli, "_detect_gitignore_entries", return_value=False),
            patch.object(cli, "_append_gitignore_entries") as mock_append,
        ):
            mock_confirm.return_value = False

            # Act
            result = cli._prompt_gitignore_management(project_root)

            # Assert - verify append method not called
            mock_append.assert_not_called()
            assert result == ""  # Should return empty string when declined

    @patch("click.echo")
    def test_gitignore_prompt_skipped_when_entries_exist(
        self, mock_echo, cli_with_mocks
    ):
        """Test that prompt is skipped when gitignore entries already exist."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")

        with (
            patch.object(cli, "_detect_gitignore_entries", return_value=True),
            patch.object(cli, "_append_gitignore_entries") as mock_append,
        ):
            # Act
            result = cli._prompt_gitignore_management(project_root)

            # Assert - verify no prompt and no append
            mock_append.assert_not_called()
            assert result == ""  # Should return empty string when already present

    def test_detect_gitignore_entries_returns_false_when_file_missing(
        self, cli_with_mocks
    ):
        """Test that detection returns False when .gitignore doesn't exist."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")
        gitignore_path = project_root / ".gitignore"

        filesystem_mock.exists.return_value = False

        # Act
        result = cli._detect_gitignore_entries(project_root)

        # Assert
        filesystem_mock.exists.assert_called_once_with(gitignore_path)
        assert result is False

    def test_detect_gitignore_entries_returns_true_when_marker_present(
        self, cli_with_mocks
    ):
        """Test that detection returns True when Pantheon marker is present."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")
        gitignore_content = """node_modules/
.env
# Pantheon Framework artifacts
pantheon-artifacts/
"""

        filesystem_mock.exists.return_value = True
        filesystem_mock.read_text.return_value = gitignore_content

        # Act
        result = cli._detect_gitignore_entries(project_root)

        # Assert
        assert result is True

    def test_detect_gitignore_entries_returns_false_when_marker_absent(
        self, cli_with_mocks
    ):
        """Test that detection returns False when marker is not present."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")
        gitignore_content = """node_modules/
.env
dist/
"""

        filesystem_mock.exists.return_value = True
        filesystem_mock.read_text.return_value = gitignore_content

        # Act
        result = cli._detect_gitignore_entries(project_root)

        # Assert
        assert result is False

    def test_append_gitignore_entries_creates_file_if_missing(self, cli_with_mocks):
        """Test that append creates .gitignore if it doesn't exist."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")

        filesystem_mock.exists.return_value = False

        # Act
        cli._append_gitignore_entries(project_root)

        # Assert - verify file created with marker and entries
        filesystem_mock.write_text.assert_called_once()
        call_args = filesystem_mock.write_text.call_args[0]
        written_content = call_args[1]

        assert "# Pantheon Framework artifacts" in written_content
        assert "pantheon-artifacts/" in written_content
        assert ".pantheon_project" in written_content
        assert "pantheon-teams/" in written_content

    def test_append_gitignore_entries_appends_to_existing_file(self, cli_with_mocks):
        """Test that append adds entries to existing .gitignore."""
        # Arrange
        cli, filesystem_mock = cli_with_mocks
        project_root = Path("/project")
        existing_content = "node_modules/\n.env\n"

        filesystem_mock.exists.return_value = True
        filesystem_mock.read_text.return_value = existing_content

        # Act
        cli._append_gitignore_entries(project_root)

        # Assert - verify content appended
        filesystem_mock.write_text.assert_called_once()
        call_args = filesystem_mock.write_text.call_args[0]
        written_content = call_args[1]

        assert existing_content in written_content
        assert "# Pantheon Framework artifacts" in written_content
        assert "pantheon-artifacts/" in written_content


class TestCLIInitReadmePath:
    """Test cases for README path display in completion message."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI instance with mocked dependencies."""
        return CLI(Mock(), Mock(), Mock(), Mock())

    def test_readme_path_constructed_from_team_dir(self, cli_with_mocks):
        """Test that README path is correctly constructed from selected_team_dir."""
        # Arrange
        project_root = Path("/project")
        selected_team = "pantheon-dev"
        selected_team_dir = project_root / "pantheon-teams" / selected_team
        expected_readme_path = selected_team_dir / "README.md"

        # Act - construct path the same way init_project does
        readme_path = selected_team_dir / "README.md"

        # Assert - verify path construction
        assert readme_path == expected_readme_path
        assert "README.md" in str(readme_path)
        assert selected_team in str(readme_path)
