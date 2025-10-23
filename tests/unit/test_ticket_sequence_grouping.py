"""Unit tests for ticket sequence grouping feature (T087)."""

from unittest.mock import Mock

import pytest

from pantheon.artifact_engine import ArtifactEngine


class TestSequenceGroupingSchemaValidation:
    """Test schema validation for sequence grouping fields."""

    def test_schema_accepts_both_sequence_fields(self):
        """Test that schema validation accepts tickets with both sequence fields populated."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Schema with sequence fields and all-or-nothing dependency
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "sequence_number": {"type": "integer", "minimum": 1},
                "sequence_description": {
                    "type": "string",
                    "maxLength": 11,
                    "pattern": "^[a-z]+$",
                },
            },
            "required": ["title", "description"],
            "dependentRequired": {
                "sequence_number": ["sequence_description"],
                "sequence_description": ["sequence_number"],
            },
        }

        # Valid data with both sequence fields
        valid_data = {
            "title": "Test Ticket",
            "description": "Test description",
            "sequence_number": 1,
            "sequence_description": "foundation",
        }

        # Test validation passes
        result = engine.validate(valid_data, schema)
        assert result is True

    def test_schema_rejects_only_sequence_number(self):
        """Test that schema validation rejects tickets with only sequence_number (all-or-nothing constraint)."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Schema with all-or-nothing dependency
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "sequence_number": {"type": "integer", "minimum": 1},
                "sequence_description": {
                    "type": "string",
                    "maxLength": 11,
                    "pattern": "^[a-z]+$",
                },
            },
            "required": ["title", "description"],
            "dependentRequired": {
                "sequence_number": ["sequence_description"],
                "sequence_description": ["sequence_number"],
            },
        }

        # Invalid data - only sequence_number provided
        invalid_data = {
            "title": "Test Ticket",
            "description": "Test description",
            "sequence_number": 1,
            # Missing sequence_description - should fail dependency check
        }

        # Test validation fails
        with pytest.raises(ValueError) as exc_info:
            engine.validate(invalid_data, schema)

        error_message = str(exc_info.value)
        assert (
            "sequence_description" in error_message
            or "dependencies" in error_message.lower()
        )

    def test_schema_rejects_only_sequence_description(self):
        """Test that schema validation rejects tickets with only sequence_description (all-or-nothing constraint)."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Schema with all-or-nothing dependency
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "sequence_number": {"type": "integer", "minimum": 1},
                "sequence_description": {
                    "type": "string",
                    "maxLength": 11,
                    "pattern": "^[a-z]+$",
                },
            },
            "required": ["title", "description"],
            "dependentRequired": {
                "sequence_number": ["sequence_description"],
                "sequence_description": ["sequence_number"],
            },
        }

        # Invalid data - only sequence_description provided
        invalid_data = {
            "title": "Test Ticket",
            "description": "Test description",
            "sequence_description": "foundation",
            # Missing sequence_number - should fail dependency check
        }

        # Test validation fails
        with pytest.raises(ValueError) as exc_info:
            engine.validate(invalid_data, schema)

        error_message = str(exc_info.value)
        assert (
            "sequence_number" in error_message
            or "dependencies" in error_message.lower()
        )

    def test_schema_accepts_ticket_without_sequence_fields(self):
        """Test that schema validation accepts tickets without any sequence fields (backward compatible)."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Schema with optional sequence fields
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "sequence_number": {"type": "integer", "minimum": 1},
                "sequence_description": {
                    "type": "string",
                    "maxLength": 11,
                    "pattern": "^[a-z]+$",
                },
            },
            "required": ["title", "description"],
            "dependentRequired": {
                "sequence_number": ["sequence_description"],
                "sequence_description": ["sequence_number"],
            },
        }

        # Valid data without sequence fields
        valid_data = {"title": "Test Ticket", "description": "Test description"}

        # Test validation passes
        result = engine.validate(valid_data, schema)
        assert result is True


class TestSequenceGroupingPlacementTemplate:
    """Test placement template rendering for sequence grouping."""

    def test_placement_template_with_sequence_fields(self):
        """Test that placement template generates S{:02d}-{description} directory when sequence fields present."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Template with sequence grouping logic
        placement_template = """{% if sequence_number and sequence_description %}tickets/0_backlog/S{{ '{:02d}'.format(sequence_number) }}-{{ sequence_description }}/{{ assignee | replace('@', '') | slugify }}{% else %}tickets/0_backlog/{{ assignee | replace('@', '') | slugify }}{% endif %}"""

        # Input data with sequence fields
        input_data = {
            "sequence_number": 1,
            "sequence_description": "foundation",
            "assignee": "tech-lead",
        }

        # Render template using actual Jinja2 rendering
        result = engine.render_template(placement_template, input_data)

        # Verify correct S{:02d}-{description} format
        assert result == "tickets/0_backlog/S01-foundation/tech-lead"

    def test_placement_template_backward_compatibility(self):
        """Test that placement template maintains backward compatibility without sequence fields."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Template with sequence grouping logic (backward compatible)
        placement_template = """{% if sequence_number and sequence_description %}tickets/0_backlog/S{{ '{:02d}'.format(sequence_number) }}-{{ sequence_description }}/{{ assignee | replace('@', '') | slugify }}{% else %}tickets/0_backlog/{{ assignee | replace('@', '') | slugify }}{% endif %}"""

        # Input data without sequence fields
        input_data = {"assignee": "framework-engineer"}

        # Render template using actual Jinja2 rendering
        result = engine.render_template(placement_template, input_data)

        # Verify backward compatible flat structure
        assert result == "tickets/0_backlog/framework-engineer"

    def test_placement_template_various_sequence_numbers(self):
        """Test placement template correctly formats various sequence numbers."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Template with sequence grouping
        placement_template = """{% if sequence_number and sequence_description %}tickets/0_backlog/S{{ '{:02d}'.format(sequence_number) }}-{{ sequence_description }}/{{ assignee | replace('@', '') | slugify }}{% else %}tickets/0_backlog/{{ assignee | replace('@', '') | slugify }}{% endif %}"""

        # Test various sequence numbers
        test_cases = [
            (1, "foundation", "S01-foundation"),
            (9, "core", "S09-core"),
            (10, "polish", "S10-polish"),
            (99, "final", "S99-final"),
        ]

        for seq_num, seq_desc, expected_dir in test_cases:
            input_data = {
                "sequence_number": seq_num,
                "sequence_description": seq_desc,
                "assignee": "tech-lead",
            }

            # Test actual Jinja2 template rendering
            result = engine.render_template(placement_template, input_data)
            assert f"/{expected_dir}/" in result
