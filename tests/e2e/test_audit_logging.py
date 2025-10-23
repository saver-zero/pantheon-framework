"""End-to-end tests for CLI audit logging."""

import json
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_audit_log_records_get_process_event(
    temp_project: Path, run_pantheon, setup_test_project
) -> None:
    """Enable auditing and verify that a GET command produces a JSONL event."""

    # Set up project with test team
    setup_test_project()

    # Enable audit logging in .pantheon_project
    project_file = temp_project / ".pantheon_project"
    content = project_file.read_text()
    if "audit_enabled:" not in content:
        content += "\naudit_enabled: true\n"
        content += "audit_directory: pantheon-audit\n"
        project_file.write_text(content)
    else:
        # Replace if present
        content = content.replace("audit_enabled: false", "audit_enabled: true")
        project_file.write_text(content)

    # Execute a simple GET command
    res = run_pantheon(["get", "process", "create-ticket", "--actor", "ticket-handler"])
    assert res.returncode == 0

    # Find today's audit file
    audit_root = temp_project / "pantheon-artifacts" / "pantheon-audit"
    # The filename follows YYYY-MM-DD_cli.jsonl; glob for any .jsonl created today
    jsonl_files = list(audit_root.glob("*_cli.jsonl"))
    assert jsonl_files, (
        "No audit file found; expected one JSONL file in audit directory"
    )

    # Load and parse events
    lines = []
    for f in jsonl_files:
        lines.extend(f.read_text(encoding="utf-8").splitlines())

    assert any(lines), "Audit file contains no events"

    # Verify at least one event matches our command + actor and has required fields
    matched = False
    for line in lines:
        try:
            evt = json.loads(line)
        except Exception:
            continue
        if (
            evt.get("command") == "get process create-ticket"
            and evt.get("actor") == "ticket-handler"
            and evt.get("team") == "pantheon-e2e-test"
            and evt.get("result")
            in {"success", "bad_input", "permission_denied", "error"}
        ):
            matched = True
            # basic shape expectations
            assert isinstance(evt.get("timestamp"), str)
            break

    assert matched, (
        "Expected an audit event for 'get process create-ticket' by 'ticket-handler'"
    )
