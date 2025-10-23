"""
Centralized logging module for the Pantheon framework.

This module provides a singleton-like logger instance that can be imported
and used throughout the framework without requiring individual logger instantiation.
"""

import logging
import sys

# The module-level instance, which acts as our singleton.
Log: logging.Logger = logging.getLogger("pantheon")


def configure_logger(level: str = "INFO") -> None:
    """
    Configures the root pantheon logger.
    This function should only be called once at application startup.

    Args:
        level: The log level as a string (DEBUG, INFO, WARNING, ERROR)
    """
    # Validate and set log level, fallback to INFO for invalid levels
    log_level = getattr(logging, level.upper(), logging.INFO)
    Log.setLevel(log_level)

    # Clear existing handlers to prevent duplicates on multiple calls
    Log.handlers.clear()

    # Prevent propagation to avoid pytest capturing in tests
    Log.propagate = False

    # Create and configure StreamHandler for stderr (not stdout)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    Log.addHandler(handler)


# Initialize with a default level. This can be reconfigured by the CLI.
configure_logger()
