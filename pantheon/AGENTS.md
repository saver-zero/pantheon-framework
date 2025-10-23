# Repository Guidelines

## Project Structure & Roles
- `cli.py`: Presentation layer. Parses args, validates `--actor`, returns exit codes (0/1/13). No business logic.
- `process_handler.py`: Application layer. Orchestrates Unified Execute Model (CREATE/UPDATE/RETRIEVE), redirects, reserved params.
- `workspace.py`: Service facade. Only place that unwraps `PantheonPath`; provides high-level getters.
- `artifact_engine.py`: Pure computation (render/validate/locate). No direct I/O.
- `filesystem.py`: I/O adapter used by `Workspace`.
- `rae_engine.py`, `path.py`, `logger.py`: Routine retrieval, path proxy, logging.

## Development Commands
- Lint/Format: `ruff check .` • `ruff format .`
- Types: `mypy pantheon`
- Tests (core focus): `pytest tests/unit -k pantheon` then broader suites.

## Coding Style & Conventions
- Never use `print()`. Import `Log` from `pantheon.logger`.
- Inject dependencies; do not instantiate `FileSystem` inside business logic.
- Only `Workspace` performs real I/O and unwraps `PantheonPath`.
- Keep CLI thin; move logic to `ProcessHandler`.
- Filenames and APIs are explicit and verb-noun oriented.

## Testing Guidelines
- Unit: Mock `FileSystem`; validate orchestration and operation detection.
- Integration: Real `FileSystem` with `tmp_path`; verify `Workspace` paths and permissions.
- E2E: CLI subprocess covering exit codes, actor validation, artifacts created.

## Error Handling & Security
- Exit codes: 0 success, 1 invalid input, 13 permission denied.
- Validate actor against permissions before processing.
- Keep computation vs I/O separation strict to maintain testability and safety.

## PR Checklist
- Prove separation of concerns (CLI thinness, DI, no direct I/O).
- Include unit tests for new branches, and update docs if user-facing behavior changes.
- Run `ruff`, `mypy`, and `pytest` locally before submitting.

