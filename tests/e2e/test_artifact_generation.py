"""End-to-end tests for artifact generation processes."""

import json
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_create_ticket_artifact_generation(
    temp_project: Path, run_pantheon, setup_test_project, sample_ticket_data
):
    """Test that create-ticket generates artifacts with correct content and location."""

    # Set up test project with fixture team
    setup_test_project()

    # Prepare ticket data
    ticket_data = sample_ticket_data
    ticket_json_path = temp_project / "ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    # Execute create-ticket
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

    # Verify artifact was created in correct location
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    assert len(ticket_files) >= 1

    ticket_file = ticket_files[0]
    content = ticket_file.read_text()

    # Verify content structure includes all required sections
    assert "# T" in content  # Title with ticket ID
    assert ticket_data["description"] in content
    assert ticket_data["plan"] in content

    # Verify section markers are present for future updates
    assert "PANTHEON:SECTION:" in content or "## " in content


@pytest.mark.e2e
def test_update_plan_modifies_existing_ticket(
    temp_project: Path,
    run_pantheon,
    setup_test_project,
    sample_ticket_data,
    sample_plan_data,
):
    """Test that update-plan modifies existing ticket with plan section."""

    # Set up test project with fixture team
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

    # Find created ticket
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    ticket_file = ticket_files[0]
    original_content = ticket_file.read_text()

    # Prepare plan data (no ticket_id needed since it's now a framework parameter)
    # For file "T1-User Authentication System.md", extract "T1" as artifact ID
    filename_without_ext = ticket_file.stem  # "T1-User Authentication System"
    ticket_id = filename_without_ext.split("-")[0]  # Extract "T1" part
    plan_data = sample_plan_data.copy()  # Make a copy to avoid modifying the fixture

    plan_json_path = temp_project / "plan_data.json"
    with open(plan_json_path, "w") as f:
        json.dump(plan_data, f)

    # Execute update-plan with --id flag
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

    # Verify ticket was updated
    updated_content = ticket_file.read_text()

    # Original content should still be present
    assert ticket_data["description"] in updated_content

    # New plan content should be added
    assert plan_data["technical_summary"] in updated_content
    assert plan_data["implementation_approach"] in updated_content

    # Content should be longer than original
    assert len(updated_content) > len(original_content)


@pytest.mark.e2e
def test_json_file_parameter_processing(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that --from-file parameter correctly processes JSON input."""

    # Set up test project with fixture team
    setup_test_project()

    # Create test data with various data types
    test_data = {
        "title": "Special Chars Test",
        "description": "Multi-line test description with newlines and special characters: <>&\"' that meets minimum character requirements",
        "plan": "Implementation plan with unicode: café résumé and symbols: $@#% that provides sufficient detail for schema validation",
    }

    test_json_path = temp_project / "test_data.json"
    with open(test_json_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False)

    # Execute with JSON file
    result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(test_json_path),
            "--actor",
            "ticket-handler",
        ]
    )
    assert result.returncode == 0

    # Verify all special content was processed correctly
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    ticket_file = ticket_files[0]
    content = ticket_file.read_text(encoding="utf-8")

    assert test_data["title"] in content
    # Check for core description content (HTML entities will be escaped)
    assert "Multi-line" in content and "newlines" in content
    assert "special characters" in content
    assert "café résumé" in content  # Unicode should be preserved
    assert "$@#%" in content  # These symbols should be preserved


@pytest.mark.e2e
def test_artifact_id_consistency(
    temp_project: Path, run_pantheon, setup_test_project, sample_ticket_data
):
    """Test that artifact IDs are consistent across create and update operations."""

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

    # Extract ticket ID from created file
    artifacts_dir = temp_project / "pantheon-artifacts"
    ticket_files = list(artifacts_dir.glob("**/T*.md"))
    ticket_file = ticket_files[0]

    # Verify ticket ID in filename matches content
    filename_id = ticket_file.stem.split("-")[0]  # Get just the T1 part from T1-title
    content = ticket_file.read_text()

    # The ticket ID should appear in the content (as "Ticket N" format)
    ticket_number = filename_id[1:]  # Extract number from "T1" -> "1"
    expected_title_format = f"Ticket {ticket_number}"
    assert expected_title_format in content
    assert filename_id.startswith("T")
    assert len(filename_id) >= 2  # At least T + number


@pytest.mark.e2e
def test_error_handling_invalid_json(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling for invalid JSON input files."""

    # Set up test project with fixture team
    setup_test_project()

    # Create invalid JSON file
    invalid_json_path = temp_project / "invalid.json"
    invalid_json_path.write_text('{"invalid": json content}')

    # Execute with invalid JSON (should fail gracefully)
    result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(invalid_json_path),
            "--actor",
            "ticket-handler",
        ],
        check=False,
    )

    assert result.returncode != 0
    assert "json" in result.stderr.lower() or "parse" in result.stderr.lower()


@pytest.mark.e2e
def test_error_handling_missing_file(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test error handling for missing JSON input files."""

    # Set up test project with fixture team
    setup_test_project()

    # Execute with non-existent file
    result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            "non_existent_file.json",
            "--actor",
            "ticket-handler",
        ],
        check=False,
    )

    assert result.returncode != 0
    assert (
        "not found" in result.stderr.lower() or "no such file" in result.stderr.lower()
    )
