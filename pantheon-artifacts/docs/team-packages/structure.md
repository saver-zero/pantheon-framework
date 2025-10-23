---
doc_id: team-package-structure
title: "Team Package Structure"
description: "Complete directory structure and organization of Pantheon team packages with bundled templates and installed teams."
keywords: [team-package, structure, directory, agents, processes, artifacts, conventions]
relevance: "Use this document to understand team package organization, file naming conventions, and the relationship between bundled templates and installed teams."
---

# Team Package Structure

A **Team Package** is the user-defined, version-controlled, and portable definition of an AI team. Team packages exist in two locations:

1. **Bundled Teams** (`pantheon/_templates/pantheon-teams/`): Default teams shipped with the framework package, serving as templates for user projects.
2. **Installed Teams** (`my-project/pantheon-teams/`): Team packages installed and customized within user projects.

Both follow the same standardized structure that enables the framework's convention-based discovery system.

## Full Directory Structure

```
# For installed teams in user projects:
/pantheon-teams/
└── /<team_name>/

# For bundled teams in framework (source templates):
/pantheon/_templates/pantheon-teams/
└── /<team_name>/               # Contains template files to copy
    ├── team-profile.yaml        # Template configuration copied during init
    ├── /agents/
    │   ├── <agent_name>.md
    │   └── ...
    └── /processes/
        └── /<verb-noun>/
            ├── routine.md
            ├── permissions.jsonnet
            ├── schema.jsonnet
            ├── build-schema.jsonnet    # BUILD: Process family specification schema
            └── /artifact/              # Process-specific files determine process behavior
                ├── content.md          # CREATE: Artifact content template
                ├── placement.jinja     # CREATE: Directory placement template
                ├── naming.jinja        # CREATE: Filename generation template
                ├── patch.md            # UPDATE: Section replacement template
                ├── target.jsonnet      # UPDATE: Target section definition
                ├── locator.jsonnet     # UPDATE/GET: Artifact finding pattern
                ├── parser.jsonnet      # UPDATE/GET: ID normalization rules
                ├── sections.jsonnet    # UPDATE/GET: Section marker definitions
                └── /sections/          # BUILD: Section snippets + schema fragments (no $schema header)
```

## Directory Breakdown

### Root Level
- **`pantheon-teams/`**: The root directory for all Team Packages in the repository.
- **`<team_name>/`**: A directory representing a single, self-contained Team Package.

### Team Configuration
- **`team-profile.yaml`**: The central control panel for the team. When a team is first initialized, this file is **copied** from the bundled template during the `pantheon init` command.
- **`team-data.yaml`** (optional): Additional team-specific data including path configurations for automatic directory creation.

### Path-Based Directory Creation

Team packages can include a `team-data.yaml` file that defines directory paths to be created automatically during `pantheon init`. This follows the **convention over configuration** philosophy by establishing standard directory structures without manual setup.

**Features:**
- **Automatic Creation**: All paths defined in the `path` section are created during project initialization
- **Jinja2 Templates**: Paths can use `{{ pantheon_artifacts_root }}` and `{{ pantheon_project_root }}` variables
- **Nested Paths**: Supports nested dictionary structures for organized path definitions
- **Security Validation**: Paths are validated to stay within project boundaries
- **Idempotent Behavior**: Re-running init safely handles existing directories

**Example `team-data.yaml`:**
```yaml
path:
  docs: '{{ pantheon_artifacts_root }}/docs/'
  diagrams: '{{ pantheon_artifacts_root }}/docs/diagrams/'
  tickets:
    backlog: '{{ pantheon_artifacts_root }}/tickets/0_backlog/'
    todo: '{{ pantheon_artifacts_root }}/tickets/1_todo/'
    done: '{{ pantheon_artifacts_root }}/tickets/2_done/'

agents:
  tech-lead: "Technical leadership agent..."
  routine-designer: "Routine design specialist..."
```

**Path Validation:**
- Paths resolving outside the project root are rejected with warnings
- Path traversal attempts (e.g., `../../etc/passwd`) are blocked
- Invalid paths don't fail init - they're logged and skipped
- Successfully created directories are reported in init success message

**Template Variables:**
- `{{ pantheon_artifacts_root }}`: Resolves to the artifacts directory (default: `pantheon-artifacts`)
- `{{ pantheon_project_root }}`: Resolves to the project root directory

This enables teams to define their standard directory structure once in team-data.yaml, and have it automatically created for all users who initialize with that team.

### Team Components
- **`agents/`**: Contains the persona definitions for all agents in the team.
- **`processes/`**: Contains a subdirectory for each process the team can execute.

### Process Structure
- **`processes/<verb-noun>/`**: A directory for a single process (e.g., `create-plan`).
- **`routine.md`**: The core instruction set for the process.
- **`permissions.jsonnet`**: Actor-based access control with process and section-level permissions.
- **`schema.jsonnet`**: The composable Jsonnet file that defines the data contract for the process.

### Artifact Definition (Process-Specific)
- **`artifact/`**: Contains process-specific files that determine process behavior through the **Unified Execute Model**.
- **`build-schema.jsonnet`**: BUILD-specific schema at process root (not in artifact/ subdirectory).

**BUILD Process Files** (at process root level):
- **`build-schema.jsonnet`**: Complete schema for build specification input defining process family structure.
- **`routine.md`**: Instructions for agents on how to create build specifications.
- **`permissions.jsonnet`**: Access control for BUILD operations.
- **`directory.jinja`** (optional): Template for bundle output location.
- **Outputs**: Every build scaffolds `create-`, `get-`, and a consolidated `update-<artifact>` process (even in `complete` mode).

**CREATE Process Files**:
- **`content.md`**: Jinja2 template for rendering new artifact content.
- **`placement.jinja`**: Template defining where new artifacts are saved.
- **`naming.jinja`**: Template for generating artifact filenames.

**UPDATE Process Files**:
- **`patch.md`**: Jinja2 template for section replacement content.
- **`target.jsonnet`**: Defines which section to modify in existing artifacts.
- **`locator.jsonnet`**: Pattern for locating existing artifacts.
- **`parser.jsonnet`**: Rules for normalizing fuzzy inputs to canonical IDs.
- **`sections.jsonnet`**: Section markers for structured document parsing.
- **`sections/<name>.schema.jsonnet`**: Section-level schema fragment compiled without `$schema`, imported by the consolidated update schema.

**GET Process Files**:
- **`locator.jsonnet`**: Pattern for locating existing artifacts (shared with UPDATE).
- **`parser.jsonnet`**: Rules for normalizing fuzzy inputs (shared with UPDATE).
- **`sections.jsonnet`**: Section markers for parsing (shared with UPDATE).

## Convention-Based Discovery

The framework's "convention over configuration" philosophy relies on this standardized structure. The Pantheon Workspace encapsulates all knowledge of these conventions and provides high-level content-retrieval methods to other components, eliminating the need for them to understand the directory structure:

### Process Discovery Through Workspace
- Process directories use `<verb-noun>` naming (e.g., `create-ticket`, `update-plan`)
- Workspace provides methods like `get_process_schema(process_name)` and `get_process_routine(process_name)`
- Other components only need to know process names, not file locations
- Optional artifacts are accessed via `get_artifact_normalizer()`, `get_artifact_finder()`, etc.

### Agent Discovery Through Workspace
- Agent files follow `<agent_name>.md` pattern in the `agents/` directory
- Workspace handles agent validation without exposing file paths
- Agent names become valid `--actor` values for CLI commands
- No registration required - Workspace discovers files at runtime

### Team Discovery and Active Team Resolution
- Team packages are any directory under `pantheon-teams/`
- Workspace automatically resolves the active team from `.pantheon_project`
- Other components receive content without knowing which team it came from
- Workspace handles all team-specific path construction

## File Naming Conventions

### Processes: Verb-Noun Pattern
- `build-team-process` - Scaffolds complete process families
- `create-ticket` - Creates a new ticket
- `update-plan` - Updates an implementation plan
- `get-team-info` - Retrieves team information
- `submit-feedback` - Submits user feedback

### Agents: Descriptive Names
- `tech-lead.md` - Technical leadership agent
- `backend-engineer.md` - Backend development specialist
- `code-reviewer.md` - Code review specialist
- `scribe.md` - Feedback logging agent

### Artifacts: Process-Driven
- **BUILD**: Process family bundles staged in `pantheon-artifacts/` using `directory.jinja` template
- **CREATE**: File locations determined by `placement.jinja`, filenames by `naming.jinja`, content by `content.md`
- **UPDATE**: Section targeting by `target.jsonnet`, replacement content by `patch.md`
- **GET**: Artifact location by `locator.jsonnet`, ID parsing by `parser.jsonnet`, section extraction by `sections.jsonnet`

## Component Relationships

### Team → Processes → Artifacts
- A Team Package contains multiple processes
- Each process may produce zero or one artifact type
- Artifacts are versioned and stored in the configured output directory

### Agents → Processes → Permissions
- Agents are defined at the team level
- Each process defines which agents can execute it via `permissions.jsonnet` (supports both process and section-level access control)
- Permissions are checked at runtime by the CLI

### Profiles → Schema → Templates
- Team profiles provide configuration context
- Process schemas adapt based on active profile
- Templates render differently based on profile settings

## Self-Contained Design

Each Team Package is completely self-contained and accessed through the Workspace's content-retrieval architecture:

- **All Dependencies Included**: Schema definitions, templates, and validation rules accessed via Workspace methods
- **Portable**: Can be copied between projects or shared between teams with Workspace automatically handling discovery
- **Version-Controlled**: All components tracked together as a unit, with Workspace providing consistent access
- **Extensible**: New processes and agents can be added without framework changes - Workspace discovers them automatically
- **Abstracted Access**: Other components interact with team packages through Workspace methods, never directly with file paths

This design ensures that Team Packages are true "applications" that run on the Pantheon Framework "operating system". The Workspace serves as the interface layer that allows these applications to focus on their business logic while the framework handles all filesystem complexity.

---

**See Also:**
- **Team Profiles**: Understand how profiles control team behavior
- **Agents and Processes**: Learn about agent definitions and process workflows
- **Process Development**: Master creating and customizing processes
