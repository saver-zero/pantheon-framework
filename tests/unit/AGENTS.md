# Repository Guidelines

## Scope & Goals
- Validate single components in isolation with mocks and dependency injection.
- Keep tests fast (<10ms) and focused on a component’s responsibility.

## Patterns
- Arrange-Act-Assert. Verify outcomes and mock interactions.
- Mock `FileSystem`; avoid real I/O. Prefer `Mock(spec=...)` for interface safety.
- Do not instantiate dependencies in tests—inject them.

## Targets
- CLI: argument parsing, `--actor` enforcement, exit codes; mock `ProcessHandler`.
- ProcessHandler: Unified Execute Model detection, redirects, reserved `sections` handling; mock `Workspace`.
- Artifact Engine: schema composition, validation, template rendering (pure computation); no I/O.
- Workspace: use mocks for read methods when unit-testing its coordination logic.

## Commands
- Run: `pytest tests/unit -v`
- Lint/format: `ruff check . && ruff format .`
- Types: `mypy pantheon`

## Naming
- Files `test_*.py`, classes `Test*`, functions `test_*` per `pytest.ini`.

## Tips
- Assert no unexpected calls: `mock.assert_not_called()` / call counts.
- Keep fixtures minimal; reuse shared ones from `tests/conftest.py`.
- Avoid redundant cases—optimize for meaningful coverage.

### Cross‑platform path handling (Windows vs POSIX)
- Prefer deriving expected Paths from the system under test rather than hardcoding absolute strings.
  - Example: `expected_root = workspace._artifacts_root / DEFAULT_AUDIT_DIRECTORY`
  - This avoids mismatches like `C:/project/...` (Windows) vs `/project/...` (POSIX).
- When you must compare strings, normalize via `Path(...).as_posix()` or compare suffixes with `.endswith(...)`.
- If a test requires an absolute path sample, branch by platform:
  - `absolute = "C:\\temp" if os.name == "nt" else "/tmp"`
- Avoid asserting drive letters or root prefixes directly; assert relative relationships instead (e.g., `path.parent == base / "subdir"`).
