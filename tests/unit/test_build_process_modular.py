"""Unit tests for modular BUILD process methods.

Tests each phase of the BUILD process in isolation using dependency injection
and mocks for fast, focused validation of business logic.
"""

import json
from unittest.mock import Mock

import pytest

from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessHandler, _BuildContext
from tests.helpers.process_input import make_framework_params


class TestBuildInitContext:
    """Unit tests for _build_init_context method."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_artifact_engine(self):
        """Create mock artifact engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_rae_engine(self):
        """Create mock RAE engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def process_handler(self, mock_workspace, mock_artifact_engine, mock_rae_engine):
        """Create ProcessHandler with all dependencies mocked."""
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_params(self):
        """Create user and framework parameters for BUILD process tests."""
        input_params = {
            "target_team": "test-team",
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
                    "schema": {"properties": {"title": {"type": "string"}}},
                },
                {
                    "section": "plan",
                    "section_description": "Details for the plan section.",
                    "template": "## Plan\n{{ plan_detail }}\n",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                },
            ],
            "artifact_location": {
                "directory": "tickets/",
                "filename_template": "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            },
            "permissions": {
                "create": {"allow": ["test-actor"]},
                "get": {"allow": ["test-actor"]},
                "update": {"allow": ["test-actor"]},
            },
        }
        framework_params = make_framework_params(
            "build-team-process",
            "test-actor",
            pantheon_active_profile={},
            pantheon_full_profile={},
            pantheon_sections=["description", "plan"],
        )
        return input_params, framework_params

    def test_build_init_context_success(
        self,
        process_handler,
        mock_workspace,
        mock_artifact_engine,
        build_params,
    ):
        """Test successful BUILD context initialization."""
        input_params, framework_params = build_params

        # Arrange: Configure mocks for successful validation
        mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_workspace.get_team_profile.return_value = "{}"
        mock_artifact_engine.compile_schema.return_value = {}
        mock_artifact_engine.validate.return_value = True
        mock_workspace.get_process_directory_template.return_value = (
            "{{ target_team }}-builds"
        )
        mock_artifact_engine._create_template_context.return_value = {
            **input_params,
            **framework_params,
        }
        mock_artifact_engine.render_template.return_value = "test-team-builds"

        # Mock the new context methods
        mock_workspace.get_context_schema.return_value = '{"type": "object", "properties": {"introduction": {"type": "string"}, "key_concepts": {"type": "array"}, "core_capabilities": {"type": "array"}, "key_principles": {"type": "array"}}}'
        mock_workspace.get_context_template.return_value = (
            "## Context\\n\\n{{ introduction }}"
        )

        # Act: Initialize BUILD context
        success, ctx, compiled_schema, error, build_mode = (
            process_handler._build_init_context(
                "build-team-process", input_params, framework_params
            )
        )

        # Assert: Verify successful context creation
        assert success is True
        assert error is None
        assert isinstance(ctx, _BuildContext)
        assert ctx.process_name == "build-team-process"
        assert ctx.target_team == "test-team"
        assert ctx.artifact == "ticket"
        assert ctx.sections == ["description", "context", "plan"]
        assert ctx.initial_section == "description"
        assert ctx.create_proc == "create-ticket"
        assert ctx.get_proc == "get-ticket"
        assert isinstance(ctx.bundle_root, PantheonPath)

    def test_build_init_context_schema_validation_failure(
        self,
        process_handler,
        mock_workspace,
        mock_artifact_engine,
        build_params,
    ):
        """Test BUILD context initialization with schema validation failure."""
        input_params, framework_params = build_params

        # Arrange: Configure mocks for validation failure
        mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_workspace.get_team_profile.return_value = "{}"
        mock_artifact_engine.compile_schema.return_value = {}

        # Mock validation to raise detailed validation error (new behavior)
        detailed_error = "Schema validation failed:\n  - Field 'target_team': 'target_team' is a required property"
        mock_artifact_engine.validate.side_effect = ValueError(detailed_error)

        # Mock the new context methods
        mock_workspace.get_context_schema.return_value = (
            '{"type": "object", "properties": {"introduction": {"type": "string"}}}'
        )
        mock_workspace.get_context_template.return_value = (
            "## Context\\n\\n{{ introduction }}"
        )

        # Act: Initialize BUILD context
        success, ctx, compiled_schema, error, build_mode = (
            process_handler._build_init_context(
                "build-team-process", input_params, framework_params
            )
        )

        # Assert: Verify failure handling with detailed validation error
        assert success is False
        assert ctx is None
        assert "Schema validation failed:" in error
        assert "target_team" in error

    def test_build_init_context_missing_required_field(
        self, process_handler, mock_workspace, mock_artifact_engine
    ):
        """Test BUILD context initialization with missing required field."""
        # Arrange: Create parameters missing target_team
        input_params = {
            "artifact": "ticket",
            "artifact_sections": ["description"],
            "initial_section": "description",
        }
        framework_params = make_framework_params(
            "build-team-process",
            "test-actor",
            pantheon_sections=["description"],
        )
        mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_workspace.get_team_profile.return_value = "{}"
        mock_artifact_engine.compile_schema.return_value = {}
        mock_artifact_engine.validate.return_value = True

        # Act: Initialize BUILD context
        success, ctx, compiled_schema, error, build_mode = (
            process_handler._build_init_context(
                "build-team-process", input_params, framework_params
            )
        )

        # Assert: Verify failure handling
        assert success is False
        assert ctx is None
        assert "Invalid build-spec structure" in error

    def test_build_init_context_invalid_initial_section(
        self,
        process_handler,
        mock_workspace,
        mock_artifact_engine,
        build_params,
    ):
        """Test BUILD context initialization with invalid initial section."""
        input_params, framework_params = build_params

        # Arrange: Set initial_section not in sections list
        invalid_input_params = input_params.copy()
        invalid_input_params["initial_section"] = "nonexistent"

        mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_workspace.get_team_profile.return_value = "{}"
        mock_artifact_engine.compile_schema.return_value = {}
        mock_artifact_engine.validate.return_value = True
        mock_workspace.get_process_directory_template.return_value = "test-builds"
        mock_artifact_engine._create_template_context.return_value = {
            **invalid_input_params,
            **framework_params,
        }
        mock_artifact_engine.render_template.return_value = "test-builds"

        # Mock the new context methods
        mock_workspace.get_context_schema.return_value = (
            '{"type": "object", "properties": {"introduction": {"type": "string"}}}'
        )
        mock_workspace.get_context_template.return_value = (
            "## Context\\n\\n{{ introduction }}"
        )

        # Act: Initialize BUILD context
        success, ctx, compiled_schema, error, build_mode = (
            process_handler._build_init_context(
                "build-team-process", invalid_input_params, framework_params
            )
        )

        # Assert: Verify failure handling
        assert success is False
        assert ctx is None
        assert "Initial section 'nonexistent' not in sections list" in error


class TestBuildScaffoldCreate:
    """Unit tests for _build_scaffold_create method."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def process_handler(self, mock_workspace):
        """Create ProcessHandler with mocked workspace."""
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_context(self):
        """Create valid BuildContext for testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["context", "description", "plan"],
            initial_section="description",
            section_defs={
                "context": {
                    "template": "",
                    "schema": {},
                    "description": "Context captured during the initial planning flow.",
                },
                "description": {
                    "template": "# {{ title }}\\n\\n<!-- body -->\\n",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "High-level summary of the ticket request.",
                },
                "plan": {
                    "template": "## Plan\\n{{ plan_detail }}\\n",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                    "description": "Implementation plan outlining next steps.",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={"create": {"allow": ["test-actor"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    def test_build_scaffold_create_success(
        self, process_handler, mock_workspace, build_context
    ):
        """Test successful CREATE process scaffolding."""
        # Arrange: Configure mock workspace response
        expected_paths = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "create-ticket",
                "artifact",
                "content.md",
            )
        ]
        mock_workspace.scaffold_create_process.return_value = expected_paths

        # Act: Scaffold CREATE process
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        result_paths = process_handler._build_scaffold_create(
            build_context, input_params, framework_params, "modular"
        )

        # Assert: Verify scaffold method called correctly
        assert result_paths == expected_paths
        mock_workspace.scaffold_create_process.assert_called_once()

        # Verify call arguments
        call_args = mock_workspace.scaffold_create_process.call_args
        assert call_args[0][0] == build_context.bundle_root  # bundle_root
        assert call_args[0][1] == "create-ticket"  # create_proc
        # Multi-section builds now use modular generation with conditional toggles
        assert "{% set" in call_args[0][2]  # content_md has toggle variables
        assert call_args[0][3] == "tickets/"  # placement
        # Now we always prepend the acronym pattern
        assert (
            call_args[0][4]
            == "[T{{ pantheon_artifact_id }}]_T{{ pantheon_artifact_id }}_{{ title | slugify }}.md"
        )  # naming
        # Multi-section builds now use Jsonnet with semantic URI imports
        assert 'import "process-schema://' in call_args[0][5]  # schema_jsonnet
        assert "test-actor" in call_args[0][6]  # perms_create  # perms_create

    def test_build_scaffold_create_content_structure(
        self, process_handler, mock_workspace, build_context
    ):
        """Test CREATE process generates correct modular content structure."""
        # Arrange: Configure mock workspace response
        mock_workspace.scaffold_create_process.return_value = []

        # Act: Scaffold CREATE process
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        process_handler._build_scaffold_create(
            build_context, input_params, framework_params, "modular"
        )

        # Assert: Verify modular content structure in call arguments
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Multi-section builds now use modular generation with toggle variables
        # Should contain toggle set statements for each section
        assert "{% set _include_context" in content_md
        assert "{% set _include_description" in content_md
        assert "{% set _include_plan" in content_md

        # Should have conditional blocks with section markers
        assert "<!-- SECTION:START:CONTEXT -->" in content_md
        assert "{% if _include_context %}" in content_md

        # Should have semantic URI includes for section templates (using single quotes in Jinja2)
        assert "{% include 'artifact-template://update-ticket/sections/" in content_md

    def test_build_scaffold_create_incorporates_context_section(self, mock_workspace):
        """Test that context section is automatically incorporated into CREATE process templates."""
        # Create handler with mocks
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Configure mocks for build_init_context
        mock_workspace.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_workspace.get_team_profile.return_value = "{}"
        mock_artifact_engine.compile_schema.return_value = {}
        mock_artifact_engine.validate.return_value = True
        mock_workspace.get_process_directory_template.return_value = (
            "{{ target_team }}-builds"
        )
        mock_artifact_engine._create_template_context.return_value = {}
        mock_artifact_engine.render_template.return_value = "test-builds"

        # Mock the new context methods
        mock_workspace.get_context_schema.return_value = (
            '{"type": "object", "properties": {"introduction": {"type": "string"}}}'
        )
        mock_workspace.get_context_template.return_value = (
            "## Context\\n\\n{{ introduction }}"
        )

        # Create separate input and framework parameters
        input_params = {
            "target_team": "test-team",
            "artifact": "ticket",
            "build_mode": "modular",
            "include_context": True,
            "artifact_sections": ["description", "plan"],
            "initial_section": "description",
            "section_template": [
                {
                    "section": "description",
                    "section_description": "Details for the description section.",
                    "template": "# {{ title }}\n\n{{ content }}",
                    "schema": {"properties": {"title": {"type": "string"}}},
                },
                {
                    "section": "plan",
                    "section_description": "Details for the plan section.",
                    "template": "## Plan\n{{ plan_detail }}",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                },
            ],
            "artifact_location": {
                "directory": "tickets/",
                "filename_template": "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            },
            "permissions": {"create": {"allow": ["test-actor"]}},
        }

        framework_params = make_framework_params(
            "build-team-process",
            "test-actor",
            pantheon_active_profile={},
            pantheon_full_profile={},
        )

        mock_workspace.scaffold_create_process.return_value = [PantheonPath("test")]

        # Build context
        success, ctx, compiled_schema, error, build_mode = handler._build_init_context(
            "build-team-process", input_params, framework_params
        )
        assert success, f"Build context creation failed: {error}"

        # Execute scaffold CREATE with modular mode
        handler._build_scaffold_create(ctx, input_params, framework_params, "modular")

        # Verify scaffold_create_process was called
        mock_workspace.scaffold_create_process.assert_called_once()

        # Get the content.md that was passed to scaffold_create_process
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]  # Third positional argument is content_md

        # Verify Context section was added first
        assert "<!-- SECTION:START:CONTEXT -->" in content_md
        assert "<!-- SECTION:END:CONTEXT -->" in content_md

        # Since context is not the initial section, it should contain placeholder
        # Context section template content would only appear if context was the initial section
        assert "<!-- SECTION:PLACEHOLDER -->" in content_md

        # Verify other sections are still present
        assert "<!-- SECTION:START:DESCRIPTION -->" in content_md
        assert "<!-- SECTION:START:PLAN -->" in content_md

        # Verify plan section is placeholder (not initial section)
        assert "<!-- SECTION:PLACEHOLDER -->" in content_md


class TestBuildScaffoldGet:
    """Unit tests for _build_scaffold_get method."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def process_handler(self, mock_workspace):
        """Create ProcessHandler with mocked workspace."""
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_context(self):
        """Create valid BuildContext for testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["context", "description", "plan"],
            initial_section="description",
            section_defs={
                "context": {
                    "template": "",
                    "schema": {},
                    "description": "Context captured during the initial planning flow.",
                },
                "description": {
                    "template": "",
                    "schema": {},
                    "description": "High-level summary of the ticket request.",
                },
                "plan": {
                    "template": "",
                    "schema": {},
                    "description": "Implementation plan outlining next steps.",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={"get": {"allow": ["test-actor"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    def test_build_scaffold_get_success(
        self, process_handler, mock_workspace, build_context
    ):
        """Test successful GET process scaffolding."""
        # Arrange: Configure mock workspace response
        expected_paths = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "get-ticket",
                "artifact",
                "sections.jsonnet",
            )
        ]
        mock_workspace.scaffold_get_process.return_value = expected_paths

        # Act: Scaffold GET process
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        result_paths = process_handler._build_scaffold_get(
            build_context, input_params, framework_params
        )

        # Assert: Verify scaffold method called correctly
        assert result_paths == expected_paths
        mock_workspace.scaffold_get_process.assert_called_once()

        # Verify call arguments
        call_args = mock_workspace.scaffold_get_process.call_args
        assert call_args[0][0] == build_context.bundle_root  # bundle_root
        assert call_args[0][1] == "get-ticket"  # get_proc

        # Verify sections_json structure
        sections_json = call_args[0][2]
        sections_data = json.loads(sections_json)
        assert "sections" in sections_data
        assert "description" in sections_data["sections"]
        assert "plan" in sections_data["sections"]
        assert (
            sections_data["sections"]["description"]["description"]
            == "High-level summary of the ticket request."
        )
        assert (
            sections_data["sections"]["context"]["description"]
            == "Context captured during the initial planning flow."
        )
        assert "placeholder" in sections_data

    def test_build_scaffold_get_sections_markers(
        self, process_handler, mock_workspace, build_context
    ):
        """Test GET process generates correct section markers."""
        # Arrange: Configure mock workspace response
        mock_workspace.scaffold_get_process.return_value = []

        # Act: Scaffold GET process
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        process_handler._build_scaffold_get(
            build_context, input_params, framework_params
        )

        # Assert: Verify section markers in call arguments
        call_args = mock_workspace.scaffold_get_process.call_args
        sections_json = call_args[0][2]
        sections_data = json.loads(sections_json)

        # Verify marker structure
        description_markers = sections_data["sections"]["description"]
        assert description_markers["start"] == "<!-- SECTION:START:DESCRIPTION -->"
        assert description_markers["end"] == "<!-- SECTION:END:DESCRIPTION -->"

        plan_markers = sections_data["sections"]["plan"]
        assert plan_markers["start"] == "<!-- SECTION:START:PLAN -->"
        assert plan_markers["end"] == "<!-- SECTION:END:PLAN -->"


class TestBuildScaffoldUpdates:
    """Unit tests for _build_scaffold_updates method."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def process_handler(self, mock_workspace):
        """Create ProcessHandler with mocked workspace."""
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_context(self):
        """Create valid BuildContext for testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["context", "description", "plan", "notes"],
            initial_section="description",
            section_defs={
                "context": {
                    "template": "",
                    "schema": {},
                    "description": "Context captured during the initial planning flow.",
                },
                "description": {
                    "template": "# {{ title }}\n\n<!-- body -->\n",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "High-level summary of the ticket request.",
                },
                "plan": {
                    "template": "## Plan\\n{{ plan_detail }}\\n",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                    "description": "Implementation plan outlining next steps.",
                },
                "notes": {
                    "template": "## Notes\\n{{ notes }}\\n",
                    "schema": {"properties": {"notes": {"type": "string"}}},
                    "description": "Additional commentary and observations.",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={"update": {"allow": ["test-actor"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    def test_build_scaffold_updates_success(
        self, process_handler, mock_workspace, build_context
    ):
        """Test successful UPDATE processes scaffolding."""
        # Arrange: Configure mock workspace response
        expected_paths = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "update-ticket",
                "artifact",
                "patch.md",
            )
        ]
        mock_workspace.scaffold_update_process.return_value = expected_paths
        mock_workspace.save_artifact.side_effect = lambda content, path: path

        # Act: Scaffold UPDATE processes
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        mock_compiled_schema = {
            "properties": {
                "target_team": {"type": "string"},
                "artifact": {"type": "string"},
                "sections": {"type": "array"},
                "initial_section": {"type": "string"},
            }
        }
        result_paths, process_names = process_handler._build_scaffold_updates(
            build_context, input_params, framework_params, mock_compiled_schema
        )

        assert process_names == ["update-ticket"]
        assert mock_workspace.scaffold_update_process.call_count == 1

    def test_build_scaffold_updates_semantic_refs(
        self, process_handler, mock_workspace, build_context
    ):
        """Test UPDATE processes use correct semantic import statements."""
        # Arrange: Configure mock workspace response
        mock_workspace.scaffold_update_process.return_value = []
        mock_workspace.save_artifact.side_effect = lambda content, path: path

        # Act: Scaffold UPDATE processes
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        mock_compiled_schema = {
            "properties": {
                "target_team": {"type": "string"},
                "artifact": {"type": "string"},
                "sections": {"type": "array"},
                "initial_section": {"type": "string"},
            }
        }
        process_handler._build_scaffold_updates(
            build_context, input_params, framework_params, mock_compiled_schema
        )

        # Assert: Verify semantic URI references in call arguments
        call_args = mock_workspace.scaffold_update_process.call_args
        assert call_args[0][1] == "update-ticket"
        assert call_args[0][2] == 'import "artifact-sections://get-ticket"'
        assert call_args[0][3] == 'import "artifact-locator://get-ticket"'
        assert call_args[0][4] == 'import "artifact-parser://get-ticket"'
        assert "{% include snippet ignore missing %}" in call_args[0][5]

    def test_build_scaffold_updates_creates_placeholders_for_missing_templates(
        self, process_handler, mock_workspace, build_context
    ):
        """Sections without templates receive placeholder snippet content."""
        # Arrange: Configure mock workspace response
        mock_workspace.scaffold_update_process.return_value = []
        mock_workspace.save_artifact.side_effect = lambda content, path: path

        # Act: Scaffold UPDATE processes
        input_params = {"artifact": "ticket"}
        framework_params = make_framework_params("build-team-process", "test-actor")
        mock_compiled_schema = {
            "properties": {
                "target_team": {"type": "string"},
                "artifact": {"type": "string"},
                "sections": {"type": "array"},
                "initial_section": {"type": "string"},
            }
        }
        result_paths, _ = process_handler._build_scaffold_updates(
            build_context, input_params, framework_params, mock_compiled_schema
        )

        placeholder_paths = [
            path
            for path in result_paths
            if path.parts[-3:] == ("artifact", "sections", "description.md")
        ]
        assert placeholder_paths, "expected placeholder snippet for description"


class TestSerializePermissions:
    """Unit tests for _serialize_permissions helper method."""

    @pytest.fixture
    def process_handler(self):
        """Create ProcessHandler for testing helper method."""
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    def test_serialize_permissions_valid_permission(self, process_handler):
        """Test serializing valid permission configuration."""
        # Arrange: Valid permissions dictionary
        permissions = {
            "create": {"allow": ["test-actor"], "deny": []},
            "get": {"allow": ["test-actor"], "deny": []},
            "update": {"allow": ["test-actor"], "deny": []},
        }

        # Act: Serialize CREATE permissions
        result = process_handler._serialize_permissions(permissions, "create")

        # Assert: Verify JSON serialization
        assert result is not None
        parsed = json.loads(result)
        assert parsed["allow"] == ["test-actor"]
        assert parsed["deny"] == []

    def test_serialize_permissions_missing_permission(self, process_handler):
        """Test serializing missing permission returns None."""
        # Arrange: Permissions without 'delete' permission
        permissions = {
            "create": {"allow": ["test-actor"]},
            "get": {"allow": ["test-actor"]},
        }

        # Act: Try to serialize missing permission
        result = process_handler._serialize_permissions(permissions, "delete")

        # Assert: Verify None returned for missing permission
        assert result is None

    def test_serialize_permissions_invalid_dict(self, process_handler):
        """Test serializing with invalid permissions dictionary."""
        # Arrange: Invalid permissions (not a dict)
        permissions = "not-a-dict"

        # Act: Try to serialize from invalid permissions
        result = process_handler._serialize_permissions(permissions, "create")

        # Assert: Verify None returned for invalid input
        assert result is None


class TestBuildModeComplete:
    """Tests for complete build mode functionality."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_artifact_engine(self):
        """Create mock artifact engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def mock_rae_engine(self):
        """Create mock RAE engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def process_handler(self, mock_workspace, mock_artifact_engine, mock_rae_engine):
        """Create ProcessHandler with all dependencies mocked."""
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def complete_build_context(self):
        """Create valid BuildContext for complete mode testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["context", "description", "plan"],
            initial_section="description",
            section_defs={
                "description": {
                    "template": "# {{ title }}\\n\\n<!-- body -->\\n",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "High-level summary of the ticket request.",
                },
                "plan": {
                    "template": "## Plan\\n{{ plan_detail }}\\n",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                    "description": "Implementation plan outlining next steps.",
                },
                "context": {
                    "template": "## Context\\n{{ introduction }}\\n",
                    "schema": {"properties": {"introduction": {"type": "string"}}},
                    "description": "Context captured during the initial planning flow.",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={
                "create": {"allow": ["creator"]},
                "update": {"allow": ["updater"]},
            },
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    def test_complete_mode_scaffolds_has_updates(
        self, process_handler, complete_build_context, mock_workspace
    ):
        """Test that complete mode also generates UPDATE processes."""
        input_params = {}
        framework_params = make_framework_params("build-team-process", "test-actor")
        compiled_schema = {}

        mock_workspace.scaffold_update_process.return_value = []
        mock_workspace.save_artifact.side_effect = lambda content, path: path

        # Act
        created_paths, process_names = process_handler._build_scaffold_updates(
            complete_build_context, input_params, framework_params, compiled_schema
        )

        # Assert - UPDATE process should still be created in complete mode
        assert process_names == ["update-ticket"]
        mock_workspace.scaffold_update_process.assert_called_once()

    def test_complete_mode_renders_all_sections_in_create(
        self, process_handler, complete_build_context, mock_workspace
    ):
        """Test that complete mode uses modular generation with semantic URI includes."""
        input_params = {}
        framework_params = make_framework_params("build-team-process", "test-actor")

        # Configure mocks
        mock_workspace.scaffold_create_process.return_value = [PantheonPath("test")]

        # Act
        process_handler._build_scaffold_create(
            complete_build_context, input_params, framework_params, "complete"
        )

        # Assert - scaffold_create_process was called
        mock_workspace.scaffold_create_process.assert_called_once()

        # Get the content.md that was passed to scaffold_create_process
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]  # Third positional argument is content_md

        # Multi-section builds use modular generation with toggle variables
        # Verify toggle variables are present for all sections
        assert "{% set _include_context" in content_md
        assert "{% set _include_description" in content_md
        assert "{% set _include_plan" in content_md

        # Verify semantic URI includes are used instead of inline templates (using single quotes in Jinja2)
        assert "{% include 'artifact-template://update-ticket/sections/" in content_md

    def test_complete_mode_merges_all_schemas(
        self, process_handler, complete_build_context, mock_workspace
    ):
        """Test that complete mode uses modular generation with Jsonnet imports."""
        input_params = {}
        framework_params = make_framework_params("build-team-process", "test-actor")

        # Configure mocks
        mock_workspace.scaffold_create_process.return_value = [PantheonPath("test")]

        # Act
        process_handler._build_scaffold_create(
            complete_build_context, input_params, framework_params, "complete"
        )

        # Assert - scaffold_create_process was called
        mock_workspace.scaffold_create_process.assert_called_once()

        # Get the schema that was passed to scaffold_create_process
        call_args = mock_workspace.scaffold_create_process.call_args
        schema_jsonnet = call_args[0][5]  # Sixth positional argument is schema_jsonnet

        # Multi-section builds use Jsonnet with semantic URI imports
        # Verify imports for all sections are present
        assert (
            'import "process-schema://update-ticket/sections/context"' in schema_jsonnet
        )
        assert (
            'import "process-schema://update-ticket/sections/description"'
            in schema_jsonnet
        )
        assert 'import "process-schema://update-ticket/sections/plan"' in schema_jsonnet

        # Verify object-based array structure with std.foldl composition
        assert "local sections = [" in schema_jsonnet
        assert 'name: "context"' in schema_jsonnet
        assert 'name: "description"' in schema_jsonnet
        assert 'name: "plan"' in schema_jsonnet
        assert "local properties = std.foldl(" in schema_jsonnet
        assert "local required = std.foldl(" in schema_jsonnet

    def test_complete_mode_merges_permissions(self, process_handler):
        """Test that complete mode merges create and update permissions."""
        permissions_dict = {
            "create": {"allow": ["creator1"], "deny": ["denied1"]},
            "update": {"allow": ["updater1", "creator1"], "deny": ["denied2"]},
        }

        # Act
        result = process_handler._merge_permissions_for_complete_mode(permissions_dict)

        # Assert - permissions are merged with no duplicates
        assert result is not None
        assert set(result["allow"]) == {"creator1", "updater1"}
        assert set(result["deny"]) == {"denied1", "denied2"}

    def test_merge_permissions_handles_empty_perms(self, process_handler):
        """Test permission merging with empty or missing permissions."""
        # Test with empty dict
        result = process_handler._merge_permissions_for_complete_mode({})
        assert result is None

        # Test with only create permissions
        permissions_dict = {"create": {"allow": ["creator"], "deny": []}}
        result = process_handler._merge_permissions_for_complete_mode(permissions_dict)
        assert result["allow"] == ["creator"]
        assert result["deny"] == []

        # Test with only update permissions
        permissions_dict = {"update": {"allow": ["updater"], "deny": []}}
        result = process_handler._merge_permissions_for_complete_mode(permissions_dict)
        assert result["allow"] == ["updater"]
        assert result["deny"] == []
