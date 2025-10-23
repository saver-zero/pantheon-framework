"""Unit tests for ArtifactEngine section extraction functionality."""

import json
from unittest.mock import MagicMock

import pytest

from pantheon.artifact_engine import ArtifactEngine
from pantheon.path import PantheonPath


class TestArtifactEngineSections:
    """Test section extraction functionality for all supported cases."""

    @pytest.fixture
    def mock_workspace(self):
        """Create a mock workspace for testing."""
        return MagicMock()

    @pytest.fixture
    def artifact_engine(self, mock_workspace):
        """Create ArtifactEngine instance with mock workspace."""
        return ArtifactEngine(mock_workspace)

    def test_case_3_multiple_sections_with_section_names(
        self, artifact_engine, mock_workspace
    ):
        """Test Case 3: Multiple sections with nested structure - specific sections requested."""
        # Setup markers configuration (Case 3: nested sections structure)
        markers_config = {
            "sections": {
                "description": {
                    "start": "<!-- SECTION:START:DESCRIPTION -->",
                    "end": "<!-- SECTION:END:DESCRIPTION -->",
                },
                "plan": {
                    "start": "<!-- SECTION:START:PLAN -->",
                    "end": "<!-- SECTION:END:PLAN -->",
                },
                "status": {
                    "start": "<!-- SECTION:START:STATUS -->",
                    "end": "<!-- SECTION:END:STATUS -->",
                },
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        # Setup file content with sections
        file_content = """# Test Artifact

<!-- SECTION:START:DESCRIPTION -->
This is the description content.
Multiple lines of description here.
<!-- SECTION:END:DESCRIPTION -->

<!-- SECTION:START:PLAN -->
This is the implementation plan.
Step 1: Do something
Step 2: Do something else
<!-- SECTION:END:PLAN -->

<!-- SECTION:START:STATUS -->
Status: In Progress
<!-- SECTION:END:STATUS -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test requesting specific sections
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description", "plan"]
        )

        # Verify results
        assert len(result) == 2
        assert "description" in result
        assert "plan" in result
        assert "status" not in result  # Not requested

        assert "This is the description content." in result["description"]
        assert "Multiple lines of description here." in result["description"]
        assert "This is the implementation plan." in result["plan"]
        assert "Step 1: Do something" in result["plan"]

    def test_case_3_multiple_sections_no_section_names(
        self, artifact_engine, mock_workspace
    ):
        """Test Case 3: Multiple sections with nested structure - no sections specified (return all)."""
        # Setup markers configuration (Case 3: nested sections structure)
        markers_config = {
            "sections": {
                "description": {
                    "start": "<!-- SECTION:START:DESCRIPTION -->",
                    "end": "<!-- SECTION:END:DESCRIPTION -->",
                },
                "plan": {
                    "start": "<!-- SECTION:START:PLAN -->",
                    "end": "<!-- SECTION:END:PLAN -->",
                },
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        # Setup file content
        file_content = """# Test Artifact

<!-- SECTION:START:DESCRIPTION -->
Description content here.
<!-- SECTION:END:DESCRIPTION -->

<!-- SECTION:START:PLAN -->
Plan content here.
<!-- SECTION:END:PLAN -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test requesting no specific sections (should return all)
        result = artifact_engine.get_artifact_sections(
            "test-process",
            PantheonPath("test/artifact.md"),
            [],  # Empty list - should return all sections
        )

        # Verify all sections are returned
        assert len(result) == 2
        assert "description" in result
        assert "plan" in result

        assert "Description content here." in result["description"]
        assert "Plan content here." in result["plan"]

    def test_case_3_multiple_sections_with_placeholder(
        self, artifact_engine, mock_workspace
    ):
        """Test Case 3: Multiple sections - skip sections with only placeholder content."""
        # Setup markers configuration
        markers_config = {
            "sections": {
                "description": {
                    "start": "<!-- SECTION:START:DESCRIPTION -->",
                    "end": "<!-- SECTION:END:DESCRIPTION -->",
                },
                "plan": {
                    "start": "<!-- SECTION:START:PLAN -->",
                    "end": "<!-- SECTION:END:PLAN -->",
                },
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        # Setup file content with one real section and one placeholder section
        file_content = """# Test Artifact

<!-- SECTION:START:DESCRIPTION -->
Real description content.
<!-- SECTION:END:DESCRIPTION -->

<!-- SECTION:START:PLAN -->
<!-- SECTION:PLACEHOLDER -->
<!-- SECTION:END:PLAN -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description", "plan"]
        )

        # Verify only non-placeholder section is returned
        assert len(result) == 1
        assert "description" in result
        assert "plan" not in result  # Should be skipped because it's just a placeholder

        assert "Real description content." in result["description"]

    def test_case_2_single_section_with_section_names(
        self, artifact_engine, mock_workspace
    ):
        """Test Case 2: Single section with flat structure - specific sections requested."""
        # Setup markers configuration (Case 2: flat structure)
        markers_config = {
            "section_start": "<!-- START:{name} -->",
            "section_end": "<!-- END:{name} -->",
            "placeholder": "<!-- PLACEHOLDER -->",
        }

        # Setup file content with formatted sections
        file_content = """# Test Artifact

<!-- START:description -->
Single section description content.
<!-- END:description -->

<!-- START:notes -->
Some notes content.
<!-- END:notes -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test requesting specific sections
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description"]
        )

        # Verify results
        assert len(result) == 1
        assert "description" in result
        assert "Single section description content." in result["description"]

    def test_case_2_single_section_no_section_names(
        self, artifact_engine, mock_workspace
    ):
        """Test Case 2: Single section with flat structure - no sections specified (return empty)."""
        # Setup markers configuration (Case 2: flat structure)
        markers_config = {
            "section_start": "<!-- START:{name} -->",
            "section_end": "<!-- END:{name} -->",
            "placeholder": "<!-- PLACEHOLDER -->",
        }

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = "Some content"

        # Test requesting no specific sections (should return empty for single section case)
        result = artifact_engine.get_artifact_sections(
            "test-process",
            PantheonPath("test/artifact.md"),
            [],  # Empty list
        )

        # Verify empty result (can't auto-determine sections in flat structure)
        assert len(result) == 0

    def test_single_section_skips_placeholder(self, artifact_engine, mock_workspace):
        """Test Case 2: Single section extraction filters placeholder-only sections."""
        # Setup markers configuration (Case 2: flat structure)
        markers_config = {
            "section_start": "<!-- START:{name} -->",
            "section_end": "<!-- END:{name} -->",
            "placeholder": "<!-- PLACEHOLDER -->",
        }

        # Setup file content with placeholder section
        file_content = """# Test Artifact

<!-- START:description -->
<!-- PLACEHOLDER -->
<!-- END:description -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test extraction requesting the placeholder section
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description"]
        )

        # Verify placeholder section is filtered (empty dict returned)
        assert len(result) == 0
        assert "description" not in result

    def test_placeholder_whitespace_handling(self, artifact_engine, mock_workspace):
        """Test placeholder filtering detects presence of marker, not just exact equality."""
        # Setup markers configuration
        markers_config = {
            "section_start": "<!-- START:{name} -->",
            "section_end": "<!-- END:{name} -->",
            "placeholder": "<!-- PLACEHOLDER -->",
        }

        # Setup file content with different placeholder scenarios
        file_content = """# Test Artifact

<!-- START:whitespace_only -->
   <!-- PLACEHOLDER -->
<!-- END:whitespace_only -->

<!-- START:placeholder_with_content -->
<!-- PLACEHOLDER -->
Additional content here
<!-- END:placeholder_with_content -->

<!-- START:actual_content -->
Real content without placeholder marker
<!-- END:actual_content -->
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process",
            PantheonPath("test/artifact.md"),
            ["whitespace_only", "placeholder_with_content", "actual_content"],
        )

        # Verify sections with placeholder marker (anywhere) are filtered
        assert "whitespace_only" not in result
        assert "placeholder_with_content" not in result

        # Verify section without placeholder marker is NOT filtered
        assert "actual_content" in result
        assert "Real content without placeholder marker" in result["actual_content"]

    def test_case_1_no_sections_placeholder_only(self, artifact_engine, mock_workspace):
        """Test Case 1: No sections structure - document with only placeholder."""
        # Setup markers configuration (Case 1: only placeholder)
        markers_config = {"placeholder": "<!-- PLACEHOLDER -->"}

        # Setup file content with just placeholder
        file_content = "<!-- PLACEHOLDER -->"

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), []
        )

        # Verify empty result (placeholder only)
        assert len(result) == 0

    def test_case_1_no_sections_with_content(self, artifact_engine, mock_workspace):
        """Test Case 1: No sections structure - document with actual content."""
        # Setup markers configuration (Case 1: only placeholder)
        markers_config = {"placeholder": "<!-- PLACEHOLDER -->"}

        # Setup file content with actual content
        file_content = """# Real Document

This is actual document content.
It has multiple lines and real information.
"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), []
        )

        # Verify entire content is returned as single section
        assert len(result) == 1
        assert "content" in result
        assert "# Real Document" in result["content"]
        assert "This is actual document content." in result["content"]

    def test_missing_markers_configuration(self, artifact_engine, mock_workspace):
        """Test handling of missing marker configuration."""
        # Mock workspace methods with empty markers
        mock_workspace.get_artifact_section_markers.return_value = ""

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description"]
        )

        # Verify empty result
        assert len(result) == 0

    def test_invalid_markers_json(self, artifact_engine, mock_workspace):
        """Test handling of invalid JSON in markers configuration."""
        # Mock workspace methods with invalid JSON
        mock_workspace.get_artifact_section_markers.return_value = "invalid json {"

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description"]
        )

        # Verify empty result (graceful error handling)
        assert len(result) == 0

    def test_file_read_error(self, artifact_engine, mock_workspace):
        """Test handling of file read errors."""
        # Setup valid markers
        markers_config = {
            "sections": {
                "description": {"start": "<!-- START -->", "end": "<!-- END -->"}
            },
            "placeholder": "<!-- PLACEHOLDER -->",
        }

        # Mock workspace methods - markers work but file read fails
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.side_effect = Exception("File not found")

        # Test extraction
        result = artifact_engine.get_artifact_sections(
            "test-process", PantheonPath("test/artifact.md"), ["description"]
        )

        # Verify empty result (graceful error handling)
        assert len(result) == 0

    def test_section_not_in_configuration(self, artifact_engine, mock_workspace):
        """Test requesting a section that doesn't exist in configuration."""
        # Setup markers configuration
        markers_config = {
            "sections": {
                "description": {
                    "start": "<!-- SECTION:START:DESCRIPTION -->",
                    "end": "<!-- SECTION:END:DESCRIPTION -->",
                }
            },
            "placeholder": "<!-- SECTION:PLACEHOLDER -->",
        }

        file_content = """<!-- SECTION:START:DESCRIPTION -->
Description content
<!-- SECTION:END:DESCRIPTION -->"""

        # Mock workspace methods
        mock_workspace.get_artifact_section_markers.return_value = json.dumps(
            markers_config
        )
        mock_workspace.read_artifact_file.return_value = file_content

        # Test requesting non-existent section
        result = artifact_engine.get_artifact_sections(
            "test-process",
            PantheonPath("test/artifact.md"),
            ["description", "nonexistent"],  # One exists, one doesn't
        )

        # Verify only existing section is returned
        assert len(result) == 1
        assert "description" in result
        assert "nonexistent" not in result
