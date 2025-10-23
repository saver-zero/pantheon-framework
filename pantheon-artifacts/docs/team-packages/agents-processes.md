---
doc_id: team-packages-agents-processes
title: "Agents & Processes"
description: "Complete guide to agent personas and process workflows that define team behavior, including structure, permissions, and interaction patterns."
keywords: [team-packages, agents, processes, routines, permissions, RAE, workflow, agent-definition]
relevance: "Use this document to understand how agents and processes work together to create AI teams, including agent definition structure, process types, and the RAE interaction model."
---

# Agents & Processes

Team Packages contain two main types of components that define their behavior: **Agents** (the personas) and **Processes** (the workflows). Together, these components create a complete AI team capable of executing complex, multi-step workflows.

## Agents

**Agents** are LLM-powered actors with specific personas, roles, and skill sets. Each agent is defined by a Markdown file in the `agents/` directory that serves as their "prompt" or persona definition.

### Agent Definition Structure

```
agents/
├── tech-lead.md           # Strategic technical leadership
├── backend-engineer.md   # Backend development specialist
├── code-reviewer.md      # Code quality and review
└── scribe.md            # Feedback logging and classification
```

### Agent File Format

Each agent file contains:
- **Role and Responsibilities**: Clear definition of the agent's purpose
- **Skills and Expertise**: Technical capabilities and domain knowledge
- **Working Style**: How the agent approaches tasks and interacts
- **Context and Constraints**: Specific guidelines and limitations

### Agent Discovery

- Agent names are derived from filenames (e.g., `tech-lead.md` → `tech-lead`)
- Valid agents become available as `--actor` values for CLI commands
- No registration required - agents are discovered at runtime by the framework

## Processes

**Processes** are complete workflows for specific tasks, following the `verb-noun` naming convention. Each process is a self-contained directory with all necessary components for execution.

### Process Structure

The exact files in the `artifact/` directory determine the operation type using the new **Operation-Specific Naming Conventions**:

```
processes/
└── create-ticket/              # CREATE operation example
    ├── routine.md              # Step-by-step instructions for agents
    ├── permissions.jsonnet     # Access control rules
    ├── schema.jsonnet          # Data contract definition
    └── artifact/               # Operation-specific artifact files
        ├── content.md          # Template for artifact content (CREATE)
        ├── placement.jinja     # Directory template for placement (CREATE)
        ├── naming.jinja        # Filename template for naming (CREATE)
        └── sections.jsonnet    # Section markers for structured documents
```

**Operation Types by File Combination:**
- **CREATE**: `content.md` + `placement.jinja` + `naming.jinja`
- **UPDATE**: `patch.md` + `locator.jsonnet` + `parser.jsonnet` + `target.jsonnet`
- **GET**: `locator.jsonnet` + `parser.jsonnet` + `sections.jsonnet`

### Core Process Files

#### routine.md
Contains the literal, step-by-step sequence of `pantheon` commands an agent must follow. This is the "source code" of the process, written in human-readable Markdown.

Example:
```markdown
Step 1. **Get schema:** Retrieve the data contract for ticket creation. Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated with relevant business and technical context.

Step 3. **Get temp file:** Obtain a temporary file path for atomic operations. Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.

Step 4 (terminate). **Submit ticket:** Execute the ticket creation process. Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done, report back to the user.
```

#### schema.jsonnet
Defines the data contract for the process input. Written in Jsonnet to support dynamic composition based on team profiles.

Example:
```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    title: {
      type: 'string',
      description: 'Brief, action-oriented ticket title'
    },
    business_context: {
      type: 'string',
      description: 'Why this work is needed from business perspective'
    },
    technical_context: {
      type: 'string',
      description: if profile.verbosity == 'detailed' then
        'Comprehensive technical background and constraints'
      else
        'Key technical considerations'
    }
  },
  required: ['title', 'business_context', 'technical_context']
}
```

#### permissions.jsonnet
Defines access control rules using allowlist/denylist patterns.

Example:
```jsonnet
{
  allow: ['tech-lead', 'pantheon'],
  deny: []
}
```

### Process Types

The framework uses a **Unified Execute Model** where process behavior is determined by the **combination of files in the `artifact/` directory**:

#### CREATE Processes
- **File Combination**: `content.md` + `placement.jinja` + `naming.jinja`
- **Behavior**: Generates and saves new formatted artifacts to disk
- **Examples**: `create-ticket`, `create-document`, `create-architecture-doc`
- **Output**: New file written to the configured output directory

#### UPDATE Processes
- **File Combination**: `patch.md` + GET files + `target.jsonnet`
- **Behavior**: Locates existing artifacts and modifies specific sections
- **Examples**: `update-plan`, `update-ticket-status`, `update-code-review`
- **Output**: Modified file written to the same location

#### GET Processes
- **File Combination**: `locator.jsonnet` + `parser.jsonnet` + `sections.jsonnet` (no `content.md` or `patch.md`)
- **Behavior**: Finds and parses existing artifacts, returns structured JSON data
- **Examples**: `get-ticket`, `get-team-info`, `get-planning-context`
- **Output**: JSON data printed to stdout

## Agent-Process Interaction Model

### Permission-Based Access
- Each process defines which agents can execute it via `permissions.jsonnet`
- CLI validates actor permissions before allowing process execution
- Fine-grained control over who can perform what actions

### RAE (Retrieval-Augmented Execution) Loop
1. **Agent requests instructions**: `pantheon get process <process-name>`
2. **Framework returns routine**: Step-by-step instructions in Markdown
3. **Agent follows routine**: Executes each step as specified
4. **Framework enforces contracts**: Validates data and permissions at each step

### Example Workflow: Planning Agent Creates a Plan

```bash
# Step 1: Agent gets its instructions
pantheon get process update-plan --actor backend-engineer

# Step 2: Agent follows returned routine
pantheon get schema update-plan --actor backend-engineer
pantheon execute get-planning-context --actor backend-engineer --ticket T004
# (Agent prepares JSON data based on schema and context)
pantheon get tempfile --process update-plan --actor backend-engineer
# (Agent writes JSON to temp file)
pantheon execute update-plan --from-file /tmp/update-plan_123.json --actor backend-engineer
```

## Team Composition Patterns

### Core Agent Roles
Most teams include these fundamental roles:

- **Strategic Agent** (e.g., `tech-lead`): Creates tickets, assigns work, makes architectural decisions
- **Specialist Agents** (e.g., `backend-engineer`, `frontend-engineer`): Execute technical work in their domain
- **Quality Agent** (e.g., `code-reviewer`): Reviews and validates completed work
- **Process Agent** (e.g., `scribe`): Handles meta-tasks like logging and feedback

### Workflow Processes
Common process patterns include:

- **Creation Processes**: `create-ticket`, `create-architecture-doc`
- **Update Processes**: `update-plan`, `update-code-review`, `update-context`
- **Retrieval Processes**: `get-ticket`, `get-team-info`, `get-planning-context`
- **Management Processes**: `submit-feedback`, `log-progress`

## Extensibility and Customization

### Adding New Agents
1. Create a new `.md` file in the `agents/` directory
2. Define the agent's persona and capabilities
3. Agent becomes immediately available for `--actor` flag
4. Update process permissions as needed to grant access

### Adding New Processes
1. Create a new `<verb-noun>/` directory in `processes/`
2. Add required files: `routine.md`, `schema.jsonnet`, `permissions.jsonnet`
3. Optionally add `artifact/` directory for write processes
4. Process becomes immediately available for execution

### Team Package Evolution
- All changes are version-controlled with the team package
- Profiles can modify process behavior without changing core definitions
- Agents and processes can be added/removed without framework modifications

This flexible composition model allows teams to evolve their capabilities organically while maintaining the structured, auditable approach central to the Glass Box philosophy.

---

**Cross-References:**
- [Team Profiles](./profiles.md) - How profiles control agent and process behavior
- [Structure](./structure.md) - Complete team package directory organization
- [../security-permissions/overview.md](../security-permissions/overview.md) - Permission system details
