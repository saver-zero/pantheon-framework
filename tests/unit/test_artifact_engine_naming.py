"""
Test suite for ArtifactEngine new naming convention support.

This test suite validates that the ArtifactEngine correctly handles only the new
operation-specific naming conventions and properly rejects legacy filename patterns.
"""

from unittest.mock import Mock

import pytest

from pantheon.artifact_engine import ArtifactEngine, OperationType
from pantheon.workspace import PantheonWorkspace
from tests.helpers.process_input import make_framework_params


class TestArtifactEngineNaming:
    """Test ArtifactEngine naming convention handling."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_workspace = Mock(spec=PantheonWorkspace)

        # Mock the Jinja2 environment with proper filters support
        mock_env = Mock()
        filters_dict = {}  # Use a real dict that supports item assignment
        mock_env.filters = filters_dict
        mock_workspace.get_artifact_template_environment.return_value = mock_env
        mock_env.from_string.return_value.render.side_effect = (
            lambda **kwargs: f"# {kwargs.get('title', 'Default')}\n{kwargs.get('description', 'Default content')}"
        )

        self.engine = ArtifactEngine(mock_workspace)
        self.framework_params = make_framework_params("test-process", "test-actor")

    def test_detect_operation_type_create(self):
        """Test operation type detection for CREATE operations."""
        templates = {
            "content": "{{ title }}",
            "placement": "output/",
            "naming": "{{ id }}.md",
        }

        result = self.engine.detect_operation_type(templates)
        assert result == OperationType.CREATE

    def test_detect_operation_type_retrieve(self):
        """Test operation type detection for RETRIEVE operations."""
        templates = {
            "locator": "finder config",
            "parser": "normalizer rules",
            "sections": "section markers",
        }

        result = self.engine.detect_operation_type(templates)
        assert result == OperationType.RETRIEVE

    def test_detect_operation_type_update(self):
        """Test operation type detection for UPDATE operations."""
        templates = {
            "patch": "{{ updated_content }}",
            "locator": "finder config",
            "parser": "normalizer rules",
            "target": "section_bounds",
        }

        result = self.engine.detect_operation_type(templates)
        assert result == OperationType.UPDATE

    def test_detect_operation_type_invalid_combination(self):
        """Test that invalid template combinations are rejected."""
        templates = {"invalid": "template", "unknown": "keys"}

        with pytest.raises(ValueError, match="Invalid template combination"):
            self.engine.detect_operation_type(templates)

    def test_detect_operation_type_empty_templates(self):
        """Test that empty templates dictionary is rejected."""
        templates = {}

        with pytest.raises(ValueError, match="Invalid template combination"):
            self.engine.detect_operation_type(templates)

    def test_generate_artifact_create_operation(self):
        """Test generate_artifact with new CREATE naming convention."""
        templates = {
            "content": "# {{ title }}\n{{ description }}",
            "placement": "docs/",
            "naming": "{{ id }}.md",
        }
        input_data = {
            "title": "Test Document",
            "description": "Test content",
            "id": "test-001",
        }

        content, path = self.engine.generate_artifact(
            templates, input_data, self.framework_params
        )

        assert "# Test Document" in content
        assert "Test content" in content
        assert str(path).endswith("test-001.md")

    def test_generate_artifact_missing_content_key(self):
        """Test that missing content key raises proper error."""
        templates = {"placement": "docs/", "naming": "{{ id }}.md"}
        input_data = {"id": "test"}

        with pytest.raises(ValueError, match="Missing required template key: content"):
            self.engine.generate_artifact(templates, input_data, self.framework_params)

    def test_generate_artifact_missing_placement_key(self):
        """Test that missing placement key raises proper error."""
        templates = {"content": "# {{ title }}", "naming": "{{ id }}.md"}
        input_data = {"id": "test", "title": "Test"}

        with pytest.raises(
            ValueError, match="Missing required template key: placement"
        ):
            self.engine.generate_artifact(templates, input_data, self.framework_params)

    def test_generate_artifact_missing_naming_key(self):
        """Test that missing naming key raises proper error."""
        templates = {"content": "# {{ title }}", "placement": "docs/"}
        input_data = {"id": "test", "title": "Test"}

        with pytest.raises(ValueError, match="Missing required template key: naming"):
            self.engine.generate_artifact(templates, input_data, self.framework_params)


class TestArtifactEngineLegacyRejection:
    """Test that legacy filename patterns are properly rejected."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_workspace = Mock(spec=PantheonWorkspace)
        self.engine = ArtifactEngine(mock_workspace)
        self.framework_params = make_framework_params("test-process", "test-actor")

    def test_legacy_template_md_rejected(self):
        """Test that legacy template.md key is rejected in generate_artifact."""
        templates = {
            "template.md": "# {{ title }}",
            "directory.jinja": "docs/",
            "filename.jinja": "{{ id }}.md",
        }
        input_data = {"title": "Test", "id": "test-001"}

        with pytest.raises(ValueError, match="Missing required template key: content"):
            self.engine.generate_artifact(templates, input_data, self.framework_params)

    def test_legacy_directory_jinja_rejected(self):
        """Test that legacy directory.jinja key is rejected in generate_artifact."""
        templates = {
            "content": "# {{ title }}",
            "directory.jinja": "docs/",
            "filename.jinja": "{{ id }}.md",
        }
        input_data = {"title": "Test", "id": "test-001"}

        with pytest.raises(
            ValueError, match="Missing required template key: placement"
        ):
            self.engine.generate_artifact(templates, input_data, self.framework_params)

    def test_legacy_filename_jinja_rejected(self):
        """Test that legacy filename.jinja key is rejected in generate_artifact."""
        templates = {
            "content": "# {{ title }}",
            "placement": "docs/",
            "filename.jinja": "{{ id }}.md",
        }
        input_data = {"title": "Test", "id": "test-001"}

        with pytest.raises(ValueError, match="Missing required template key: naming"):
            self.engine.generate_artifact(templates, input_data, self.framework_params)

    def test_legacy_combination_rejected_by_operation_detection(self):
        """Test that legacy filename combinations are rejected by operation type detection."""
        legacy_templates = {
            "template.md": "content",
            "directory.jinja": "path",
            "filename.jinja": "name",
            "finder.jsonnet": "finder",
            "normalizer.jsonnet": "normalizer",
            "markers.jsonnet": "markers",
        }

        with pytest.raises(ValueError, match="Invalid template combination"):
            self.engine.detect_operation_type(legacy_templates)

    def test_mixed_legacy_new_rejected(self):
        """Test that mixing legacy and new naming is rejected."""
        mixed_templates = {
            "content": "# {{ title }}",  # New
            "directory.jinja": "docs/",  # Legacy
            "naming": "{{ id }}.md",  # New
        }

        with pytest.raises(
            ValueError, match="Missing required template key: placement"
        ):
            self.engine.generate_artifact(
                mixed_templates,
                {"title": "Test", "id": "test"},
                self.framework_params,
            )

    def test_error_messages_reference_new_naming_only(self):
        """Test that error messages reference only new naming scheme."""
        templates = {}
        input_data = {"title": "Test"}

        # Test content key error message
        with pytest.raises(ValueError) as exc_info:
            self.engine.generate_artifact(templates, input_data, self.framework_params)

        error_msg = str(exc_info.value)
        assert "content.md" in error_msg
        assert "template.md" not in error_msg

        # Test placement key error message
        templates = {"content": "test"}
        with pytest.raises(ValueError) as exc_info:
            self.engine.generate_artifact(
                templates,
                input_data,
                make_framework_params("test-process", "test-actor"),
            )

        error_msg = str(exc_info.value)
        assert "placement.jinja" in error_msg
        assert "directory.jinja" not in error_msg

        # Test naming key error message
        templates = {"content": "test", "placement": "docs/"}
        with pytest.raises(ValueError) as exc_info:
            self.engine.generate_artifact(
                templates,
                input_data,
                make_framework_params("test-process", "test-actor"),
            )

        error_msg = str(exc_info.value)
        assert "naming.jinja" in error_msg
        assert "filename.jinja" not in error_msg
