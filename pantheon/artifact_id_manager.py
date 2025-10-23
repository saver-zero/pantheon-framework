"""
Artifact ID generation module for framework-managed process IDs.

This module provides simple ID generation operations for artifacts,
ensuring unique sequential IDs per team/process combination without
requiring manual ID management by agents.
"""

import json
from typing import TYPE_CHECKING

from pantheon.logger import Log

if TYPE_CHECKING:
    from pantheon.workspace import PantheonWorkspace


class ArtifactId:
    """
    Manages simple ID operations for artifact generation.

    Provides framework-managed IDs that automatically increment and
    are available as {{artifact_id}} template variables. Simple implementation
    without locking - occasional race conditions are acceptable.
    """

    def __init__(self, workspace: "PantheonWorkspace") -> None:
        """
        Initialize ArtifactId with workspace dependency.

        Args:
            workspace: PantheonWorkspace instance for file operations

        The artifact ID file will be located at {artifacts_root}/.artifact_id.json
        using workspace methods for all file operations.
        """
        self._workspace = workspace

    def get_next_count(self, process_name: str) -> int:
        """
        Get the next artifact ID value for a process, incrementing automatically.

        Simple implementation that reads current value, increments by 1,
        and writes back to file. Team name is resolved from workspace config.

        Args:
            process_name: Name of the process (e.g., "create-ticket")

        Returns:
            The new artifact ID value (starting from 1)

        Raises:
            OSError: If file operations fail
        """
        try:
            # Get team name from workspace config
            team_name = self._workspace._project_config.get("active_team")
            if not team_name:
                Log.warning("No active_team in workspace config, using 'default'")
                team_name = "default"

            # Read current artifact ID data through workspace as plain text
            content = self._workspace.read_artifact_id()

            if not content.strip():
                artifact_id_data = {}
            else:
                try:
                    artifact_id_data = json.loads(content)
                    if not isinstance(artifact_id_data, dict):
                        Log.warning("Invalid artifact ID data, reinitializing")
                        artifact_id_data = {}
                except json.JSONDecodeError:
                    Log.warning(
                        "Artifact ID file contains invalid JSON, reinitializing"
                    )
                    artifact_id_data = {}

            # Initialize team structure if needed
            if team_name not in artifact_id_data:
                artifact_id_data[team_name] = {}
            elif not isinstance(artifact_id_data[team_name], dict):
                Log.warning(f"Team '{team_name}' data corrupted, reinitializing")
                artifact_id_data[team_name] = {}

            # Get current artifact ID and increment
            current_value = artifact_id_data[team_name].get(process_name, 0)
            new_value = current_value + 1
            artifact_id_data[team_name][process_name] = new_value

            # Save updated data through workspace as JSON string
            updated_json = json.dumps(artifact_id_data, indent=2)
            self._workspace.save_artifact_id(updated_json)

            Log.debug(f"Artifact ID for {team_name}/{process_name}: {new_value}")
            return new_value

        except Exception as e:
            Log.error(f"Failed to get next artifact ID for {process_name}: {e}")
            raise
