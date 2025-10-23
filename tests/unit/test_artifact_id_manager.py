"""
Simple unit tests for ArtifactId functionality.

Tests the core artifact ID generation operations without unnecessary complexity.
"""

import json
from unittest.mock import MagicMock

import pytest

from pantheon.artifact_id_manager import ArtifactId


class TestArtifactId:
    """Test suite for ArtifactId core functionality."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock PantheonWorkspace for testing."""
        workspace = MagicMock()
        workspace._project_config = {"active_team": "test-team"}
        workspace.read_artifact_id.return_value = ""
        workspace.save_artifact_id = MagicMock()
        return workspace

    @pytest.fixture
    def artifact_id(self, mock_workspace):
        """Create ArtifactId instance for testing."""
        return ArtifactId(mock_workspace)

    def test_init_sets_workspace(self, artifact_id, mock_workspace):
        """Test ArtifactId initialization sets workspace dependency."""
        assert artifact_id._workspace is mock_workspace

    def test_get_next_count_starts_from_one(self, artifact_id):
        """Test get_next_count returns 1 for new process."""
        # Setup: empty artifact ID content
        artifact_id._workspace.read_artifact_id.return_value = ""

        # Execute
        result = artifact_id.get_next_count("process1")

        # Verify
        assert result == 1
        artifact_id._workspace.save_artifact_id.assert_called_once()

    def test_get_next_count_increments_existing_value(self, artifact_id):
        """Test get_next_count increments existing artifact ID value."""
        # Setup: artifact ID content with existing value
        artifact_id_content = json.dumps({"test-team": {"process1": 5}})
        artifact_id._workspace.read_artifact_id.return_value = artifact_id_content

        # Execute
        result = artifact_id.get_next_count("process1")

        # Verify
        assert result == 6
        # Verify save was called with incremented value
        expected_content = json.dumps({"test-team": {"process1": 6}}, indent=2)
        artifact_id._workspace.save_artifact_id.assert_called_once_with(
            expected_content
        )

    def test_get_next_count_handles_invalid_artifact_id_data(self, artifact_id):
        """Test get_next_count handles invalid artifact ID data by reinitializing."""
        # Setup: invalid JSON content
        artifact_id._workspace.read_artifact_id.return_value = "invalid json"

        # Execute
        result = artifact_id.get_next_count("process1")

        # Verify: starts from 1 after reinitializing
        assert result == 1
        expected_content = json.dumps({"test-team": {"process1": 1}}, indent=2)
        artifact_id._workspace.save_artifact_id.assert_called_once_with(
            expected_content
        )

    def test_get_next_count_uses_default_team_when_no_active_team(self, artifact_id):
        """Test get_next_count falls back to 'default' team when no active_team configured."""
        # Setup: workspace config without active_team
        artifact_id._workspace._project_config = {}
        artifact_id._workspace.read_artifact_id.return_value = ""

        # Execute
        result = artifact_id.get_next_count("process1")

        # Verify: uses default team and starts at 1
        assert result == 1
        expected_content = json.dumps({"default": {"process1": 1}}, indent=2)
        artifact_id._workspace.save_artifact_id.assert_called_once_with(
            expected_content
        )

    def test_process_isolation_within_team(self, artifact_id):
        """Test that different processes maintain separate artifact IDs within the same team."""
        # Setup: existing artifact IDs for different processes
        artifact_id_content = json.dumps({"test-team": {"process1": 3, "process2": 7}})
        artifact_id._workspace.read_artifact_id.return_value = artifact_id_content

        # Execute: increment process1
        result1 = artifact_id.get_next_count("process1")

        # Verify: process1 incremented
        assert result1 == 4
        expected_content = json.dumps(
            {"test-team": {"process1": 4, "process2": 7}}, indent=2
        )
        artifact_id._workspace.save_artifact_id.assert_called_with(expected_content)

        # Reset for second call
        artifact_id._workspace.save_artifact_id.reset_mock()
        updated_content = json.dumps({"test-team": {"process1": 4, "process2": 7}})
        artifact_id._workspace.read_artifact_id.return_value = updated_content

        # Execute: increment process2
        result2 = artifact_id.get_next_count("process2")

        # Verify: process2 incremented independently
        assert result2 == 8
        expected_content2 = json.dumps(
            {"test-team": {"process1": 4, "process2": 8}}, indent=2
        )
        artifact_id._workspace.save_artifact_id.assert_called_with(expected_content2)

    def test_get_next_count_handles_corrupted_team_data(self, artifact_id):
        """Test get_next_count handles corrupted team data by reinitializing team."""
        # Setup: team data is not a dictionary
        artifact_id_content = json.dumps({"test-team": "corrupted_data"})
        artifact_id._workspace.read_artifact_id.return_value = artifact_id_content

        # Execute
        result = artifact_id.get_next_count("process1")

        # Verify: reinitializes team and starts from 1
        assert result == 1
        expected_content = json.dumps({"test-team": {"process1": 1}}, indent=2)
        artifact_id._workspace.save_artifact_id.assert_called_once_with(
            expected_content
        )

        # Verify: no exceptions raised (method completes successfully)
        # In current implementation, this is a no-op that just logs
