"""End-to-end tests for ticket sequence grouping feature (T087)."""

import json
from pathlib import Path
import re

import pytest


@pytest.mark.e2e
def test_create_ticket_with_sequence_grouping(
    temp_project: Path, run_pantheon, setup_test_project, sequence_ticket_factory
):
    """Test complete ticket creation workflow with sequence grouping via CLI."""
    # Set up test project with fixture team
    setup_test_project()

    # Prepare ticket data with sequence fields using fixture
    ticket_data = sequence_ticket_factory(
        sequence_number=1, sequence_description="foundation"
    )

    ticket_json_path = temp_project / "sequence_ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    # Execute create-ticket with sequence fields
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

    # Verify command succeeded
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Verify artifact created at expected path with sequence directory
    artifacts_dir = temp_project / "pantheon-artifacts"

    # Expected path pattern: tickets/0_backlog/S01-foundation/tech-lead/[T*]_*.md
    sequence_dir = (
        artifacts_dir / "tickets" / "0_backlog" / "S01-foundation" / "tech-lead"
    )

    # Check if sequence directory exists
    assert sequence_dir.exists(), f"Sequence directory not found: {sequence_dir}"

    # Verify the sequence directory name matches S{:02d}-{description} format
    sequence_dir_name = sequence_dir.parent.name  # Gets "S01-foundation"
    sequence_pattern = re.compile(r"^S\d{2}-[a-z]+$")
    assert sequence_pattern.match(sequence_dir_name), (
        f"Directory name '{sequence_dir_name}' does not match S{{:02d}}-{{description}} format. "
        f"Expected pattern: S01-foundation, S02-core, etc."
    )
    # Verify zero-padding specifically
    assert sequence_dir_name == "S01-foundation", (
        f"Expected 'S01-foundation' with zero-padded number, got '{sequence_dir_name}'"
    )

    # Find ticket files in sequence directory
    ticket_files = list(sequence_dir.glob("T*.md"))
    assert len(ticket_files) >= 1, f"No ticket files found in {sequence_dir}"

    # Verify ticket content includes sequence metadata
    ticket_file = ticket_files[0]
    content = ticket_file.read_text()

    assert ticket_data["title"] in content
    assert ticket_data["description"] in content
    assert ticket_data["plan"] in content


@pytest.mark.e2e
def test_create_ticket_without_sequence_backward_compatible(
    temp_project: Path, run_pantheon, setup_test_project, sequence_ticket_factory
):
    """Test that tickets without sequence fields are placed in flat structure (backward compatible)."""
    # Set up test project with fixture team
    setup_test_project()

    # Prepare ticket data WITHOUT sequence fields using fixture
    ticket_data = sequence_ticket_factory(
        title="API Endpoint Implementation", assignee="framework-engineer"
    )

    ticket_json_path = temp_project / "standard_ticket_data.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    # Execute create-ticket without sequence fields
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

    # Verify command succeeded
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Verify artifact created at flat path (no sequence directory)
    artifacts_dir = temp_project / "pantheon-artifacts"

    # Expected path pattern: tickets/0_backlog/framework-engineer/[T*]_*.md
    flat_dir = artifacts_dir / "tickets" / "0_backlog" / "framework-engineer"

    # Check if flat directory exists
    assert flat_dir.exists(), f"Flat directory not found: {flat_dir}"

    # Find ticket files in flat directory
    ticket_files = list(flat_dir.glob("T*.md"))
    assert len(ticket_files) >= 1, f"No ticket files found in {flat_dir}"

    # Verify content
    ticket_file = ticket_files[0]
    content = ticket_file.read_text()

    assert ticket_data["title"] in content
    assert ticket_data["description"] in content


@pytest.mark.e2e
def test_sequence_validation_fails_with_only_sequence_number(
    temp_project: Path, run_pantheon, setup_test_project, base_ticket_data
):
    """Test that schema validation fails when only sequence_number is provided (all-or-nothing)."""
    # Set up test project with fixture team
    setup_test_project()

    # Prepare invalid ticket data - only sequence_number, missing sequence_description
    ticket_data = base_ticket_data.copy()
    ticket_data["sequence_number"] = 1
    # Missing sequence_description - should trigger validation error

    ticket_json_path = temp_project / "invalid_sequence_ticket.json"
    with open(ticket_json_path, "w") as f:
        json.dump(ticket_data, f)

    # Execute create-ticket (should fail validation)
    result = run_pantheon(
        [
            "execute",
            "create-ticket",
            "--from-file",
            str(ticket_json_path),
            "--actor",
            "ticket-handler",
        ],
        check=False,  # Don't raise exception on non-zero exit
    )

    # Verify command failed with validation error
    assert result.returncode != 0, "Command should have failed validation"

    # Verify error message mentions the dependency/validation issue
    error_output = result.stderr.lower()
    assert (
        "sequence" in error_output
        or "validation" in error_output
        or "dependencies" in error_output
    )


@pytest.mark.e2e
def test_multiple_sequences_in_different_groups(
    temp_project: Path, run_pantheon, setup_test_project, sequence_ticket_factory
):
    """Test creating multiple tickets in different sequence groups."""
    # Set up test project with fixture team
    setup_test_project()

    # Define sequence configurations
    sequences = [
        {
            "seq_num": 1,
            "seq_desc": "foundation",
            "title": "Foundation Authentication Setup",
        },
        {
            "seq_num": 2,
            "seq_desc": "core",
            "title": "Core Business Logic Implementation",
        },
    ]

    created_paths = []

    for seq in sequences:
        # Use fixture to create ticket data with sequence fields
        ticket_data = sequence_ticket_factory(
            sequence_number=seq["seq_num"],
            sequence_description=seq["seq_desc"],
            title=seq["title"],
        )

        ticket_json_path = temp_project / f"ticket_seq_{seq['seq_num']}.json"
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

        assert result.returncode == 0, (
            f"Failed to create ticket for sequence {seq['seq_num']}"
        )

        # Verify ticket in correct sequence directory
        expected_dir = (
            temp_project
            / "pantheon-artifacts"
            / "tickets"
            / "0_backlog"
            / f"S{seq['seq_num']:02d}-{seq['seq_desc']}"
            / "tech-lead"
        )
        assert expected_dir.exists(), f"Sequence directory not found: {expected_dir}"

        # Verify the sequence directory name matches S{:02d}-{description} format
        sequence_dir_name = expected_dir.parent.name
        sequence_pattern = re.compile(r"^S\d{2}-[a-z]+$")
        assert sequence_pattern.match(sequence_dir_name), (
            f"Directory name '{sequence_dir_name}' does not match S{{:02d}}-{{description}} format"
        )
        # Verify specific zero-padded format for each sequence
        expected_format = f"S{seq['seq_num']:02d}-{seq['seq_desc']}"
        assert sequence_dir_name == expected_format, (
            f"Expected '{expected_format}' with zero-padded number, got '{sequence_dir_name}'"
        )

        ticket_files = list(expected_dir.glob("T*.md"))
        assert len(ticket_files) >= 1, f"No ticket found in {expected_dir}"

        created_paths.append(expected_dir)

    # Verify both sequence directories exist independently
    assert len(created_paths) == 2
    assert created_paths[0] != created_paths[1]
