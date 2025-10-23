"""
Unit tests for ArtifactEngine behavior specification.

This test module defines the expected behavior of ArtifactEngine methods
through concrete test cases that specify what each method should accomplish.
These tests will naturally fail until the methods are properly implemented.
"""

import json
from unittest.mock import Mock, patch

import pytest

from pantheon.artifact_engine import ArtifactEngine
from pantheon.path import PantheonPath
from pantheon.workspace import PantheonWorkspace
from tests.helpers.process_input import make_framework_params


class TestArtifactEngine:
    """Test suite for ArtifactEngine expected behavior."""

    def test_compile_schema_returns_composed_schema(self):
        """Test that compile_schema returns a properly composed JSON schema."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        schema_jsonnet = """
        {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "priority": {"type": "string", "enum": std.extVar("priorities")}
          }
        }
        """
        # Use proper profile structure with active_profile and profiles section
        profile_data = {
            "active_profile": "test",
            "profiles": {"test": {"priorities": ["high", "medium", "low"]}},
        }

        result = engine.compile_schema(schema_jsonnet, profile_data)

        # Should return a dictionary representing the compiled schema
        assert isinstance(result, dict)
        assert result["type"] == "object"
        assert "properties" in result
        assert result["properties"]["priority"]["enum"] == ["high", "medium", "low"]

    def test_compile_schema_with_empty_profile_fallback(self):
        """Test that compile_schema handles team metadata without profiles correctly."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Schema that doesn't use profile variables
        schema_jsonnet = """
        {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"}
          }
        }
        """
        # Team metadata without profiles section (old format)
        profile_data = {
            "team_name": "Test Team",
            "description": "A test team description",
        }

        result = engine.compile_schema(schema_jsonnet, profile_data)

        # Should return a dictionary with empty profile context
        assert isinstance(result, dict)
        assert result["type"] == "object"
        assert "properties" in result
        assert result["properties"]["title"]["type"] == "string"

    def test_compile_schema_can_exclude_schema_metadata(self):
        """Test that compile_schema omits $schema when requested."""

        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        schema_jsonnet = '{ title: { type: "string" } }'

        result = engine.compile_schema(
            schema_jsonnet,
            full_profile_content={},
            include_schema_metadata=False,
        )

        assert "$schema" not in result
        assert result["type"] == "object"

    def test_yaml_filter_converts_dict_to_yaml(self):
        """Test that the to_yaml filter converts dictionary data to proper YAML format."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test data structure that should be converted to YAML
        template_str = "{{ config | to_yaml }}"
        context = {
            "config": {
                "team_name": "Test Team",
                "active_profile": "development",
                "profiles": {
                    "development": {"verbosity": True, "debug_mode": True},
                    "production": {"verbosity": False, "debug_mode": False},
                },
            }
        }

        result = engine.render_template(template_str, context)

        # Verify YAML output format
        assert "team_name: Test Team" in result
        assert "active_profile: development" in result
        assert "profiles:" in result
        assert "development:" in result
        assert "production:" in result
        assert "verbosity: true" in result
        assert "debug_mode: false" in result

    def test_yaml_filter_handles_lists_and_nested_structures(self):
        """Test that the to_yaml filter handles complex nested data structures."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        template_str = "{{ data | to_yaml }}"
        context = {
            "data": {
                "team_info": {
                    "name": "Complex Team",
                    "members": ["alice", "bob", "charlie"],
                    "settings": {
                        "notifications": True,
                        "priorities": ["high", "medium", "low"],
                    },
                }
            }
        }

        result = engine.render_template(template_str, context)

        # Verify proper YAML structure for lists and nested objects
        assert "team_info:" in result
        assert "members:" in result
        assert "- alice" in result
        assert "- bob" in result
        assert "- charlie" in result
        assert "settings:" in result
        assert "notifications: true" in result
        assert "priorities:" in result
        assert "- high" in result

    def test_yaml_filter_handles_empty_and_simple_values(self):
        """Test that the to_yaml filter handles edge cases like empty dicts and simple values."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test empty dictionary
        result1 = engine.render_template("{{ empty | to_yaml }}", {"empty": {}})
        assert result1.strip() == "{}"

        # Test simple string value
        result2 = engine.render_template(
            "{{ simple | to_yaml }}", {"simple": "test string"}
        )
        assert "test string" in result2

        # Test boolean and number values
        result3 = engine.render_template(
            "{{ values | to_yaml }}",
            {"values": {"enabled": True, "count": 42, "disabled": False}},
        )
        assert "enabled: true" in result3
        assert "count: 42" in result3
        assert "disabled: false" in result3

    def test_yaml_filter_integration_with_create_team_profile_process(self):
        """Integration test showing YAML filter usage in CREATE process for team-profile.yaml."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Simulate a CREATE process template for generating team-profile.yaml
        content_template = """# {{ team_name }} Team Profile
{{ profile_config | to_yaml }}"""

        context = {
            "team_name": "Development",
            "profile_config": {
                "team_name": "Development Team",
                "description": "Core development team for the project",
                "active_profile": "standard",
                "profiles": {
                    "prototype": {
                        "verbosity": "brief",
                        "enforce_tdd": False,
                        "test_type": "unit_test_only",
                    },
                    "standard": {
                        "verbosity": "standard",
                        "enforce_tdd": True,
                        "test_type": "unit_test_only",
                    },
                },
            },
        }

        result = engine.render_template(content_template, context)

        # Verify the result looks like a proper team-profile.yaml file
        assert "# Development Team Profile" in result
        assert "team_name: Development Team" in result
        assert "description: Core development team for the project" in result
        assert "active_profile: standard" in result
        assert "profiles:" in result
        assert "prototype:" in result
        assert "standard:" in result
        assert "verbosity: brief" in result
        assert "enforce_tdd: false" in result
        assert "test_type: unit_test_only" in result

    def test_validate_returns_true_for_valid_data(self):
        """Test that validate returns True when data matches schema."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        schema = {
            "type": "object",
            "properties": {"title": {"type": "string"}, "priority": {"type": "string"}},
            "required": ["title"],
        }
        valid_data = {"title": "Test Task", "priority": "high"}

        result = engine.validate(valid_data, schema)
        assert result is True

    def test_validate_raises_exception_for_invalid_data(self):
        """Test that validate raises ValueError with detailed message when data doesn't match schema."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        schema = {
            "type": "object",
            "properties": {"title": {"type": "string"}, "priority": {"type": "string"}},
            "required": ["title"],
        }
        invalid_data = {"priority": "high"}  # Missing required title

        with pytest.raises(ValueError) as exc_info:
            engine.validate(invalid_data, schema)

        # Verify the error message contains detailed validation information
        error_message = str(exc_info.value)
        assert "Schema validation failed:" in error_message
        assert "title" in error_message  # Should mention the missing field
        assert (
            "required" in error_message.lower()
        )  # Should mention it's a required field

    def test_generate_artifact_returns_content_and_path(self):
        """Test that generate_artifact returns rendered content and target path."""
        mock_workspace = Mock()

        # Mock the Jinja2 environment with proper filters support
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_workspace.get_artifact_template_environment.return_value = mock_env

        # Mock the template rendering result
        mock_template = Mock()
        mock_env.from_string.return_value = mock_template
        mock_template.render.return_value = "# Fix Bug\nPriority: high"

        engine = ArtifactEngine(mock_workspace)

        templates = {
            "content": "# {{title}}\nPriority: {{priority}}",
            "placement": "tasks/{{priority}}",
            "naming": "{{title|lower|replace(' ', '-')}}.md",
        }
        input_params = {"title": "Fix Bug", "priority": "high"}

        framework_params = make_framework_params("test-process", "test-actor")

        content, path = engine.generate_artifact(
            templates, input_params, framework_params
        )

        assert isinstance(content, str)
        assert "# Fix Bug" in content
        assert "Priority: high" in content
        assert isinstance(path, PantheonPath)
        assert str(path) == "tasks/high/fix-bug.md"

    def test_find_artifact_returns_path_when_found(self):
        """Test that find_artifact returns PantheonPath when artifact exists."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock the workspace methods properly
        mock_workspace.get_artifact_parser.return_value = "[]"  # No normalization rules
        mock_workspace.get_artifact_locator.return_value = (
            '{"pattern": "^({id})_.*\\\\.md$"}'
        )
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("T123_example-ticket.md")
        ]

        result = engine.find_artifact("get-ticket", "T123")

        # Should return PantheonPath to the found artifact
        assert isinstance(result, PantheonPath)
        assert "T123" in str(result)

    def test_find_artifact_returns_none_when_not_found(self):
        """Test that find_artifact returns None when artifact doesn't exist."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        result = engine.find_artifact("get-ticket", "NONEXISTENT")

        assert result is None

    def test_get_artifact_sections_returns_section_content(self):
        """Test that get_artifact_sections extracts and returns section content."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock marker definitions
        mock_workspace.get_artifact_section_markers.return_value = """{
            "section_start": "<!-- PANTHEON:SECTION:START:{name} -->",
            "section_end": "<!-- PANTHEON:SECTION:END:{name} -->",
            "placeholder": "<!-- PANTHEON:SECTION:PLACEHOLDER -->"
        }"""

        # Mock file content with sections
        file_content = """
        # Title
        <!-- PANTHEON:SECTION:START:plan -->
        This is the plan content
        <!-- PANTHEON:SECTION:END:plan -->

        <!-- PANTHEON:SECTION:START:notes -->
        These are notes
        <!-- PANTHEON:SECTION:END:notes -->
        """

        mock_workspace.read_artifact_file.return_value = file_content
        artifact_path = PantheonPath("test.md")

        result = engine.get_artifact_sections(
            "get-ticket", artifact_path, ["plan", "notes"]
        )

        # Should return dictionary mapping section names to content
        assert isinstance(result, dict)
        assert "plan" in result
        assert "notes" in result
        assert isinstance(result["plan"], str)
        assert isinstance(result["notes"], str)
        assert "This is the plan content" in result["plan"]
        assert "These are notes" in result["notes"]

    def test_workspace_dependency_injection(self):
        """Test that workspace is properly injected and accessible."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        assert engine._workspace is mock_workspace

    def test_find_artifact_with_fuzzy_id_normalization(self):
        """Test that find_artifact normalizes fuzzy IDs using process-specific rules."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock normalizer rules for ID cleaning
        mock_workspace.get_artifact_parser.return_value = """[
            {"pattern": "^\\\\s+|\\\\s+$", "replacement": ""},
            {"pattern": ".*[\\\\\\\\\\/]", "replacement": ""},
            {"pattern": "^(T\\\\d{3}).*$", "replacement": "\\\\1"}
        ]"""

        # Mock finder pattern using the expected external variable name
        mock_workspace.get_artifact_locator.return_value = (
            '{"pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        )

        # Mock the workspace delegation method
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("T012_test-ticket.md")
        ]

        # Test with fuzzy input that needs normalization
        result = engine.find_artifact("ticket", " T012.md ")

        # Should normalize " T012.md " to "T012" and find the artifact
        assert isinstance(result, PantheonPath)
        assert str(result) == "T012_test-ticket.md"

        # Verify the delegation to workspace
        mock_workspace.get_artifact_parser.assert_called_once_with("ticket")
        mock_workspace.get_artifact_locator.assert_called_once_with("ticket")
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(T012)_.*\\.md$", directory=None
        )

    def test_find_artifact_returns_none_for_multiple_matches(self):
        """Test that find_artifact returns None when multiple files match the pattern."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock normalizer and finder
        mock_workspace.get_artifact_parser.return_value = (
            '[{"pattern": ".*", "replacement": "T012"}]'
        )
        mock_workspace.get_artifact_locator.return_value = (
            '{"pattern": "^({id})_.*\\\\.md$"}'
        )

        # Mock filesystem with multiple matching files
        mock_workspace._artifacts_root = Mock()
        mock_workspace._filesystem = Mock()
        mock_workspace._filesystem.exists.return_value = True

        mock_file1 = Mock()
        mock_file1.is_file.return_value = True
        mock_file1.suffix = ".md"
        mock_file1.name = "T012_first.md"

        mock_file2 = Mock()
        mock_file2.is_file.return_value = True
        mock_file2.suffix = ".md"
        mock_file2.name = "T012_second.md"

        mock_workspace._filesystem.iterdir.return_value = [mock_file1, mock_file2]

        result = engine.find_artifact("ticket", "T012")

        # Should return None due to ambiguous matches
        assert result is None

    def test_get_artifact_sections_extracts_content_between_markers(self):
        """Test that get_artifact_sections properly extracts content between HTML markers."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock marker definitions
        mock_workspace.get_artifact_section_markers.return_value = """{
            "section_start": "<!-- PANTHEON:SECTION:START:{name} -->",
            "section_end": "<!-- PANTHEON:SECTION:END:{name} -->",
            "placeholder": "<!-- PANTHEON:SECTION:PLACEHOLDER -->"
        }"""

        # Mock file content with sections
        file_content = """
        # Title
        <!-- PANTHEON:SECTION:START:PLAN -->
        This is the plan content
        with multiple lines
        <!-- PANTHEON:SECTION:END:PLAN -->

        <!-- PANTHEON:SECTION:START:NOTES -->
        These are notes
        <!-- PANTHEON:SECTION:END:NOTES -->
        """

        mock_workspace.read_artifact_file.return_value = file_content

        artifact_path = PantheonPath("test.md")
        result = engine.get_artifact_sections(
            "ticket", artifact_path, ["PLAN", "NOTES"]
        )

        # Should extract both sections correctly
        assert isinstance(result, dict)
        assert "PLAN" in result
        assert "NOTES" in result
        assert "This is the plan content" in result["PLAN"]
        assert "with multiple lines" in result["PLAN"]
        assert "These are notes" in result["NOTES"]

    def test_get_artifact_sections_skips_placeholder_sections(self):
        """Test that get_artifact_sections skips sections containing only placeholders."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock marker definitions
        mock_workspace.get_artifact_section_markers.return_value = """{
            "section_start": "<!-- PANTHEON:SECTION:START:{name} -->",
            "section_end": "<!-- PANTHEON:SECTION:END:{name} -->",
            "placeholder": "<!-- PANTHEON:SECTION:PLACEHOLDER -->"
        }"""

        # Mock file content with placeholder section
        file_content = """
        <!-- PANTHEON:SECTION:START:EMPTY -->
        <!-- PANTHEON:SECTION:PLACEHOLDER -->
        <!-- PANTHEON:SECTION:END:EMPTY -->

        <!-- PANTHEON:SECTION:START:FILLED -->
        Actual content here
        <!-- PANTHEON:SECTION:END:FILLED -->
        """

        mock_workspace.read_artifact_file.return_value = file_content

        artifact_path = PantheonPath("test.md")
        result = engine.get_artifact_sections(
            "ticket", artifact_path, ["EMPTY", "FILLED"]
        )

        # Should skip EMPTY section (placeholder only) and include FILLED section
        assert "EMPTY" not in result
        assert "FILLED" in result
        assert "Actual content here" in result["FILLED"]

    def test_locate_artifact_with_directory_field(self):
        """Test _locate_artifact extracts and uses directory field from finder config."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config with both directory and pattern fields using Jsonnet with external variables
        finder_config = '{"directory": "tickets", "pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        mock_workspace.get_artifact_locator.return_value = finder_config

        # Mock single matching file
        mock_path = Mock(spec=PantheonPath)
        mock_workspace.get_matching_artifact.return_value = [mock_path]

        result = artifact_engine._locate_artifact("test-process", "T123")

        # Verify directory parameter was passed to get_matching_artifact
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(T123)_.*\\.md$", directory="tickets"
        )
        assert result == mock_path

    def test_locate_artifact_without_directory_field(self):
        """Test _locate_artifact handles finder config with only pattern field."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config with pattern field only using Jsonnet with external variables
        finder_config = (
            '{"pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        )
        mock_workspace.get_artifact_locator.return_value = finder_config

        # Mock single matching file
        mock_path = Mock(spec=PantheonPath)
        mock_workspace.get_matching_artifact.return_value = [mock_path]

        result = artifact_engine._locate_artifact("test-process", "T456")

        # Verify directory parameter is None (full search)
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(T456)_.*\\.md$", directory=None
        )
        assert result == mock_path

    def test_locate_artifact_invalid_finder_format_mentions_both_fields(self):
        """Test _locate_artifact error message mentions pattern field when finder is invalid."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock invalid finder config (missing pattern key)
        finder_config = '{"directory": "tickets"}'
        mock_workspace.get_artifact_locator.return_value = finder_config

        with patch("pantheon.artifact_engine.Log") as mock_log:
            result = artifact_engine._locate_artifact("test-process", "T123")

            # Verify warning message mentions the expected pattern field
            mock_log.warning.assert_called_once()
            warning_message = mock_log.warning.call_args[0][0]
            assert "pattern" in warning_message
            assert result is None

    def test_locate_artifact_logs_directory_scoped_search(self):
        """Test _locate_artifact logs when performing directory-scoped search."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config with directory field using Jsonnet with external variables
        finder_config = '{"directory": "tickets", "pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        mock_workspace.get_artifact_locator.return_value = finder_config
        mock_workspace.get_matching_artifact.return_value = [Mock(spec=PantheonPath)]

        with patch("pantheon.artifact_engine.Log") as mock_log:
            artifact_engine._locate_artifact("test-process", "T123")

            # Verify debug log mentions directory-scoped search
            # Check all debug calls for the expected message
            debug_calls = [call[0][0] for call in mock_log.debug.call_args_list]
            assert any("directory-scoped search" in msg for msg in debug_calls), (
                f"Debug calls: {debug_calls}"
            )

    def test_locate_artifact_logs_full_search_fallback(self):
        """Test _locate_artifact logs when falling back to full search."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config without directory field using Jsonnet with external variables
        finder_config = (
            '{"pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        )
        mock_workspace.get_artifact_locator.return_value = finder_config
        mock_workspace.get_matching_artifact.return_value = [Mock(spec=PantheonPath)]

        with patch("pantheon.artifact_engine.Log") as mock_log:
            artifact_engine._locate_artifact("test-process", "T123")

            # Verify debug log mentions full search
            # Check all debug calls for the expected message
            debug_calls = [call[0][0] for call in mock_log.debug.call_args_list]
            assert any("full artifacts_root search" in msg for msg in debug_calls), (
                f"Debug calls: {debug_calls}"
            )

    def test_complete_artifact_location_workflow_with_directory_scope(self):
        """Integration test for complete artifact location workflow using mock filesystem."""
        from unittest.mock import Mock

        # Create mock workspace with filesystem structure
        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config with directory field using Jsonnet with external variables
        finder_config = '{"directory": "tickets", "pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        mock_workspace.get_artifact_locator.return_value = finder_config

        # Mock filesystem with test artifacts in subdirectories
        # Simulate tickets/T123_test-ticket.md and plans/P001_plan.md
        mock_ticket_path = Mock(spec=PantheonPath)
        mock_ticket_path.name = "T123_test-ticket.md"

        # Mock ID normalization (return the ID as-is for this test)
        mock_workspace.get_artifact_parser.return_value = "[]"  # No normalization rules

        # Mock get_matching_artifact to return the correct artifact from tickets directory
        mock_workspace.get_matching_artifact.return_value = [mock_ticket_path]

        # Test the complete workflow
        result = artifact_engine.find_artifact("get-ticket", "T123")

        # Verify the complete chain:
        # 1. finder config was retrieved
        mock_workspace.get_artifact_locator.assert_called_once_with("get-ticket")

        # 2. directory and pattern were extracted and used
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(T123)_.*\\.md$", directory="tickets"
        )

        # 3. correct artifact was returned
        assert result == mock_ticket_path

    def test_integration_prevents_cross_directory_matches(self):
        """Integration test verifying directory scoping prevents false matches."""
        from unittest.mock import Mock

        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock finder config for tickets directory using Jsonnet with external variables
        finder_config = '{"directory": "tickets", "pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        mock_workspace.get_artifact_locator.return_value = finder_config

        # Mock ID normalization
        mock_workspace.get_artifact_parser.return_value = "[]"

        # Mock that no artifacts match in tickets directory (even though P001 exists elsewhere)
        mock_workspace.get_matching_artifact.return_value = []

        result = artifact_engine.find_artifact("get-ticket", "P001")

        # Verify search was scoped to tickets directory only
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(P001)_.*\\.md$", directory="tickets"
        )

        # Verify no false match from other directories
        assert result is None

    def test_integration_backward_compatibility_full_search(self):
        """Integration test for backward compatibility without directory field."""
        from unittest.mock import Mock

        mock_workspace = Mock(spec=PantheonWorkspace)
        artifact_engine = ArtifactEngine(mock_workspace)

        # Mock old-style finder config (no directory field) using Jsonnet with external variables
        finder_config = (
            '{"pattern": "^(" + std.extVar("pantheon_artifact_id") + ")_.*\\\\.md$"}'
        )
        mock_workspace.get_artifact_locator.return_value = finder_config

        # Mock ID normalization
        mock_workspace.get_artifact_parser.return_value = "[]"

        mock_artifact_path = Mock(spec=PantheonPath)
        mock_workspace.get_matching_artifact.return_value = [mock_artifact_path]

        result = artifact_engine.find_artifact("old-process", "T123")

        # Verify full search was performed (directory=None)
        mock_workspace.get_matching_artifact.assert_called_once_with(
            "^(T123)_.*\\.md$", directory=None
        )

        assert result == mock_artifact_path

    def test_generate_artifact_includes_artifact_id_in_template_context(self):
        """Test that generate_artifact includes {{pantheon_artifact_id}} variable in template context."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()
        mock_workspace._project_config = {"active_team": "test-team"}
        # Mock the template environment method
        mock_env = Mock()
        # Allow item assignment for filters dictionary
        mock_env.filters = {}
        mock_workspace.get_artifact_template_environment.return_value = mock_env
        mock_env.from_string.return_value.render.return_value = "# Fix Bug - ID: 42"

        # Create engine with mocked workspace
        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            mock_artifact_id = Mock()
            MockArtifactId.return_value = mock_artifact_id
            mock_artifact_id.get_next_count.return_value = 42

            engine = ArtifactEngine(mock_workspace)

            templates = {
                "content": "# {{title}} - ID: {{pantheon_artifact_id}}",
                "placement": "tasks",
                "naming": "T{{pantheon_artifact_id}}-{{title|lower|replace(' ', '-')}}.md",
            }
            # Use "process" key instead of "process_name" to match BUILTIN_PROCESS constant
            input_data = {"title": "Fix Bug", "process": "create-ticket"}

            framework_params = make_framework_params("create-ticket", "test-actor")
            content, path = engine.generate_artifact(
                templates, input_data, framework_params
            )

            # Verify artifact ID was generated
            mock_artifact_id.get_next_count.assert_called_once_with("create-ticket")

            # Verify artifact_id appears in rendered content and path
            assert "ID: 42" in content
            assert str(path) == "tasks/T42-fix-bug.md"

    def test_generate_artifact_uses_workspace_for_artifact_id_generation(self):
        """Test that generate_artifact uses workspace for artifact ID generation."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()
        mock_workspace._project_config = {"active_team": "workspace-team"}
        # Mock the template environment method
        mock_env = Mock()
        # Allow item assignment for filters dictionary
        mock_env.filters = {}
        mock_workspace.get_artifact_template_environment.return_value = mock_env
        mock_env.from_string.return_value.render.return_value = "Artifact ID: 5"

        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            mock_artifact_id = Mock()
            MockArtifactId.return_value = mock_artifact_id
            mock_artifact_id.get_next_count.return_value = 5

            engine = ArtifactEngine(mock_workspace)
            engine._artifact_id = mock_artifact_id

            templates = {
                "content": "Artifact ID: {{pantheon_artifact_id}}",
                "placement": "tasks",
                "naming": "T{{pantheon_artifact_id}}.md",
            }
            # Use "process" key instead of "process_name" to match BUILTIN_PROCESS constant
            input_data = {"process": "create-ticket"}

            framework_params = make_framework_params("create-ticket", "test-actor")
            content, path = engine.generate_artifact(
                templates, input_data, framework_params
            )

            # Verify artifact ID was generated
            mock_artifact_id.get_next_count.assert_called_once_with("create-ticket")

            # Verify artifact_id appears in rendered output
            assert "Artifact ID: 5" in content
            assert str(path) == "tasks/T5.md"

    def test_generate_artifact_skips_artifact_id_when_process_missing(self):
        """Test that generate_artifact gracefully handles missing process context."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()
        mock_workspace._project_config = {}

        # Mock the Jinja2 environment with proper filters support
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_workspace.get_artifact_template_environment.return_value = mock_env

        # Mock the template rendering result
        mock_template = Mock()
        mock_env.from_string.return_value = mock_template
        mock_template.render.return_value = "Title: Fix Bug"

        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            mock_artifact_id = Mock()
            MockArtifactId.return_value = mock_artifact_id

            engine = ArtifactEngine(mock_workspace)
            engine._artifact_id = mock_artifact_id

            templates = {
                "content": "Title: {{title}}{% if pantheon_artifact_id %} - Artifact ID: {{pantheon_artifact_id}}{% endif %}",
                "placement": "tasks",
                "naming": "{{title|lower|replace(' ', '-')}}.md",
            }
            input_params = {
                "title": "Fix Bug"
                # No process_name
            }

            framework_params = make_framework_params(
                None, "test-actor"
            )  # No process name
            content, path = engine.generate_artifact(
                templates, input_params, framework_params
            )

            # Verify artifact ID was not generated due to missing context
            mock_artifact_id.get_next_count.assert_not_called()

            # Verify template still renders without pantheon_artifact_id
            assert "Title: Fix Bug" in content
            assert (
                "Artifact ID:" not in content
            )  # Artifact ID section should be skipped
            assert str(path) == "tasks/fix-bug.md"

    def test_generate_artifact_handles_artifact_id_errors_gracefully(self):
        """Test that generate_artifact continues when artifact ID operations fail."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()
        mock_workspace._project_config = {"active_team": "test-team"}

        # Mock the Jinja2 environment with proper filters support
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_env.from_string.return_value.render.return_value = "Title: Fix Bug"

        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            mock_artifact_id = Mock()
            MockArtifactId.return_value = mock_artifact_id
            mock_artifact_id.get_next_count.side_effect = Exception("Artifact ID error")

            engine = ArtifactEngine(mock_workspace)
            engine._artifact_id = mock_artifact_id
            # Mock create_artifact_jinja_environment to return mock_env
            engine.create_artifact_jinja_environment = Mock(return_value=mock_env)

            templates = {
                "content": "Title: {{title}}{% if artifact_id %} - Artifact ID: {{artifact_id}}{% endif %}",
                "placement": "tasks",
                "naming": "{{title|lower|replace(' ', '-')}}.md",
            }
            input_data = {"title": "Fix Bug", "process_name": "create-task"}

            # Should not raise exception despite artifact ID error
            framework_params = make_framework_params("create-ticket", "test-actor")
            content, path = engine.generate_artifact(
                templates, input_data, framework_params
            )

            # Verify template still renders without artifact_id
            assert "Title: Fix Bug" in content
            assert "Artifact ID:" not in content
            assert str(path) == "tasks/fix-bug.md"

    def test_artifact_id_dependency_injection(self):
        """Test that ArtifactId can be injected during ArtifactEngine initialization."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_artifact_id = Mock()

        engine = ArtifactEngine(mock_workspace, artifact_id=mock_artifact_id)

        # Verify the injected artifact ID is used
        assert engine._artifact_id is mock_artifact_id

    def test_artifact_id_default_creation(self):
        """Test that ArtifactId is created by default when not injected."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()

        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            mock_artifact_id_instance = Mock()
            MockArtifactId.return_value = mock_artifact_id_instance

            engine = ArtifactEngine(mock_workspace)

            # Verify ArtifactId was created with workspace dependency
            MockArtifactId.assert_called_once_with(mock_workspace)
            assert engine._artifact_id is mock_artifact_id_instance

    def test_backward_compatibility_without_artifact_id(self):
        """Test that existing templates continue to work without {{artifact_id}} variable."""
        from unittest.mock import Mock, patch

        mock_workspace = Mock()
        mock_workspace._project_config = {}

        # Mock the Jinja2 environment with proper filters support
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_env.from_string.return_value.render.return_value = (
            "# Legacy Task\nTimestamp: 2025-01-01T00:00:00"
        )

        with patch("pantheon.artifact_engine.ArtifactId") as MockArtifactId:
            MockArtifactId.return_value = Mock()
            engine = ArtifactEngine(mock_workspace)
            # Mock create_artifact_jinja_environment to return mock_env
            engine.create_artifact_jinja_environment = Mock(return_value=mock_env)

        # Traditional template without artifact_id
        templates = {
            "content": "# {{title}}\nTimestamp: {{timestamp}}",
            "placement": "tasks",
            "naming": "{{title|lower|replace(' ', '-')}}.md",
        }
        input_data = {"title": "Legacy Task"}

        framework_params = make_framework_params("create-ticket", "test-actor")

        content, path = engine.generate_artifact(
            templates, input_data, framework_params
        )

        # Should work normally without artifact_id
        assert "# Legacy Task" in content
        assert "Timestamp:" in content
        assert str(path) == "tasks/legacy-task.md"

    def test_render_artifact_template_with_include_statements(self):
        """Test that render_artifact_template properly handles Jinja include statements."""
        from unittest.mock import Mock

        # Create a mock workspace
        mock_workspace = Mock()

        # Create a mock Jinja2 environment with FileSystemLoader
        mock_env = Mock()
        # Allow item assignment for filters dictionary
        mock_env.filters = {}
        mock_template = Mock()
        mock_env.from_string.return_value = mock_template
        mock_template.render.return_value = "Included content from create_routine.md"

        # Create engine
        engine = ArtifactEngine(mock_workspace)

        # Template content with include statement (similar to actual create-routine content.md)
        template_content = """<!-- SECTION:START:ROUTINE -->
{%- if process_type == 'create' -%}
{%- include 'create_routine.md' -%}
{%- elif process_type == 'get' -%}
{%- include 'get_routine.md' -%}
{%- else -%}
ERROR: Invalid process_type
{%- endif -%}
<!-- SECTION:END:ROUTINE -->"""

        context = {"process_type": "create", "process_name": "test-process"}

        # Test artifact template rendering with include support
        result = engine.render_artifact_template(template_content, context, mock_env)

        # Verify the mock environment was used (which enables includes)
        mock_env.from_string.assert_called_once_with(template_content)
        mock_template.render.assert_called_once_with(**context)

        # Verify the result contains the included content
        assert result == "Included content from create_routine.md"

    def test_render_artifact_template_vs_basic_render_template(self):
        """Test that render_artifact_template differs from basic render_template for includes."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Template with include statement that would fail with basic rendering
        template_with_include = "Start: {% include 'nonexistent.md' %} End"
        context = {"test": "value"}

        # Test 1: Basic render_template should handle the template without includes
        # (but would fail if it tried to resolve the include)
        basic_result = engine.render_template("Start: {{test}} End", context)
        assert basic_result == "Start: value End"

        # Test 2: render_artifact_template requires an environment parameter
        mock_env = Mock()
        # Allow item assignment for filters dictionary
        mock_env.filters = {}
        mock_template = Mock()
        mock_env.from_string.return_value = mock_template
        mock_template.render.return_value = "Start: Mock included content End"

        artifact_result = engine.render_artifact_template(
            template_with_include, context, mock_env
        )
        assert artifact_result == "Start: Mock included content End"

        # Verify the environment was used (which is what enables includes)
        mock_env.from_string.assert_called_once_with(template_with_include)


class TestArtifactEngineSchemaSanitization:
    """Test suite for ArtifactEngine schema sanitization functionality."""

    def test_sanitize_properties_only_content(self):
        """Test sanitization wraps properties-only content in proper JSON Schema structure."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Properties-only content (what LLMs typically generate)
        properties_only = """
        {
          "name": {"type": "string"},
          "age": {"type": "integer"}
        }
        """

        result = engine._sanitize_schema_structure(properties_only)
        parsed_result = json.loads(result)

        # Should wrap in proper JSON Schema structure
        assert parsed_result["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert parsed_result["type"] == "object"
        assert "properties" in parsed_result
        assert parsed_result["properties"]["name"]["type"] == "string"
        assert parsed_result["properties"]["age"]["type"] == "integer"

    def test_sanitize_complete_schema_unchanged(self):
        """Test complete JSON Schema is returned unchanged."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Complete JSON Schema
        complete_schema = """
        {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "title": {"type": "string"}
          }
        }
        """

        result = engine._sanitize_schema_structure(complete_schema)

        # Should return unchanged (normalized formatting is okay)
        parsed_original = json.loads(complete_schema)
        parsed_result = json.loads(result)
        assert parsed_result == parsed_original

    def test_sanitize_partial_schema_adds_missing_fields(self):
        """Test schema with properties but missing top-level fields gets completed."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Partial schema - has properties but missing $schema and type
        partial_schema = """
        {
          "properties": {
            "name": {"type": "string"}
          },
          "required": ["name"]
        }
        """

        result = engine._sanitize_schema_structure(partial_schema)
        parsed_result = json.loads(result)

        # Should add missing top-level fields while preserving existing content
        assert parsed_result["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert parsed_result["type"] == "object"
        assert parsed_result["properties"]["name"]["type"] == "string"
        assert parsed_result["required"] == ["name"]

    def test_sanitize_empty_content_raises_error(self):
        """Test empty or None content raises ValueError."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test empty string
        try:
            engine._sanitize_schema_structure("")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "cannot be empty" in str(e)

        # Test whitespace only
        try:
            engine._sanitize_schema_structure("   ")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "cannot be empty" in str(e)

    def test_sanitize_invalid_json_raises_error(self):
        """Test invalid JSON content raises ValueError."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        invalid_json = """
        {
          "name": "unclosed string
          "age": 25
        }
        """

        try:
            engine._sanitize_schema_structure(invalid_json)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "Invalid JSON" in str(e)

    def test_sanitize_non_object_content_raises_error(self):
        """Test non-object JSON content raises ValueError."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Array instead of object
        array_content = '["item1", "item2"]'

        try:
            engine._sanitize_schema_structure(array_content)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "must be a JSON object" in str(e)

        # String instead of object
        string_content = '"just a string"'

        try:
            engine._sanitize_schema_structure(string_content)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "must be a JSON object" in str(e)

    def test_sanitize_complex_properties_preserved(self):
        """Test complex property structures are preserved during sanitization."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Complex properties-only content
        complex_properties = """
        {
          "user": {
            "type": "object",
            "properties": {
              "name": {"type": "string", "minLength": 1},
              "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "email"]
          },
          "preferences": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "key": {"type": "string"},
                "value": {"oneOf": [{"type": "string"}, {"type": "boolean"}]}
              }
            }
          }
        }
        """

        result = engine._sanitize_schema_structure(complex_properties)
        parsed_result = json.loads(result)

        # Should wrap in proper structure while preserving complex nested schema
        assert parsed_result["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert parsed_result["type"] == "object"
        assert "properties" in parsed_result

        # Verify complex nested structure is preserved
        user_schema = parsed_result["properties"]["user"]
        assert user_schema["type"] == "object"
        assert user_schema["required"] == ["name", "email"]
        assert user_schema["properties"]["email"]["format"] == "email"

        preferences_schema = parsed_result["properties"]["preferences"]
        assert preferences_schema["type"] == "array"
        assert "oneOf" in preferences_schema["items"]["properties"]["value"]

    def test_sanitize_with_additional_fields_preserved(self):
        """Test additional schema fields are preserved during sanitization."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Properties with additional fields like title, description
        schema_with_extras = """
        {
          "title": "User Schema",
          "description": "Schema for user data",
          "name": {"type": "string"},
          "age": {"type": "integer", "minimum": 0}
        }
        """

        result = engine._sanitize_schema_structure(schema_with_extras)
        parsed_result = json.loads(result)

        # Should wrap in properties while preserving additional fields
        assert parsed_result["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert parsed_result["type"] == "object"
        assert "properties" in parsed_result

        # Additional fields should be preserved at root level
        assert parsed_result["title"] == "User Schema"
        assert parsed_result["description"] == "Schema for user data"

        # Original fields should be moved to properties
        assert parsed_result["properties"]["name"]["type"] == "string"
        assert parsed_result["properties"]["age"]["minimum"] == 0


class TestResolveUriData:
    """Test suite for ArtifactEngine.resolve_uri_data method."""

    def test_resolve_simple_path_from_json(self):
        """Test resolving a simple path from valid JSON content."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "sections": {
            "plan": {
              "start": "<!-- START:PLAN -->",
              "end": "<!-- END:PLAN -->"
            }
          }
        }
        """

        result = engine.resolve_uri_data(jsonnet_content, "sections.plan")

        expected = {"start": "<!-- START:PLAN -->", "end": "<!-- END:PLAN -->"}
        assert result == expected

    def test_resolve_no_path_returns_entire_object(self):
        """Test that empty data path returns the entire compiled result."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "sections": {"plan": {"start": "test"}},
          "placeholder": "test-placeholder"
        }
        """

        result = engine.resolve_uri_data(jsonnet_content, "")

        expected = {
            "sections": {"plan": {"start": "test"}},
            "placeholder": "test-placeholder",
        }
        assert result == expected

    def test_resolve_path_with_properties_wrapper(self):
        """Test WYSIWYG path resolution when compilation adds properties wrapper."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Mock _compile_jsonnet to simulate properties wrapper being added during compilation
        def mock_compile_jsonnet(content, ext_vars=None, import_callback=None):
            # Simulate compilation that wraps original content in properties
            original = json.loads(content)
            return {"properties": original, "metadata": {"compiled": True}}

        engine._compile_jsonnet = mock_compile_jsonnet

        jsonnet_content = """
        {
          "sections": {
            "plan": {"start": "test", "end": "test"}
          }
        }
        """

        # User specifies path based on what they see in source (sections.plan)
        result = engine.resolve_uri_data(jsonnet_content, "sections.plan")

        expected = {"start": "test", "end": "test"}
        assert result == expected

    def test_resolve_array_index_access(self):
        """Test resolving paths with array index notation."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "rules": [
            {"pattern": "first", "replacement": "1st"},
            {"pattern": "second", "replacement": "2nd"}
          ]
        }
        """

        result = engine.resolve_uri_data(jsonnet_content, "rules.0.pattern")
        assert result == "first"

        result = engine.resolve_uri_data(jsonnet_content, "rules.1.replacement")
        assert result == "2nd"

    def test_resolve_deep_nested_path(self):
        """Test resolving deeply nested paths."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "config": {
            "database": {
              "connections": {
                "primary": {
                  "host": "localhost",
                  "port": 5432
                }
              }
            }
          }
        }
        """

        result = engine.resolve_uri_data(
            jsonnet_content, "config.database.connections.primary.port"
        )
        assert result == 5432

    def test_resolve_with_external_variables(self):
        """Test resolving with external variables passed to Jsonnet compilation."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "environment": std.extVar("env"),
          "settings": {
            "debug": std.extVar("debug_mode")
          }
        }
        """

        ext_vars = {"env": "production", "debug_mode": False}
        result = engine.resolve_uri_data(
            jsonnet_content, "settings.debug", ext_vars=ext_vars
        )

        assert result is False

    def test_resolve_path_not_found_error(self):
        """Test that KeyError is raised when path cannot be found."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "sections": {
            "plan": {"start": "test"}
          }
        }
        """

        try:
            engine.resolve_uri_data(jsonnet_content, "sections.nonexistent")
            raise AssertionError("Expected KeyError to be raised")
        except KeyError as e:
            assert "nonexistent" in str(e)
            assert "Available paths:" in str(e)

    def test_resolve_invalid_array_access_error(self):
        """Test error handling for invalid array access."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "items": ["first", "second"]
        }
        """

        try:
            engine.resolve_uri_data(jsonnet_content, "items.5")  # Index out of range
            raise AssertionError("Expected KeyError to be raised")
        except KeyError as e:
            assert "items.5" in str(e)

    def test_resolve_type_mismatch_error(self):
        """Test error handling when path expects different type."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        jsonnet_content = """
        {
          "value": "string_value"
        }
        """

        try:
            engine.resolve_uri_data(
                jsonnet_content, "value.nested"
            )  # Trying to access property on string
            raise AssertionError("Expected KeyError to be raised")
        except KeyError as e:
            assert "value.nested" in str(e)
            assert "Available paths:" in str(e)

    def test_extract_path_empty_path_returns_data(self):
        """Test that _extract_path returns original data for empty path."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"test": "value"}
        result = engine._extract_path(data, "")

        assert result == data

    def test_get_available_paths_dict_structure(self):
        """Test _get_available_paths for dictionary structures."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {
            "sections": {"plan": {"start": "test"}, "description": {"end": "test"}},
            "placeholder": "value",
        }

        paths = engine._get_available_paths(data)

        expected_paths = [
            "sections",
            "sections.plan",
            "sections.plan.start",
            "sections.description",
            "sections.description.end",
            "placeholder",
        ]

        for expected in expected_paths:
            assert expected in paths

    def test_get_available_paths_list_structure(self):
        """Test _get_available_paths for list structures."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"rules": [{"pattern": "test1"}, {"pattern": "test2"}]}

        paths = engine._get_available_paths(data)

        expected_paths = [
            "rules",
            "rules.0",
            "rules.0.pattern",
            "rules.1",
            "rules.1.pattern",
        ]

        for expected in expected_paths:
            assert expected in paths

    def test_get_available_paths_max_depth_limit(self):
        """Test that _get_available_paths respects max_depth limit."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"level1": {"level2": {"level3": {"level4": "too_deep"}}}}

        paths = engine._get_available_paths(data, max_depth=2)

        # Should include up to level2, but not level3 or level4
        assert "level1" in paths
        assert "level1.level2" in paths
        assert "level1.level2.level3" not in paths
        assert "level1.level2.level3.level4" not in paths


class TestYamlFilter:
    """Test suite for enhanced YAML filter with schema-based comments."""

    def test_to_yaml_filter_without_schema_returns_basic_yaml(self):
        """Test that to_yaml filter works without schema (backward compatibility)."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test data
        data = {
            "team_name": "Test Team",
            "active_profile": "development",
            "profiles": {
                "development": {"verbosity": "detailed", "enforce_tdd": False}
            },
        }

        # Create template with to_yaml filter (no schema)
        template_str = "{{ data | to_yaml }}"
        context = {"data": data}

        result = engine.render_template(template_str, context)

        # Should produce basic YAML without comments
        assert "team_name: Test Team" in result
        assert "active_profile: development" in result
        assert "verbosity: detailed" in result
        assert "enforce_tdd: false" in result
        # Should NOT contain comments
        assert "#" not in result

    def test_to_yaml_filter_with_profile_properties_adds_documentation_header(self):
        """Test that to_yaml filter adds profile properties documentation when available."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test data with property_definitions for new data-driven approach
        data = {
            "team_name": "Mobile Development Team",
            "active_profile": "development",
            "property_definitions": {
                "verbosity": {
                    "type": "string",
                    "enum": ["brief", "standard", "detailed"],
                    "description": "Level of detail in generated artifacts",
                },
                "enforce_tdd": {
                    "type": "boolean",
                    "description": "Whether to enforce TDD practices",
                },
                "test_type": {
                    "type": "string",
                    "enum": [
                        "unit_test_only",
                        "integration_test_only",
                        "unit_and_integration_test",
                    ],
                    "description": "Types of tests to write",
                },
            },
            "profiles": {
                "development": {
                    "verbosity": "detailed",
                    "enforce_tdd": False,
                    "test_type": "unit_test_only",
                }
            },
        }

        # Create template with to_yaml filter - no schema needed
        template_str = "{{ data | to_yaml }}"
        context = {"data": data}

        result = engine.render_template(template_str, context)

        # Should contain profile properties documentation header
        assert "# Profile Properties Documentation:" in result
        assert "# verbosity:" in result
        assert "#   Description: Level of detail in generated artifacts" in result
        assert "#   Options: brief, standard, detailed" in result
        assert "# enforce_tdd:" in result
        assert "#   Type: boolean (true/false)" in result
        assert "# test_type:" in result
        assert (
            "#   Options: unit_test_only, integration_test_only, unit_and_integration_test"
            in result
        )

        # Should have clean YAML structure without property_definitions
        assert "team_name: Mobile Development Team" in result
        assert "active_profile: development" in result
        assert "verbosity: detailed" in result
        assert "enforce_tdd: false" in result

        # Should NOT include property_definitions in the output YAML
        assert "property_definitions:" not in result

    def test_to_yaml_filter_with_no_profile_properties_shows_no_header(self):
        """Test that to_yaml filter shows no header when there are no profile properties."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Simple data without nested profile properties
        data = {"team_name": "Simple Team", "simple_field": "value"}

        # Schema without profile properties structure
        schema = {
            "properties": {
                "team_name": {"type": "string", "description": "The team name"},
                "simple_field": {"type": "string", "description": "A simple field"},
            }
        }

        # Create template with to_yaml filter and schema
        template_str = "{{ data | to_yaml }}"
        context = {"data": data, "pantheon_schema": schema}

        result = engine.render_template(template_str, context)

        # Should NOT contain any documentation header
        assert "# Profile Properties Documentation:" not in result
        assert "# Field Documentation:" not in result

        # Should just have clean YAML without header
        assert "team_name: Simple Team" in result
        assert "simple_field: value" in result

        # Should have no comments at all since no profile properties to document
        assert "#" not in result

    def test_to_yaml_filter_cleans_example_prefix(self):
        """Test that to_yaml filter removes 'Example: ' prefix from property descriptions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Data with property_definitions that have "Example:" prefix
        data = {
            "property_definitions": {
                "test_field": {
                    "type": "string",
                    "description": "Example: This is a test field",
                }
            },
            "profiles": {"development": {"test_field": "value"}},
        }

        template_str = "{{ data | to_yaml }}"
        context = {"data": data}

        result = engine.render_template(template_str, context)

        # Should clean up "Example: " prefix in documentation header
        assert "# Profile Properties Documentation:" in result
        assert "#   Description: This is a test field" in result
        assert "Example:" not in result

    def test_generate_yaml_with_comments_no_profile_properties(self):
        """Test _generate_yaml_with_comments with no profile properties to document."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"simple_field": "value", "another_field": "option1"}

        # Schema without nested profile properties
        schema = {
            "properties": {
                "simple_field": {"description": "A simple test field"},
                "another_field": {"description": "Another field"},
            }
        }

        result = engine._generate_yaml_with_comments(data, schema)

        # Should NOT have documentation header (no profile properties)
        assert "# Profile Properties Documentation:" not in result
        assert "# Field Documentation:" not in result

        # Should have clean YAML
        assert "simple_field: value" in result
        assert "another_field: option1" in result

    def test_generate_yaml_with_comments_no_properties_fallback(self):
        """Test _generate_yaml_with_comments falls back to basic YAML when no properties."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"field": "value"}
        schema = {}  # No properties

        result = engine._generate_yaml_with_comments(data, schema)

        # Should fall back to basic YAML
        assert result.strip() == "field: value"
        assert "#" not in result

    def test_generate_yaml_with_comments_handles_errors_gracefully(self):
        """Test _generate_yaml_with_comments handles errors and falls back to basic YAML."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {"field": "value"}
        # Invalid schema that might cause errors
        schema = {"properties": "invalid"}

        result = engine._generate_yaml_with_comments(data, schema)

        # Should fall back to basic YAML on error
        assert "field: value" in result

    def test_add_schema_comment_basic_functionality(self):
        """Test _add_schema_comment method directly."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        properties = {
            "test_field": {
                "description": "Test description",
                "enum": ["a", "b", "c"],
                "default": "a",
            }
        }

        yaml_line = "test_field: a"
        result = engine._add_schema_comment(yaml_line, properties)

        expected = "test_field: a  # Test description | Options: a, b, c | Default: a"
        assert result == expected

    def test_add_schema_comment_boolean_type(self):
        """Test _add_schema_comment adds type info for boolean fields."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        properties = {"flag": {"type": "boolean", "description": "A boolean flag"}}

        yaml_line = "flag: true"
        result = engine._add_schema_comment(yaml_line, properties)

        assert result == "flag: true  # A boolean flag | true/false"

    def test_add_schema_comment_skips_non_key_lines(self):
        """Test _add_schema_comment skips lines that aren't property keys."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        properties = {"field": {"description": "test"}}

        # Test various non-key lines
        test_lines = [
            "",  # Empty line
            "  - item1",  # Array item
            "    value",  # Indented value
            "# Comment",  # Existing comment
            "just_value",  # Line without colon
        ]

        for line in test_lines:
            result = engine._add_schema_comment(line, properties)
            assert result == line  # Should return unchanged

    def test_add_schema_comment_no_matching_property(self):
        """Test _add_schema_comment returns unchanged line when property not in schema."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        properties = {"other_field": {"description": "test"}}

        yaml_line = "unknown_field: value"
        result = engine._add_schema_comment(yaml_line, properties)

        assert result == yaml_line  # Should return unchanged

    def test_add_schema_comment_handles_missing_schema_fields(self):
        """Test _add_schema_comment handles properties with missing schema fields."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        properties = {
            "minimal_field": {}  # No description, enum, type, or default
        }

        yaml_line = "minimal_field: value"
        result = engine._add_schema_comment(yaml_line, properties)

        # Should return unchanged since no comment parts available
        assert result == yaml_line

    def test_complex_yaml_structure_with_no_profile_properties_defined(self):
        """Test YAML filter with profiles but no profile properties schema defined."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {
            "profiles": {
                "development": {"verbosity": "detailed", "testing": True},
                "production": {"verbosity": "brief", "testing": False},
            }
        }

        # Schema without profile properties definition (just basic top-level description)
        schema = {
            "properties": {
                "profiles": {
                    "description": "Available profiles for different operating modes"
                }
            }
        }

        template_str = "{{ data | to_yaml }}"
        context = {"data": data, "pantheon_schema": schema}

        result = engine.render_template(template_str, context)

        # Should NOT have documentation header (no profile properties defined in schema)
        assert "# Profile Properties Documentation:" not in result
        assert "# Field Documentation:" not in result

        # Should have clean YAML without comments since no profile properties to document
        assert "profiles:" in result
        assert "verbosity: detailed" in result
        assert "testing: true" in result
        assert "#" not in result

    def test_yaml_filter_integration_with_team_profile_example(self):
        """Integration test with realistic team profile data using property_definitions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Data with property_definitions for new data-driven approach
        data = {
            "team_name": "Mobile Development Team",
            "team_description": "A specialized team focused on mobile application development with CI/CD integration.",
            "active_profile": "development",
            "property_definitions": {
                "verbosity": {
                    "type": "string",
                    "enum": ["brief", "standard", "detailed"],
                    "description": "Level of detail in generated artifacts",
                },
                "enforce_tdd": {
                    "type": "boolean",
                    "description": "Whether to enforce TDD practices",
                },
                "test_type": {
                    "type": "string",
                    "enum": [
                        "unit_test_only",
                        "integration_test_only",
                        "unit_and_integration_test",
                    ],
                    "description": "Types of tests to write",
                },
                "test_coverage": {
                    "type": "string",
                    "enum": ["minimal", "standard", "comprehensive"],
                    "description": "Desired test coverage level",
                },
                "enable_progress_log": {
                    "type": "boolean",
                    "description": "Whether to generate progress logs",
                },
            },
            "profiles": {
                "development": {
                    "verbosity": "detailed",
                    "enforce_tdd": False,
                    "test_type": "unit_test_only",
                    "test_coverage": "minimal",
                    "enable_progress_log": True,
                },
                "staging": {
                    "verbosity": "standard",
                    "enforce_tdd": True,
                    "test_type": "unit_and_integration_test",
                    "test_coverage": "standard",
                    "enable_progress_log": True,
                },
                "production": {
                    "verbosity": "brief",
                    "enforce_tdd": True,
                    "test_type": "unit_and_integration_test",
                    "test_coverage": "comprehensive",
                    "enable_progress_log": False,
                },
            },
        }

        template_str = "{{ data | to_yaml }}"
        context = {"data": data}

        result = engine.render_template(template_str, context)

        # Should have profile properties documentation header
        assert "# Profile Properties Documentation:" in result
        assert "# verbosity:" in result
        assert "#   Description: Level of detail in generated artifacts" in result
        assert "#   Options: brief, standard, detailed" in result
        assert "# enforce_tdd:" in result
        assert "#   Type: boolean (true/false)" in result
        assert "# test_type:" in result
        assert (
            "#   Options: unit_test_only, integration_test_only, unit_and_integration_test"
            in result
        )
        assert "# test_coverage:" in result
        assert "#   Options: minimal, standard, comprehensive" in result
        assert "# enable_progress_log:" in result

        # Should have clean YAML structure with property_definitions excluded
        assert "team_name: Mobile Development Team" in result
        assert "active_profile: development" in result
        assert "development:" in result
        assert "staging:" in result
        assert "production:" in result
        assert "verbosity: detailed" in result
        assert "enforce_tdd: false" in result

        # Should NOT include property_definitions in output YAML
        assert "property_definitions:" not in result

    def test_generate_yaml_with_data_definitions_basic_functionality(self):
        """Test _generate_yaml_with_data_definitions with basic property definitions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {
            "team_name": "Test Team",
            "property_definitions": {
                "verbosity": {
                    "type": "string",
                    "enum": ["brief", "standard", "detailed"],
                    "description": "Level of detail in artifacts",
                },
                "enforce_tdd": {
                    "type": "boolean",
                    "description": "Whether to enforce TDD practices",
                },
            },
            "profiles": {
                "development": {"verbosity": "detailed", "enforce_tdd": False}
            },
        }

        property_definitions = data["property_definitions"]
        result = engine._generate_yaml_with_data_definitions(data, property_definitions)

        # Should contain documentation header
        assert "# Profile Properties Documentation:" in result
        assert "# verbosity:" in result
        assert "#   Description: Level of detail in artifacts" in result
        assert "#   Type: string" in result
        assert "#   Options: brief, standard, detailed" in result
        assert "# enforce_tdd:" in result
        assert "#   Type: boolean (true/false)" in result

        # Should contain YAML data without property_definitions
        assert "team_name: Test Team" in result
        assert "profiles:" in result
        assert "verbosity: detailed" in result
        assert "enforce_tdd: false" in result

        # Should NOT contain property_definitions in YAML output
        assert "property_definitions:" not in result

    def test_generate_yaml_with_data_definitions_excludes_property_definitions_key(
        self,
    ):
        """Test that property_definitions key is properly excluded from YAML output."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        data = {
            "keep_this": "value",
            "property_definitions": {
                "test_prop": {"type": "string", "description": "Test property"}
            },
            "and_this": "other_value",
        }

        result = engine._generate_yaml_with_data_definitions(
            data, data["property_definitions"]
        )

        # Should contain other keys but not property_definitions
        assert "keep_this: value" in result
        assert "and_this: other_value" in result
        assert "property_definitions:" not in result

        # Should still have documentation header
        assert "# Profile Properties Documentation:" in result
        assert "# test_prop:" in result

    def test_generate_yaml_with_data_definitions_handles_errors_gracefully(self):
        """Test error handling in _generate_yaml_with_data_definitions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Invalid data that might cause errors
        data = {
            "valid_key": "valid_value",
            "property_definitions": {
                "test_prop": {"type": "string", "description": "Test"}
            },
        }

        # Mock _generate_data_documentation_header to raise an exception to test error handling
        with patch.object(
            engine,
            "_generate_data_documentation_header",
            side_effect=Exception("Documentation error"),
        ):
            result = engine._generate_yaml_with_data_definitions(
                data, data["property_definitions"]
            )

            # Should fallback to basic YAML without property_definitions
            assert "valid_key: valid_value" in result
            assert "property_definitions:" not in result

    def test_generate_data_documentation_header_basic_functionality(self):
        """Test _generate_data_documentation_header creates proper documentation."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        property_definitions = {
            "verbosity": {
                "type": "string",
                "enum": ["brief", "standard", "detailed"],
                "description": "Level of detail in artifacts",
            },
            "enforce_tdd": {
                "type": "boolean",
                "description": "Whether to enforce TDD practices",
            },
            "max_retries": {
                "type": "number",
                "description": "Maximum number of retries",
            },
        }

        result = engine._generate_data_documentation_header(property_definitions)

        # Should have proper header structure
        assert result.startswith("# Profile Properties Documentation:")
        assert "# verbosity:" in result
        assert "#   Description: Level of detail in artifacts" in result
        assert "#   Type: string" in result
        assert "#   Options: brief, standard, detailed" in result
        assert "# enforce_tdd:" in result
        assert "#   Type: boolean (true/false)" in result
        assert "# max_retries:" in result
        assert "#   Type: number" in result

    def test_generate_data_documentation_header_cleans_example_prefix(self):
        """Test that _generate_data_documentation_header removes 'Example: ' prefix."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        property_definitions = {
            "test_field": {
                "type": "string",
                "description": "Example: This is a test field with example prefix",
            }
        }

        result = engine._generate_data_documentation_header(property_definitions)

        # Should clean up the "Example: " prefix
        assert "#   Description: This is a test field with example prefix" in result
        assert "Example:" not in result

    def test_generate_data_documentation_header_handles_empty_definitions(self):
        """Test _generate_data_documentation_header with empty or invalid definitions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Test with empty definitions
        result = engine._generate_data_documentation_header({})
        assert result == ""

        # Test with None
        result = engine._generate_data_documentation_header(None)
        assert result == ""

        # Test with non-dict
        result = engine._generate_data_documentation_header("invalid")
        assert result == ""

    def test_add_minimal_data_comment_adds_comments_for_defined_properties(self):
        """Test _add_minimal_data_comment adds comments for properties in definitions."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        property_definitions = {
            "verbosity": {"type": "string", "description": "Test"},
            "enforce_tdd": {"type": "boolean", "description": "Test"},
        }

        # Test lines that should get comments
        result = engine._add_minimal_data_comment(
            "verbosity: detailed", property_definitions
        )
        assert result == "verbosity: detailed  # verbosity (documented above)"

        result = engine._add_minimal_data_comment(
            "enforce_tdd: false", property_definitions
        )
        assert result == "enforce_tdd: false  # enforce_tdd (documented above)"

        # Test lines that should NOT get comments
        result = engine._add_minimal_data_comment(
            "team_name: Test", property_definitions
        )
        assert result == "team_name: Test"  # No comment added

        result = engine._add_minimal_data_comment(
            "  nested: value", property_definitions
        )
        assert result == "  nested: value"  # Indented line, no comment

        result = engine._add_minimal_data_comment("- item", property_definitions)
        assert result == "- item"  # Array item, no comment

    def test_data_driven_yaml_generation_integration_test(self):
        """Integration test for complete data-driven YAML generation workflow."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Complete test data matching create-team-config structure
        data = {
            "team_name": "Mobile Development Team",
            "team_description": "A mobile app development team",
            "active_profile": "development",
            "property_definitions": {
                "verbosity": {
                    "type": "string",
                    "enum": ["brief", "standard", "detailed"],
                    "description": "Level of detail in generated artifacts",
                },
                "enforce_tdd": {
                    "type": "boolean",
                    "description": "Whether to enforce TDD practices",
                },
                "test_type": {
                    "type": "string",
                    "enum": ["unit_test_only", "integration_included"],
                    "description": "Example: Types of tests to generate",
                },
            },
            "profiles": {
                "development": {
                    "verbosity": "detailed",
                    "enforce_tdd": False,
                    "test_type": "unit_test_only",
                }
            },
        }

        # Test the complete workflow through the filter
        template_str = "{{ data | to_yaml }}"
        context = {"data": data}
        result = engine.render_template(template_str, context)

        # Verify complete workflow
        assert "# Profile Properties Documentation:" in result
        assert "# verbosity:" in result
        assert "#   Options: brief, standard, detailed" in result
        assert "# enforce_tdd:" in result
        assert "#   Type: boolean (true/false)" in result
        assert "# test_type:" in result
        assert (
            "#   Description: Types of tests to generate" in result
        )  # "Example:" prefix cleaned
        assert "Example:" not in result

        # Verify YAML structure
        assert "team_name: Mobile Development Team" in result
        assert "team_description: A mobile app development team" in result
        assert "active_profile: development" in result
        assert "profiles:" in result
        assert "verbosity: detailed" in result

        # Verify property_definitions excluded
        assert "property_definitions:" not in result


class TestRemoveSuffixFilter:
    """Test cases for the remove_suffix Jinja filter function."""

    def test_remove_suffix_basic_functionality(self):
        """Test basic suffix removal with exact string matching."""
        from pantheon.artifact_engine import remove_suffix

        # Basic cases from original docstring
        assert remove_suffix("pantheon-team", "-team") == "pantheon"
        assert remove_suffix("my-project", "-team") == "my-project"
        assert remove_suffix("team-name-team", "-team") == "team-name"

    def test_remove_suffix_case_sensitive_default(self):
        """Test that case-sensitive matching is the default behavior."""
        from pantheon.artifact_engine import remove_suffix

        assert remove_suffix("My Team", "team") == "My Team"  # Should not match
        assert remove_suffix("My team", "team") == "My "  # Should match
        assert (
            remove_suffix("PROJECT-TEAM", "-team") == "PROJECT-TEAM"
        )  # Should not match
        assert remove_suffix("project-team", "-team") == "project"  # Should match

    def test_remove_suffix_case_insensitive_single_suffix(self):
        """Test case-insensitive matching with single suffix."""
        from pantheon.artifact_engine import remove_suffix

        assert remove_suffix("My Team", "team", ignore_case=True) == "My "
        assert remove_suffix("My TEAM", "team", ignore_case=True) == "My "
        assert remove_suffix("My team", "TEAM", ignore_case=True) == "My "
        assert remove_suffix("PROJECT-TEAM", "-team", ignore_case=True) == "PROJECT"
        assert remove_suffix("project-Team", "-TEAM", ignore_case=True) == "project"

    def test_remove_suffix_multiple_patterns_case_sensitive(self):
        """Test multiple suffix patterns with case-sensitive matching."""
        from pantheon.artifact_engine import remove_suffix

        patterns = ["-team", " team", "_team"]

        assert remove_suffix("project-team", patterns) == "project"
        assert remove_suffix("my team", patterns) == "my"
        assert remove_suffix("app_team", patterns) == "app"
        assert remove_suffix("no-match", patterns) == "no-match"

    def test_remove_suffix_multiple_patterns_case_insensitive(self):
        """Test multiple suffix patterns with case-insensitive matching."""
        from pantheon.artifact_engine import remove_suffix

        patterns = ["-team", " team", "_team"]

        assert remove_suffix("project-TEAM", patterns, ignore_case=True) == "project"
        assert remove_suffix("My Team", patterns, ignore_case=True) == "My"
        assert remove_suffix("app_TEAM", patterns, ignore_case=True) == "app"
        assert remove_suffix("PROJECT TEAM", patterns, ignore_case=True) == "PROJECT"

    def test_remove_suffix_first_match_wins(self):
        """Test that the first matching pattern is used when multiple patterns match."""
        from pantheon.artifact_engine import remove_suffix

        # Order matters - first pattern that matches is used
        patterns = ["-team-backup", "-team"]  # Longer pattern first
        # Since "-team-backup" matches first (and completely), it removes the entire suffix
        assert remove_suffix("project-team-backup", patterns) == "project"

        patterns = ["-team", "-team-backup"]  # Shorter pattern first
        # Since "-team" doesn't match (string ends with "-backup"), "-team-backup" matches
        assert remove_suffix("project-team-backup", patterns) == "project"

        # Test that order really matters with overlapping patterns where both could match
        patterns = ["am", "team"]  # Test with a string that ends with both
        assert (
            remove_suffix("myproject-team", patterns) == "myproject-te"
        )  # "am" matches first

        patterns = ["team", "am"]  # Reverse order
        assert (
            remove_suffix("myproject-team", patterns) == "myproject-"
        )  # "team" matches first  # "-m" matches first

    def test_remove_suffix_non_string_inputs(self):
        """Test handling of non-string inputs."""
        from pantheon.artifact_engine import remove_suffix

        # Non-string text input
        assert remove_suffix(123, "3") == "12"
        assert remove_suffix(True, "e") == "Tru"

        # Non-string suffix input
        assert remove_suffix("test123", 123) == "test"

        # Both non-string
        assert remove_suffix(12345, 45) == "123"

    def test_remove_suffix_edge_cases(self):
        """Test edge cases and boundary conditions."""
        from pantheon.artifact_engine import remove_suffix

        # Empty strings
        assert remove_suffix("", "test") == ""
        assert remove_suffix("test", "") == "test"

        # Same strings
        assert remove_suffix("team", "team") == ""
        assert remove_suffix("TEAM", "team", ignore_case=True) == ""

        # Suffix longer than text
        assert remove_suffix("hi", "hello") == "hi"

        # Multiple occurrences - should only remove from end
        assert remove_suffix("team-team-team", "-team") == "team-team"

    def test_remove_suffix_empty_pattern_list(self):
        """Test behavior with empty pattern list."""
        from pantheon.artifact_engine import remove_suffix

        assert remove_suffix("test-team", []) == "test-team"

    def test_remove_suffix_complex_real_world_examples(self):
        """Test realistic usage scenarios."""
        from pantheon.artifact_engine import remove_suffix

        # Team name variations
        team_patterns = [" Team", " team", "-Team", "-team", "_Team", "_team"]

        test_cases = [
            ("Pantheon Development Team", "Pantheon Development"),
            ("my-awesome-team", "my-awesome"),
            ("API_SERVICE_TEAM", "API_SERVICE"),
            ("frontend Team", "frontend"),
            ("backend-TEAM", "backend"),
            ("mobile_team", "mobile"),
            ("no-suffix", "no-suffix"),  # No match
        ]

        for input_text, expected in test_cases:
            result = remove_suffix(input_text, team_patterns, ignore_case=True)
            assert result == expected, (
                f"Failed for input '{input_text}': got '{result}', expected '{expected}'"
            )

    def test_find_artifact_multi_artifact_mode_requires_id(self):
        """Test that find_artifact requires artifact_id when parser.jsonnet exists."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = True  # Multi-artifact mode

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact without ID in multi-artifact mode
        result = engine.find_artifact("get-ticket", None)

        # Assert: Should return None and log warning
        assert result is None
        mock_workspace.has_artifact_parser.assert_called_once_with("get-ticket")

    def test_find_artifact_multi_artifact_mode_normalizes_id(self):
        """Test that find_artifact normalizes ID in multi-artifact mode."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = True  # Multi-artifact mode
        mock_workspace.get_artifact_parser.return_value = """
        [
            { "pattern": "^\\\\s+|\\\\s+$", "replacement": "" },
            { "pattern": ".*[\\\\\\\\/]", "replacement": "" }
        ]
        """
        mock_workspace.get_artifact_locator.return_value = """
        {
            "directory": "tickets",
            "pattern": "^" + std.extVar("pantheon_artifact_id") + "_.*\\\\.md$"
        }
        """
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("tickets/T001_test.md")
        ]

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact with fuzzy ID
        result = engine.find_artifact("get-ticket", "  /path/to/T001  ")

        # Assert: Should normalize and find artifact
        assert result is not None
        assert str(result) == "tickets/T001_test.md"
        mock_workspace.has_artifact_parser.assert_called_once_with("get-ticket")
        mock_workspace.get_artifact_parser.assert_called_once_with("get-ticket")

    def test_find_artifact_singleton_mode_without_id(self):
        """Test that find_artifact works without ID when no parser.jsonnet exists."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = False  # Singleton mode
        mock_workspace.get_artifact_locator.return_value = """
        {
            "directory": "docs",
            "pattern": "^architecture-guide\\\\.md$"
        }
        """
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("docs/architecture-guide.md")
        ]

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact without ID in singleton mode
        result = engine.find_artifact("get-architecture-guide", None)

        # Assert: Should find the singleton artifact
        assert result is not None
        assert str(result) == "docs/architecture-guide.md"
        mock_workspace.has_artifact_parser.assert_called_once_with(
            "get-architecture-guide"
        )
        mock_workspace.get_artifact_locator.assert_called_once_with(
            "get-architecture-guide"
        )

    def test_find_artifact_singleton_mode_ignores_provided_id(self):
        """Test that singleton mode ignores artifact_id if provided."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = False  # Singleton mode
        mock_workspace.get_artifact_locator.return_value = """
        {
            "directory": "docs",
            "pattern": "^architecture-guide\\\\.md$"
        }
        """
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("docs/architecture-guide.md")
        ]

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact WITH ID in singleton mode (should be ignored)
        result = engine.find_artifact("get-architecture-guide", "some-ignored-id")

        # Assert: Should find the singleton artifact, ID ignored
        assert result is not None
        assert str(result) == "docs/architecture-guide.md"
        # Verify parser was NOT called (singleton mode)
        mock_workspace.get_artifact_parser.assert_not_called()

    def test_find_artifact_singleton_mode_no_artifacts_found(self):
        """Test that singleton mode returns None when no artifacts found."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = False  # Singleton mode
        mock_workspace.get_artifact_locator.return_value = """
        {
            "directory": "docs",
            "pattern": "^architecture-guide\\\\.md$"
        }
        """
        mock_workspace.get_matching_artifact.return_value = []  # No matches

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact when no artifacts exist
        result = engine.find_artifact("get-architecture-guide", None)

        # Assert: Should return None with appropriate warning
        assert result is None

    def test_find_artifact_singleton_mode_multiple_artifacts_error(self):
        """Test that singleton mode returns None when multiple artifacts found."""
        from unittest.mock import Mock

        mock_workspace = Mock()
        mock_workspace.has_artifact_parser.return_value = False  # Singleton mode
        mock_workspace.get_artifact_locator.return_value = """
        {
            "directory": "docs",
            "pattern": "^.*-guide\\\\.md$"
        }
        """
        mock_workspace.get_matching_artifact.return_value = [
            PantheonPath("docs/architecture-guide.md"),
            PantheonPath("docs/developer-guide.md"),
        ]  # Multiple matches (error condition)

        engine = ArtifactEngine(mock_workspace)

        # Act: Call find_artifact when multiple artifacts exist
        result = engine.find_artifact("get-guide", None)

        # Assert: Should return None and log warning about multiple matches
        assert result is None
