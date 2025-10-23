# Repository Guidelines

## Template Structure
- `pantheon-teams/pantheon-skeleton/`: Reference team with all operation types.
- Agents: `agents/<agent>.md` define personas and responsibilities.
- Processes: `<verb-noun>/` with `routine.md`, `schema.jsonnet` (optional), `permissions.jsonnet`.
- Artifact templates (per operation):
  - CREATE: `artifact/{content.md,naming.jinja,placement.jinja}`
  - RETRIEVE: `artifact/{locator.jsonnet,parser.jsonnet,sections.jsonnet}`
  - UPDATE: `artifact/{patch.md,target.jsonnet}` + RETRIEVE files

## Conventions
- Process dirs: `<verb-noun>` (e.g., `create-ticket`, `get-ticket`).
- Built-ins in templates: `pantheon_actor`, `pantheon_timestamp`, `pantheon_datestamp`, `pantheon_artifact_id`, `pantheon_profile`.
- Permissions: allow/deny lists in `permissions.jsonnet` (secure by default).

## Usage Examples
- Initialize from skeleton: `pantheon init --team-template pantheon-skeleton`
- Execute create: `pantheon execute create-ticket --actor ticket-handler --title "Hello"`
- Retrieve: `pantheon execute get-ticket --actor ticket-handler --id T123`

## Authoring Tips
- Routine: clear, stepwise instructions; include redirects via `redirect.md` if needed.
- Schema (Jsonnet): inject profile via `std.extVar('profile')`; validate inputs.
- Templates: avoid non-deterministic output; keep section markers stable for updates.
- Naming/placement Jinja: deterministic paths; prefer kebab-case filenames.

## Testing
- Unit: render content with sample data; validate schema composition.
- Integration: use real fixture teams under `tests/fixtures/`.
- E2E: run CLI to ensure bundled templates work end-to-end.

## PR Checklist
- New process follows structure above; permissions defined; routines documented.
- Profile-aware schemas where appropriate; examples updated.

