---
doc_id: getting-started-team-management
title: Team Package Management and Switching
description: Guide for managing multiple team packages including adding new teams, switching active teams, preserving customizations, and understanding team isolation with safe context switching through pantheon init
keywords: [team switching, active team, team management, pantheon init, team packages, multiple teams, team isolation, context switching, end-user]
relevance: Essential for projects using multiple team packages or switching between different development contexts while preserving team customizations
---

# Team Package Management and Switching

Pantheon supports multiple team packages within a single project, allowing you to switch between different development contexts while preserving all team customizations. This document covers adding, switching, and managing team packages.

## Understanding Team Packages

### What is a Team Package?

A Team Package is a complete, self-contained collection of:
- **Agents**: AI personas with specific capabilities (e.g., tech-lead, backend-engineer)
- **Processes**: Structured workflows for artifact creation and management
- **Configuration**: Team profile and runtime data
- **Documentation**: README and process documentation

### Team Package Location

All team packages reside in the project's `pantheon-teams/` directory:

```
project-root/
├── pantheon-teams/
│   ├── pantheon-dev/
│   │   ├── agents/
│   │   ├── processes/
│   │   ├── team-profile.yaml
│   │   ├── team-data.yaml
│   │   └── README.md
│   ├── pantheon-team-builder/
│   │   ├── agents/
│   │   ├── processes/
│   │   ├── team-profile.yaml
│   │   ├── team-data.yaml
│   │   └── README.md
│   └── custom-team/
│       └── ...
└── .pantheon_project
```

### Active Team Concept

The **active team** is the team package currently in use for all process executions and agent operations. It is defined in `.pantheon_project`:

```yaml
active_team: pantheon-dev
```

**Key Points:**
- Only one team can be active at a time
- All `pantheon` commands use the active team's definitions
- Switching teams changes which agents and processes are available
- Inactive teams remain in `pantheon-teams/` but are not used

## Adding New Teams

### Adding Bundled Teams

Pantheon ships with bundled team packages that can be added to your project.

**Command:**
```bash
pantheon init
```

**Process:**
1. Run `pantheon init` from project root
2. View available teams from bundled templates
3. Select a team that doesn't exist in your project
4. Framework scaffolds the new team's directory
5. New team becomes the active team

**Example:**

```bash
$ pantheon init

Available teams:
1. pantheon-dev (default - press enter to select) - Core development team
2. pantheon-team-builder - Team package builder
3. custom-team - Custom team definition

Select a team (1-3): 2

Scaffolding pantheon-team-builder...
Created directory: pantheon-teams/pantheon-team-builder/
Copied team files from bundled template
Generated fresh team-profile.yaml

Configuration files:
  - .pantheon_project: /project/.pantheon_project
  - team-profile.yaml: /project/pantheon-teams/pantheon-team-builder/team-profile.yaml

Active team set to: pantheon-team-builder
```

**Result:**
- `pantheon-teams/pantheon-team-builder/` directory created
- All team files copied from framework template
- `.pantheon_project` updated with `active_team: pantheon-team-builder`
- Agent installation and integration prompts offered

### Adding Custom Teams

Custom teams can be added by manually creating team directories or importing team packages.

**Manual Creation:**
1. Create directory: `mkdir -p pantheon-teams/my-custom-team`
2. Copy structure from existing team: `cp -r pantheon-teams/pantheon-dev/* pantheon-teams/my-custom-team/`
3. Customize agents, processes, and configuration
4. Switch to custom team: `pantheon init` and select custom team

**Import (Future Feature):**
```bash
# Planned: Import packaged team
pantheon package import my-team-package.tar.gz
```

## Switching Between Teams

### Safe Team Switching

The `pantheon init` command provides safe team switching that preserves all customizations.

**Command:**
```bash
pantheon init
```

**Process:**
1. Run `pantheon init` from project root
2. View available teams (including already installed teams)
3. Select a team that exists in your project
4. Framework updates active team **without** modifying team files

**Example:**

```bash
$ pantheon init

Available teams:
1. pantheon-dev (default - press enter to select) - Core development team
2. pantheon-team-builder - Team package builder (already installed)

Select a team (1-3): 1

Switching to pantheon-dev...

Active team set to: pantheon-dev

Configuration files:
  - .pantheon_project: /project/.pantheon_project
  - team-profile.yaml: /project/pantheon-teams/pantheon-dev/team-profile.yaml

Get started with the team documentation at: /project/pantheon-teams/pantheon-dev/README.md
```

**Result:**
- `.pantheon_project` updated with `active_team: pantheon-dev`
- **No files modified** in `pantheon-teams/pantheon-dev/`
- All customizations preserved
- Agent installation and integration prompts offered (if not already done)

### What Gets Switched?

**Changes When Switching:**
- Active team reference in `.pantheon_project`
- Available agents for `--actor` flag validation
- Available processes for `pantheon execute` commands
- Team profile used for schema and template rendering
- Team data accessed by `pantheon get team-data`

**Preserved During Switch:**
- All files in inactive team directories
- Team customizations (agents, processes, profiles)
- Team data (metrics, configuration)
- Generated artifacts in `pantheon-artifacts/`

### Verifying Active Team

**Check Current Active Team:**
```bash
# Method 1: Check .pantheon_project
cat .pantheon_project | grep active_team

# Method 2: List available agents
ls pantheon-teams/$(grep active_team .pantheon_project | cut -d: -f2 | tr -d ' ')/agents/
```

**Example Output:**
```yaml
active_team: pantheon-dev
```

## Team Isolation and Sandboxing

### Process Isolation

Each team's processes operate independently:
- Team A cannot execute Team B's processes
- Processes reference only their team's agents
- Schema and templates are team-specific
- Permissions enforce team boundaries

### Agent Isolation

Agents are team-specific:
- Agent names must match filenames in active team's `agents/` directory
- Agent validation checks active team only
- Switching teams changes available agents
- Cross-team agent references are not supported

### Artifact Isolation

Generated artifacts are shared across teams:
- All teams write to same `pantheon-artifacts/` directory
- Artifacts are not team-specific
- Multiple teams can operate on same artifacts (if desired)
- Artifact IDs are globally unique within project

**Example Artifact Paths:**
```
pantheon-artifacts/tickets/T001_feature.md    # Created by pantheon-dev
pantheon-artifacts/tickets/T002_process.md    # Created by pantheon-team-builder
```

### Configuration Isolation

Each team maintains separate configuration:
- Independent `team-profile.yaml` files
- Separate `team-data.yaml` stores
- Team-specific profile settings
- No configuration sharing between teams

## Multi-Team Workflows

### Common Multi-Team Scenarios

#### Scenario 1: Development and Team Building

Use different teams for different purposes:

```bash
# Use pantheon-dev for regular development
pantheon init  # Select: pantheon-dev
pantheon execute create-ticket --actor tech-lead --from-file ticket.json

# Switch to pantheon-team-builder for process development
pantheon init  # Select: pantheon-team-builder
pantheon execute build-team-process --actor pantheon --from-file build-spec.json

# Switch back to pantheon-dev
pantheon init  # Select: pantheon-dev
```

#### Scenario 2: Multiple Specialized Teams

Maintain different teams for different domains:

```bash
# Backend development team
pantheon init  # Select: backend-team

# Frontend development team
pantheon init  # Select: frontend-team

# DevOps team
pantheon init  # Select: devops-team
```

#### Scenario 3: Environment-Specific Teams

Use different teams for different environments:

```bash
# Development team with relaxed settings
pantheon init  # Select: dev-team

# Production team with strict validation
pantheon init  # Select: prod-team
```

### Team Switching Best Practices

1. **Document Active Team**: Include active team in project README
2. **Use Descriptive Names**: Name teams based on their purpose
3. **Consistent Structure**: Keep similar directory structures across teams
4. **Version Control All Teams**: Commit all team directories to git
5. **Test After Switching**: Verify commands work after team switch
6. **Coordinate Switches**: Communicate team switches in team environments

## Team Package Maintenance

### Updating Team Definitions

Team packages can be updated while preserving runtime data:

**Update Agents:**
```bash
# Modify agent files directly
vim pantheon-teams/pantheon-dev/agents/tech-lead.md

# Or use team builder processes
pantheon execute update-agent-prompt --actor pantheon --from-file agent.json
```

**Update Processes:**
```bash
# Modify process files directly
vim pantheon-teams/pantheon-dev/processes/create-ticket/routine.md

# Or use build processes to scaffold new processes
pantheon execute build-team-process --actor pantheon --from-file build-spec.json
```

**Update Configuration:**
```bash
# Modify team profile
vim pantheon-teams/pantheon-dev/team-profile.yaml

# Update team data via CLI
pantheon set team-data --actor pantheon --set config.new_setting=value
```

### Team Package Portability

Team packages are designed to be portable:

**Export Team (Manual):**
```bash
# Archive team directory
tar -czf my-team-package.tar.gz pantheon-teams/my-team/

# Share or backup the archive
```

**Import Team (Manual):**
```bash
# Extract team archive
tar -xzf my-team-package.tar.gz -C pantheon-teams/

# Verify team structure
ls pantheon-teams/my-team/

# Switch to imported team
pantheon init  # Select imported team
```

**Future Package Management:**
```bash
# Planned: Export team package
pantheon package export my-team

# Planned: Import team package
pantheon package import my-team-package.tar.gz

# Planned: List available teams
pantheon package list

# Planned: Update installed team
pantheon package update my-team
```

## Troubleshooting Team Management

### Team Not Found

**Problem:** `Team 'xyz' not found in pantheon-teams/`

**Solution:**
- Verify team directory exists: `ls pantheon-teams/`
- Add team via `pantheon init`
- Check for typos in directory name
- Ensure proper directory structure

### Agent Not Found After Switch

**Problem:** `Agent 'tech-lead' not found in active team`

**Solution:**
- Check active team: `cat .pantheon_project | grep active_team`
- Verify agent exists: `ls pantheon-teams/pantheon-dev/agents/`
- Use agents from active team only
- Switch to team containing desired agent

### Process Not Found After Switch

**Problem:** `Process 'create-ticket' not found`

**Solution:**
- Verify process exists in active team: `ls pantheon-teams/pantheon-dev/processes/`
- Check process name spelling
- Switch to team containing desired process
- Scaffold process if needed

### Configuration Conflicts

**Problem:** Team profiles have conflicting settings

**Solution:**
- Review both team profiles: `cat pantheon-teams/*/team-profile.yaml`
- Adjust profile settings to avoid conflicts
- Use different profile names across teams
- Document profile differences

## Team Management Best Practices

1. **One Team Per Purpose**: Create separate teams for distinct purposes
2. **Consistent Naming**: Use clear, descriptive team names
3. **Document Team Purpose**: Include purpose in team README
4. **Version Control**: Commit all teams to git
5. **Test After Switch**: Verify commands work after switching
6. **Preserve Customizations**: Never manually edit inactive teams during switch
7. **Coordinate Switches**: Communicate active team in shared environments
8. **Regular Backups**: Backup team packages before major changes
9. **Use Profiles**: Leverage profiles instead of multiple similar teams
10. **Review Permissions**: Check agent permissions when switching teams

Team management in Pantheon provides flexibility for multi-context development while maintaining the framework's opinionated structure and ensuring safe, predictable team switching.
