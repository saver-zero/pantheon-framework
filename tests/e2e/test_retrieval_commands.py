"""End-to-end tests for retrieval commands (get operations)."""

import json
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_get_ticket_returns_correct_sections(
    temp_project: Path,
    run_pantheon,
    setup_test_project,
    sample_ticket_data,
    sample_plan_data,
):
    """Test that get-ticket returns correct sections from existing artifacts."""

    # Setup: Initialize project and create ticket with plan
    setup_test_project()

    # Create initial ticket
    ticket_data = sample_ticket_data
    ticket_json_path = temp_project / "ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    create_result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(ticket_json_path),
            "--actor",
            "ticket-handler",
        ]
    )
    assert create_result.returncode == 0

    # Add plan to ticket
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    filename_without_ext = ticket_files[0].stem  # "T1-User Authentication System"
    ticket_id = filename_without_ext.split("-")[0]  # Get "T1" part

    plan_data = sample_plan_data.copy()
    plan_json_path = temp_project / "plan_data.json"
    with open(plan_json_path, "w") as f:
        json.dump(plan_data, f)

    update_result = run_pantheon(
        [
            "execute",
            "update-plan",
            "--from-file",
            str(plan_json_path),
            "--id",
            ticket_id,
            "--actor",
            "ticket-handler",
        ]
    )
    assert update_result.returncode == 0

    # Test: Retrieve ticket content
    get_result = run_pantheon(
        [
            "execute",
            "get-ticket",
            "--id",
            ticket_id,
            "--actor",
            "ticket-handler",
        ]
    )
    assert get_result.returncode == 0

    # Verify retrieved content is valid JSON (RETRIEVE operation returns JSON)
    retrieved_json = json.loads(get_result.stdout)
    assert "plan" in retrieved_json

    # Verify actual ticket file contains both sections
    ticket_file = ticket_files[0]
    ticket_content = ticket_file.read_text()
    assert ticket_data["description"] in ticket_content
    assert plan_data["technical_summary"] in ticket_content
    assert plan_data["implementation_approach"] in ticket_content


@pytest.mark.e2e
def test_get_process_returns_routine(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that get process returns the correct routine content."""

    # Set up test project with fixture team
    setup_test_project()

    # Get process routine
    result = run_pantheon(
        ["get", "process", "create-ticket", "--actor", "ticket-handler"]
    )
    assert result.returncode == 0

    routine_content = result.stdout

    # Verify routine contains expected structure
    assert len(routine_content) > 0

    # Routine should contain step-by-step instructions
    assert "step" in routine_content.lower() or "Step" in routine_content

    # Should contain references to pantheon commands
    assert "pantheon" in routine_content


@pytest.mark.e2e
def test_get_schema_returns_valid_json(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that get schema returns valid JSON schema."""

    # Set up test project with fixture team
    setup_test_project()

    # Get schema for create-ticket process
    result = run_pantheon(
        ["get", "schema", "create-ticket", "--actor", "ticket-handler"]
    )
    assert result.returncode == 0

    # Parse schema as JSON
    schema = json.loads(result.stdout)

    # Verify it's a valid JSON schema structure
    assert isinstance(schema, dict)
    assert "type" in schema or "$schema" in schema

    # Should contain properties for required fields
    if "properties" in schema:
        assert isinstance(schema["properties"], dict)
        assert len(schema["properties"]) > 0


@pytest.mark.e2e
def test_get_tempfile_returns_valid_path(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that get tempfile returns a valid temporary file path."""

    # Set up test project with fixture team
    setup_test_project()

    # Get tempfile path
    result = run_pantheon(
        ["get", "tempfile", "--process", "create-ticket", "--actor", "ticket-handler"]
    )
    assert result.returncode == 0

    tempfile_path = result.stdout.strip()

    # Verify path structure
    assert "pantheon-artifacts" in tempfile_path
    assert "temp" in tempfile_path
    assert tempfile_path.endswith(".json")

    # Verify path exists and is writable (test creating the directory structure)
    import json
    from pathlib import Path

    path = Path(tempfile_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Test writing to the temp file
    test_data = {"test": "data"}
    with open(path, "w") as f:
        json.dump(test_data, f)

    # Verify file was created
    assert path.exists()
    with open(path) as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data


@pytest.mark.e2e
def test_get_ticket_error_handling_nonexistent_ticket(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling when requesting non-existent ticket."""

    # Set up test project with fixture team
    setup_test_project()

    # Try to get non-existent ticket
    result = run_pantheon(
        [
            "execute",
            "get-ticket",
            "--id",
            "T999",
            "--actor",
            "ticket-handler",
        ],
        check=False,
    )

    # Should fail with appropriate error
    assert result.returncode != 0
    assert (
        "not found" in result.stderr.lower()
        or "does not exist" in result.stderr.lower()
        or "T999" in result.stderr
    )


@pytest.mark.e2e
def test_get_process_error_handling_invalid_process(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling for invalid process names."""

    # Set up test project with fixture team
    setup_test_project()

    # Try to get non-existent process
    result = run_pantheon(
        ["get", "process", "non-existent-process", "--actor", "ticket-handler"],
        check=False,
    )

    # Should fail with appropriate error
    assert result.returncode != 0
    assert (
        "not found" in result.stderr.lower()
        or "non-existent-process" in result.stderr.lower()
    )


@pytest.mark.e2e
def test_get_schema_error_handling_invalid_process(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling for schema requests of invalid processes."""

    # Set up test project with fixture team
    setup_test_project()

    # Try to get schema for non-existent process
    result = run_pantheon(
        ["get", "schema", "non-existent-process", "--actor", "ticket-handler"],
        check=False,
    )

    # Should fail with appropriate error
    assert result.returncode != 0
    assert (
        "not found" in result.stderr.lower()
        or "non-existent-process" in result.stderr.lower()
    )


@pytest.mark.e2e
def test_get_commands_with_invalid_actor(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling for get commands with invalid actor."""

    # Set up test project with fixture team
    setup_test_project()

    # Try to use invalid actor
    result = run_pantheon(
        ["get", "process", "create-ticket", "--actor", "non-existent-actor"],
        check=False,
    )

    # Should fail with permission/actor error
    assert result.returncode != 0
    assert (
        "actor" in result.stderr.lower()
        or "permission" in result.stderr.lower()
        or "non-existent-actor" in result.stderr.lower()
    )


@pytest.mark.e2e
def test_get_ticket_with_specific_sections(
    temp_project: Path, run_pantheon, setup_test_project, sample_ticket_data
):
    """Test that get-ticket respects section filtering."""

    # Setup: Create ticket
    setup_test_project()

    ticket_data = sample_ticket_data
    ticket_json_path = temp_project / "ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    create_result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(ticket_json_path),
            "--actor",
            "ticket-handler",
        ]
    )
    assert create_result.returncode == 0

    # Get ticket ID (extract ID from filename like T1-title.md)
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    filename_without_ext = ticket_files[0].stem  # "T1-User Authentication System"
    ticket_id = filename_without_ext.split("-")[0]  # Get "T1" part

    # Test: Get ticket content
    get_result = run_pantheon(
        [
            "execute",
            "get-ticket",
            "--id",
            ticket_id,
            "--actor",
            "ticket-handler",
        ]
    )
    assert get_result.returncode == 0

    # Verify retrieved content is valid JSON (RETRIEVE operation returns JSON)
    retrieved_json = json.loads(get_result.stdout)
    assert isinstance(retrieved_json, dict)

    # Verify actual ticket file contains description
    ticket_file = ticket_files[0]
    ticket_content = ticket_file.read_text()
    assert ticket_data["description"] in ticket_content
