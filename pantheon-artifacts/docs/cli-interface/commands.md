---
doc_id: cli-commands
title: CLI Commands Reference
description: Complete reference for all Pantheon CLI commands including initialization, information retrieval, process execution, and framework data management with detailed usage examples and parameter documentation
keywords: [cli, commands, pantheon init, pantheon get, pantheon execute, pantheon set, actor validation, framework flags, process execution, team management]
relevance: Essential reference for all CLI operations and command patterns used by agents and developers to interact with the Pantheon Framework
---

# CLI Commands Reference

The Pantheon CLI provides a stable, opinionated interface for agent orchestration through information retrieval and process execution. All commands enforce accountability through mandatory actor identification.

## Command Structure

All Pantheon commands follow a consistent pattern:
```bash
pantheon <command> <subcommand> [options] --actor <agent_name>
```

Every command **must** include the `--actor <name>` flag to identify which agent is performing the action. This enforces accountability and enables permission checking.

## Built-in Framework Flags

- **`--actor <agent_name>`**: **Required** - Identifies which agent is performing the action
- **`--id <artifact_id>`**: **Optional** - Specifies artifact ID for GET and UPDATE processes
- **`--sections <section1,section2,...>`**: **Optional** - Comma-separated list of sections to retrieve
- **`--insert-mode <append|prepend>`**: **Optional** - Non-destructive section updates for UPDATE processes
- **`--from-file <filepath>`**: **Optional** - Submit parameters via JSON file instead of command line

## Project Initialization

### `pantheon init`

Initializes a project to use Pantheon or switches the active team. Provides enhanced user experience with clear feedback and transparent operations.

**Usage:**
```bash
pantheon init
```

**Interactive Features:**

1. **Default Team Selection**: If a default team is configured in framework defaults, it appears as option 1 with a clear indicator "(default - press enter to select)". Simply pressing Enter selects the default team without needing to type a number.

2. **Detailed Directory Creation Feedback**: Shows actual directory paths created during initialization:
   ```
   Created directory: pantheon-artifacts/docs
   Created directory: pantheon-artifacts/tickets
   Created directory: pantheon-artifacts/diagrams
   ```

3. **Agent Installation Prompt**: Prompts to install team agents to `.claude/agents/`, defaulting to yes. Simply press Enter to accept:
   ```
   Install team agents to .claude/agents/? [Y/n]:
   ```
   Displays the list of installed agent files after confirmation:
   ```
   Installed agents to .claude/agents/pantheon-dev/:
   tech-lead.md, backend-engineer.md, frontend-engineer.md
   ```

4. **Content Preview and Integration Prompts**: Before appending content to CLAUDE.md or AGENTS.md, shows a preview and prompts for confirmation, both defaulting to yes:
   ```
   --- Preview of content to append ---
   [First 10 lines of content...]
   ... (45 more lines)
   --- End preview ---

   Append the above content to CLAUDE.md? [Y/n]:
   Append the above content to AGENTS.md? [Y/n]:
   ```

5. **Gitignore Management**: Prompts to add Pantheon-related files to `.gitignore`, defaulting to yes for typical git-based workflows:
   ```
   Add Pantheon files to .gitignore? [Y/n]:
   ```
   Adds `pantheon-artifacts/`, `.pantheon_project`, and `pantheon-teams/` entries with a marker comment for idempotent operations.

6. **Configuration File Locations**: After successful initialization, displays paths to key configuration files and the team README:
   ```
   Configuration files:
     - .pantheon_project: C:/project/.pantheon_project
     - team-data.yaml: C:/project/pantheon-teams/pantheon-dev/team-data.yaml
     - team-profile.yaml: C:/project/pantheon-teams/pantheon-dev/team-profile.yaml

   Get started with the team documentation at: C:/project/pantheon-teams/pantheon-dev/README.md
   ```

**Default Team Configuration:**

The framework ships with a default team configuration in `pantheon/_templates/pantheon-teams/defaults.yaml`:
```yaml
# Framework-level defaults for team initialization
default_team: pantheon-dev
```

This configuration can be modified to set a different default team for your organization's framework installation.

## Information Retrieval Commands

Pantheon provides five built-in information retrieval commands that allow agents to gather necessary information to execute processes.

### `pantheon get process <process-name>`

The core RAE (Retrieval-Augmented Execution) command. Retrieves the Markdown routine for a specific process.

**Usage:**
```bash
pantheon get process update-plan --actor backend-engineer
```

**Returns:** Step-by-step Markdown instructions for the agent to follow.

### `pantheon get schema <process-name>`

Retrieves the composed JSON Schema for a process, taking into account the active team profile.

**Usage:**
```bash
pantheon get schema create-ticket --actor tech-lead
```

**Returns:** JSON Schema defining the data contract for the process input.

### `pantheon get sections <process-name>`

Returns the list of sections that a process exposes, along with human-readable descriptions.

Supports both UPDATE processes and RETRIEVE/GET processes:
- **UPDATE processes**: Uses `artifact/target.jsonnet` to define section boundaries for targeted updates
- **RETRIEVE/GET processes**: Uses `artifact/sections.jsonnet` to define section markers for structured retrieval

The CLI delegates to the Process Handler, which evaluates the appropriate configuration file to extract section metadata. Both file types follow the same structure and should resolve to an object shaped like:

```json
{
  "sections": {
    "overview": {
      "start": "<!-- SECTION:START:OVERVIEW -->",
      "end": "<!-- SECTION:END:OVERVIEW -->",
      "description": "The team's mission, value proposition, and key capabilities."
    }
  }
}
```

**Usage:**
```bash
# Get sections from an UPDATE process
pantheon get sections update-team-readme --actor readme-writer

# Get sections from a RETRIEVE/GET process
pantheon get sections get-ticket --actor developer
```

**Returns:**
```json
[
  {
    "name": "overview",
    "description": "The team's mission, value proposition, and key capabilities."
  },
  {
    "name": "getting_started",
    "description": "Steps for a first-time user to begin working with the team."
  }
]
```

### `pantheon get tempfile --process <process-name>`

Provides a safe, temporary file path for an agent to write its JSON data. Files are created within the project's output directory sandbox.

**Usage:**
```bash
pantheon get tempfile --process update-plan --actor backend-engineer
```

**Returns:** Absolute path to a temporary file (e.g., `/project/pantheon-artifacts/tmp/update-plan_123.json`).

### `pantheon get team-data`

Retrieves runtime team data from `team-data.yaml`. This provides a generic key-value store for teams to track dynamic information like created agents, metrics, or configuration.

**Usage:**
```bash
# Get all team data
pantheon get team-data --actor pantheon

# Get specific key (supports dot notation for nested data)
pantheon get team-data --key agents.backend --actor pantheon
```

**Returns:** YAML-formatted data for complex objects, or direct values for scalars (strings, numbers, booleans).

## Process Execution

### `pantheon execute <process-name>`

The unified execution command runs any process, with behavior determined by the process's internal structure.

#### File-Based Input (Recommended)

For complex structured data, use temporary files:

```bash
pantheon execute create-ticket --actor tech-lead --from-file /tmp/ticket_data.json
```

**Important:** Built-in flags (`--actor`, `--id`, `--sections`) are always provided via CLI, even with `--from-file`:

```bash
pantheon execute get-ticket --actor backend-engineer --id T001 --sections context,plan --from-file /tmp/params.json
```

The JSON file contains only user business data - no framework variables:
```json
{
  "format": "detailed",
  "include_history": true
}
```

#### Built-in Flags (Simple Operations)

For common operations, use built-in flags directly:

```bash
# Get specific sections from a ticket
pantheon execute get-ticket --actor backend-engineer --id T001 --sections context,plan

# Get entire ticket
pantheon execute get-ticket --actor backend-engineer --id T001

# Non-destructive updates with insert modes
pantheon execute update-progress --actor developer --id T001 --insert-mode append --from-file progress.json
pantheon execute update-changelog --actor tech-lead --id T001 --insert-mode prepend --from-file update.json
```

#### Direct Arguments (Custom Data)

For additional custom parameters, use the `--param` format:

```bash
pantheon execute some-process --actor engineer --param priority=high --param category=bug
```

#### BUILD Process Execution

`build-*` processes scaffold complete process families from a JSON specification. Regardless of build mode, Pantheon now emits the full trio of `create-`, `get-`, and a consolidated `update-<artifact>` process.

```bash
# Scaffold a process family from build-spec.json
pantheon execute build-team-process \
  --actor pantheon \
  --from-file artifacts/build-spec.json
```

**Build Output Highlights:**
- **Complete mode** renders every section with real content in both `create-` and `update-` processes; section schema fragments are compiled without `$schema` and imported into the consolidated update schema.
- **Modular mode** renders the initial (and optional context) section, leaves placeholders elsewhere, and relies on the shared `update-` process (with `--sections`) for incremental collaboration.
- Generated processes are staged under `pantheon-artifacts/pantheon-team-builds/<team>/processes/` for review before promotion.

## Framework Data Management

### `pantheon set team-data`

Updates runtime team data in `team-data.yaml`. Supports setting multiple key-value pairs and deleting keys in a single atomic operation.

**Usage:**
```bash
# Set values (supports dot notation for nested keys)
pantheon set team-data --actor pantheon \
  --set agents.backend="Backend specialist" \
  --set metrics.count=15 \
  --set config.debug=true

# Delete keys
pantheon set team-data --actor pantheon \
  --del old_key \
  --del metrics.outdated_metric

# Combine operations
pantheon set team-data --actor pantheon \
  --set agents.frontend="Frontend engineer" \
  --del temporary_data
```

**Smart Type Coercion:**
- Unquoted values are automatically converted to appropriate types:
  - `--set count=15` → `count: 15` (integer)
  - `--set rate=87.5` → `rate: 87.5` (float)
  - `--set debug=true` → `debug: true` (boolean)
- Quoted values are preserved as strings:
  - `--set name="backend engineer"` → `name: backend engineer` (string with spaces)

**Key Features:**
- **Dot notation**: Set nested values like `agents.backend`
- **Deep merge**: Preserves existing data while adding/updating new values
- **Atomic operations**: All changes applied together or none at all
- **Type preservation**: YAML output maintains proper data types

## Framework Parameter Handling

The Pantheon framework provides consistent handling for framework variables through dedicated CLI flags.

### Template Variables

All processes have access to these built-in template variables:

- `{{ pantheon_actor }}` - The authenticated actor name
- `{{ pantheon_timestamp }}` - Current timestamp
- `{{ pantheon_datestamp }}` - Current date
- `{{ pantheon_artifact_id }}` - Unique artifact ID
- `{{ pantheon_profile }}` - Active team profile object

**Schema Independence:** User schemas define business data without reserving framework variable names.

### JSON File Contents

JSON files contain **only user business data** - never framework variables:

```json
{
  "ticket": "T001",
  "priority": "high",
  "description": "Fix authentication bug"
}
```

**Key Rule:**
- **CLI flags** handle framework operations (`--actor`, `--id`, `--sections`)
- **JSON files** contain your business data only

**Important:** Framework flags must be provided via CLI, not in JSON files. If you include `pantheon_actor`, `pantheon_artifact_id`, or `pantheon_sections` in your JSON file, you'll get an error message asking you to use the proper CLI flags instead.

## Error Handling and Exit Codes

The CLI uses standardized exit codes for programmatic handling:

- **0**: Success - Command completed successfully
- **1**: Bad Input / Invalid Actor - Invalid arguments or unknown agent
- **13**: Permission Denied - Agent lacks permission to execute process

Error messages are written to `stderr`, while successful output goes to `stdout`.

## Permission Model

The Pantheon Framework implements a comprehensive actor-based permission system with both process-level and section-level access control.

### Actor Validation

Every command validates that the specified `--actor` corresponds to a known agent in the active team. Agent names are derived from filenames in the `agents/` directory.

### Access Control

The CLI enforces permissions through `permissions.jsonnet` files in each process. The system supports:
- **Process-level permissions**: Control access to entire processes
- **Section-level permissions**: Fine-grained control over UPDATE operations
- **Wildcard permissions**: Universal access using `"*"`
- **Explicit deny precedence**: Deny always overrides allow

## Example Command Sequences

### Agent Planning Workflow

```bash
# 1. Get instructions
pantheon get process update-plan --actor backend-engineer

# 2. Get schema for data validation
pantheon get schema update-plan --actor backend-engineer

# 3. Get context from existing ticket
pantheon execute get-ticket --actor backend-engineer --id T004 --sections context

# 4. Get temp file for atomic operations
pantheon get tempfile --process update-plan --actor backend-engineer

# 5. Execute the planning process
pantheon execute update-plan --from-file /tmp/plan_456.json --actor backend-engineer
```

### Code Review Workflow

```bash
# 1. Get review instructions
pantheon get process update-code-review --actor code-reviewer

# 2. Get current ticket state
pantheon execute get-ticket --actor code-reviewer --id T004 --sections plan,context

# 3. Prepare review data
pantheon get tempfile --process update-code-review --actor code-reviewer

# 4. Submit code review
pantheon execute update-code-review --from-file /tmp/review_789.json --actor code-reviewer
```

### Team Management Workflow

```bash
# 1. Get team information
pantheon execute get-team-info --actor pantheon

# 2. Get current agent definitions
pantheon execute get-agent-prompt --actor pantheon

# 3. Update agent capabilities
pantheon get tempfile --process update-agent-prompt --actor pantheon
pantheon execute update-agent-prompt --from-file /tmp/agent_123.json --actor pantheon
```

### Team Data Management Workflow

```bash
# 1. Check existing team data
pantheon get team-data --actor pantheon

# 2. Record new specialist agents after creation
pantheon set team-data --actor pantheon \
  --set agents.backend="Backend development specialist" \
  --set agents.frontend="Frontend UI/UX specialist"

# 3. Track team metrics
pantheon set team-data --actor pantheon \
  --set metrics.agents_created=2 \
  --set metrics.last_update="2025-09-26"

# 4. Query specific information
pantheon get team-data --key agents --actor pantheon
pantheon get team-data --key agents.backend --actor pantheon

# 5. Update configuration and clean up old data
pantheon set team-data --actor pantheon \
  --set config.auto_create_agents=true \
  --del temporary_flags
```

### Non-Destructive Update Workflow

```bash
# 1. Get available sections for an update process
pantheon get sections update-progress --actor developer

# 2. Append new progress entries without losing existing data
pantheon execute update-progress --actor developer --id T001 \
  --insert-mode append --from-file new-progress.json

# 3. Prepend latest changelog entries for immediate visibility
pantheon execute update-changelog --actor tech-lead --id T001 \
  --insert-mode prepend --from-file release-notes.json

# 4. Traditional replacement for complete section updates
pantheon execute update-status --actor tech-lead --id T001 \
  --from-file status-update.json
```

## Command Design Philosophy

### Simplicity
- Minimal command surface area reduces learning curve
- Consistent patterns across all operations
- Clear separation between information and action

### Reliability
- All file operations use atomic temporary files
- Permission checking prevents unauthorized access
- Error handling provides clear feedback

### Auditability
- Actor identification enables full accountability
- All operations are logged and traceable
- Process execution follows documented routines

### Extensibility
- New processes automatically work with existing commands
- Team packages can add processes without CLI changes
- Convention-based discovery eliminates configuration

This command design ensures that the CLI remains a stable, reliable interface while supporting the dynamic, extensible nature of Team Packages and their processes.
