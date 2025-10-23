---
doc_id: getting-started-initialization
title: Project Initialization Workflow
description: Comprehensive guide to the pantheon init command including team selection, directory scaffolding, agent installation, CLAUDE.md integration, gitignore management, and transparent feedback during setup
keywords: [pantheon init, project setup, team selection, directory creation, agent installation, default team, initialization workflow, project configuration, end-user, beginner]
relevance: Critical workflow documentation for setting up new projects or switching active teams with detailed interactive prompts and configuration steps
---

# Project Initialization Workflow

A new project is configured to use Pantheon via a single, multi-purpose `pantheon init` command. This command scaffolds the necessary starter files and is also used to switch the active team.

## The `pantheon init` Command

The initialization command provides an enhanced user experience with clear feedback and transparent operations throughout the setup process.

### Basic Usage

```bash
cd my-project
pantheon init
```

## Initialization Process Steps

The `pantheon init` command executes the following steps in sequence:

### 1. Discover Bundled Teams

Identifies the available starter Team Packages (e.g., `pantheon-dev`, `pantheon-team-builder`) from the framework's `pantheon/_templates/pantheon-teams/` directory.

### 2. Prompt for Team Selection

Interactively prompts the user to choose a team. If a default team is configured in the framework defaults (`pantheon/_templates/pantheon-teams/defaults.yaml`), it appears as option 1 with a clear indicator.

**Example with Default Team:**
```
Available teams:
1. pantheon-dev (default - press enter to select) - Core development team
2. pantheon-team-builder - Team package builder
3. custom-team - Custom team definition

Select a team (1-3): [Press Enter to select option 1]
```

**Example without Default Team:**
```
Available teams:
1. pantheon-dev - Core development team
2. pantheon-team-builder - Team package builder
3. custom-team - Custom team definition

Select a team (1-3):
```

Simply pressing Enter selects the default team without requiring explicit input.

### 3. Scaffold and Configure

Based on the selection, the command performs the following actions:

#### Create pantheon-teams Directory

If the `pantheon-teams/` directory does not exist, it is created at the project root.

#### Copy Team Package

If the selected team's directory does not exist within `pantheon-teams/`, it is copied from the bundled template at `pantheon/_templates/pantheon-teams/<team-name>/`.

#### Generate team-profile.yaml

**Crucially, `pantheon init` generates a fresh `team-profile.yaml` file by reading the default values from the team's `team-profile-schema.json`.** This ensures the team starts with a valid, default configuration.

**Profile Selection:** If the selected team supports profiles, `pantheon init` will prompt you to select a profile and update the `active_profile` field in the team's `team-profile.yaml` file. This establishes team-profile.yaml as the single source of truth for profile configuration.

#### Create or Update .pantheon_project

Creates or updates the `.pantheon_project` file at the project root, setting the `active_team` to the user's selection. Note that `.pantheon_project` contains only project-level settings (`active_team` and `artifacts_root`). Team behavioral settings, including profile selection, are stored in `team-profile.yaml` within the team's directory.

### 4. Interactive Prompts with Sensible Defaults

The init command prompts for common configuration options, all defaulting to yes for a streamlined setup experience.

#### Agent Installation Prompts

The initialization process now supports installing agents for multiple platforms. You'll be prompted separately for each platform your development environment uses.

**Claude Agent Installation:**

Prompts to install team agents to `.claude/agents/`, defaulting to yes. Simply press Enter to accept:

```
Do you want to auto-install team agents for Claude? [Y/n]:
```

After confirmation, displays the list of installed agent files:

```
Installed agents to .claude/agents/pantheon-dev/:
tech-lead.md, backend-engineer.md, frontend-engineer.md
```

**What This Does:**
- Creates `.claude/agents/<team-name>/` directory
- Copies all `.md` files from `pantheon-teams/<team-name>/agents/` to the Claude agents directory
- Enables direct agent invocation through Claude Code interface

**OpenCode Agent Installation:**

Prompts to install team agents to `.opencode/agent/`, defaulting to yes. Simply press Enter to accept:

```
Do you want to auto-install team agents for OpenCode? [Y/n]:
```

After confirmation, displays the list of installed agent files:

```
Installed agents to .opencode/agent/pantheon-dev/:
tech-lead.md, backend-engineer.md, frontend-engineer.md
```

**What This Does:**
- Creates `.opencode/agent/<team-name>/` directory (note: singular 'agent', not 'agents')
- Copies all `.md` files from `pantheon-teams/<team-name>/agents/` to the OpenCode agent directory
- Enables direct agent invocation through OpenCode interface

**Multi-Platform Support:**
- Both platforms use identical installation processes with the same conflict resolution options
- Agent installation is independent for each platform - you can install to one, both, or neither
- The same team agents work across all platforms without modification
- All platforms maintain their own agent directory structures within your project

#### CLAUDE.md Integration Prompt

Prompts to append team protocol to `CLAUDE.md`, defaulting to yes. Shows content preview before confirmation:

```
--- Preview of content to append ---
# Pantheon Framework Protocol

The project uses the Pantheon Framework for structured AI development...

[First 10 lines of content...]
... (45 more lines)
--- End preview ---

Append the above content to CLAUDE.md? [Y/n]:
```

**What This Does:**
- Appends team-specific development protocols to project's `CLAUDE.md`
- Provides agents with context-specific guidance for the team
- Includes markers for idempotent operations (won't duplicate on re-init)

#### AGENTS.md Integration Prompt

Prompts to append agent usage instructions to `AGENTS.md`, defaulting to yes. Shows content preview before confirmation:

```
--- Preview of content to append ---
# Pantheon Team Agents

This project uses Pantheon Framework agents for structured development...

[First 10 lines of content...]
... (35 more lines)
--- End preview ---

Append the above content to AGENTS.md? [Y/n]:
```

**What This Does:**
- Appends agent roster and usage instructions to `AGENTS.md`
- Documents available agents and their capabilities
- Includes markers for idempotent operations

#### Gitignore Management Prompt

Prompts to add Pantheon-related files to `.gitignore`, defaulting to yes for typical git-based workflows:

```
Add Pantheon files to .gitignore? [Y/n]:
```

**What This Does:**
- Adds the following entries to `.gitignore`:
  - `pantheon-artifacts/` - Generated artifacts directory
  - `.pantheon_project` - Project configuration file
  - `pantheon-teams/` - Team package source files
- Includes marker comment for idempotent operations
- Creates `.gitignore` if it doesn't exist

### 5. Detailed Feedback

The command provides transparent feedback throughout the initialization process.

#### Directory Creation Feedback

Shows the actual directory paths created (e.g., "Created directory: pantheon-artifacts/docs") rather than just counts:

```
Creating project structure...
Created directory: pantheon-artifacts/docs
Created directory: pantheon-artifacts/tickets
Created directory: pantheon-artifacts/diagrams
Created directory: pantheon-artifacts/tmp
```

#### Configuration File Locations

Displays absolute paths to key configuration files for easy reference:

```
Configuration files:
  - .pantheon_project: C:/project/.pantheon_project (project-level: active_team, artifacts_root)
  - team-data.yaml: C:/project/pantheon-teams/pantheon-dev/team-data.yaml
  - team-profile.yaml: C:/project/pantheon-teams/pantheon-dev/team-profile.yaml (team-level: active_profile, profiles)
```

#### README Location

Displays the path to the team's README.md file for quick access to getting started documentation:

```
Get started with the team documentation at: C:/project/pantheon-teams/pantheon-dev/README.md
```

## Generated Directory Structure

After running `pantheon init` with the `pantheon-dev` team and installing agents for both Claude and OpenCode, your project will look like this:

```
my-project/
├── .pantheon_project
├── .gitignore (updated)
├── CLAUDE.md (updated)
├── AGENTS.md (updated)
├── .claude/
│   └── agents/
│       └── pantheon-dev/
│           ├── tech-lead.md
│           ├── backend-engineer.md
│           └── frontend-engineer.md
├── .opencode/
│   └── agent/
│       └── pantheon-dev/
│           ├── tech-lead.md
│           ├── backend-engineer.md
│           └── frontend-engineer.md
├── pantheon-teams/
│   └── pantheon-dev/
│       ├── team-profile.yaml
│       ├── team-data.yaml
│       ├── agents/
│       ├── processes/
│       └── README.md
├── pantheon-artifacts/
│   ├── .gitignore
│   └── tmp/
└── (your existing project files...)
```

**Note:** The `.opencode/` directory structure uses the singular 'agent' directory name, while `.claude/` uses the plural 'agents'. This follows each platform's respective conventions.

## Switching and Adding Teams

You can switch the active team or add a new starter team at any time by running `pantheon init` again.

### Adding a New Team

If you select a team that is not yet in your project, `init` will scaffold the new team's directory into `pantheon-teams/` and set it as the `active_team`.

**Example:**
```bash
# First init with pantheon-dev
pantheon init
# Select: 1 (pantheon-dev)

# Later, add pantheon-team-builder
pantheon init
# Select: 2 (pantheon-team-builder)
```

**Result:**
- `pantheon-teams/pantheon-team-builder/` directory created
- `.pantheon_project` updated with `active_team: pantheon-team-builder`
- `pantheon-teams/pantheon-dev/` remains untouched

### Switching the Active Team

If you select a team that already exists in your project, `init` will **not** overwrite any of your modifications. It will simply update the `active_team` key in `.pantheon_project` to your selection, making it a safe way to switch context.

**Example:**
```bash
# Switch back to pantheon-dev
pantheon init
# Select: 1 (pantheon-dev)
```

**Result:**
- `.pantheon_project` updated with `active_team: pantheon-dev`
- No files modified in `pantheon-teams/pantheon-dev/`
- All existing customizations preserved

## Default Team Configuration

The framework ships with a default team configuration that affects the `pantheon init` behavior.

### Framework Defaults Location

```
pantheon/_templates/pantheon-teams/defaults.yaml
```

### Default Configuration

```yaml
# Framework-level defaults for team initialization
default_team: pantheon-dev
```

### Customizing the Default Team

**For Framework Maintainers:**
1. Locate the framework installation directory (via `pip show pantheon-framework`)
2. Edit `pantheon/_templates/pantheon-teams/defaults.yaml`
3. Set `default_team` to your preferred team name
4. The change applies to all new `pantheon init` commands across all projects

**For Development Builds:**
- Modify `pantheon/_templates/pantheon-teams/defaults.yaml` in the source repository
- Changes become part of the framework installation when the package is built

## Idempotent Operations

The `pantheon init` command is designed to be idempotent, meaning it can be run multiple times safely:

### Directory Creation
- Only creates directories if they don't exist
- Never overwrites existing directories or files

### Agent Installation
- Works independently for each platform (Claude and OpenCode)
- Only copies agent files if the target directory doesn't exist
- Prompts before overwriting if agents directory exists for that platform
- Supports conflict resolution options: overwrite all, skip all, or ask for each file

### File Appending
- Uses marker comments to detect previous appends
- Won't duplicate content if markers are found
- Examples:
  ```
  # BEGIN PANTHEON FRAMEWORK INTEGRATION
  ...
  # END PANTHEON FRAMEWORK INTEGRATION
  ```

### Gitignore Entries
- Checks for existing entries before adding
- Uses marker comment for section identification
- Won't create duplicate ignore rules

## Initialization Validation

After running `pantheon init`, validate the setup:

### Check Project Configuration

```bash
cat .pantheon_project
```

Expected output:
```yaml
active_team: pantheon-dev
artifacts_root: pantheon-artifacts
```

### Verify Team Structure

```bash
ls pantheon-teams/pantheon-dev/
```

Expected output:
```
agents/  processes/  team-profile.yaml  team-data.yaml  README.md
```

### Test Basic Commands

```bash
# Get team information
pantheon get team-data --actor pantheon

# List available processes
ls pantheon-teams/pantheon-dev/processes/
```

## Common Initialization Issues

### No Teams Available

**Problem:** `No teams found in bundled templates`

**Solution:**
- Verify framework installation: `pip show pantheon-framework`
- Reinstall framework: `pip install --force-reinstall pantheon-framework`

### Permission Errors

**Problem:** `Permission denied when creating directories`

**Solution:**
- Ensure write permissions in project directory: `chmod u+w .`
- Run from project root with proper ownership

### Existing Files Conflict

**Problem:** `File already exists and cannot be overwritten`

**Solution:**
- Review existing `.pantheon_project` for conflicts
- Manually merge or remove conflicting files
- Re-run `pantheon init`

### Invalid Team Selection

**Problem:** `Invalid team selection`

**Solution:**
- Enter a number from the displayed range
- Check for typos in manual entry
- Press Enter to accept default team

## Post-Initialization Next Steps

After successful initialization:

1. **Review Team README**: `cat pantheon-teams/<team-name>/README.md`
2. **Configure Team Profile**: Edit `pantheon-teams/<team-name>/team-profile.yaml` if needed
3. **Verify Agents**: Check installed agents for your platform(s):
   - Claude: `ls .claude/agents/<team-name>/`
   - OpenCode: `ls .opencode/agent/<team-name>/`
4. **Test First Command**: `pantheon get team-data --actor pantheon`
5. **Read Process Documentation**: `ls pantheon-teams/<team-name>/processes/`

The initialization process sets up your project with a complete, working Pantheon team package, ready for agent-driven development workflows across Claude, OpenCode, or both platforms.
