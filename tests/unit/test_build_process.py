from unittest.mock import Mock

from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessHandler
from tests.helpers.process_input import make_process_input


def test_happy_path_build_scaffolds_process_family():
    # Arrange: mocks for Workspace, ArtifactEngine, RaeEngine
    mock_workspace = Mock()
    mock_engine = Mock()
    mock_rae = Mock()

    # Process identifiers
    process_name = "build-team-process"
    actor = "pantheon"

    # Minimal routine to pass existence check
    mock_workspace.get_process_routine.return_value = "# routine"
    mock_workspace.has_process_redirect.return_value = False
    # Force BUILD detection
    mock_workspace.get_artifact_patch_template.side_effect = FileNotFoundError()
    mock_workspace.get_artifact_content_template.side_effect = FileNotFoundError()
    mock_workspace.has_build_schema.return_value = True
    # Directory template resolves to default bundle dir
    mock_workspace.get_process_directory_template.return_value = "pantheon-team-builds"

    # Schema compilation + validation pass-through
    mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
    mock_workspace.get_team_profile.return_value = "{}"  # YAML dict
    mock_engine.compile_schema.return_value = {
        "properties": {
            "target_team": {"type": "string"},
            "artifact": {"type": "string"},
            "build_mode": {"type": "string"},
            "include_context": {"type": "boolean"},
            "sections": {"type": "array"},
            "initial_section": {"type": "string"},
            "section_template": {"type": "array"},
            "artifact_location": {"type": "object"},
        }
    }

    # Mock the new context methods
    mock_workspace.get_context_schema.return_value = '{"type": "object", "properties": {"introduction": {"type": "string"}, "key_concepts": {"type": "array"}, "core_capabilities": {"type": "array"}, "key_principles": {"type": "array"}}}'
    mock_workspace.get_context_template.return_value = (
        "## Context\\n\\n{{ introduction }}"
    )
    mock_engine.validate.return_value = True
    # Template rendering for directory
    mock_engine._create_template_context.side_effect = (
        lambda input_params, framework_params, op=None: {
            **input_params,
            **framework_params,
        }
    )
    mock_engine.render_template.return_value = "pantheon-team-builds"

    # Mock the new scaffold methods that replace individual save_artifact calls
    def _scaffold_create_process(*args, **kwargs) -> list[PantheonPath]:
        return [
            PantheonPath(
                "pantheon-team-builds",
                "pantheon-dev",
                "processes",
                "create-ticket",
                "artifact",
                "content.md",
            )
        ]

    def _scaffold_get_process(*args, **kwargs) -> list[PantheonPath]:
        return [
            PantheonPath(
                "pantheon-team-builds",
                "pantheon-dev",
                "processes",
                "get-ticket",
                "artifact",
                "sections.jsonnet",
            )
        ]

    def _scaffold_update_process(*args, **kwargs) -> list[PantheonPath]:
        return [
            PantheonPath(
                "pantheon-team-builds",
                "pantheon-dev",
                "processes",
                "update-ticket",
                "artifact",
                "patch.md",
            )
        ]

    mock_workspace.scaffold_create_process.side_effect = _scaffold_create_process
    mock_workspace.scaffold_get_process.side_effect = _scaffold_get_process
    mock_workspace.scaffold_update_process.side_effect = _scaffold_update_process

    saved_artifacts: list[tuple[str, PantheonPath]] = []

    def _save_artifact(content: str, path: PantheonPath) -> PantheonPath:
        saved_artifacts.append((content, path))
        return path

    mock_workspace.save_artifact.side_effect = _save_artifact
    mock_workspace.summarize_created_files.return_value = [
        {
            "path": "pantheon-artifacts/processes/create-ticket/content.md",
            "type": "template",
            "description": "CREATE process content template",
        },
        {
            "path": "pantheon-artifacts/processes/get-ticket/sections.jsonnet",
            "type": "sections",
            "description": "GET process sections configuration",
        },
        {
            "path": "pantheon-artifacts/processes/update-ticket-plan/patch.md",
            "type": "patch",
            "description": "UPDATE process patch template",
        },
    ]

    handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)

    # Build-spec parameters
    parameters = {
        "target_team": "pantheon-dev",
        "artifact": "ticket",
        "build_mode": "modular",
        "include_context": True,
        "artifact_sections": ["description", "plan"],
        "initial_section": "description",
        "section_template": [
            {
                "section": "description",
                "section_description": "Details for the description section.",
                "template": "# {{ title }}\n\n<!-- body -->\n",
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                },
            },
            {
                "section": "plan",
                "section_description": "Details for the plan section.",
                "template": "## Plan\n{{ plan_detail }}\n",
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "properties": {"plan_detail": {"type": "string"}},
                    "required": ["plan_detail"],
                },
            },
        ],
        "artifact_location": {
            "directory": "tickets/",
            "filename_template": "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
        },
        "permissions": {
            "create": {"allow": ["pantheon"], "deny": []},
            "get": {"allow": ["pantheon"], "deny": []},
            "update": {"allow": ["pantheon"], "deny": []},
        },
    }

    input_data = make_process_input(
        process_name,
        actor,
        input_params=parameters,
    )

    # Act
    result = handler.execute(input_data)

    # Debug: Print result if test fails
    if not result["success"]:
        print(f"BUILD process failed: {result['error']}")

    # Assert
    assert result["success"] is True
    assert "completed successfully" in result["output"]
    assert "All verifications complete" in result["output"]
    assert "BUILD" in result["output"]
    # Verify files_created contains process information
    assert result["files_created"] is not None
    assert len(result["files_created"]) > 0

    # Verify scaffold methods were called correctly
    mock_workspace.scaffold_create_process.assert_called_once()
    mock_workspace.scaffold_get_process.assert_called_once()
    mock_workspace.scaffold_update_process.assert_called_once()

    update_call = mock_workspace.scaffold_update_process.call_args
    assert update_call[0][1] == "update-ticket"

    section_schema_contents = {
        str(path): content
        for content, path in saved_artifacts
        if str(path).endswith(".schema.jsonnet")
    }

    assert section_schema_contents, "Expected section schema files to be generated"
    for payload in section_schema_contents.values():
        assert '"$schema"' not in payload
