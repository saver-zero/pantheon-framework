"""
Unit tests for the centralized logging module.
"""

from io import StringIO
import logging
from unittest.mock import patch

from pantheon.logger import Log, configure_logger


class TestLoggerInstance:
    """Test the module-level Log instance."""

    def test_log_instance_exists(self):
        """Test that Log instance is available for import."""
        assert Log is not None
        assert isinstance(Log, logging.Logger)
        assert Log.name == "pantheon"

    def test_log_info_method(self):
        """Test that Log.info() works correctly."""
        # This will fail initially due to no handler configuration
        with patch("sys.stdout", new=StringIO()):
            Log.info("Test info message")
            # We expect this to work once implemented

    def test_log_debug_method(self):
        """Test that Log.debug() works correctly."""
        with patch("sys.stdout", new=StringIO()):
            Log.debug("Test debug message")

    def test_log_warning_method(self):
        """Test that Log.warning() works correctly."""
        with patch("sys.stdout", new=StringIO()):
            Log.warning("Test warning message")

    def test_log_error_method(self):
        """Test that Log.error() works correctly."""
        with patch("sys.stdout", new=StringIO()):
            Log.error("Test error message")


class TestConfigureLogger:
    """Test the configure_logger function."""

    def test_configure_logger_exists(self):
        """Test that configure_logger function exists and is callable."""
        assert callable(configure_logger)

    def test_configure_logger_default_info_level(self):
        """Test configure_logger with default INFO level."""
        configure_logger()
        assert Log.level == logging.INFO

    def test_configure_logger_with_debug_level(self):
        """Test configure_logger with DEBUG level."""
        configure_logger("DEBUG")
        assert Log.level == logging.DEBUG

    def test_configure_logger_with_warning_level(self):
        """Test configure_logger with WARNING level."""
        configure_logger("WARNING")
        assert Log.level == logging.WARNING

    def test_configure_logger_with_error_level(self):
        """Test configure_logger with ERROR level."""
        configure_logger("ERROR")
        assert Log.level == logging.ERROR

    def test_configure_logger_with_invalid_level(self):
        """Test configure_logger with invalid level falls back to INFO."""
        configure_logger("INVALID")
        assert Log.level == logging.INFO

    def test_configure_logger_multiple_calls_no_duplicate_handlers(self):
        """Test that multiple configure_logger calls don't create duplicate handlers."""
        configure_logger("INFO")
        initial_handler_count = len(Log.handlers)
        configure_logger("DEBUG")
        assert len(Log.handlers) == initial_handler_count

    def test_configure_logger_case_insensitive(self):
        """Test that configure_logger handles case insensitive level strings."""
        configure_logger("info")
        assert Log.level == logging.INFO
        configure_logger("Debug")
        assert Log.level == logging.DEBUG


class TestLoggerFormatting:
    """Test logger message formatting."""

    def test_log_message_format_includes_timestamp(self):
        """Test that log messages include timestamp."""
        configure_logger("INFO")
        # Capture the handler's stream directly
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.info("Test message")
        output = fake_out.getvalue()
        # Check for timestamp format (YYYY-MM-DD HH:MM:SS,mmm)
        assert " - " in output
        # Basic check that it looks like a timestamp at the beginning
        assert output.split(" - ")[0].count(":") == 2

    def test_log_message_format_includes_module_name(self):
        """Test that log messages include module name."""
        configure_logger("INFO")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.info("Test message")
        output = fake_out.getvalue()
        assert "pantheon" in output

    def test_log_message_format_includes_level(self):
        """Test that log messages include log level."""
        configure_logger("INFO")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.info("Test message")
        output = fake_out.getvalue()
        assert "INFO" in output

    def test_log_message_format_includes_message_content(self):
        """Test that log messages include the actual message content."""
        configure_logger("INFO")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        test_message = "This is a test message"
        Log.info(test_message)
        output = fake_out.getvalue()
        assert test_message in output


class TestLoggerIntegration:
    """Test logger integration scenarios."""

    def test_logger_works_without_configuration(self):
        """Test that logger works with default settings without explicit configuration."""
        # The logger is initialized with default configuration on import
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.info("Default configuration test")
        output = fake_out.getvalue()
        assert "Default configuration test" in output
        assert "INFO" in output

    def test_same_logger_instance_across_imports(self):
        """Test that the same logger instance is returned across different imports."""
        from pantheon.logger import Log as Log1
        from pantheon.logger import Log as Log2

        assert Log1 is Log2
        assert Log1 is Log

    def test_logger_singleton_behavior(self):
        """Test that the logger behaves as a singleton."""
        import pantheon.logger

        assert pantheon.logger.Log is Log
        assert id(pantheon.logger.Log) == id(Log)


class TestLoggerLevels:
    """Test different logging levels behavior."""

    def test_info_level_shows_info_and_above(self):
        """Test that INFO level shows INFO, WARNING, ERROR but not DEBUG."""
        configure_logger("INFO")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.debug("Debug message")
        Log.info("Info message")
        Log.warning("Warning message")
        Log.error("Error message")
        output = fake_out.getvalue()

        # DEBUG should not appear, others should
        assert "Debug message" not in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output

    def test_debug_level_shows_all_messages(self):
        """Test that DEBUG level shows all message types."""
        configure_logger("DEBUG")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.debug("Debug message")
        Log.info("Info message")
        Log.warning("Warning message")
        Log.error("Error message")
        output = fake_out.getvalue()

        # All messages should appear
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output

    def test_warning_level_shows_warning_and_above(self):
        """Test that WARNING level shows WARNING, ERROR but not INFO, DEBUG."""
        configure_logger("WARNING")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.debug("Debug message")
        Log.info("Info message")
        Log.warning("Warning message")
        Log.error("Error message")
        output = fake_out.getvalue()

        # Only WARNING and ERROR should appear
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" in output
        assert "Error message" in output

    def test_error_level_shows_only_error(self):
        """Test that ERROR level shows only ERROR messages."""
        configure_logger("ERROR")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out
        Log.debug("Debug message")
        Log.info("Info message")
        Log.warning("Warning message")
        Log.error("Error message")
        output = fake_out.getvalue()

        # Only ERROR should appear
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" not in output
        assert "Error message" in output
