"""Test data builders for creating consistent test fixtures.

This module provides helper functions to create properly typed test data structures
including ProcessInput, ProcessResult, and mock workspace configurations. These
builders ensure consistency across all tests and reduce duplication.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessInput, ProcessResult
from pantheon.workspace import PantheonWorkspace
from tests.helpers.process_input import make_process_input


def build_process_input(
    process: str = "test-process",
    actor: str = "test-actor",
    input_params: dict[str, Any] | None = None,
    framework_params: dict[str, Any] | None = None,
) -> ProcessInput:
    """Build a valid ProcessInput TypedDict for testing.

    Args:
        process: Process name
        actor: Actor name
        input_params: User-provided parameters dict
        framework_params: Framework parameter overrides

    Returns:
        ProcessInput: Properly typed process input structure
    """
    if input_params is None:
        input_params = {"key": "value"}

    return make_process_input(
        process,
        actor,
        input_params=input_params,
        framework_params=framework_params,
    )


def build_process_result(
    success: bool = True,
    output: str = "Test output",
    error: str | None = None,
    artifact_created: PantheonPath | None = None,
) -> ProcessResult:
    """Build a ProcessResult with default values for testing.

    Args:
        success: Whether process succeeded
        output: Process output message
        error: Error message if failed
        artifact_created: Created artifact path

    Returns:
        ProcessResult: Properly typed process result structure
    """
    return {
        "success": success,
        "output": output,
        "error": error,
        "artifact_created": artifact_created,
    }


def mock_workspace_with_agents(agents: list[str] | None = None) -> Mock:
    """Create a configured mock workspace with agents.

    Args:
        agents: List of agent names to return

    Returns:
        Mock: Configured PantheonWorkspace mock
    """
    if agents is None:
        agents = ["test-actor", "another-actor"]

    mock_workspace = Mock(spec=PantheonWorkspace)
    mock_workspace.get_permissions.return_value = '{"allow": ["test-actor"]}'
    mock_workspace.get_process_schema.return_value = SAMPLE_SCHEMA_CONTENT
    mock_workspace.get_team_profile.return_value = SAMPLE_PROFILE_CONTENT
    mock_workspace.get_artifact_content_template.return_value = SAMPLE_TEMPLATE_CONTENT
    mock_workspace.get_artifact_directory_template.return_value = "artifacts/"
    mock_workspace.get_artifact_filename_template.return_value = (
        "{{process}}_{{timestamp}}.md"
    )

    return mock_workspace


def mock_workspace_with_permissions(
    allow: list[str] | None = None, deny: list[str] | None = None
) -> Mock:
    """Create a configured mock workspace with specific permissions.

    Args:
        allow: List of allowed actors
        deny: List of denied actors

    Returns:
        Mock: Configured PantheonWorkspace mock with permissions
    """
    mock_workspace = Mock(spec=PantheonWorkspace)

    # Build permissions JSON
    permissions = {}
    if allow:
        permissions["allow"] = allow
    if deny:
        permissions["deny"] = deny

    import json

    mock_workspace.get_permissions.return_value = json.dumps(permissions)

    return mock_workspace


# Sample test data constants
SAMPLE_SCHEMA_CONTENT = """{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "description": {"type": "string"}
  },
  "required": ["title"]
}"""

SAMPLE_PROFILE_CONTENT = """
active_profile: development
profiles:
  development:
    verbosity: detailed
    enforce_tdd: true
"""

SAMPLE_TEMPLATE_CONTENT = """# {{title}}

{{description}}

Created by: {{actor}}
Date: {{timestamp}}
"""

SAMPLE_COMPILED_SCHEMA = {
    "type": "object",
    "properties": {"title": {"type": "string"}, "description": {"type": "string"}},
    "required": ["title"],
}

SAMPLE_ARTIFACT_SECTIONS = {
    "title": "Test Artifact",
    "description": "This is a test artifact description",
    "status": "active",
}

SAMPLE_ROUTINE_CONTENT = """# Test Process Routine

## Objective
This is a test process routine for unit testing.

## Steps
1. Validate input parameters
2. Process the request
3. Generate output
"""


def create_temp_json_file(data: dict[str, Any], tmp_path: Path) -> Path:
    """Create a temporary JSON file with test data.

    Args:
        data: Data to write to JSON file
        tmp_path: Temporary directory path

    Returns:
        Path: Path to created JSON file
    """
    import json

    json_file = tmp_path / "test_input.json"
    json_file.write_text(json.dumps(data, indent=2))
    return json_file


def build_cli_test_input(
    process_name: str = "test-process",
    actor: str = "test-actor",
    input_params: dict[str, Any] | None = None,
    framework_params: dict[str, Any] | None = None,
    from_file: Path | None = None,
) -> dict[str, Any]:
    """Build input data for CLI command testing.

    Args:
        process_name: Process to execute
        actor: Actor performing the action
        input_params: Process input parameters
        framework_params: Framework parameter overrides
        from_file: Optional file path for --from-file

    Returns:
        Dict: CLI test input configuration
    """
    if input_params is None:
        input_params = {"key": "value", "number": 42}
    if framework_params is None:
        framework_params = {}

    return {
        "process_name": process_name,
        "actor": actor,
        "input_params": input_params,
        "framework_params": framework_params,
        "from_file": from_file,
    }
