# Repository Guidelines

## Scope & Goals
- Validate complete user workflows via CLI subprocess calls.
- Use isolated temporary projects; verify outputs in `pantheon-artifacts/`.

## Infrastructure
- Fixtures: `temp_project`, `run_pantheon`, `pantheon_cli` (see `tests/conftest.py`).
- Project setup: create `.pantheon_project`, copy fixture team under `pantheon-teams/`.

## Patterns
- Golden-path scenarios first; then error cases (permission denied → exit 13, invalid input → exit 1).
- Multi-command flows: init → execute CREATE → retrieve/update.
- Assert returncode, stdout/stderr, and filesystem state.

## Commands
- Run E2E only: `pytest -m e2e -v`
- Example: initialize and run
  - `pantheon init --team-template pantheon-skeleton`
  - `pantheon execute create-ticket --actor ticket-handler --title "Hello"`

## Tips
- Keep runs deterministic; avoid time/date assertions beyond presence.
- Prefer stable text anchors and section markers in artifact assertions.

