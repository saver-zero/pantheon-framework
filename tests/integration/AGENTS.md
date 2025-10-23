# Repository Guidelines

## Scope & Goals
- Validate component interactions with real objects at moderate speed.
- Exercise `Workspace` + `ArtifactEngine` + `FileSystem` together using temporary directories.

## Patterns
- Use `tmp_path` to build realistic team/package structures.
- Inject real `FileSystem` into `Workspace`; avoid mocks unless isolating external systems.
- Verify end-to-end behavior of service/application boundaries (not CLI subprocess).

## Targets
- FileSystem integration: real reads/writes and error handling.
- Workspace: active team resolution via `.pantheon_project`, path conventions, permissions.
- ProcessHandler: orchestrating service components using real Workspace.

## Commands
- Run: `pytest tests/integration -v`
- Coverage: `pytest tests/integration --cov=pantheon`

## Naming & Structure
- Keep tests self-contained; create minimal realistic project trees.
- Place reusable builders under `tests/fixtures/` when helpful.

## Tips
- Prefer clear, high-signal scenarios over broad permutations.
- Assert both returned data and side effects (created files, content).

