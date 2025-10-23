"""Unit tests for the RaeEngine routine rendering behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from pantheon.constants import PARAM_SECTIONS, PROCESS_TYPE_UPDATE
from pantheon.rae_engine import RaeEngine


class TestRaeEngine:
    """Validate routine rendering and context enrichment."""

    def test_get_routine_renders_with_artifact_engine(self) -> None:
        """RaeEngine should render the routine via ArtifactEngine with provided context."""

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_workspace.get_process_routine.return_value = "Routine template"
        process_dir = Path("/tmp/process-dir")
        mock_workspace.get_process_directory.return_value = process_dir
        mock_artifact_engine._create_template_context.return_value = {
            "pantheon_process": "test-process",
            "input_data": {},
        }
        mock_artifact_engine.render_artifact_template.return_value = "Rendered output"

        engine = RaeEngine(mock_workspace, mock_artifact_engine)

        result = engine.get_routine(
            "test-process",
            input_params={"foo": "bar"},
            framework_params={"baz": "qux"},
            process_type="get",
        )

        mock_workspace.get_process_routine.assert_called_once_with("test-process")
        mock_workspace.get_process_directory.assert_called_once_with("test-process")
        mock_artifact_engine._create_template_context.assert_called_once()
        args, _ = mock_artifact_engine._create_template_context.call_args
        assert args[0] == {"foo": "bar"}
        assert args[1]["baz"] == "qux"
        assert args[1]["pantheon_process"] == "test-process"
        # RaeEngine always uses "ROUTINE" operation type when retrieving instructions
        # to avoid triggering artifact ID generation for CREATE processes
        assert args[2] == "ROUTINE"

        mock_artifact_engine.render_artifact_template.assert_called_once()
        (
            render_args,
            render_kwargs,
        ) = mock_artifact_engine.render_artifact_template.call_args
        assert render_args[0] == "Routine template"
        assert render_kwargs["template_name"] == "test-process/routine.md"
        env = render_args[2]
        assert isinstance(env.loader.searchpath, list)
        assert str(process_dir) in env.loader.searchpath[0]
        assert result == "Rendered output"

    def test_get_routine_enriches_update_context(self) -> None:
        """For UPDATE processes, RaeEngine should inject section metadata."""

        mock_workspace = Mock()
        mock_artifact_engine = Mock()
        mock_workspace.get_process_routine.return_value = "Routine"
        mock_workspace.get_process_directory.return_value = Path("/tmp/update-process")
        mock_workspace.get_process_schema.return_value = '{"properties": {"sections": {"properties": {"plan": {}}}, "section_order": {"default": ["plan", "summary"]}}}'
        compiled_schema = {
            "properties": {
                "sections": {"properties": {"plan": {}, "summary": {}}},
                "section_order": {"default": ["plan", "summary"]},
            }
        }
        mock_artifact_engine.compile_schema.return_value = compiled_schema
        mock_artifact_engine._create_template_context.return_value = {}
        mock_artifact_engine.render_artifact_template.return_value = "Rendered"

        engine = RaeEngine(mock_workspace, mock_artifact_engine)

        engine.get_routine(
            "update-team-blueprint",
            input_params={},
            framework_params={PARAM_SECTIONS: ["plan"]},
            process_type=PROCESS_TYPE_UPDATE,
        )

        mock_artifact_engine.compile_schema.assert_called_once()
        context_args, _ = mock_artifact_engine._create_template_context.call_args
        framework_context = context_args[1]
        assert framework_context["section_order"] == ["plan", "summary"]
        assert framework_context["initial_section"] == "plan"
        assert framework_context["artifact"] == "team-blueprint"
        assert framework_context[PARAM_SECTIONS] == ["plan"]

    def test_get_routine_file_not_found_propagates(self) -> None:
        """FileNotFoundError from workspace should propagate to caller."""

        mock_workspace = Mock()
        mock_workspace.get_process_routine.side_effect = FileNotFoundError("missing")
        mock_artifact_engine = Mock()

        engine = RaeEngine(mock_workspace, mock_artifact_engine)

        with pytest.raises(FileNotFoundError):
            engine.get_routine("missing-process")

        mock_workspace.get_process_routine.assert_called_once_with("missing-process")
