import json
import re
from unittest.mock import Mock, patch

import pytest

from pantheon.filesystem import FileSystem
from pantheon.path import PantheonPath
from pantheon.workspace import (
    CONFIG_KEY_AUDIT_DIRECTORY,
    CONFIG_KEY_AUDIT_ENABLED,
    DEFAULT_AUDIT_DIRECTORY,
    PantheonWorkspace,
    SecurityError,
)


def test_save_audit_log_appends_and_creates_dir() -> None:
    fs = Mock(spec=FileSystem)
    # Directory does not exist initially
    fs.exists.return_value = False

    config = {
        "active_team": "team-a",
        "artifacts_root": "/project/pantheon-artifacts",
        CONFIG_KEY_AUDIT_ENABLED: True,
        CONFIG_KEY_AUDIT_DIRECTORY: DEFAULT_AUDIT_DIRECTORY,
    }

    with patch.object(PantheonWorkspace, "load_project_config", return_value=config):
        ws = PantheonWorkspace("/project", "/project/pantheon-artifacts", fs)

    event = {
        "timestamp": "2025-09-02 10:32:22 PM PDT",
        "team": "team-a",
        "command": "execute create-ticket",
        "actor": "tech-lead",
        "id": "",
        "sections": "",
        "result": "success",
    }

    ws.save_audit_log(event)

    # Assert directory created under artifacts_root/audit_directory (platform-agnostic)
    expected_root = ws._artifacts_root / DEFAULT_AUDIT_DIRECTORY
    fs.mkdir.assert_called_once()
    mkdir_args, mkdir_kwargs = fs.mkdir.call_args
    assert mkdir_args[0] == expected_root
    assert mkdir_kwargs.get("parents") is True
    assert mkdir_kwargs.get("exist_ok") is True

    # Assert append_text called with daily file and valid JSON line
    fs.append_text.assert_called_once()
    append_args, _ = fs.append_text.call_args
    audit_file_path = append_args[0]
    content_line = append_args[1]

    # Path checks
    assert audit_file_path.parent == expected_root
    assert re.match(r"\d{4}-\d{2}-\d{2}_cli\.jsonl$", audit_file_path.name)

    # Content is one JSON object + newline
    assert content_line.endswith("\n")
    parsed = json.loads(content_line.strip())
    assert parsed == event


def test_save_audit_log_noop_when_disabled() -> None:
    fs = Mock(spec=FileSystem)
    # Directory existence shouldn't matter; saving should early-return
    fs.exists.return_value = False

    config = {
        "active_team": "team-a",
        "artifacts_root": "/project/pantheon-artifacts",
        CONFIG_KEY_AUDIT_ENABLED: False,
        CONFIG_KEY_AUDIT_DIRECTORY: DEFAULT_AUDIT_DIRECTORY,
    }

    with patch.object(PantheonWorkspace, "load_project_config", return_value=config):
        ws = PantheonWorkspace("/project", "/project/pantheon-artifacts", fs)

    ws.save_audit_log({"foo": "bar"})

    fs.mkdir.assert_not_called()
    fs.append_text.assert_not_called()


def test_save_artifact_blocks_writes_into_audit_dir() -> None:
    fs = Mock(spec=FileSystem)
    fs.exists.return_value = True

    config = {
        "active_team": "team-a",
        "artifacts_root": "/project/pantheon-artifacts",
        CONFIG_KEY_AUDIT_ENABLED: True,
        CONFIG_KEY_AUDIT_DIRECTORY: DEFAULT_AUDIT_DIRECTORY,
    }

    with patch.object(PantheonWorkspace, "load_project_config", return_value=config):
        ws = PantheonWorkspace("/project", "/project/pantheon-artifacts", fs)

    # Attempt to write into the reserved audit directory
    evil_path = PantheonPath(DEFAULT_AUDIT_DIRECTORY, "intrusion.txt")

    with pytest.raises(SecurityError):
        ws.save_artifact("should not write", evil_path)

    fs.write_text.assert_not_called()


def test_read_artifact_blocks_reads_from_audit_dir() -> None:
    fs = Mock(spec=FileSystem)
    fs.exists.return_value = True

    config = {
        "active_team": "team-a",
        "artifacts_root": "/project/pantheon-artifacts",
        CONFIG_KEY_AUDIT_ENABLED: True,
        CONFIG_KEY_AUDIT_DIRECTORY: DEFAULT_AUDIT_DIRECTORY,
    }

    with patch.object(PantheonWorkspace, "load_project_config", return_value=config):
        ws = PantheonWorkspace("/project", "/project/pantheon-artifacts", fs)

    # Attempt to read from the reserved audit directory
    audit_file = PantheonPath(DEFAULT_AUDIT_DIRECTORY, "some_day_cli.jsonl")

    with pytest.raises(SecurityError):
        ws.read_artifact_file(audit_file)

    fs.read_text.assert_not_called()
