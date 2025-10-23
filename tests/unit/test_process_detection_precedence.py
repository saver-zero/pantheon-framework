from unittest.mock import Mock

from pantheon.process_handler import (
    PROCESS_TYPE_CREATE,
    PROCESS_TYPE_GET,
    ProcessHandler,
)


def _make_handler_for_detection() -> tuple[ProcessHandler, Mock, Mock, Mock]:
    ws = Mock()
    eng = Mock()
    rae = Mock()
    # routine existence check must pass
    ws.get_process_routine.return_value = "# routine"
    return ProcessHandler(ws, eng, rae), ws, eng, rae


def test_precedence_create_over_update_and_build():
    handler, ws, _eng, _rae = _make_handler_for_detection()

    # Simulate all signals present: content+patch+build
    ws.get_artifact_content_template.return_value = "content.md"
    ws.get_artifact_patch_template.return_value = "patch.md"
    ws.has_build_schema.return_value = True

    ptype, templates = handler.determine_process_type("proc")
    assert ptype == PROCESS_TYPE_CREATE
    assert "content" in templates


def test_precedence_create_over_build():
    handler, ws, _eng, _rae = _make_handler_for_detection()

    # No UPDATE; both BUILD and CREATE present
    ws.get_artifact_patch_template.side_effect = FileNotFoundError()
    ws.has_build_schema.return_value = True
    ws.get_artifact_content_template.return_value = "content.md"

    ptype, templates = handler.determine_process_type("proc")
    assert ptype == PROCESS_TYPE_CREATE
    assert "content" in templates


def test_precedence_create_over_get():
    handler, ws, _eng, _rae = _make_handler_for_detection()

    # Only CREATE present
    ws.get_artifact_patch_template.side_effect = FileNotFoundError()
    ws.has_build_schema.return_value = False
    ws.get_artifact_content_template.return_value = "content.md"

    ptype, templates = handler.determine_process_type("proc")
    assert ptype == PROCESS_TYPE_CREATE
    assert "content" in templates


def test_default_get_when_no_other_signals():
    handler, ws, _eng, _rae = _make_handler_for_detection()

    # No UPDATE, BUILD, or CREATE
    ws.get_artifact_patch_template.side_effect = FileNotFoundError()
    ws.has_build_schema.return_value = False
    ws.get_artifact_content_template.side_effect = FileNotFoundError()

    ptype, templates = handler.determine_process_type("proc")
    assert ptype == PROCESS_TYPE_GET
    assert templates == {}
