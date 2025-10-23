---
doc_id: pantheon-team-builder-team
title: Pantheon Team Builder Meta-Team
description: Documentation for the pantheon-team-builder meta-team that creates and manages other team packages through recursive framework capabilities including artifact scaffolding, agent management, team blueprints, and workflow orchestration
keywords: [pantheon-team-builder, meta-team, build-team-artifact, team-blueprint, process scaffolding, agent creation, team management, recursive framework, self-hosting]
relevance: Essential for creating new team packages and understanding the framework's recursive meta-programming capabilities for team package generation and management
---

# Pantheon Team Builder Meta-Team

To bootstrap the creation of new Team Packages, the Pantheon Framework includes a special "meta-team" called the **Pantheon Team Builder**. This is a standard Team Package located at `pantheon-teams/pantheon-team-builder/` whose sole purpose is to **create and manage other Team Packages**.

## Meta-Team Concept

The Pantheon Team Builder demonstrates the framework's recursive capabilities - it uses Pantheon to build Pantheon components. This "eating your own dog food" approach ensures that:

- **The process of creating AI teams is itself a "glass box" operation**
- **Team creation workflows are transparent and auditable**
- **Framework capabilities are thoroughly tested through self-use**
- **New team creation benefits from the same reliability as other processes**

## The Team Builder Architecture

The Pantheon Team Builder uses a **blueprint-driven approach** where team design happens in structured artifacts before implementation. This ensures team packages are well-planned, consistent, and maintainable.

### Core Architecture Components

1. **Team Blueprint Artifact**: The central planning document (`team-blueprint.md`) that defines the team's foundation, context, artifacts, agents, and profile configuration. This artifact serves as the single source of truth for team design.

2. **Specialized Designer Agents**: Six specialized agents handle different aspects of team creation:
   - `pantheon-team-builder`: Lead architect for team strategy and blueprints
   - `artifact-designer`: Designs artifact data models and schemas
   - `agent-designer`: Designs AI agent personas and capabilities
   - `profile-designer`: Designs team profiles and configuration
   - `routine-builder`: Creates RAE-compliant routines
   - `team-readme-writer`: Creates user-facing documentation

3. **Build Processes**: Schema-driven processes that generate concrete implementations from blueprint specifications:
   - `build-team-artifact`: Generates complete artifact and process families (CREATE, GET, UPDATE)
   - `create-agent`: Generates agent definition files
   - `create-basic-routine`: Generates simple boilerplate routines
   - `create-custom-routine`: Generates detailed custom routines
   - `create-team-profile`: Generates team profile configuration
   - `create-team-readme`: Generates team documentation

4. **Blueprint Update Processes**: Modular update processes for refining team blueprints section-by-section without recreating the entire design.

## Team Processes

The Pantheon Team Builder provides a comprehensive set of processes for creating and managing team packages. These processes follow a blueprint-driven workflow where design happens first, then implementation is generated from the blueprint.

### Blueprint Management

The team blueprint is the central planning artifact that drives all team creation activities.

#### `create-team-blueprint`

Creates a new team blueprint defining the team's foundation, context, artifacts, agents, and profile configuration.

**Purpose:**
- Establishes team identity, mission, and core strategy
- Defines key concepts and terminology
- Lists artifacts the team will produce
- Specifies agents and their responsibilities
- Defines configuration profiles and properties

**Usage:**
```bash
pantheon execute create-team-blueprint --actor pantheon-team-builder --from-file blueprint.json
```

#### `update-team-blueprint --sections <section_list>`

Updates specific sections of an existing team blueprint. Supports modular updates to:
- `foundation`: Team identity and core strategy
- `context`: Key concepts and terminology
- `artifacts`: Artifact definitions and purposes
- `agents`: Agent roles and responsibilities
- `profile`: Configuration properties and profiles

**Usage:**
```bash
pantheon execute update-team-blueprint --sections foundation,context --id TB01 --actor pantheon-team-builder --from-file update.json
```

#### `get-team-blueprint --id <blueprint_id> --sections <section_list>`

Retrieves the team blueprint or specific sections of it. Returns all sections if `--sections` is not specified.

**Usage:**
```bash
pantheon execute get-team-blueprint --id TB01 --actor pantheon-team-builder
pantheon execute get-team-blueprint --id TB01 --sections artifacts,agents --actor artifact-designer
```

### Artifact Scaffolding

The artifact scaffolding process generates complete artifact definitions and supporting process families.

#### `build-team-artifact`

Generates a complete artifact and its supporting process family (CREATE, GET, UPDATE processes) from a build specification. This is the primary mechanism for implementing artifacts defined in the team blueprint.

**Features:**
- Generates CREATE process with schema, content template, placement, and naming
- Generates GET process with locator, parser, and sections configuration
- Generates UPDATE processes for each artifact section
- Supports two build modes: `complete` (single-pass creation) and `modular` (section-by-section updates)
- Includes optional context section for process artifacts
- Stages output in `pantheon-artifacts/pantheon-team-builds/<team>/` for review

**Usage:**
```bash
pantheon execute build-team-artifact --actor artifact-designer --from-file build-spec.json
```

### Agent Management

Processes for creating and managing agent definitions.

#### `create-agent`

Creates a new agent definition file with role, competencies, philosophy, technical understanding, and workflows.

**Purpose:**
- Defines agent persona and expertise boundaries
- Establishes agent's problem-solving approach
- Documents technical context and system knowledge
- Defines primary workflows using RAE pattern

**Usage:**
```bash
pantheon execute create-agent --actor agent-designer --from-file agent.json
```

#### `update-agent`

Updates an existing agent definition. Supports updating specific sections of the agent's prompt.

**Usage:**
```bash
pantheon execute update-agent --id agent-name --actor agent-designer --from-file update.json
```

#### `get-agent --id <agent_name>`

Retrieves an existing agent definition.

**Usage:**
```bash
pantheon execute get-agent --id artifact-designer --actor agent-designer
```

### Routine Management

Processes for creating different types of routine files.

#### `create-basic-routine`

Creates basic routine files with boilerplate steps for standard CREATE, GET, or UPDATE processes. Suitable for simple processes that follow standard patterns.

**Purpose:**
- Generates standard routine structure
- Includes boilerplate steps (get schema, get context, execute process)
- Minimal customization required

**Usage:**
```bash
pantheon execute create-basic-routine --actor routine-builder --from-file routine.json
```

#### `create-custom-routine`

Creates detailed custom routines with sophisticated cognitive steps, branching logic, and process-specific guidance. Used for complex processes requiring careful thought process design.

**Purpose:**
- Defines high-level cognitive guidance organized into thematic buckets
- Includes conditional branching logic
- Provides process-specific guardrails and best practices
- Avoids mechanical field-by-field checklists

**Usage:**
```bash
pantheon execute create-custom-routine --actor routine-builder --from-file routine.json
```

#### `get-custom-routine --id <process_name>`

Retrieves an existing custom routine definition.

**Usage:**
```bash
pantheon execute get-custom-routine --id build-team-artifact --actor routine-builder
```

### Profile Management

Processes for creating and retrieving team profile configurations.

#### `create-team-profile`

Creates a team profile YAML file defining the team's configuration properties, profiles, and default settings.

**Purpose:**
- Defines configuration properties for schema and template control
- Specifies available profiles with different configuration values
- Sets default active profile

**Usage:**
```bash
pantheon execute create-team-profile --actor profile-designer --from-file profile.json
```

#### `get-team-profile --id <team_name>`

Retrieves an existing team profile configuration.

**Usage:**
```bash
pantheon execute get-team-profile --id my-team --actor profile-designer
```

### Documentation

Processes for creating and maintaining team README documentation.

#### `create-team-readme`

Creates comprehensive team README documentation explaining team purpose, agents, artifacts, and usage examples.

**Purpose:**
- Establishes team value proposition
- Documents all agents with their specialties
- Provides workflow examples and usage guidance
- Creates onboarding experience for new users

**Usage:**
```bash
pantheon execute create-team-readme --actor team-readme-writer --from-file readme.json
```

#### `update-team-readme --sections <section_list>`

Updates specific sections of the team README. Supports modular updates to:
- `overview`: Team mission and capabilities
- `agents`: Agent roster and profiles
- `artifacts`: Artifact types and usage
- `getting_started`: Onboarding and first steps
- `workflow_examples`: Example workflows
- `working_with_agents`: Collaboration best practices

**Usage:**
```bash
pantheon execute update-team-readme --sections overview,agents --actor team-readme-writer --from-file update.json
```

#### `get-team-readme --id <team_name> --sections <section_list>`

Retrieves team README documentation or specific sections.

**Usage:**
```bash
pantheon execute get-team-readme --id my-team --actor team-readme-writer
```

## Team Builder Workflow

A typical team creation workflow using the Pantheon Team Builder follows a blueprint-first approach:

### 1. Create Team Blueprint

Start by creating a comprehensive team blueprint that defines the team's purpose, artifacts, agents, and configuration.

```bash
# Create initial team blueprint
pantheon execute create-team-blueprint --actor pantheon-team-builder --from-file blueprint.json
```

The blueprint includes:
- **Foundation**: Team identity, mission, strategy, and key principles
- **Context**: Key concepts, terminology, and domain knowledge
- **Artifacts**: List of artifacts the team will produce with purposes
- **Agents**: Agent roles, responsibilities, and required expertise
- **Profile**: Configuration properties and operational profiles

### 2. Refine Blueprint Sections

Use modular updates to refine specific sections of the blueprint as the design evolves.

```bash
# Refine artifact definitions
pantheon execute update-team-blueprint --sections artifacts --id TB01 --actor artifact-designer --from-file artifacts.json

# Refine agent definitions
pantheon execute update-team-blueprint --sections agents --id TB01 --actor agent-designer --from-file agents.json

# Refine profile configuration
pantheon execute update-team-blueprint --sections profile --id TB01 --actor profile-designer --from-file profile.json
```

### 3. Build Team Components

Once the blueprint is complete, generate the concrete implementation components.

```bash
# Build artifacts and their process families
pantheon execute build-team-artifact --actor artifact-designer --from-file ticket-artifact-spec.json
pantheon execute build-team-artifact --actor artifact-designer --from-file plan-artifact-spec.json

# Create agent definitions
pantheon execute create-agent --actor agent-designer --from-file strategist-agent.json
pantheon execute create-agent --actor agent-designer --from-file implementer-agent.json

# Create custom routines for complex processes
pantheon execute create-custom-routine --actor routine-builder --from-file analyze-routine.json

# Create basic routines for standard processes
pantheon execute create-basic-routine --actor routine-builder --from-file update-status-routine.json

# Create team profile
pantheon execute create-team-profile --actor profile-designer --from-file profile.json
```

### 4. Generate Documentation

Create user-facing documentation to help users understand and interact with the team.

```bash
# Generate team README
pantheon execute create-team-readme --actor team-readme-writer --from-file readme.json
```

### 5. Review and Deploy

Review the generated team package components and deploy to the team directory.

```bash
# Review generated components in staging area
ls pantheon-artifacts/pantheon-team-builds/my-team/

# Copy to team directory after review
cp -r pantheon-artifacts/pantheon-team-builds/my-team/* pantheon-teams/my-team/

# Initialize the new team
pantheon init  # Select my-team from the menu
```

## Benefits of the Meta-Team Approach

### Self-Validation

- The Team Builder validates the framework's capabilities through actual use
- Process improvements automatically benefit team creation workflows
- Framework limitations are discovered through real-world application

### Consistency

- All teams are created using the same structured approach
- Standard conventions are enforced through templated processes
- Quality patterns are automatically propagated to new teams

### Transparency

- Team creation process is fully auditable and version-controlled
- Decision rationale is captured in tickets and documentation
- Changes to team structures are systematically tracked

### Scalability

- New team types can be created without framework modifications
- Common patterns can be identified and standardized
- Organizational knowledge is captured in reusable templates

## Team Builder Agents

The Pantheon Team Builder includes six specialized agents, each focused on a specific aspect of team creation:

### `pantheon-team-builder`

**Role**: Lead architect for team blueprints and high-level strategy

**Responsibilities**:
- Creates and updates team blueprints
- Defines team foundation, mission, and core strategy
- Establishes key concepts and terminology
- Orchestrates overall team design

**Primary Processes**: `create-team-blueprint`, `update-team-blueprint`

### `artifact-designer`

**Role**: Specialist in artifact data models and schemas

**Responsibilities**:
- Designs artifact structures with lifecycle sections
- Creates JSON schemas for data validation
- Designs Jinja2 templates for artifact rendering
- Generates complete artifact and process families

**Primary Processes**: `build-team-artifact`, `update-team-blueprint --sections artifacts`

### `agent-designer`

**Role**: Specialist in AI agent persona and capability design

**Responsibilities**:
- Designs agent personas with clear expertise boundaries
- Defines agent competencies and philosophical approaches
- Creates agent workflows following RAE patterns
- Establishes technical understanding sections

**Primary Processes**: `create-agent`, `update-agent`, `update-team-blueprint --sections agents`

### `profile-designer`

**Role**: Specialist in team configuration and profiles

**Responsibilities**:
- Designs profile properties for schema and template control
- Creates configuration profiles for different operational modes
- Ensures properties work in both Jsonnet and Jinja2 contexts
- Balances flexibility with simplicity

**Primary Processes**: `create-team-profile`, `update-team-blueprint --sections profile`

### `routine-builder`

**Role**: Specialist in RAE-compliant routine design

**Responsibilities**:
- Creates structured step-by-step routines
- Designs cognitive guidance and branching logic
- Implements proper node types and control flow
- Ensures routines work with schemas for reliable execution

**Primary Processes**: `create-basic-routine`, `create-custom-routine`

### `team-readme-writer`

**Role**: Documentation specialist for team user guides

**Responsibilities**:
- Creates comprehensive team README files
- Documents agent capabilities in user-friendly terms
- Provides workflow examples and usage guidance
- Designs onboarding experiences for new users

**Primary Processes**: `create-team-readme`, `update-team-readme`

## Recursive Capability Demonstration

The Team Builder showcases Pantheon's recursive design:

### Framework Building Framework

- Uses standard Pantheon processes to create Pantheon components
- Validates that the framework can handle its own complexity
- Demonstrates extensibility through self-application

### Artifact Creating Artifact

- The `build-team-artifact` process generates complete artifact definitions
- Each artifact includes its own CREATE, GET, and UPDATE processes
- Template-driven approach ensures consistency across all generated processes
- Meta-processes benefit from the same quality standards as regular processes

### Blueprint-Driven Development

- Team blueprints serve as the single source of truth for team design
- All implementation components are generated from blueprint specifications
- Changes to blueprints can be propagated to implementations
- Design-first approach prevents ad-hoc implementation inconsistencies

### Team Creating Team

- Team Builder can create other Team Builders if needed
- Self-hosting capability proves the framework's completeness
- Recursive depth is limited only by practical needs

## Integration with Development Teams

### Handoff Process

Once a Team Package is created by the Team Builder:

1. **Package Validation**: Ensure all required components are present
2. **Documentation Review**: Verify processes and agents are well-defined
3. **Integration Testing**: Validate the team works with existing workflows
4. **Deployment**: Move team package to active use in development

**Manual Promotion:**
```bash
# Review generated processes
ls pantheon-artifacts/pantheon-team-builds/my-team/processes/

# Copy to team directory
cp -r pantheon-artifacts/pantheon-team-builds/my-team/* pantheon-teams/my-team/

# Switch to new team
pantheon init  # Select my-team
```

### Ongoing Maintenance

The Team Builder can also handle updates to existing teams:

- Adding new agents or processes to existing teams
- Updating team profiles for changing requirements
- Refactoring common patterns across multiple teams

## Build Artifact Output Structure

When `build-team-artifact` generates a new artifact and process family, it creates a complete, staged bundle in the team builds directory:

```
pantheon-artifacts/pantheon-team-builds/my-team/processes/
├── create-report/
│   ├── routine.md                    # CREATE routine with schema retrieval and execution steps
│   ├── schema.jsonnet                # Data contract for report creation
│   ├── permissions.jsonnet           # Access control for creation
│   └── artifact/
│       ├── content.md                # Jinja2 template for rendering report content
│       ├── placement.jinja           # Template for determining report directory
│       └── naming.jinja              # Template for generating report filename
├── get-report/
│   ├── routine.md                    # GET routine for retrieving reports
│   ├── permissions.jsonnet           # Access control for retrieval
│   └── artifact/
│       ├── locator.jsonnet           # Pattern for finding report files
│       ├── parser.jsonnet            # Logic for extracting report ID from filename
│       └── sections.jsonnet          # Definition of retrievable report sections
└── update-report-<section>/          # One UPDATE process per section
    ├── routine.md                    # UPDATE routine for specific section
    ├── schema.jsonnet                # Data contract for section update
    ├── permissions.jsonnet           # Access control for updates
    └── artifact/
        ├── patch.md                  # Template for section replacement
        ├── target.jsonnet            # Logic for identifying section boundaries
        ├── locator.jsonnet           # (import from get-report)
        └── parser.jsonnet            # (import from get-report)
```

**Key Features:**
- Complete process family with CREATE, GET, and UPDATE operations
- Each process includes schema, routine, and permissions
- UPDATE processes are section-specific for modular updates
- Locator and parser are shared across GET and UPDATE processes
- All files staged for review before deployment

## Best Practices

### Blueprint-First Design

1. **Start with team blueprint**: Create comprehensive blueprint before implementation
2. **Define clear mission**: Articulate team purpose and core strategy
3. **List artifacts first**: Identify all artifacts team will produce
4. **Design agent roles**: Define specialized agents with clear boundaries
5. **Plan configuration**: Design profile properties for operational flexibility
6. **Document key concepts**: Establish shared terminology and domain knowledge

### Artifact Design

1. **Classify artifact type**: Determine if Process Artifact (guides work) or Terminal Artifact (final deliverable)
2. **Choose build mode**: Use `complete` for simple docs, `modular` for collaborative multi-stage updates
3. **Design lifecycle sections**: Break artifacts into logical, updatable sections
4. **Include context wisely**: Add context section only for Process Artifacts
5. **Create tight schemas**: Validate all required data with clear constraints
6. **Design flexible templates**: Use Jinja2 conditionals for optional fields and profile-based customization

### Agent Creation

1. **Define clear persona**: Establish role, philosophy, and expertise boundaries
2. **Document technical context**: Provide comprehensive technical understanding section
3. **Design RAE workflows**: Follow two-step pattern (Get Instructions, Follow Instructions)
4. **Match CREATE with UPDATE**: Ensure every CREATE workflow has corresponding UPDATE workflow
5. **Specify tool commands**: Reference exact Pantheon CLI commands in workflows
6. **Keep prompts focused**: Avoid overlapping or redundant responsibilities

### Routine Design

1. **Use thematic buckets**: Organize steps into 3-5 high-level thematic sections
2. **Provide cognitive guidance**: Guide thought process, not just data entry
3. **Include branching logic**: Use `branch` nodes for conditional paths
4. **Terminate early exits**: Use `branchfinishnode` for failure conditions
5. **Avoid micro-checklists**: Don't create separate steps for each schema field
6. **Skip boilerplate in custom**: Don't include setup/wrap-up steps in custom routines

### Profile Configuration

1. **Design schema-first**: Primarily use profiles to control schema behavior
2. **Keep templates simple**: Minimize profile-aware template logic
3. **Use simple values**: Stick to simple types that work in both Jsonnet and Jinja2
4. **Justify properties**: Only add configuration when benefit clearly outweighs maintenance cost
5. **Test all profiles**: Validate each profile configuration with actual usage

### Implementation and Validation

1. **Review staged output**: Inspect all generated files in `pantheon-artifacts/pantheon-team-builds/`
2. **Test incrementally**: Validate each component before moving to next
3. **Verify permissions**: Check agent access control for all processes
4. **Execute workflows**: Test complete CREATE, GET, UPDATE cycles
5. **Generate documentation**: Create README after implementation is complete
6. **Deploy systematically**: Copy reviewed components to team directory

By serving as both a practical tool and a validation mechanism, the Pantheon Team Builder ensures that the framework's team creation capabilities are robust, reliable, and aligned with the Glass Box philosophy of transparent, systematic AI development.
