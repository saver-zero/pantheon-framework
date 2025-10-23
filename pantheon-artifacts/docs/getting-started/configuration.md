---
doc_id: getting-started-configuration
title: Configuration Files and Settings
description: Complete reference for Pantheon configuration including .pantheon_project structure, artifacts_root sandbox, audit logging, temp file cleanup, team-profile.yaml, team-data.yaml, and framework-level defaults
keywords: [configuration, .pantheon_project, artifacts_root, audit logging, temp file cleanup, team profile, team data, framework defaults, project settings, end-user]
relevance: Essential reference for all project and team configuration options controlling framework behavior and artifact management
---

# Configuration Files and Settings

Pantheon uses multiple configuration files at different levels to control framework behavior, project settings, and team customization. This document provides a complete reference for all configuration options.

## Project-Level Configuration

### The `.pantheon_project` File

Located at the project root, this file is the single source of truth for the framework's project-specific configuration.

**Location:** `<project-root>/.pantheon_project`

**Format:** YAML

**Complete Example:**

```yaml
# The active team to use for this project
active_team: pantheon-dev

# The directory where all Pantheon-generated files will be stored
artifacts_root: pantheon-artifacts

# Optional: Audit logging configuration (disabled by default)
audit_enabled: false
# Directory is always resolved under artifacts_root
audit_directory: pantheon-audit

# Optional: Control when temporary files are cleaned up (default: always)
# Values: "always", "on_failure", "never"
temp_file_cleanup: always
```

### Configuration Fields

**Note:** `.pantheon_project` contains only project-level settings (`active_team` and `artifacts_root`). Team behavioral settings, including profile configuration, are stored in `team-profile.yaml` within each team's directory. The `.pantheon_project` file does NOT contain an `active_profile` field.

#### `active_team` (Required)

**Type:** String

**Description:** Specifies which team package to use for this project. All process executions and agent operations use this team's definitions.

**Example:**
```yaml
active_team: pantheon-dev
```

**Behavior:**
- Must correspond to a directory in `pantheon-teams/<team-name>/`
- Changed via `pantheon init` to switch teams
- Validated on every command execution

#### `artifacts_root` (Required)

**Type:** String

**Description:** Defines the directory where all Pantheon-generated files are stored. This creates a sandboxed output area separate from source code.

**Default:** `pantheon-artifacts`

**Example:**
```yaml
artifacts_root: pantheon-artifacts
```

**Behavior:**
- All CREATE process outputs are resolved relative to this directory
- Temporary files stored in `<artifacts_root>/tmp/`
- Audit logs stored in `<artifacts_root>/<audit_directory>/`
- Final artifact path: `<project-root>/<artifacts_root>/<process-directory>/<filename>`

**Example Artifact Paths:**
```
/project/pantheon-artifacts/tickets/T012_refactor-init.md
/project/pantheon-artifacts/docs/architecture-guide.md
/project/pantheon-artifacts/tmp/create-ticket_789.json
```

#### `audit_enabled` (Optional)

**Type:** Boolean

**Default:** `false`

**Description:** Enables append-only audit trail of CLI commands to JSON Lines files.

**Example:**
```yaml
audit_enabled: true
```

**Behavior:**
- When enabled, records all CLI commands to daily log files
- Logs stored in `<artifacts_root>/<audit_directory>/<YYYY-MM-DD>_cli.jsonl`
- One JSON object per line containing timestamp, team, command, actor, result
- Scope: `get process`, `get schema`, `get tempfile`, `execute`
- Excluded: `init` command
- Guardrails: Process artifacts cannot read/write inside audit directory

**Log Entry Format:**
```json
{
  "timestamp": "2025-01-15T14:23:45.123456",
  "team": "pantheon-dev",
  "command": "execute",
  "process": "create-ticket",
  "actor": "tech-lead",
  "id": "T042",
  "sections": null,
  "result": "success"
}
```

#### `audit_directory` (Optional)

**Type:** String

**Default:** `pantheon-audit`

**Description:** Subdirectory under `artifacts_root` where audit logs are stored.

**Example:**
```yaml
audit_directory: pantheon-audit
```

**Behavior:**
- Always resolved relative to `artifacts_root`
- Final path: `<artifacts_root>/<audit_directory>/`
- Only used when `audit_enabled: true`

#### `temp_file_cleanup` (Optional)

**Type:** String

**Default:** `always`

**Valid Values:** `always`, `on_failure`, `never`

**Description:** Controls when temporary files are automatically cleaned up after process execution.

**Examples:**

```yaml
# Keep temp directory clean (recommended for production)
temp_file_cleanup: always

# Preserve successful executions for debugging
temp_file_cleanup: on_failure

# Manual temp file management
temp_file_cleanup: never
```

**Behavior:**

- **`always`**: Clean up temporary files after every execution regardless of outcome. Keeps the temp directory clean and prevents accumulation of old files.
- **`on_failure`**: Only clean up temporary files if process execution fails. Preserves successful execution files for inspection and debugging.
- **`never`**: Never clean up temporary files. Useful for debugging, audit trails, or when you want to manually manage temp files.

**Scope:**
- Only files within `<artifacts_root>/temp/` directory are subject to cleanup
- User-provided files outside the temp directory are never touched
- Cleanup occurs after process execution completes (success or failure)

## Team-Level Configuration

### The `team-profile.yaml` File

Located in each team's directory, this file defines team-specific behavior and customization.

**Location:** `pantheon-teams/<team-name>/team-profile.yaml`

**Format:** YAML

**Example for pantheon-dev:**

```yaml
team_name: Pantheon Development Team
team_description: "The default, general-purpose team designed for day-to-day software development tasks operating under the Glass Box philosophy."

# The currently active profile for this team (set during 'pantheon init')
active_profile: standard

# Available profile definitions
profiles:
  prototype:
    enforce_tdd: false
    enable_progress_log: false

  standard:
    enforce_tdd: false
    enable_progress_log: true

  production:
    enforce_tdd: true
    enable_progress_log: true
```

### Profile System

**Purpose:** Adapts team behavior for different development contexts without modifying process definitions.

**Profile Selection:** The `active_profile` field is set during `pantheon init` when you select a profile for teams that support profiles. This value is persisted to `team-profile.yaml` in the project's team directory, establishing team-profile.yaml as the single source of truth for profile configuration. You can change the active profile at any time by manually editing this field in team-profile.yaml - changes take effect immediately without requiring project reinitialization.

**Mechanism:** Profile data is injected into schema and template rendering via `std.extVar('profile')` in Jsonnet and `{{ pantheon_profile }}` in Jinja2. The runtime system reads the `active_profile` value from team-profile.yaml and injects the corresponding profile settings during process execution.

**Common Profile Fields:**
- `enforce_tdd`: Whether processes require test specifications
- `enable_progress_log`: Whether to log agent progress automatically

**Impact:**
- Process schemas adapt required fields based on profile
- Templates render different content based on profile settings
- Agent behavior adjusts to profile configuration

### The `team-data.yaml` File

Located in each team's directory, this file provides a generic key-value store for runtime team data.

**Location:** `pantheon-teams/<team-name>/team-data.yaml`

**Format:** YAML

**Purpose:** Store dynamic information like created agents, metrics, or runtime configuration that doesn't fit in the static profile.

**Example:**

```yaml
agents:
  backend: "Backend development specialist"
  frontend: "Frontend UI/UX specialist"

metrics:
  agents_created: 2
  last_update: "2025-09-26"
  tickets_processed: 47

config:
  auto_create_agents: true
  default_verbosity: standard
```

### Team Data Operations

**Reading:**
```bash
# Get all team data
pantheon get team-data --actor pantheon

# Get specific key (supports dot notation)
pantheon get team-data --key agents.backend --actor pantheon
```

**Writing:**
```bash
# Set values (supports dot notation for nested keys)
pantheon set team-data --actor pantheon \
  --set agents.backend="Backend specialist" \
  --set metrics.count=15

# Delete keys
pantheon set team-data --actor pantheon \
  --del old_key

# Combine operations
pantheon set team-data --actor pantheon \
  --set agents.frontend="Frontend engineer" \
  --del temporary_data
```

**Type Coercion:**
- Unquoted values: `--set count=15` → `count: 15` (integer)
- Quoted values: `--set name="engineer"` → `name: engineer` (string)
- Booleans: `--set debug=true` → `debug: true` (boolean)
- Floats: `--set rate=87.5` → `rate: 87.5` (float)

## Framework-Level Configuration

### Framework Defaults

**Location:** `pantheon/_templates/pantheon-teams/defaults.yaml` (within framework installation)

**Format:** YAML

**Purpose:** Provides framework-wide defaults that apply to all projects using this framework installation.

**Example:**

```yaml
# Framework-level defaults for team initialization
default_team: pantheon-dev
```

### Supported Settings

#### `default_team`

**Type:** String

**Default:** `pantheon-dev`

**Description:** Sets the default team for the `pantheon init` command. When configured, the default team appears as option 1 during team selection with "(default - press enter to select)" indicator.

**Valid Values:** Any team name available in bundled templates (`pantheon/_templates/pantheon-teams/`)

**Behavior:**
- Affects team selection menu during `pantheon init`
- Simply pressing Enter selects the default team
- Can be overridden by explicit selection
- Does not affect projects already initialized

### Modifying Framework Defaults

**For Framework Maintainers:**

1. Locate framework installation: `pip show pantheon-framework`
2. Edit `pantheon/_templates/pantheon-teams/defaults.yaml`
3. Set `default_team` to preferred team name
4. Change applies to all new `pantheon init` commands across all projects

**For Development Builds:**

1. Modify `pantheon/_templates/pantheon-teams/defaults.yaml` in source repository
2. Changes become part of framework installation when package is built

## Configuration Hierarchy

Configuration values are resolved in the following order (later values override earlier ones):

1. **Framework Defaults**: Built-in framework configuration
2. **Project Configuration**: `.pantheon_project` in project root
3. **Team Profile**: `team-profile.yaml` in active team directory
4. **Team Data**: `team-data.yaml` for runtime values
5. **Command-Line Flags**: CLI parameters override all configuration

## Version Control Recommendations

### Commit to Version Control

- `.pantheon_project` - Project configuration (track team selection)
- `pantheon-teams/` - All team package files (agents, processes, profiles)
- Generated artifacts - Team outputs for review and history

### Exclude from Version Control

- `pantheon-artifacts/tmp/` - Temporary files (auto-ignored via `.gitignore`)
- `pantheon-artifacts/pantheon-audit/` - Audit logs (optional exclusion)

### Gitignore Template

During `pantheon init`, the following entries are offered to `.gitignore`:

```gitignore
# Pantheon Framework
pantheon-artifacts/tmp/
# Optional: Exclude all artifacts (uncomment if desired)
# pantheon-artifacts/
# Optional: Exclude project config (uncomment if desired)
# .pantheon_project
# Optional: Exclude team packages (uncomment if desired)
# pantheon-teams/
```

## Configuration Validation

### Validate Project Configuration

```bash
# Check .pantheon_project exists and is valid YAML
cat .pantheon_project

# Verify active team exists
ls pantheon-teams/$(grep active_team .pantheon_project | cut -d: -f2 | tr -d ' ')
```

### Validate Team Configuration

```bash
# Check team profile exists
cat pantheon-teams/pantheon-dev/team-profile.yaml

# Verify active profile is defined
grep -A 10 "active_profile:" pantheon-teams/pantheon-dev/team-profile.yaml
```

### Test Configuration

```bash
# Test basic command to verify configuration
pantheon get team-data --actor pantheon

# Check artifacts directory exists
ls pantheon-artifacts/
```

## Common Configuration Issues

### Invalid YAML Syntax

**Problem:** `Error parsing .pantheon_project: invalid YAML`

**Solution:**
- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('.pantheon_project'))"`
- Check for tabs (use spaces only)
- Verify proper indentation

### Missing Required Fields

**Problem:** `Missing required field: active_team`

**Solution:**
- Ensure `.pantheon_project` contains all required fields
- Regenerate with `pantheon init`

### Invalid Team Reference

**Problem:** `Team 'xyz' not found in pantheon-teams/`

**Solution:**
- Verify team directory exists: `ls pantheon-teams/`
- Run `pantheon init` to scaffold team
- Fix typo in `active_team` field

### Audit Directory Conflicts

**Problem:** `Cannot write to audit directory`

**Solution:**
- Ensure `artifacts_root` directory has write permissions
- Verify `audit_directory` doesn't conflict with other process outputs
- Check disk space availability

## Configuration Best Practices

1. **Use Version Control**: Track `.pantheon_project` and team configurations
2. **Document Profile Changes**: Comment profile modifications in `team-profile.yaml`
3. **Consistent Naming**: Use consistent team names across projects
4. **Regular Backups**: Backup team configurations before major changes
5. **Test After Changes**: Run test commands after modifying configuration
6. **Use Defaults**: Leverage framework defaults for organizational consistency
7. **Audit Production**: Enable audit logging for production environments
8. **Clean Temp Files**: Use `temp_file_cleanup: always` in production

This configuration system provides flexibility while maintaining the framework's opinionated structure, enabling both standardization and customization as needed.
