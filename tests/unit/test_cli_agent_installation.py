"""Unit tests for CLI platform-agnostic agent installation.

This test module validates the refactored multi-platform agent installation:
- Platform-agnostic agent copying to correct directories
- Conflict resolution working identically across platforms
- Platform-specific display messages
- Backward compatibility with existing Claude installation
- OpenCode installation support
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pantheon.cli import CLI


class TestPlatformAgnosticAgentInstallation:
    """Test cases for platform-agnostic agent installation functionality."""

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

    @pytest.fixture
    def claude_platform_config(self):
        """Claude platform configuration for testing."""
        return {
            "target_base_dir": ".claude/agents",
            "platform_display_name": "Claude",
            "validation_base": Path("/project") / ".claude" / "agents",
        }

    @pytest.fixture
    def opencode_platform_config(self):
        """OpenCode platform configuration for testing."""
        return {
            "target_base_dir": ".opencode/agent",
            "platform_display_name": "OpenCode",
            "validation_base": Path("/project") / ".opencode" / "agent",
        }

    @pytest.fixture
    def mock_agent_files(self):
        """Create list of mock agent file paths."""
        return [
            Path("/teams/test-team/agents/agent1.md"),
            Path("/teams/test-team/agents/agent2.md"),
            Path("/teams/test-team/agents/agent3.md"),
        ]

    def test_copy_agents_to_platform_uses_claude_directory(
        self,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
        claude_platform_config,
    ):
        """Test platform-agnostic method copies files to Claude directory when configured."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.return_value = False  # No conflicts
        mock_fs.read_text.return_value = "# Agent content"
        project_root = Path("/project")
        team_name = "test-team"
        team_dir = Path("/teams/test-team")

        # Act
        results = cli_with_mocks._copy_agents_to_platform(
            mock_agent_files, team_name, team_dir, project_root, claude_platform_config
        )

        # Assert - verify files copied to .claude/agents/test-team/
        expected_dir = project_root / ".claude" / "agents" / team_name
        mock_fs.mkdir.assert_called_once()
        call_args = mock_fs.mkdir.call_args
        assert expected_dir in call_args[0] or str(expected_dir) in str(call_args)

        # Verify each agent file was written to correct location
        assert mock_fs.write_text.call_count == 3
        write_calls = [call[0][0] for call in mock_fs.write_text.call_args_list]
        for agent_file in mock_agent_files:
            expected_path = expected_dir / agent_file.name
            assert any(
                str(expected_path) in str(write_call) for write_call in write_calls
            ), f"Expected write to {expected_path}"

        assert results["installed"] == 3
        assert results["skipped"] == 0
        assert results["failed"] == 0

    def test_copy_agents_to_platform_uses_opencode_directory(
        self,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
        opencode_platform_config,
    ):
        """Test platform-agnostic method copies files to OpenCode directory when configured."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.return_value = False  # No conflicts
        mock_fs.read_text.return_value = "# Agent content"
        project_root = Path("/project")
        team_name = "test-team"
        team_dir = Path("/teams/test-team")

        # Act
        results = cli_with_mocks._copy_agents_to_platform(
            mock_agent_files,
            team_name,
            team_dir,
            project_root,
            opencode_platform_config,
        )

        # Assert - verify files copied to .opencode/agent/test-team/
        expected_dir = project_root / ".opencode" / "agent" / team_name
        mock_fs.mkdir.assert_called_once()
        call_args = mock_fs.mkdir.call_args
        assert expected_dir in call_args[0] or str(expected_dir) in str(call_args)

        # Verify each agent file was written to correct location
        assert mock_fs.write_text.call_count == 3
        write_calls = [call[0][0] for call in mock_fs.write_text.call_args_list]
        for agent_file in mock_agent_files:
            expected_path = expected_dir / agent_file.name
            assert any(
                str(expected_path) in str(write_call) for write_call in write_calls
            ), f"Expected write to {expected_path}"

        assert results["installed"] == 3
        assert results["skipped"] == 0
        assert results["failed"] == 0

    @patch("pantheon.cli.click.confirm")
    @patch("pantheon.cli.click.prompt")
    def test_conflict_resolution_overwrite_all_works_for_claude(
        self,
        mock_prompt,
        mock_confirm,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
        claude_platform_config,
    ):
        """Test 'overwrite all' conflict strategy works for Claude platform."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.return_value = True  # All files conflict
        mock_fs.read_text.return_value = "# Agent content"
        mock_prompt.return_value = "o"  # User chooses overwrite all
        project_root = Path("/project")
        team_name = "test-team"
        team_dir = Path("/teams/test-team")

        # Act
        results = cli_with_mocks._copy_agents_to_platform(
            mock_agent_files, team_name, team_dir, project_root, claude_platform_config
        )

        # Assert - all files should be overwritten
        assert results["installed"] == 3
        assert results["skipped"] == 0
        assert mock_fs.write_text.call_count == 3
        # Prompt should only be called once for batch strategy
        assert mock_prompt.call_count == 1

    @patch("pantheon.cli.click.confirm")
    @patch("pantheon.cli.click.prompt")
    def test_conflict_resolution_skip_all_works_for_opencode(
        self,
        mock_prompt,
        mock_confirm,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
        opencode_platform_config,
    ):
        """Test 'skip all' conflict strategy works for OpenCode platform."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.return_value = True  # All files conflict
        mock_fs.read_text.return_value = "# Agent content"
        mock_prompt.return_value = "s"  # User chooses skip all
        project_root = Path("/project")
        team_name = "test-team"
        team_dir = Path("/teams/test-team")

        # Act
        results = cli_with_mocks._copy_agents_to_platform(
            mock_agent_files,
            team_name,
            team_dir,
            project_root,
            opencode_platform_config,
        )

        # Assert - all files should be skipped
        assert results["installed"] == 0
        assert results["skipped"] == 3
        assert mock_fs.write_text.call_count == 0
        # Prompt should only be called once for batch strategy
        assert mock_prompt.call_count == 1

    @patch("pantheon.cli.click.confirm")
    @patch("pantheon.cli.click.prompt")
    def test_conflict_resolution_ask_each_time_works_across_platforms(
        self,
        mock_prompt,
        mock_confirm,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
        claude_platform_config,
    ):
        """Test 'ask each time' conflict strategy prompts for each file."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.return_value = True  # All files conflict
        mock_fs.read_text.return_value = "# Agent content"
        mock_prompt.return_value = "a"  # User chooses ask each time
        # Configure per-file responses: yes, no, yes
        mock_confirm.side_effect = [True, False, True]
        project_root = Path("/project")
        team_name = "test-team"
        team_dir = Path("/teams/test-team")

        # Act
        results = cli_with_mocks._copy_agents_to_platform(
            mock_agent_files, team_name, team_dir, project_root, claude_platform_config
        )

        # Assert - 2 files installed (overwritten), 1 skipped
        assert results["installed"] == 2
        assert results["skipped"] == 1
        assert mock_fs.write_text.call_count == 2
        # Should prompt once for strategy, then confirm for each file
        assert mock_prompt.call_count == 1
        assert mock_confirm.call_count == 3

    @patch("pantheon.cli.click.echo")
    def test_display_platform_result_shows_claude_platform_name(
        self, mock_echo, cli_with_mocks, claude_platform_config
    ):
        """Test display method shows 'Claude' platform name in output."""
        # Arrange
        results = {
            "installed": 2,
            "skipped": 1,
            "failed": 0,
            "installed_files": ["agent1.md", "agent2.md"],
        }
        selected_team = "test-team"

        # Act
        cli_with_mocks._display_platform_agent_installation_result(
            results, selected_team, claude_platform_config
        )

        # Assert - verify output contains Claude platform name and directory
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        echo_output = " ".join(echo_calls)

        assert "Claude" in echo_output or "claude" in echo_output.lower()
        assert ".claude" in echo_output or "agents" in echo_output
        assert "agent1.md" in echo_output
        assert "agent2.md" in echo_output

    @patch("pantheon.cli.click.echo")
    def test_display_platform_result_shows_opencode_platform_name(
        self, mock_echo, cli_with_mocks, opencode_platform_config
    ):
        """Test display method shows 'OpenCode' platform name in output."""
        # Arrange
        results = {
            "installed": 3,
            "skipped": 0,
            "failed": 0,
            "installed_files": ["agent1.md", "agent2.md", "agent3.md"],
        }
        selected_team = "test-team"

        # Act
        cli_with_mocks._display_platform_agent_installation_result(
            results, selected_team, opencode_platform_config
        )

        # Assert - verify output contains OpenCode platform name and directory
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        echo_output = " ".join(echo_calls)

        assert "OpenCode" in echo_output or "opencode" in echo_output.lower()
        assert ".opencode" in echo_output or "agent" in echo_output

    @patch("pantheon.cli.click.confirm")
    def test_refactored_claude_installation_maintains_behavior(
        self, mock_confirm, cli_with_mocks, mock_dependencies, mock_agent_files
    ):
        """Test refactored Claude installation produces identical results to original."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.side_effect = [
            True,  # agents dir exists
            False,  # agent1.md destination doesn't exist
            False,  # agent2.md destination doesn't exist
            False,  # agent3.md destination doesn't exist
        ]
        mock_fs.glob.return_value = mock_agent_files
        mock_fs.read_text.return_value = "# Agent content"
        mock_confirm.return_value = True  # User confirms installation
        project_root = Path("/project")
        selected_team = "test-team"
        selected_team_dir = Path("/teams/test-team")

        # Act
        with patch.object(cli_with_mocks, "_display_agent_installation_result"):
            cli_with_mocks._prompt_claude_agent_installation(
                selected_team, selected_team_dir, project_root
            )

        # Assert - verify files written to .claude/agents/test-team/
        assert mock_fs.write_text.call_count == 3
        write_calls = [call[0][0] for call in mock_fs.write_text.call_args_list]

        for agent_file in mock_agent_files:
            expected_path = (
                project_root / ".claude" / "agents" / selected_team / agent_file.name
            )
            assert any(
                str(expected_path) in str(write_call) for write_call in write_calls
            ), f"Expected write to {expected_path}"

    @patch("pantheon.cli.click.confirm")
    @patch("pantheon.cli.click.echo")
    def test_opencode_installation_uses_singular_agent_directory(
        self,
        mock_echo,
        mock_confirm,
        cli_with_mocks,
        mock_dependencies,
        mock_agent_files,
    ):
        """Test OpenCode installation uses '.opencode/agent' (singular) directory."""
        # Arrange
        mock_fs = mock_dependencies["filesystem"]
        mock_fs.exists.side_effect = [
            True,  # agents dir exists
            False,  # agent1.md destination doesn't exist
            False,  # agent2.md destination doesn't exist
            False,  # agent3.md destination doesn't exist
        ]
        mock_fs.glob.return_value = mock_agent_files
        mock_fs.read_text.return_value = "# Agent content"
        mock_confirm.return_value = True  # User confirms installation
        project_root = Path("/project")
        selected_team = "test-team"
        selected_team_dir = Path("/teams/test-team")

        # Act
        cli_with_mocks._prompt_opencode_agent_installation(
            selected_team, selected_team_dir, project_root
        )

        # Assert - verify files written to .opencode/agent/test-team/ (singular 'agent')
        assert mock_fs.write_text.call_count == 3
        write_calls = [call[0][0] for call in mock_fs.write_text.call_args_list]

        for agent_file in mock_agent_files:
            expected_path = (
                project_root / ".opencode" / "agent" / selected_team / agent_file.name
            )
            assert any(
                str(expected_path) in str(write_call) for write_call in write_calls
            ), f"Expected write to {expected_path}"

            # Verify it's NOT using plural 'agents'
            for write_call in write_calls:
                assert ".opencode/agents" not in str(write_call), (
                    "Should use singular 'agent' not plural 'agents'"
                )
