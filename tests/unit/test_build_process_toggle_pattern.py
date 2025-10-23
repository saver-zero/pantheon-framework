"""Unit tests for BUILD process toggle pattern refactoring.

Tests verify that build_mode parameter controls toggle defaults in generated
schemas and templates, while the rendering mechanism remains constant regardless
of build_mode value.
"""

from unittest.mock import Mock

import pytest

from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessHandler, _BuildContext
from tests.helpers.process_input import make_framework_params, make_process_input


class TestBuildModeToggleDefaults:
    """Tests for build_mode parameter controlling toggle defaults."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        mock_ws = Mock()
        # Setup minimal responses for BUILD detection
        mock_ws.get_process_routine.return_value = "# routine"
        mock_ws.has_process_redirect.return_value = False
        mock_ws.get_artifact_patch_template.side_effect = FileNotFoundError()
        mock_ws.get_artifact_content_template.side_effect = FileNotFoundError()
        mock_ws.has_build_schema.return_value = True
        mock_ws.get_process_directory_template.return_value = "test-builds"
        mock_ws.get_process_schema.return_value = "import 'build-schema.jsonnet'"
        mock_ws.get_team_profile.return_value = "{}"
        mock_ws.get_context_schema.return_value = (
            '{"type": "object", "properties": {"introduction": {"type": "string"}}}'
        )
        mock_ws.get_context_template.return_value = "## Context\\n\\n{{ introduction }}"
        return mock_ws

    @pytest.fixture
    def mock_engine(self):
        """Create mock artifact engine for dependency injection."""
        mock_eng = Mock()
        mock_eng.compile_schema.return_value = {
            "properties": {
                "target_team": {"type": "string"},
                "artifact": {"type": "string"},
                "build_mode": {"type": "string"},
                "artifact_sections": {"type": "array"},
                "initial_section": {"type": "string"},
                "section_template": {"type": "array"},
                "artifact_location": {"type": "object"},
            }
        }
        mock_eng.validate.return_value = True
        mock_eng._create_template_context.side_effect = (
            lambda input_params, framework_params, op=None: {
                **input_params,
                **framework_params,
            }
        )
        mock_eng.render_template.return_value = "test-builds"
        return mock_eng

    @pytest.fixture
    def mock_rae(self):
        """Create mock RAE engine for dependency injection."""
        return Mock()

    @pytest.fixture
    def saved_artifacts_fixture(self, mock_workspace):
        """Configure mock workspace to capture saved artifacts."""
        saved_artifacts = []

        def _save_artifact(content: str, path: PantheonPath) -> PantheonPath:
            saved_artifacts.append((content, path))
            return path

        mock_workspace.save_artifact.side_effect = _save_artifact
        mock_workspace.scaffold_create_process.return_value = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "create-ticket",
                "artifact",
                "content.md",
            )
        ]
        mock_workspace.scaffold_get_process.return_value = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "get-ticket",
                "artifact",
                "sections.jsonnet",
            )
        ]
        mock_workspace.scaffold_update_process.return_value = [
            PantheonPath(
                "test-builds",
                "test-team",
                "processes",
                "update-ticket",
                "artifact",
                "patch.md",
            )
        ]
        mock_workspace.summarize_created_files.return_value = []
        return saved_artifacts

    @pytest.fixture
    def build_params(self):
        """Create base build parameters for testing."""
        return {
            "target_team": "test-team",
            "artifact": "ticket",
            "include_context": True,
            "artifact_sections": ["description", "plan"],
            "initial_section": "description",
            "section_template": [
                {
                    "section": "description",
                    "section_description": "Description section",
                    "template": "# {{ title }}",
                    "schema": {"properties": {"title": {"type": "string"}}},
                },
                {
                    "section": "plan",
                    "section_description": "Plan section",
                    "template": "## Plan\\n{{ plan_detail }}",
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

    def test_build_process_execution_with_complete_mode(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test BUILD process execution completes successfully with build_mode='complete'."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "complete"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        result = handler.execute(input_data)

        # Assert
        assert result["success"] is True
        assert "BUILD" in result["output"]

    def test_build_process_execution_with_modular_mode(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test BUILD process execution completes successfully with build_mode='modular'."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "modular"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        result = handler.execute(input_data)

        # Assert
        assert result["success"] is True
        assert "BUILD" in result["output"]

    def test_complete_mode_sets_all_enabled_flags_true_in_schema(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test build_mode='complete' sets all enabled flags to true in generated schemas."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "complete"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        handler.execute(input_data)

        # Assert - inspect generated schema content
        schema_contents = [
            content
            for content, path in saved_artifacts_fixture
            if str(path).endswith(".schema.jsonnet")
        ]
        assert len(schema_contents) > 0, "Expected schema files to be generated"

        # Check that schemas contain enabled flags with true values for complete mode
        for schema_content in schema_contents:
            # Complete mode should have all sections enabled
            if "enabled:" in schema_content or "enabled :" in schema_content:
                # Schema should use enabled: true for complete mode
                assert (
                    "enabled: true" in schema_content
                    or "enabled:true" in schema_content
                )

    def test_modular_mode_sets_only_initial_enabled_flag_true_in_schema(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test build_mode='modular' sets only initial section enabled flag to true in generated schemas."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "modular"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        handler.execute(input_data)

        # Assert - inspect generated schema content
        schema_contents = [
            content
            for content, path in saved_artifacts_fixture
            if str(path).endswith(".schema.jsonnet")
        ]
        assert len(schema_contents) > 0, "Expected schema files to be generated"

        # Check that schemas contain enabled flags with appropriate boolean values for modular mode
        for schema_content in schema_contents:
            if "enabled:" in schema_content or "enabled :" in schema_content:
                # Modular mode should have mix of enabled: true (initial) and enabled: false (others)
                assert (
                    "enabled: true" in schema_content
                    or "enabled:true" in schema_content
                )
                assert (
                    "enabled: false" in schema_content
                    or "enabled:false" in schema_content
                )

    def test_complete_mode_sets_all_include_variables_true_in_template(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test build_mode='complete' sets all _include_* variables to true in generated templates."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "complete"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        handler.execute(input_data)

        # Assert - inspect generated content.md
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Complete mode should set all _include_* variables to true
        assert "{% set _include_description = true %}" in content_md
        assert "{% set _include_plan = true %}" in content_md

    def test_modular_mode_sets_only_initial_include_variable_true_in_template(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
    ):
        """Test build_mode='modular' sets only initial section _include_* variable to true in generated templates."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "modular"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        handler.execute(input_data)

        # Assert - inspect generated content.md
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Modular mode should set only initial section _include_* to true
        assert "{% set _include_description = true %}" in content_md  # initial_section
        assert "{% set _include_plan = false %}" in content_md  # non-initial section

    @pytest.mark.parametrize(
        "build_mode,expected_description_enabled,expected_plan_enabled",
        [
            ("complete", True, True),
            ("modular", True, False),  # description is initial_section
        ],
    )
    def test_both_modes_generate_toggle_pattern_with_different_defaults(
        self,
        mock_workspace,
        mock_engine,
        mock_rae,
        saved_artifacts_fixture,
        build_params,
        build_mode,
        expected_description_enabled,
        expected_plan_enabled,
    ):
        """Test both complete and modular modes generate toggle pattern with appropriate defaults."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": build_mode}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        handler.execute(input_data)

        # Assert - check template toggle variables
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        expected_description_str = "true" if expected_description_enabled else "false"
        expected_plan_str = "true" if expected_plan_enabled else "false"

        assert (
            f"{{% set _include_description = {expected_description_str} %}}"
            in content_md
        )
        assert f"{{% set _include_plan = {expected_plan_str} %}}" in content_md

        # Verify conditional blocks are present regardless of mode
        assert "{% if _include_description %}" in content_md
        assert "{% if _include_plan %}" in content_md

    def test_invalid_build_mode_value_is_rejected(
        self, mock_workspace, mock_engine, mock_rae, build_params
    ):
        """Test BUILD process rejects invalid build_mode parameter values with clear error message."""
        # Arrange
        handler = ProcessHandler(mock_workspace, mock_engine, mock_rae)
        parameters = {**build_params, "build_mode": "invalid_mode"}
        input_data = make_process_input(
            "build-team-process", "test-actor", input_params=parameters
        )

        # Act
        result = handler.execute(input_data)

        # Assert
        assert result["success"] is False
        assert "build_mode" in result["error"].lower()
        # Error message should indicate valid values
        assert (
            "complete" in result["error"].lower()
            or "modular" in result["error"].lower()
        )


class TestTogglePatternVerification:
    """Tests verifying toggle pattern structure in generated artifacts."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for dependency injection."""
        mock_ws = Mock()
        mock_ws.scaffold_create_process.return_value = [PantheonPath("test")]
        return mock_ws

    @pytest.fixture
    def process_handler(self, mock_workspace):
        """Create ProcessHandler with mocked workspace."""
        mock_engine = Mock()
        mock_rae = Mock()
        return ProcessHandler(mock_workspace, mock_engine, mock_rae)

    @pytest.fixture
    def build_context_complete(self):
        """Create BuildContext for complete mode testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["description", "plan"],
            initial_section="description",
            section_defs={
                "description": {
                    "template": "# {{ title }}",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "Description section",
                },
                "plan": {
                    "template": "## Plan\\n{{ plan_detail }}",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                    "description": "Plan section",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={"create": {"allow": ["test-actor"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    @pytest.fixture
    def build_context_modular(self):
        """Create BuildContext for modular mode testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="ticket",
            sections=["description", "plan"],
            initial_section="description",
            section_defs={
                "description": {
                    "template": "# {{ title }}",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "Description section",
                },
                "plan": {
                    "template": "## Plan\\n{{ plan_detail }}",
                    "schema": {"properties": {"plan_detail": {"type": "string"}}},
                    "description": "Plan section",
                },
            },
            placement="tickets/",
            naming="T{{ pantheon_artifact_id }}_{{ title | slugify }}.md",
            permissions={"create": {"allow": ["test-actor"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-ticket",
            get_proc="get-ticket",
        )

    def test_toggle_pattern_structure_complete_mode(
        self, process_handler, mock_workspace, build_context_complete
    ):
        """Test toggle pattern structure is correctly generated for complete mode."""
        # Arrange
        input_params = {}
        framework_params = make_framework_params("build-team-process", "test-actor")

        # Act
        process_handler._build_scaffold_create(
            build_context_complete, input_params, framework_params, "complete"
        )

        # Assert
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Verify toggle variable declarations with true defaults
        assert "{% set _include_description = true %}" in content_md
        assert "{% set _include_plan = true %}" in content_md

        # Verify conditional blocks wrap sections
        assert "{% if _include_description %}" in content_md
        assert "{% if _include_plan %}" in content_md

        # Verify section markers are present
        assert "<!-- SECTION:START:DESCRIPTION -->" in content_md
        assert "<!-- SECTION:END:DESCRIPTION -->" in content_md
        assert "<!-- SECTION:START:PLAN -->" in content_md
        assert "<!-- SECTION:END:PLAN -->" in content_md

    def test_toggle_pattern_structure_modular_mode(
        self, process_handler, mock_workspace, build_context_modular
    ):
        """Test toggle pattern structure is correctly generated for modular mode."""
        # Arrange
        input_params = {}
        framework_params = make_framework_params("build-team-process", "test-actor")

        # Act
        process_handler._build_scaffold_create(
            build_context_modular, input_params, framework_params, "modular"
        )

        # Assert
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Verify toggle variable declarations with appropriate defaults
        assert "{% set _include_description = true %}" in content_md  # initial section
        assert "{% set _include_plan = false %}" in content_md  # non-initial section

        # Verify conditional blocks wrap sections (same structure regardless of mode)
        assert "{% if _include_description %}" in content_md
        assert "{% if _include_plan %}" in content_md

        # Verify section markers are present (same structure regardless of mode)
        assert "<!-- SECTION:START:DESCRIPTION -->" in content_md
        assert "<!-- SECTION:END:DESCRIPTION -->" in content_md
        assert "<!-- SECTION:START:PLAN -->" in content_md
        assert "<!-- SECTION:END:PLAN -->" in content_md
