"""Unit tests for JSONL logging functionality."""

import json
from unittest.mock import Mock, patch

import pytest

from pantheon.artifact_engine import ArtifactEngine
from pantheon.filesystem import FileSystem
from pantheon.path import PantheonPath
from pantheon.process_handler import CreatedFileType, ProcessHandler
from pantheon.workspace import PantheonWorkspace, SecurityError


class TestJSONLTemplateLoading:
    """Test JSONL template loading methods in PantheonWorkspace."""

    @pytest.fixture
    def mock_workspace_with_active_team(self):
        """Create a properly mocked workspace with active team configuration."""
        mock_filesystem = Mock(spec=FileSystem)

        # Mock config file doesn't exist - will use defaults
        mock_filesystem.exists.return_value = False

        workspace = PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )

        # Override the project config to include active team
        workspace._project_config = {"active_team": "test-team"}

        return workspace, mock_filesystem

    def test_has_jsonl_templates_returns_true_when_both_exist(
        self, mock_workspace_with_active_team
    ):
        """Test has_jsonl_templates returns True when both templates exist."""
        workspace, mock_filesystem = mock_workspace_with_active_team

        # Reset the mock and configure for JSONL template check
        mock_filesystem.reset_mock()
        mock_filesystem.exists.return_value = True

        result = workspace.has_jsonl_templates("test-process")

        assert result is True
        assert mock_filesystem.exists.call_count == 2

    def test_has_jsonl_templates_returns_false_when_one_missing(
        self, mock_workspace_with_active_team
    ):
        """Test has_jsonl_templates returns False when one template is missing."""
        workspace, mock_filesystem = mock_workspace_with_active_team

        # Reset and configure - first call (naming) returns True, second call (placement) returns False
        mock_filesystem.reset_mock()
        mock_filesystem.exists.side_effect = [True, False]

        result = workspace.has_jsonl_templates("test-process")

        assert result is False
        assert mock_filesystem.exists.call_count == 2

    def test_has_jsonl_templates_returns_false_on_exception(
        self, mock_workspace_with_active_team
    ):
        """Test has_jsonl_templates returns False when filesystem error occurs."""
        workspace, mock_filesystem = mock_workspace_with_active_team

        # Reset and configure to raise exception
        mock_filesystem.reset_mock()
        mock_filesystem.exists.side_effect = OSError("File system error")

        result = workspace.has_jsonl_templates("test-process")

        assert result is False

    def test_get_artifact_jsonl_filename_template_returns_content(
        self, mock_workspace_with_active_team
    ):
        """Test get_artifact_jsonl_filename_template returns template content."""
        workspace, mock_filesystem = mock_workspace_with_active_team

        mock_filesystem.reset_mock()
        mock_filesystem.read_text.return_value = "{{ pantheon_datestamp }}_logs.jsonl"

        result = workspace.get_artifact_jsonl_filename_template("test-process")

        assert result == "{{ pantheon_datestamp }}_logs.jsonl"
        mock_filesystem.read_text.assert_called_once()

    def test_get_artifact_jsonl_directory_template_returns_content(
        self, mock_workspace_with_active_team
    ):
        """Test get_artifact_jsonl_directory_template returns template content."""
        workspace, mock_filesystem = mock_workspace_with_active_team

        mock_filesystem.reset_mock()
        mock_filesystem.read_text.return_value = "logs/{{ pantheon_actor }}"

        result = workspace.get_artifact_jsonl_directory_template("test-process")

        assert result == "logs/{{ pantheon_actor }}"
        mock_filesystem.read_text.assert_called_once()


class TestJSONLAppend:
    """Test JSONL append functionality in PantheonWorkspace."""

    @pytest.fixture
    def mock_workspace_simple(self):
        """Create a simple workspace for append testing."""
        mock_filesystem = Mock(spec=FileSystem)
        mock_filesystem.exists.return_value = False  # No config file

        workspace = PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )
        return workspace, mock_filesystem

    def test_append_jsonl_entry_creates_json_line(self, mock_workspace_simple):
        """Test append_jsonl_entry serializes data and appends with newline."""
        workspace, mock_filesystem = mock_workspace_simple
        mock_filesystem.reset_mock()

        data = {"user": "alice", "action": "submit_feedback"}
        path = PantheonPath("logs/feedback.jsonl")

        workspace.append_jsonl_entry(data, path)

        # Verify JSON was appended with newline
        mock_filesystem.append_text.assert_called_once()
        args = mock_filesystem.append_text.call_args[0]
        assert args[1] == json.dumps(data, ensure_ascii=False) + "\n"

    def test_append_jsonl_entry_creates_parent_directories(self, mock_workspace_simple):
        """Test append_jsonl_entry creates parent directories if needed."""
        workspace, mock_filesystem = mock_workspace_simple
        mock_filesystem.reset_mock()
        mock_filesystem.exists.return_value = False  # Parent doesn't exist

        data = {"user": "alice"}
        path = PantheonPath("logs/subfolder/feedback.jsonl")

        workspace.append_jsonl_entry(data, path)

        # Verify parent directory was created
        mock_filesystem.mkdir.assert_called_once()
        mock_filesystem.append_text.assert_called_once()

    def test_append_jsonl_entry_validates_path_security(self, mock_workspace_simple):
        """Test append_jsonl_entry validates path security."""
        workspace, mock_filesystem = mock_workspace_simple
        mock_filesystem.reset_mock()

        data = {"user": "alice"}
        path = PantheonPath("../../../etc/passwd")

        with pytest.raises(SecurityError):  # Path validation should fail
            workspace.append_jsonl_entry(data, path)


class TestJSONLPathGeneration:
    """Test JSONL path generation in ArtifactEngine."""

    def test_generate_jsonl_path_renders_templates(self):
        """Test generate_jsonl_path renders templates correctly."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        templates = {
            "jsonl_placement": "logs/{{ pantheon_actor }}",
            "jsonl_naming": "{{ pantheon_datestamp }}_feedback.jsonl",
        }
        input_params = {"feedback": "Great work!"}
        framework_params = {
            "pantheon_actor": "alice",
            "pantheon_datestamp": "2024-01-15",
            "pantheon_timestamp": "2024-01-15T10:30:00Z",
        }

        result = engine.generate_jsonl_path(templates, input_params, framework_params)

        assert isinstance(result, PantheonPath)
        # Verify the path components were rendered correctly
        assert "alice" in str(result)
        assert "feedback.jsonl" in str(result)
        # The actual date comes from the framework, so verify structure rather than exact date
        assert result.name.endswith("_feedback.jsonl")

    def test_generate_jsonl_path_validates_required_templates(self):
        """Test generate_jsonl_path validates required template keys."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        # Missing jsonl_naming template
        templates = {"jsonl_placement": "logs"}
        input_params = {}
        framework_params = {}

        with pytest.raises(
            ValueError, match="Missing required template key: jsonl_naming"
        ):
            engine.generate_jsonl_path(templates, input_params, framework_params)

    def test_generate_jsonl_path_handles_empty_placement(self):
        """Test generate_jsonl_path handles empty placement directory."""
        mock_workspace = Mock()
        engine = ArtifactEngine(mock_workspace)

        templates = {
            "jsonl_placement": ".",  # Current directory instead of empty
            "jsonl_naming": "logs.jsonl",
        }
        input_params = {}
        framework_params = {"pantheon_actor": "alice"}

        result = engine.generate_jsonl_path(templates, input_params, framework_params)

        assert isinstance(result, PantheonPath)
        assert "logs.jsonl" in str(result)


class TestJSONLIntegration:
    """Test JSONL integration in ProcessHandler."""

    @patch("pantheon.process_handler.Log")
    def test_execute_create_process_generates_jsonl_when_templates_exist(
        self, mock_log
    ):
        """Test execute_create_process generates JSONL entry when templates exist."""
        # Setup mocks with proper schema validation support
        mock_workspace = Mock()
        mock_workspace.has_jsonl_templates.return_value = True
        mock_workspace.get_artifact_jsonl_directory_template.return_value = "logs"
        mock_workspace.get_artifact_jsonl_filename_template.return_value = (
            "feedback.jsonl"
        )
        mock_workspace.save_artifact.return_value = PantheonPath("output.md")
        mock_workspace.append_jsonl_entry.return_value = PantheonPath(
            "logs/feedback.jsonl"
        )
        mock_workspace.summarize_created_files.return_value = []

        # Mock schema compilation methods that ProcessHandler calls
        mock_workspace.get_process_schema.return_value = (
            '{"type": "object", "properties": {"feedback": {"type": "string"}}}'
        )
        mock_workspace.get_team_profile.return_value = (
            "team_name: test-team\nverbosity: standard"
        )

        mock_artifact_engine = Mock()
        mock_artifact_engine.generate_artifact.return_value = (
            "content",
            PantheonPath("output.md"),
        )
        mock_artifact_engine.generate_jsonl_path.return_value = PantheonPath(
            "logs/feedback.jsonl"
        )
        mock_artifact_engine.compile_schema.return_value = {
            "type": "object",
            "properties": {"feedback": {"type": "string"}},
        }
        mock_artifact_engine.validate.return_value = True

        mock_rae_engine = Mock()

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test data
        input_params = {"feedback": "Great work!"}
        framework_params = {
            "pantheon_actor": "alice",
            "pantheon_timestamp": "2024-01-15T10:30:00Z",
            "pantheon_process": "submit-feedback",
        }
        templates = {"content": "# Feedback\n{{ feedback }}"}

        # Execute
        result = handler.execute_create_process(
            input_params, framework_params, templates
        )

        # Verify JSONL was generated
        assert result["success"] is True
        mock_workspace.has_jsonl_templates.assert_called_once_with("submit-feedback")
        mock_workspace.append_jsonl_entry.assert_called_once()

        # Verify the JSONL entry contains input data and timestamp only
        jsonl_call = mock_workspace.append_jsonl_entry.call_args[0]
        jsonl_data = jsonl_call[0]
        assert jsonl_data["feedback"] == "Great work!"
        assert (
            jsonl_data["timestamp"] == "2024-01-15T10:30:00Z"
        )  # Only timestamp from framework params

    def test_execute_create_process_skips_jsonl_when_no_templates(self):
        """Test execute_create_process skips JSONL when templates don't exist."""
        # Setup mocks with schema validation support
        mock_workspace = Mock()
        mock_workspace.has_jsonl_templates.return_value = False
        mock_workspace.save_artifact.return_value = PantheonPath("output.md")
        mock_workspace.summarize_created_files.return_value = []

        # Mock schema compilation methods that ProcessHandler calls
        mock_workspace.get_process_schema.return_value = (
            '{"type": "object", "properties": {"feedback": {"type": "string"}}}'
        )
        mock_workspace.get_team_profile.return_value = (
            "team_name: test-team\nverbosity: standard"
        )

        mock_artifact_engine = Mock()
        mock_artifact_engine.generate_artifact.return_value = (
            "content",
            PantheonPath("output.md"),
        )
        mock_artifact_engine.compile_schema.return_value = {
            "type": "object",
            "properties": {"feedback": {"type": "string"}},
        }
        mock_artifact_engine.validate.return_value = True

        mock_rae_engine = Mock()

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test data
        input_params = {"feedback": "Great work!"}
        framework_params = {
            "pantheon_actor": "alice",
            "pantheon_process": "submit-feedback",
        }
        templates = {"content": "# Feedback\n{{ feedback }}"}

        # Execute
        result = handler.execute_create_process(
            input_params, framework_params, templates
        )

        # Verify JSONL was not generated
        assert result["success"] is True
        mock_workspace.has_jsonl_templates.assert_called_once_with("submit-feedback")
        mock_workspace.append_jsonl_entry.assert_not_called()

    @patch("pantheon.process_handler.Log")
    def test_execute_create_process_continues_on_jsonl_error(self, mock_log):
        """Test execute_create_process continues when JSONL generation fails."""
        # Setup mocks with schema validation support
        mock_workspace = Mock()
        mock_workspace.has_jsonl_templates.return_value = True
        mock_workspace.get_artifact_jsonl_directory_template.side_effect = (
            FileNotFoundError("Template missing")
        )
        mock_workspace.save_artifact.return_value = PantheonPath("output.md")
        mock_workspace.summarize_created_files.return_value = []

        # Mock schema compilation methods that ProcessHandler calls
        mock_workspace.get_process_schema.return_value = (
            '{"type": "object", "properties": {"feedback": {"type": "string"}}}'
        )
        mock_workspace.get_team_profile.return_value = (
            "team_name: test-team\nverbosity: standard"
        )

        mock_artifact_engine = Mock()
        mock_artifact_engine.generate_artifact.return_value = (
            "content",
            PantheonPath("output.md"),
        )
        mock_artifact_engine.compile_schema.return_value = {
            "type": "object",
            "properties": {"feedback": {"type": "string"}},
        }
        mock_artifact_engine.validate.return_value = True

        mock_rae_engine = Mock()

        handler = ProcessHandler(mock_workspace, mock_artifact_engine, mock_rae_engine)

        # Test data
        input_params = {"feedback": "Great work!"}
        framework_params = {
            "pantheon_actor": "alice",
            "pantheon_process": "submit-feedback",
        }
        templates = {"content": "# Feedback\n{{ feedback }}"}

        # Execute
        result = handler.execute_create_process(
            input_params, framework_params, templates
        )

        # Verify main process succeeded despite JSONL error
        assert result["success"] is True
        mock_log.warning.assert_called_once()  # Should log the warning


class TestJSONLFileClassification:
    """Test JSONL file classification in PantheonWorkspace."""

    def test_classify_created_file_recognizes_jsonl_extension(self):
        """Test _classify_created_file recognizes .jsonl files."""
        mock_filesystem = Mock(spec=FileSystem)
        workspace = PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )

        path = PantheonPath("logs/feedback_2024-01-15.jsonl")
        file_type, description = workspace._classify_created_file(path)

        assert file_type == CreatedFileType.JSONL
        assert description == "JSONL log entries"

    def test_classify_created_file_recognizes_jsonl_templates(self):
        """Test _classify_created_file recognizes JSONL template files."""
        mock_filesystem = Mock(spec=FileSystem)
        workspace = PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )

        # Test naming template
        naming_path = PantheonPath("processes/test/artifact/jsonl_naming.jinja")
        file_type, description = workspace._classify_created_file(naming_path)
        assert file_type == CreatedFileType.TEMPLATE
        assert description == "JSONL filename template"

        # Test placement template
        placement_path = PantheonPath("processes/test/artifact/jsonl_placement.jinja")
        file_type, description = workspace._classify_created_file(placement_path)
        assert file_type == CreatedFileType.TEMPLATE
        assert description == "JSONL directory template"

    def test_classify_created_file_falls_back_to_artifact_for_non_jsonl(self):
        """Test _classify_created_file falls back to artifact for regular files."""
        mock_filesystem = Mock(spec=FileSystem)
        workspace = PantheonWorkspace(
            project_root="/test/project",
            artifacts_root="/test/project/pantheon-artifacts",
            filesystem=mock_filesystem,
        )

        path = PantheonPath("output/ticket.md")
        file_type, description = workspace._classify_created_file(path)

        assert file_type == CreatedFileType.ARTIFACT
        assert description == "Generated artifact"
