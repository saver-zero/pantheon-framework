"""End-to-end tests for BUILD process type functionality."""

import json
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_build_process_scaffolds_process_family(
    temp_project: Path, run_pantheon, setup_test_project, sample_build_spec_data
):
    """Test that build-team-process scaffolds a complete process family."""

    # Set up test project with fixture team (pantheon-e2e-test)
    setup_test_project()

    # Prepare build-spec data
    build_spec_data = sample_build_spec_data
    build_spec_json_path = temp_project / "build_spec.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(build_spec_data, f)

    # Execute build-team-process
    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert result.returncode == 0
    assert "build-team-process completed successfully" in result.stdout
    assert "All verifications complete. Operation: BUILD." in result.stdout

    # Verify bundle was created in artifacts directory
    artifacts_dir = temp_project / "pantheon-artifacts"

    # Find the generated bundle directory (it should be under pantheon-team-builds based on the output)
    team_build_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(team_build_dirs) >= 1, (
        f"Expected team build directory not found in {list(artifacts_dir.glob('**/*'))}"
    )

    bundle_dir = team_build_dirs[0] / "processes"

    # Verify CREATE process was generated
    create_process_dir = bundle_dir / "create-task"
    assert create_process_dir.exists(), (
        f"CREATE process not found: {create_process_dir}"
    )
    assert (create_process_dir / "routine.md").exists()
    assert (create_process_dir / "schema.jsonnet").exists()
    assert (create_process_dir / "artifact" / "content.md").exists()
    assert (create_process_dir / "artifact" / "placement.jinja").exists()
    assert (create_process_dir / "artifact" / "naming.jinja").exists()

    # Verify GET process was generated
    get_process_dir = bundle_dir / "get-task"
    assert get_process_dir.exists(), f"GET process not found: {get_process_dir}"
    assert (get_process_dir / "routine.md").exists()
    assert (get_process_dir / "artifact" / "locator.jsonnet").exists()
    assert (get_process_dir / "artifact" / "parser.jsonnet").exists()
    assert (get_process_dir / "artifact" / "sections.jsonnet").exists()

    # Verify UPDATE process was generated for non-initial section
    update_process_dir = bundle_dir / "update-task"
    assert update_process_dir.exists(), (
        f"UPDATE process not found: {update_process_dir}"
    )
    assert (update_process_dir / "routine.md").exists()
    assert (update_process_dir / "schema.jsonnet").exists()
    assert (update_process_dir / "artifact" / "patch.md").exists()
    assert (update_process_dir / "artifact" / "target.jsonnet").exists()
    assert (update_process_dir / "artifact" / "locator.jsonnet").exists()
    assert (update_process_dir / "artifact" / "parser.jsonnet").exists()


@pytest.mark.e2e
def test_build_process_validates_input(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that build-team-process validates input and handles errors properly."""

    # Set up test project with fixture team (pantheon-e2e-test)
    setup_test_project()

    # Test with invalid build-spec (missing required fields)
    invalid_build_spec = {
        "artifact": "task",
        # Missing required fields: target_team, sections, initial_section, etc.
    }

    build_spec_json_path = temp_project / "invalid_build_spec.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(invalid_build_spec, f)

    # Execute build-team-process with invalid data
    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ],
        check=False,
    )  # Allow non-zero exit codes

    # Should fail with validation error
    assert result.returncode != 0
    # Error message should be informative with detailed validation errors
    error_output = result.stderr + result.stdout
    assert "Schema validation failed:" in error_output
    # Should mention specific missing fields
    assert "target_team" in error_output or "required" in error_output.lower()


@pytest.mark.e2e
def test_build_process_generates_correct_structure(
    temp_project: Path, run_pantheon, setup_test_project, sample_build_spec_data
):
    """Test that build process generates processes with correct structure and content."""

    # Set up test project with fixture team (pantheon-e2e-test)
    setup_test_project()

    # Execute build process
    build_spec_data = sample_build_spec_data
    build_spec_json_path = temp_project / "build_spec.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(build_spec_data, f)

    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert result.returncode == 0

    # Find generated bundle
    artifacts_dir = temp_project / "pantheon-artifacts"
    bundle_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(bundle_dirs) >= 1
    bundle_dir = bundle_dirs[0] / "processes"

    # Verify CREATE process content template includes expected sections
    create_content_file = bundle_dir / "create-task" / "artifact" / "content.md"
    assert create_content_file.exists()

    content_template = create_content_file.read_text()

    # Multi-section builds now use modular generation with semantic URI includes
    # Should have toggle variables for each section
    assert "{% set _include_description" in content_template
    assert "{% set _include_context" in content_template

    # Should have section markers with conditional blocks
    assert "<!-- SECTION:START:DESCRIPTION -->" in content_template
    assert "<!-- SECTION:END:DESCRIPTION -->" in content_template
    assert "<!-- SECTION:START:CONTEXT -->" in content_template
    assert "<!-- SECTION:END:CONTEXT -->" in content_template

    # Should use semantic URI includes instead of inline templates
    assert "{% include 'artifact-template://update-task/sections/" in content_template
    assert "{% if _include_description %}" in content_template
    assert "{% if _include_context %}" in content_template

    # Verify UPDATE process patch template
    update_process_dir = bundle_dir / "update-task"
    update_patch_file = update_process_dir / "artifact" / "patch.md"
    assert update_patch_file.exists()

    implementation_snippet = (
        update_process_dir / "artifact" / "sections" / "implementation.md"
    ).read_text()
    assert "{{ implementation_details }}" in implementation_snippet
    assert "{{ testing_approach }}" in implementation_snippet

    # Verify generated schemas use modular generation with semantic URI imports
    create_schema_file = bundle_dir / "create-task" / "schema.jsonnet"
    assert create_schema_file.exists()

    schema_content = create_schema_file.read_text()
    # Multi-section builds now use Jsonnet with semantic URI imports
    # Should have imports for sections instead of inline field references
    assert 'import "process-schema://update-task/sections/' in schema_content
    # Verify object-based array structure with std.foldl composition
    assert "local sections = [" in schema_content
    assert 'name: "description"' in schema_content
    assert (
        'name: "context"' in schema_content
        or 'name: "implementation"' in schema_content
    )
    assert "local properties = std.foldl(" in schema_content

    # The permissions would be implemented according to the build-spec
    # but may not be generated as separate files in this framework version


@pytest.mark.e2e
def test_build_process_complete_mode_no_updates(
    temp_project: Path,
    run_pantheon,
    setup_test_project,
    sample_build_spec_data_complete,
):
    """Test that complete mode scaffolds only CREATE and GET processes, no UPDATE processes."""

    # Set up test project with fixture team (pantheon-e2e-test)
    setup_test_project()

    # Prepare complete mode build-spec data
    build_spec_data = sample_build_spec_data_complete
    build_spec_json_path = temp_project / "build_spec_complete.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(build_spec_data, f)

    # Execute build-team-process with complete mode
    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert result.returncode == 0
    assert "build-team-process completed successfully" in result.stdout
    assert "All verifications complete. Operation: BUILD." in result.stdout

    # Verify bundle was created in artifacts directory
    artifacts_dir = temp_project / "pantheon-artifacts"
    team_build_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(team_build_dirs) >= 1
    bundle_dir = team_build_dirs[0] / "processes"

    # Verify CREATE process was generated
    create_process_dir = bundle_dir / "create-agent"
    assert create_process_dir.exists(), (
        f"CREATE process not found: {create_process_dir}"
    )
    assert (create_process_dir / "routine.md").exists()
    assert (create_process_dir / "schema.jsonnet").exists()
    assert (create_process_dir / "artifact" / "content.md").exists()
    assert (create_process_dir / "artifact" / "placement.jinja").exists()
    assert (create_process_dir / "artifact" / "naming.jinja").exists()

    # Verify GET process was generated
    get_process_dir = bundle_dir / "get-agent"
    assert get_process_dir.exists(), f"GET process not found: {get_process_dir}"
    assert (get_process_dir / "routine.md").exists()
    assert (get_process_dir / "artifact" / "locator.jsonnet").exists()
    assert (get_process_dir / "artifact" / "parser.jsonnet").exists()
    assert (get_process_dir / "artifact" / "sections.jsonnet").exists()

    # Verify NO UPDATE processes were generated
    update_processes = list(bundle_dir.glob("update-agent-*"))
    assert len(update_processes) == 0, (
        f"UPDATE processes found but shouldn't exist in complete mode: {update_processes}"
    )


@pytest.mark.e2e
def test_build_process_complete_mode_content_structure(
    temp_project: Path,
    run_pantheon,
    setup_test_project,
    sample_build_spec_data_complete,
):
    """Test that complete mode generates CREATE process with all sections included."""

    # Set up test project
    setup_test_project()

    # Execute build process with complete mode
    build_spec_data = sample_build_spec_data_complete
    build_spec_json_path = temp_project / "build_spec_complete.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(build_spec_data, f)

    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert result.returncode == 0

    # Find generated bundle
    artifacts_dir = temp_project / "pantheon-artifacts"
    bundle_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(bundle_dirs) >= 1
    bundle_dir = bundle_dirs[0] / "processes"

    # Verify CREATE process content template includes ALL sections with actual content
    create_content_file = bundle_dir / "create-agent" / "artifact" / "content.md"
    assert create_content_file.exists()

    content_template = create_content_file.read_text()

    # Multi-section builds now use modular generation with semantic URI includes
    # even in complete mode. Should have toggle variables for each section
    assert "{% set _include_persona" in content_template
    assert "{% set _include_capabilities" in content_template

    # Should have section markers with conditional blocks
    assert "<!-- SECTION:START:PERSONA -->" in content_template
    assert "<!-- SECTION:END:PERSONA -->" in content_template
    assert "<!-- SECTION:START:CAPABILITIES -->" in content_template
    assert "<!-- SECTION:END:CAPABILITIES -->" in content_template

    # Should use semantic URI includes instead of inline templates
    assert "{% include 'artifact-template://update-agent/sections/" in content_template
    assert "{% if _include_persona %}" in content_template
    assert "{% if _include_capabilities %}" in content_template

    # Should NOT include Context section (include_context=false for agent artifact)
    assert "<!-- SECTION:START:CONTEXT -->" not in content_template
    assert "<!-- SECTION:END:CONTEXT -->" not in content_template

    # Verify CREATE schema uses modular generation with semantic URI imports
    create_schema_file = bundle_dir / "create-agent" / "schema.jsonnet"
    assert create_schema_file.exists()

    schema_content = create_schema_file.read_text()
    # Multi-section builds now use Jsonnet with semantic URI imports
    # Should have imports for each section instead of inline field definitions
    assert 'import "process-schema://update-agent/sections/persona"' in schema_content
    assert (
        'import "process-schema://update-agent/sections/capabilities"' in schema_content
    )

    # Verify object-based array structure with std.foldl composition
    assert "local sections = [" in schema_content
    assert 'name: "persona"' in schema_content
    assert 'name: "capabilities"' in schema_content
    assert "local properties = std.foldl(" in schema_content
    assert "local required = std.foldl(" in schema_content


@pytest.mark.e2e
def test_build_process_single_section_simplification(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that build process correctly handles single-section artifacts with simplified structure."""

    # Set up test project with fixture team (pantheon-e2e-test)
    setup_test_project()

    # Create build-spec for single-section artifact (simple status document)
    single_section_build_spec = {
        "target_team": "pantheon-test-dev-team",
        "artifact": "status",
        "build_mode": "modular",
        "include_context": False,
        "artifact_sections": ["content"],
        "initial_section": "content",
        "section_template": [
            {
                "section": "content",
                "section_description": "Status content",
                "template": "{{ status_message }}\n\n**Last Updated:** {{ updated_by }}\n**Date:** {{ pantheon_datestamp }}",
                "schema": {
                    "status_message": {
                        "type": "string",
                        "purpose": "To provide the main status message",
                        "description_for_schema": "Main status message",
                    },
                    "updated_by": {
                        "type": "string",
                        "purpose": "To track who updated the status",
                        "description_for_schema": "Person updating the status",
                    },
                },
            }
        ],
        "artifact_location": {
            "directory": "status/",
            "filename_template": "status_{{ pantheon_datestamp }}.md",
        },
        "permissions": {
            "create": {"allow": ["status-manager"], "deny": []},
            "get": {"allow": ["status-manager", "viewer"], "deny": []},
            "update": {"allow": ["status-manager"], "deny": []},
        },
    }

    build_spec_json_path = temp_project / "single_section_build_spec.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(single_section_build_spec, f)

    # Execute build-team-process
    result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert result.returncode == 0
    assert "build-team-process completed successfully" in result.stdout

    # Find generated bundle
    artifacts_dir = temp_project / "pantheon-artifacts"
    team_build_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(team_build_dirs) >= 1
    bundle_dir = team_build_dirs[0] / "processes"

    # Verify CREATE process was generated with simplified structure
    create_process_dir = bundle_dir / "create-status"
    assert create_process_dir.exists()
    assert (create_process_dir / "routine.md").exists()
    assert (create_process_dir / "schema.jsonnet").exists()
    assert (create_process_dir / "artifact" / "content.md").exists()
    assert (create_process_dir / "artifact" / "placement.jinja").exists()
    assert (create_process_dir / "artifact" / "naming.jinja").exists()

    # Verify CREATE content template is simple (no section markers for single section)
    create_content_file = create_process_dir / "artifact" / "content.md"
    content_template = create_content_file.read_text()

    # Should contain template variables but NO section markers
    assert "{{ status_message }}" in content_template
    assert "{{ updated_by }}" in content_template
    assert "{{ pantheon_datestamp }}" in content_template
    assert "<!-- SECTION:START:" not in content_template
    assert "<!-- SECTION:END:" not in content_template

    # Verify GET process was generated with simplified structure (no sections.jsonnet)
    get_process_dir = bundle_dir / "get-status"
    assert get_process_dir.exists()
    assert (get_process_dir / "routine.md").exists()
    assert (get_process_dir / "artifact" / "locator.jsonnet").exists()
    assert (get_process_dir / "artifact" / "parser.jsonnet").exists()

    # Key assertion: NO sections.jsonnet file for single-section artifact
    assert not (get_process_dir / "artifact" / "sections.jsonnet").exists()

    # Verify UPDATE process was generated with simplified structure (no target.jsonnet)
    update_process_dir = bundle_dir / "update-status"
    assert update_process_dir.exists()
    assert (update_process_dir / "routine.md").exists()
    assert (update_process_dir / "schema.jsonnet").exists()
    assert (update_process_dir / "artifact" / "patch.md").exists()
    assert (update_process_dir / "artifact" / "locator.jsonnet").exists()
    assert (update_process_dir / "artifact" / "parser.jsonnet").exists()

    # Key assertion: NO target.jsonnet file for single-section artifact
    assert not (update_process_dir / "artifact" / "target.jsonnet").exists()

    # Key assertion: NO individual section templates directory
    assert not (update_process_dir / "artifact" / "sections").exists()

    # Verify UPDATE patch template is simple (whole document replacement)
    update_patch_file = update_process_dir / "artifact" / "patch.md"
    patch_template = update_patch_file.read_text()

    # Should contain template variables for direct content replacement
    assert "{{ status_message }}" in patch_template
    assert "{{ updated_by }}" in patch_template
    # Should NOT contain section iteration logic
    assert "{% for section_name in requested_sections %}" not in patch_template
    assert "{% include snippet ignore missing %}" not in patch_template

    # Verify schemas use flat structure (no section_updates)
    create_schema_file = create_process_dir / "schema.jsonnet"
    create_schema_content = create_schema_file.read_text()

    update_schema_file = update_process_dir / "schema.jsonnet"
    update_schema_content = update_schema_file.read_text()

    # Should have direct properties, not nested in section_updates
    assert "status_message" in create_schema_content
    assert "updated_by" in create_schema_content
    assert "status_message" in update_schema_content
    assert "updated_by" in update_schema_content

    # Should NOT have section_updates structure
    assert "section_updates" not in create_schema_content
    assert "section_updates" not in update_schema_content


@pytest.mark.e2e
def test_single_section_update_process_execution(
    temp_project: Path, run_pantheon, setup_test_project
):
    """Test that single-section UPDATE process executes correctly with whole document replacement."""

    # Set up test project with fixture team
    setup_test_project()

    # First, build the single-section process family
    single_section_build_spec = {
        "target_team": "pantheon-test-dev-team",
        "artifact": "status",
        "build_mode": "modular",
        "include_context": False,
        "artifact_sections": ["content"],
        "initial_section": "content",
        "section_template": [
            {
                "section": "content",
                "section_description": "Status content",
                "template": "{{ status_message }}\n\n**Last Updated:** {{ updated_by }}\n**Date:** {{ pantheon_datestamp }}",
                "schema": {
                    "status_message": {
                        "type": "string",
                        "purpose": "To provide the main status message",
                        "description_for_schema": "Main status message",
                    },
                    "updated_by": {
                        "type": "string",
                        "purpose": "To track who updated the status",
                        "description_for_schema": "Person updating the status",
                    },
                },
            }
        ],
        "artifact_location": {
            "directory": "status/",
            "filename_template": "status_{{ pantheon_datestamp }}.md",
        },
        "permissions": {
            "create": {"allow": ["ticket-handler"], "deny": []},
            "get": {"allow": ["ticket-handler", "viewer"], "deny": []},
            "update": {"allow": ["ticket-handler"], "deny": []},
        },
    }

    build_spec_json_path = temp_project / "single_section_build_spec.json"
    with open(build_spec_json_path, "w") as f:
        json.dump(single_section_build_spec, f)

    # Build the process family
    build_result = run_pantheon(
        [
            "execute",
            "build-team-process",
            "--from-file",
            str(build_spec_json_path),
            "--actor",
            "pantheon",
        ]
    )

    assert build_result.returncode == 0

    # Copy generated processes to the test team directory for execution
    artifacts_dir = temp_project / "pantheon-artifacts"
    team_build_dirs = list(artifacts_dir.glob("**/pantheon-test-dev-team"))
    assert len(team_build_dirs) >= 1
    generated_processes_dir = team_build_dirs[0] / "processes"

    test_team_dir = temp_project / "pantheon-teams" / "pantheon-e2e-test"
    test_processes_dir = test_team_dir / "processes"

    # Copy the generated single-section processes to test team
    import shutil

    for process in ["create-status", "get-status", "update-status"]:
        src = generated_processes_dir / process
        dst = test_processes_dir / process
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # Step 1: Create a status document using single-section CREATE process
    create_data = {
        "status_message": "Initial system status: All services running normally",
        "updated_by": "System Administrator",
    }

    create_json_path = temp_project / "create_status.json"
    with open(create_json_path, "w") as f:
        json.dump(create_data, f)

    create_result = run_pantheon(
        [
            "execute",
            "create-status",
            "--from-file",
            str(create_json_path),
            "--actor",
            "ticket-handler",
        ]
    )

    assert create_result.returncode == 0
    assert "create-status completed successfully" in create_result.stdout

    # Verify the status file was created
    status_dir = temp_project / "pantheon-artifacts" / "status"
    assert status_dir.exists()

    # Look for any .md files (filename format includes [S1] prefix)
    status_files = list(status_dir.glob("*.md"))
    assert len(status_files) >= 1, f"No status files found in {status_dir}"

    original_status_file = status_files[0]
    original_content = original_status_file.read_text()

    # Verify original content is clean (no section markers)
    assert "Initial system status: All services running normally" in original_content
    assert "System Administrator" in original_content
    assert "<!-- SECTION:START:" not in original_content
    assert "<!-- SECTION:END:" not in original_content

    # Step 2: Update the status using single-section UPDATE process (whole document replacement)
    update_data = {
        "status_message": "Updated system status: Maintenance window scheduled for tonight",
        "updated_by": "DevOps Team",
    }

    update_json_path = temp_project / "update_status.json"
    with open(update_json_path, "w") as f:
        json.dump(update_data, f)

    # Extract the status ID for the update (from filename like [S1]_status_2025-09-23 PDT.md)
    status_filename = original_status_file.name
    # Extract the ID from the [S1] part
    if status_filename.startswith("[") and "]" in status_filename:
        status_id = status_filename.split("]")[0][1:]  # Extract S1 from [S1]
    else:
        status_id = status_filename.replace(".md", "")

    update_result = run_pantheon(
        [
            "execute",
            "update-status",
            "--from-file",
            str(update_json_path),
            "--id",
            status_id,
            "--actor",
            "ticket-handler",
        ]
    )

    assert update_result.returncode == 0
    assert "update-status completed successfully" in update_result.stdout

    # Step 3: Verify the update replaced the entire document content
    updated_content = original_status_file.read_text()

    # Should contain new content
    assert (
        "Updated system status: Maintenance window scheduled for tonight"
        in updated_content
    )
    assert "DevOps Team" in updated_content

    # Should NOT contain old content (whole document replacement)
    assert "Initial system status: All services running normally" not in updated_content
    assert "System Administrator" not in updated_content

    # Should still be clean (no section markers)
    assert "<!-- SECTION:START:" not in updated_content
    assert "<!-- SECTION:END:" not in updated_content

    # Step 4: Verify GET process can retrieve the updated content
    get_result = run_pantheon(
        [
            "execute",
            "get-status",
            "--id",
            status_id,
            "--actor",
            "ticket-handler",
        ]
    )

    assert get_result.returncode == 0

    # Should return entire content (not sections) - parse JSON directly from stdout
    output_data = json.loads(get_result.stdout.strip())

    # For single-section artifacts, should return {"content": "..."} not {"sections": {...}}
    assert "content" in output_data
    assert "sections" not in output_data

    # Verify the content matches our update
    content = output_data["content"]
    assert "Updated system status: Maintenance window scheduled for tonight" in content
    assert "DevOps Team" in content
