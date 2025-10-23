"""Unit tests for BUILD process modular multi-section artifact scaffolding.

Tests the enhancement to BUILD process that automatically generates CREATE processes
with conditional section toggles, semantic URI imports, and variable naming conversions
for modular artifact scaffolding without section definition duplication.
"""

from unittest.mock import Mock

import pytest

from pantheon.path import PantheonPath
from pantheon.process_handler import ProcessHandler, _BuildContext
from tests.helpers.process_input import make_framework_params


class TestSectionNamingConversion:
    """Unit tests for section name to variable name conversion utilities."""

    @pytest.fixture
    def process_handler(self):
        """Create ProcessHandler with mocked dependencies."""
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.mark.parametrize(
        "section_name,expected_template_var",
        [
            ("high-level-overview", "_include_high_level_overview"),
            ("project-context", "_include_project_context"),
            ("single", "_include_single"),
            ("multi-word-section", "_include_multi_word_section"),
        ],
    )
    def test_section_name_to_template_variable(
        self, process_handler, section_name, expected_template_var
    ):
        """Test conversion of hyphenated section names to underscore-prefixed template variables."""
        result = process_handler._section_name_to_template_variable(section_name)
        assert result == expected_template_var

    @pytest.mark.parametrize(
        "section_name,expected_constant",
        [
            ("high-level-overview", "HIGH_LEVEL_OVERVIEW"),
            ("project-context", "PROJECT_CONTEXT"),
            ("single", "SINGLE"),
            ("multi-word-section", "MULTI_WORD_SECTION"),
        ],
    )
    def test_section_name_to_constant_case(
        self, process_handler, section_name, expected_constant
    ):
        """Test conversion of hyphenated section names to CONSTANT_CASE for HTML markers."""
        result = process_handler._section_name_to_constant_case(section_name)
        assert result == expected_constant


class TestModularSchemaGeneration:
    """Unit tests for modular CREATE schema generation with semantic URI imports."""

    @pytest.fixture
    def process_handler(self):
        """Create ProcessHandler with mocked dependencies."""
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_context_with_sections(self):
        """Create BuildContext with multiple sections for modular testing."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="guide",
            sections=["high-level-overview", "core-principles", "implementation"],
            initial_section="high-level-overview",
            section_defs={
                "high-level-overview": {
                    "template": "## Overview\n{{ overview_text }}",
                    "schema": {"properties": {"overview_text": {"type": "string"}}},
                    "description": "High-level overview section",
                },
                "core-principles": {
                    "template": "## Principles\n{{ principles }}",
                    "schema": {"properties": {"principles": {"type": "string"}}},
                    "description": "Core principles section",
                },
                "implementation": {
                    "template": "## Implementation\n{{ impl_details }}",
                    "schema": {"properties": {"impl_details": {"type": "string"}}},
                    "description": "Implementation details section",
                },
            },
            placement="docs/",
            naming="guide.md",
            permissions={"create": {"allow": ["tech-lead"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-guide",
            get_proc="get-guide",
        )

    def test_generate_modular_schema_with_semantic_imports(
        self, process_handler, build_context_with_sections
    ):
        """Test modular schema generation includes process-schema:// imports."""
        schema_jsonnet = process_handler._generate_modular_create_schema(
            build_context_with_sections, "modular"
        )

        # Verify sections array with name/schema/enabled objects
        assert "local sections = [" in schema_jsonnet
        assert 'name: "high-level-overview"' in schema_jsonnet
        assert 'name: "core-principles"' in schema_jsonnet
        assert 'name: "implementation"' in schema_jsonnet

        # Verify semantic URI imports in schema field
        assert (
            'schema: import "process-schema://update-guide/sections/high-level-overview"'
            in schema_jsonnet
        )
        assert (
            'schema: import "process-schema://update-guide/sections/core-principles"'
            in schema_jsonnet
        )
        assert (
            'schema: import "process-schema://update-guide/sections/implementation"'
            in schema_jsonnet
        )

    def test_generate_modular_schema_with_toggle_variables(
        self, process_handler, build_context_with_sections
    ):
        """Test modular schema uses std.foldl for properties and required composition."""
        schema_jsonnet = process_handler._generate_modular_create_schema(
            build_context_with_sections, "modular"
        )

        # Verify std.foldl is used for properties composition
        assert "local properties = std.foldl(" in schema_jsonnet

        # Verify std.foldl is used for required array composition
        assert "local required = std.foldl(" in schema_jsonnet

        # Verify enabled flag is checked in accumulator function
        assert "sec.enabled" in schema_jsonnet or "if sec.enabled" in schema_jsonnet

        # Verify first section has enabled: true
        assert "enabled: true" in schema_jsonnet

    def test_generate_modular_schema_with_conditional_composition(
        self, process_handler, build_context_with_sections
    ):
        """Test modular schema uses std.foldl with accumulator for conditional composition."""
        schema_jsonnet = process_handler._generate_modular_create_schema(
            build_context_with_sections, "modular"
        )

        # Verify accumulator function structure for properties
        assert (
            "function(acc, sec)" in schema_jsonnet
            or "function (acc, sec)" in schema_jsonnet
        )

        # Verify accumulator uses enabled field check
        assert "if sec.enabled" in schema_jsonnet

        # Verify accumulator merges properties
        assert (
            "acc + sec.schema.properties" in schema_jsonnet
            or "sec.schema.properties" in schema_jsonnet
        )

        # Verify sections array is folded
        assert "sections" in schema_jsonnet

    def test_generate_modular_schema_guards_missing_required_field(
        self, process_handler
    ):
        """Test modular schema handles sections without required field using std.objectHas guard."""
        # Create context with section that has NO required field
        ctx = _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="guide",
            sections=["optional-section"],
            initial_section="optional-section",
            section_defs={
                "optional-section": {
                    "template": "## Optional\n{{ content }}",
                    "schema": {
                        "properties": {"content": {"type": "string"}}
                        # Note: NO 'required' field in schema
                    },
                    "description": "Optional section with no required fields",
                },
            },
            placement="docs/",
            naming="guide.md",
            permissions={"create": {"allow": ["tech-lead"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-guide",
            get_proc="get-guide",
        )

        schema_jsonnet = process_handler._generate_modular_create_schema(ctx, "modular")

        # Verify guard logic includes std.objectHas check
        assert "std.objectHas(sec.schema, 'required')" in schema_jsonnet

        # Verify multi-line conditional structure
        assert (
            "if sec.enabled && std.objectHas(sec.schema, 'required')" in schema_jsonnet
        )
        assert "then acc + sec.schema.required" in schema_jsonnet
        assert "else acc," in schema_jsonnet


class TestModularTemplateGeneration:
    """Unit tests for modular CREATE template generation with artifact-template:// includes."""

    @pytest.fixture
    def process_handler(self):
        """Create ProcessHandler with mocked dependencies."""
        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_rae_engine = Mock()
        return ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

    @pytest.fixture
    def build_context_with_sections(self):
        """Create BuildContext with multiple sections."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="guide",
            sections=["high-level-overview", "core-principles"],
            initial_section="high-level-overview",
            section_defs={
                "high-level-overview": {
                    "template": "## Overview\n{{ text }}",
                    "schema": {"properties": {"text": {"type": "string"}}},
                    "description": "Overview section",
                },
                "core-principles": {
                    "template": "## Principles\n{{ content }}",
                    "schema": {"properties": {"content": {"type": "string"}}},
                    "description": "Principles section",
                },
            },
            placement="docs/",
            naming="guide.md",
            permissions={"create": {"allow": ["tech-lead"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-guide",
            get_proc="get-guide",
        )

    def test_generate_modular_template_with_frontmatter(
        self, process_handler, build_context_with_sections
    ):
        """Test modular template includes YAML frontmatter with built-in variables."""
        template_md = process_handler._generate_modular_create_template(
            build_context_with_sections, "modular"
        )

        # Verify frontmatter with pantheon built-in variables
        assert "---" in template_md
        assert "created_at: {{ pantheon_timestamp }}" in template_md
        assert "created_by: {{ pantheon_actor }}" in template_md

    def test_generate_modular_template_with_toggle_set_statements(
        self, process_handler, build_context_with_sections
    ):
        """Test modular template includes Jinja2 set statements for section toggles."""
        template_md = process_handler._generate_modular_create_template(
            build_context_with_sections, "modular"
        )

        # Verify set statements with first section true, rest false
        # Implementation uses simple boolean values, not schema variable references
        assert "{% set _include_high_level_overview = true %}" in template_md
        assert "{% set _include_core_principles = false %}" in template_md

    def test_generate_modular_template_with_conditional_sections(
        self, process_handler, build_context_with_sections
    ):
        """Test modular template includes conditional blocks for section includes."""
        template_md = process_handler._generate_modular_create_template(
            build_context_with_sections, "modular"
        )

        # Verify conditional section blocks
        assert "{% if _include_high_level_overview %}" in template_md
        # Implementation uses single quotes for Jinja2 include statements
        assert (
            "{% include 'artifact-template://update-guide/sections/high-level-overview' %}"
            in template_md
        )
        assert "{% else %}" in template_md
        assert "<!-- SECTION:PLACEHOLDER -->" in template_md
        assert "{% endif %}" in template_md

    def test_generate_modular_template_with_html_markers(
        self, process_handler, build_context_with_sections
    ):
        """Test modular template includes HTML comment markers in CONSTANT_CASE."""
        template_md = process_handler._generate_modular_create_template(
            build_context_with_sections, "modular"
        )

        # Verify HTML comment markers using CONSTANT_CASE conversion
        assert "<!-- SECTION:START:HIGH_LEVEL_OVERVIEW -->" in template_md
        assert "<!-- SECTION:END:HIGH_LEVEL_OVERVIEW -->" in template_md
        assert "<!-- SECTION:START:CORE_PRINCIPLES -->" in template_md
        assert "<!-- SECTION:END:CORE_PRINCIPLES -->" in template_md


class TestBuildProcessModularBranching:
    """Unit tests for BUILD process branching to modular generation when sections present."""

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
    def build_context_with_sections(self):
        """Create BuildContext with sections for modular build."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="guide",
            sections=["overview", "details"],
            initial_section="overview",
            section_defs={
                "overview": {
                    "template": "## Overview",
                    "schema": {"properties": {"text": {"type": "string"}}},
                    "description": "Overview section",
                },
                "details": {
                    "template": "## Details",
                    "schema": {"properties": {"content": {"type": "string"}}},
                    "description": "Details section",
                },
            },
            placement="docs/",
            naming="guide.md",
            permissions={"create": {"allow": ["tech-lead"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-guide",
            get_proc="get-guide",
        )

    @pytest.fixture
    def build_context_without_sections(self):
        """Create BuildContext without sections for standard build."""
        return _BuildContext(
            process_name="build-team-process",
            target_team="test-team",
            artifact="simple",
            sections=["content"],
            initial_section="content",
            section_defs={
                "content": {
                    "template": "# {{ title }}",
                    "schema": {"properties": {"title": {"type": "string"}}},
                    "description": "Main content",
                }
            },
            placement="docs/",
            naming="simple.md",
            permissions={"create": {"allow": ["tech-lead"]}},
            bundle_root=PantheonPath("test-builds", "test-team", "processes"),
            create_proc="create-simple",
            get_proc="get-simple",
        )

    def test_scaffold_create_uses_modular_generation_with_sections(
        self, process_handler, mock_workspace, build_context_with_sections
    ):
        """Test BUILD scaffolds CREATE with modular generation when sections present."""
        # Arrange
        mock_workspace.scaffold_create_process.return_value = [PantheonPath("test")]

        input_params = {"artifact": "guide"}
        framework_params = make_framework_params("build-team-process", "tech-lead")

        # Act
        process_handler._build_scaffold_create(
            build_context_with_sections, input_params, framework_params, "modular"
        )

        # Assert: Verify modular schema was generated
        call_args = mock_workspace.scaffold_create_process.call_args
        schema_json = call_args[0][5]

        # Should contain sections array with object-based structure
        assert "local sections = [" in schema_json or 'name: "overview"' in schema_json

    def test_scaffold_create_detects_multi_section_build(
        self, process_handler, mock_workspace, build_context_with_sections
    ):
        """Test BUILD detects multi-section builds via build_context.sections."""
        # Arrange
        mock_workspace.scaffold_create_process.return_value = [PantheonPath("test")]

        input_params = {"artifact": "guide"}
        framework_params = make_framework_params("build-team-process", "tech-lead")

        # Act
        process_handler._build_scaffold_create(
            build_context_with_sections, input_params, framework_params, "modular"
        )

        # Assert: Verify modular template was generated
        call_args = mock_workspace.scaffold_create_process.call_args
        content_md = call_args[0][2]

        # Should contain conditional section includes
        assert "{% if " in content_md or "artifact-template://" in content_md


class TestSemanticUriSectionResolution:
    """Unit tests for semantic URI resolution with section sub-paths."""

    @pytest.fixture
    def mock_workspace(self):
        """Create mock workspace for testing URI resolution."""
        return Mock()

    def test_process_schema_uri_with_section_subpath(self, mock_workspace):
        """Test process-schema:// URI correctly resolves section sub-paths."""
        # Arrange
        uri = "process-schema://update-guide/sections/core-principles"
        expected_content = '{"properties": {"principles": {"type": "string"}}}'
        mock_workspace.get_resolved_content.return_value = expected_content

        # Act
        result = mock_workspace.get_resolved_content(uri)

        # Assert
        assert result == expected_content
        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_artifact_template_uri_with_section_subpath(self, mock_workspace):
        """Test artifact-template:// URI correctly resolves section includes."""
        # Arrange
        uri = "artifact-template://update-guide/sections/high-level-overview"
        expected_content = "## High-Level Overview\n\n{{ overview_text }}"
        mock_workspace.get_resolved_content.return_value = expected_content

        # Act
        result = mock_workspace.get_resolved_content(uri)

        # Assert
        assert result == expected_content
        mock_workspace.get_resolved_content.assert_called_once_with(uri)

    def test_semantic_uri_section_resolution_with_multiple_segments(
        self, mock_workspace
    ):
        """Test semantic URI correctly handles multi-segment section paths."""
        # Arrange
        uri = "process-schema://update-architecture-guide/sections/convention-over-configuration"
        expected_content = '{"properties": {"description": {"type": "string"}}}'
        mock_workspace.get_resolved_content.return_value = expected_content

        # Act
        result = mock_workspace.get_resolved_content(uri)

        # Assert
        assert result == expected_content
        mock_workspace.get_resolved_content.assert_called_once_with(uri)
