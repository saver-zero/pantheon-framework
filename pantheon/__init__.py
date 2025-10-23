"""Pantheon Framework - Operating System for Containerized AI Teams.

The Pantheon Framework applies the Retrieval-Augmented Execution (RAE) pattern
to solve prompt drift and output inconsistency in AI agent orchestration.
"""

__version__ = "0.1.0"

# Import core abstractions
from .cli import CLI
from .filesystem import FileSystem
from .logger import Log
from .path import PantheonPath
from .process_handler import ProcessHandler
from .rae_engine import RaeEngine

# Core exports - foundational abstractions for the framework
__all__ = [
    "__version__",
    "CLI",
    "FileSystem",
    "Log",
    "PantheonPath",
    "ProcessHandler",
    "RaeEngine",
]
