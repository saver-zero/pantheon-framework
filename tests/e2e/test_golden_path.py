"""End-to-end tests for the complete golden path workflow."""

import json
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_golden_path_workflow(
    temp_project: Path,
    run_pantheon,
    setup_test_project,
    sample_ticket_data,
    sample_plan_data,
):
    """Test the complete workflow: setup -> create-ticket -> update-plan -> get-ticket."""

    # Phase 1: Set up test project with fixture team
    project_info = setup_test_project()
    assert project_info["team_name"] == "pantheon-e2e-test"

    # Phase 2: Create a ticket
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

    # Verify ticket was created in artifacts directory
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    assert len(ticket_files) >= 1

    ticket_file = ticket_files[0]
    ticket_content = ticket_file.read_text()

    # Verify ticket contains expected content
    assert ticket_data["description"] in ticket_content
    assert ticket_data["plan"] in ticket_content

    # Phase 3: Update the ticket with a plan
    plan_data = sample_plan_data.copy()  # Make a copy to avoid modifying the fixture
    # Extract ticket ID (T1 from T1-title.md)
    filename_without_ext = ticket_file.stem  # "T1-User Authentication System"
    ticket_id = filename_without_ext.split("-")[0]  # Extract "T1" part

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

    # Verify plan was added to ticket
    updated_content = ticket_file.read_text()
    assert plan_data["technical_summary"] in updated_content
    assert plan_data["implementation_approach"] in updated_content

    # Phase 4: Retrieve ticket content
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

    # Verify actual ticket file contains both original and updated sections
    assert ticket_data["description"] in updated_content
    assert plan_data["technical_summary"] in updated_content


@pytest.mark.e2e
def test_artifact_file_structure(
    temp_project: Path, run_pantheon, setup_test_project, sample_ticket_data
):
    """Test that artifacts are created with correct file structure and naming."""

    # Set up test project with fixture team
    setup_test_project()

    ticket_data = sample_ticket_data
    ticket_json_path = temp_project / "ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(ticket_json_path),
            "--actor",
            "ticket-handler",
        ]
    )
    assert result.returncode == 0

    # Verify artifact structure
    artifacts_dir = temp_project / "pantheon-artifacts"
    assert artifacts_dir.exists()

    # Find created ticket file
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    assert len(ticket_files) >= 1

    ticket_file = ticket_files[0]

    # Verify file naming follows convention (e.g., T001_implement-user-authentication.md)
    assert ticket_file.name.startswith("T")
    assert ticket_file.suffix == ".md"

    # Verify directory structure (should be in tickets subdirectory)
    assert "tickets" in str(ticket_file.parent)


@pytest.mark.e2e
def test_tempfile_operations(temp_project: Path, run_pantheon, setup_test_project):
    """Test that temporary file operations work correctly."""

    # Set up test project with fixture team
    setup_test_project()

    # Test tempfile generation
    tempfile_result = run_pantheon(
        ["get", "tempfile", "--process", "create-ticket", "--actor", "ticket-handler"]
    )
    assert tempfile_result.returncode == 0

    # Verify tempfile path is in artifacts/temp directory
    tempfile_path = tempfile_result.stdout.strip()
    assert "pantheon-artifacts" in tempfile_path
    assert "temp" in tempfile_path
    assert tempfile_path.endswith(".json")


@pytest.mark.e2e
def test_process_schema_retrieval(temp_project: Path, run_pantheon, setup_test_project):
    """Test that process schemas can be retrieved correctly."""

    # Set up test project with fixture team
    setup_test_project()

    # Test schema retrieval
    schema_result = run_pantheon(
        ["get", "schema", "create-ticket", "--actor", "ticket-handler"]
    )
    assert schema_result.returncode == 0

    # Verify schema is valid JSON
    schema_json = json.loads(schema_result.stdout)
    assert isinstance(schema_json, dict)
    assert "$schema" in schema_json or "type" in schema_json


@pytest.mark.e2e
def test_process_routine_retrieval(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that process routines can be retrieved correctly."""

    # Set up test project with fixture team
    setup_test_project()

    # Test routine retrieval
    routine_result = run_pantheon(
        ["get", "process", "create-ticket", "--actor", "ticket-handler"]
    )
    assert routine_result.returncode == 0

    # Verify routine content is markdown-formatted
    routine_content = routine_result.stdout
    assert len(routine_content) > 0
    assert "Step" in routine_content or "step" in routine_content
