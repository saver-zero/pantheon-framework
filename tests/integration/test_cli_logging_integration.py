"""Integration tests for CLI logging configuration.

This module contains integration tests that verify the logging configuration
system works correctly with Click command parsing and help text generation.
"""

from click.testing import CliRunner
import pytest

from pantheon.cli import main


class TestCLILoggingIntegration:
    """Integration tests for CLI logging configuration."""

    def test_help_text_includes_logging_options(self) -> None:
        """Test that --help shows logging options with proper descriptions."""
        runner = CliRunner()

        # Act
        result = runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "--log-level" in result.output
        assert "--debug" in result.output
        assert "Set log level" in result.output
        assert "Enable debug logging" in result.output
        # Click shows choices in lowercase
        assert "debug" in result.output
        assert "info" in result.output
        assert "warning" in result.output
        assert "error" in result.output

    def test_log_level_flag_parsing(self) -> None:
        """Test that --log-level flag is properly parsed by Click."""
        runner = CliRunner()

        # Act - test flag parsing with --help to avoid project discovery issues
        result = runner.invoke(main, ["--log-level", "DEBUG", "--help"])

        # Assert - should parse flag successfully and show help
        assert result.exit_code == 0
        assert "--log-level" in result.output

    def test_debug_flag_parsing(self) -> None:
        """Test that --debug flag is properly parsed by Click."""
        runner = CliRunner()

        # Act - test flag parsing with --help to avoid project discovery issues
        result = runner.invoke(main, ["--debug", "--help"])

        # Assert - should parse flag successfully and show help
        assert result.exit_code == 0
        assert "--debug" in result.output

    def test_both_logging_flags_parsing(self) -> None:
        """Test that both --log-level and --debug flags work together."""
        runner = CliRunner()

        # Act - test both flags with --help to avoid project discovery issues
        result = runner.invoke(main, ["--debug", "--log-level", "ERROR", "--help"])

        # Assert - should parse both flags successfully and show help
        assert result.exit_code == 0
        assert "--log-level" in result.output
        assert "--debug" in result.output

    def test_invalid_log_level_shows_error(self) -> None:
        """Test that invalid --log-level values are rejected by Click."""
        runner = CliRunner()

        # Act - invalid log level should fail before --help is processed
        result = runner.invoke(main, ["--log-level", "INVALID"])

        # Assert - Click should show error for invalid choice
        assert result.exit_code != 0
        assert (
            "Invalid value" in result.output
            or "invalid choice" in result.output.lower()
            or "INVALID" in result.output
        )

    @pytest.mark.parametrize(
        "log_level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "debug", "info", "warning", "error"],
    )
    def test_valid_log_levels_accepted(self, log_level: str) -> None:
        """Test that all valid log level values are accepted by Click."""
        runner = CliRunner()

        # Act - test valid log levels with --help to avoid project discovery issues
        result = runner.invoke(main, ["--log-level", log_level, "--help"])

        # Assert - should not error on valid log levels
        assert result.exit_code == 0
        assert "--log-level" in result.output


class TestCLILoggingConfiguration:
    """Integration tests for logging configuration functionality."""

    def test_help_command_shows_logging_options(self) -> None:
        """Test that help command consistently shows logging options."""
        runner = CliRunner()

        # Act
        result = runner.invoke(main, ["--help"])

        # Assert - verify the help shows our new logging options
        assert result.exit_code == 0
        assert "--log-level" in result.output
        assert "--debug" in result.output
        # Check for partial text that spans lines in the help output
        assert "overrides project" in result.output
        assert "shorthand for" in result.output
