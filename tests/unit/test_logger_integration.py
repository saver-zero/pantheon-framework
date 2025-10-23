"""
Integration tests for the centralized logging module.
"""

from io import StringIO

from pantheon import Log
from pantheon.logger import Log as DirectLog
from pantheon.logger import configure_logger


class TestLoggerFrameworkIntegration:
    """Test logger integration with the framework's public API."""

    def test_log_import_from_pantheon_package(self):
        """Test that Log can be imported from pantheon package."""
        # Log should be importable from the main package
        assert Log is not None
        assert hasattr(Log, "info")
        assert hasattr(Log, "debug")
        assert hasattr(Log, "warning")
        assert hasattr(Log, "error")

    def test_log_same_instance_from_different_imports(self):
        """Test that Log is the same instance when imported from different paths."""
        # Import from main package
        from pantheon import Log as PackageLog

        # Import directly from logger module
        from pantheon.logger import Log as ModuleLog

        # All should be the same instance
        assert PackageLog is ModuleLog
        assert PackageLog is Log
        assert PackageLog is DirectLog

    def test_log_functionality_through_package_import(self):
        """Test that logger works when imported through main package."""
        configure_logger("INFO")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out

        # Use logger imported from main package
        Log.info("Integration test message")
        output = fake_out.getvalue()

        assert "Integration test message" in output
        assert "INFO" in output
        assert "pantheon" in output

    def test_log_configuration_affects_all_imports(self):
        """Test that configuring the logger affects all import paths."""
        # Configure through direct import
        configure_logger("DEBUG")
        fake_out = StringIO()
        DirectLog.handlers[0].stream = fake_out

        # Log through package import
        Log.debug("Debug message from package import")
        output = fake_out.getvalue()

        assert "Debug message from package import" in output
        assert "DEBUG" in output

    def test_multiple_modules_same_logger_instance(self):
        """Test that multiple modules get the same logger instance."""
        configure_logger("WARNING")
        fake_out = StringIO()

        # Simulate multiple modules importing the logger
        def module_a_function():
            from pantheon import Log as LogA

            LogA.handlers[0].stream = fake_out
            LogA.warning("Message from module A")
            return LogA

        def module_b_function():
            from pantheon.logger import Log as LogB

            LogB.warning("Message from module B")
            return LogB

        log_a = module_a_function()
        log_b = module_b_function()

        # Both should be the same instance
        assert log_a is log_b
        assert log_a is Log

        output = fake_out.getvalue()
        assert "Message from module A" in output
        assert "Message from module B" in output

    def test_logger_works_without_explicit_configuration(self):
        """Test that logger works immediately after import without configuration."""
        # Reset to default configuration
        configure_logger()
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out

        # Should work immediately with default INFO level
        Log.info("Default configuration message")
        Log.debug("Debug message should not appear")

        output = fake_out.getvalue()
        assert "Default configuration message" in output
        assert "Debug message should not appear" not in output

    def test_cross_module_level_consistency(self):
        """Test that log level is consistent across all import methods."""
        # Set to ERROR level
        configure_logger("ERROR")
        fake_out = StringIO()
        Log.handlers[0].stream = fake_out

        # Test through different import paths
        Log.info("Info from package import")  # Should not appear
        DirectLog.warning("Warning from direct import")  # Should not appear
        Log.error("Error from package import")  # Should appear

        from pantheon import Log as AnotherImport

        AnotherImport.error("Error from another import")  # Should appear

        output = fake_out.getvalue()
        assert "Info from package import" not in output
        assert "Warning from direct import" not in output
        assert "Error from package import" in output
        assert "Error from another import" in output
