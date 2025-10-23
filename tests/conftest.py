"""Shared pytest fixtures for Pantheon Framework tests."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root directory for testing."""
    return tmp_path


@pytest.fixture
def mock_filesystem():
    """Create a mock filesystem for dependency injection in tests."""
    return Mock()
