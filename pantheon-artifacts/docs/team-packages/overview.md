---
doc_id: team-packages-overview
title: "Team Packages Overview"
description: "Introduction to Team Packages architecture including agents, processes, and the three-component model that separates persona, procedure, and contract."
keywords: [team-packages, overview, agents, processes, routines, schemas, architecture, separation-of-concerns, three-component-model]
relevance: "Use this document to understand the complete Team Packages architecture, including the three-component model and how agents, routines, and schemas work together."
---

# Team Packages Overview

A **Team Package** is a portable, version-controlled, and self-contained definition of an AI team. Team packages are the "applications" that run on the Pantheon Framework "operating system", containing all the components necessary to execute structured AI workflows.

## Team Package Structure

Team Packages are built on a **three-component model** that separates persona, procedure, and contract into distinct, orthogonal files. This separation of concerns enables independent evolution of each component while maintaining clear architectural boundaries.

### Core Components

```
pantheon-teams/<team_name>/
├── team-profile.yaml         # Central control panel
├── agents/                   # WHO: Agent personas
│   ├── tech-lead.md
│   └── backend-engineer.md
└── processes/                # WHAT and HOW: Workflows
    └── <verb-noun>/
        ├── routine.md        # HOW: Step-by-step instructions
        ├── schema.jsonnet    # WHAT DATA: Data contracts
        ├── permissions.jsonnet
        └── artifact/         # Operation-specific files
```

## The Three-Component Model

The three-component model separates concerns along two dimensions:

**Dimension 1: Responsibility (WHO / HOW / WHAT)**
- Agents = WHO performs the work
- Routines = HOW to perform the work
- Schemas = WHAT DATA is involved

**Dimension 2: Abstraction Level (Team / Process / Field)**
- Agents = TEAM level (highest abstraction) - How to operate in general across all processes
- Routines = PROCESS level (mid abstraction) - How to approach this specific workflow
- Schemas = FIELD level (lowest abstraction) - Individual data fields and constraints

This dual separation ensures clarity: each component has both a unique responsibility AND operates at a distinct level of abstraction.

### 1. Agent Definitions (agents/*.md)
**What:** Persona and capabilities
**Purpose:** Defines WHO the agent is and WHAT they can do
**Level:** TEAM level - General operating principles across all processes
**File Type:** Markdown
**Location:** `agents/<agent-name>.md`

**Contains:**
- Role and responsibilities
- Skills and expertise
- Working style and approach
- Context and constraints
- Team-wide behaviors and values

**Does NOT Contain:**
- Specific workflow steps (process level)
- Data contracts (field level)
- Process-specific instructions (process level)

**Example Content:**
```markdown
## Working Style
- Prioritizes business value and user impact
- Breaks complex problems into manageable tasks
- Communicates technical decisions with business justification
```

### 2. Routines (processes/*/routine.md)
**What:** Step-by-step workflow instructions
**Purpose:** Defines HOW to execute a specific process
**Level:** PROCESS level - Specific workflow approach for this operation
**File Type:** Markdown (optionally Jinja2 template)
**Location:** `processes/<process-name>/routine.md`

**Contains:**
- Structured step sequence
- Tool execution commands
- Cognitive guidance for THIS process
- Conditional logic and branching
- Thinking prompts relevant to this workflow

**Does NOT Contain:**
- Agent persona information (team level)
- Data validation rules (field level)
- Field-by-field enumeration (field level)

**Example Content:**
```markdown
Step 2. Generate JSON following the retrieved schema.

Think through:
- What business problem does this solve?
- What are the technical considerations?
```

### 3. Schemas (processes/*/schema.jsonnet)
**What:** Data contracts and validation rules
**Purpose:** Defines WHAT DATA is required for execution
**Level:** FIELD level - Individual field definitions and constraints
**File Type:** Jsonnet (compiles to JSON Schema)
**Location:** `processes/<process-name>/schema.jsonnet`

**Contains:**
- Property definitions
- Type specifications
- Validation constraints
- Field-level descriptions
- Profile-aware requirements

**Does NOT Contain:**
- Workflow steps (process level)
- Agent capabilities (team level)
- Execution procedures (process level)

**Example Content:**
```jsonnet
{
  properties: {
    title: {
      type: 'string',
      maxLength: 80,
      description: 'Brief, action-oriented ticket title'
    }
  }
}
```

### Abstraction Level Hierarchy

```
┌─────────────────────────────────────────────────┐
│ TEAM LEVEL (Agents)                             │
│ "How we operate across all work"                │
│ • General principles                             │
│ • Team values                                    │
│ • Cross-process behaviors                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ PROCESS LEVEL (Routines)                        │
│ "How to approach this specific workflow"        │
│ • Step sequence                                  │
│ • Tool commands                                  │
│ • Process-specific thinking                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ FIELD LEVEL (Schemas)                           │
│ "Individual data field definitions"             │
│ • Field types                                    │
│ • Validation rules                               │
│ • Field constraints                              │
└─────────────────────────────────────────────────┘
```

**Key Insight:** Never mix abstraction levels. If you find yourself describing individual fields in a routine, you've dropped from PROCESS level to FIELD level. If you find yourself describing team-wide behaviors in a routine, you've elevated from PROCESS level to TEAM level. Both violate separation of concerns.

## Component Interaction Model

### The RAE (Retrieval-Augmented Execution) Loop

```
1. User invokes process with --actor flag
   ↓
2. Framework validates agent exists (checks agents/*.md)
   ↓
3. Framework validates permissions (checks permissions.jsonnet)
   ↓
4. Agent requests routine (retrieves processes/*/routine.md)
   ↓
5. Routine instructs agent to get schema
   ↓
6. Agent requests schema (retrieves processes/*/schema.jsonnet)
   ↓
7. Agent prepares data conforming to schema
   ↓
8. Agent executes process with data
   ↓
9. Framework validates data against schema
   ↓
10. Framework executes process logic
```

### Why This Separation Matters

**Independent Evolution:**
- Change agent capabilities without modifying processes
- Update routines without changing schemas
- Refine validation without rewriting instructions

**Clear Responsibilities:**
- Agents focus on WHO and WHAT capabilities
- Routines focus on HOW to execute
- Schemas focus on WHAT DATA is required

**Reusability:**
- Multiple agents can execute the same process
- Processes can share common schemas
- Agents can have similar personas across teams

## Process Types

The framework uses a **Unified Execute Model** where process behavior is determined by the combination of files in the `artifact/` directory:

### CREATE Processes
- **File Combination**: `content.md` + `placement.jinja` + `naming.jinja`
- **Behavior**: Generates and saves new formatted artifacts to disk
- **Examples**: `create-ticket`, `create-document`, `create-architecture-doc`

### UPDATE Processes
- **File Combination**: `patch.md` + GET files + `target.jsonnet`
- **Behavior**: Locates existing artifacts and modifies specific sections
- **Examples**: `update-plan`, `update-ticket-status`, `update-code-review`

### GET Processes
- **File Combination**: `locator.jsonnet` + `parser.jsonnet` + `sections.jsonnet`
- **Behavior**: Finds and parses existing artifacts, returns structured JSON data
- **Examples**: `get-ticket`, `get-team-info`, `get-planning-context`

## Composition Patterns

### Multiple Agents, One Process

**Scenario:** Different agents with different skill sets execute the same process

**Structure:**
```
agents/
├── tech-lead.md           # Strategic planning focus
└── backend-engineer.md   # Implementation focus

processes/create-ticket/
├── routine.md            # Same workflow for both agents
├── schema.jsonnet        # Same data contract
└── permissions.jsonnet   # { allow: ['tech-lead', 'backend-engineer'] }
```

**Benefit:** Agents bring different perspectives to the same structured workflow.

### One Agent, Multiple Processes

**Scenario:** Single agent executes multiple related processes

**Structure:**
```
agents/
└── tech-lead.md          # Single agent definition

processes/
├── create-ticket/
│   ├── routine.md
│   └── schema.jsonnet
├── update-plan/
│   ├── routine.md
│   └── schema.jsonnet
└── review-code/
    ├── routine.md
    └── schema.jsonnet
```

**Benefit:** Agent capabilities defined once, applied to multiple workflows.

### Shared Schemas Across Processes

**Scenario:** UPDATE process reuses CREATE schema

**Structure:**
```
processes/create-ticket/
└── schema.jsonnet        # Canonical data contract

processes/update-ticket/
└── schema.jsonnet        # import "process-schema://create-ticket"
```

**Benefit:** Data contract consistency without duplication.

## Process Family Pattern

A **process family** is a set of related processes that operate on the same artifact type:

**Typical Family Structure:**
```
processes/
├── create-ticket/        # CREATE operation
│   ├── routine.md
│   ├── schema.jsonnet
│   └── artifact/
│       ├── content.md
│       ├── placement.jinja
│       └── naming.jinja
├── get-ticket/          # GET operation
│   ├── routine.md
│   └── artifact/
│       ├── locator.jsonnet
│       ├── parser.jsonnet
│       └── sections.jsonnet
└── update-plan/         # UPDATE operation
    ├── routine.md
    ├── schema.jsonnet
    └── artifact/
        ├── patch.md
        ├── locator.jsonnet    # import "artifact-locator://get-ticket"
        ├── parser.jsonnet     # import "artifact-parser://get-ticket"
        └── target.jsonnet     # import "artifact-sections://get-ticket?data=sections.plan"
```

**Family Characteristics:**
- Operate on same artifact type (tickets)
- Share artifact configuration (locators, parsers)
- May share schemas (UPDATE imports CREATE)
- All accessible to authorized agents

## Component Discovery

### Runtime Discovery via Convention

The framework discovers components automatically:

**Agent Discovery:**
- Scans `agents/*.md` files
- Derives agent names from filenames
- Makes agents available as `--actor` values

**Process Discovery:**
- Scans `processes/<verb-noun>/` directories
- Discovers process types from artifact files
- Registers processes for execution

**Schema Resolution:**
- Locates `schema.jsonnet` via convention
- Compiles Jsonnet to JSON Schema on demand
- No registration required

### No Manifests Required

Unlike traditional systems, Pantheon requires NO:
- Central process registry
- Agent registration files
- Schema catalogs
- Routing configuration

**Convention over Configuration** enables zero-config discovery.

## Profile-Driven Behavior

Team Packages use profiles to adapt behavior for different contexts (development, production, etc.):

**Profile Control Mechanisms:**
1. **Schema-Level Control**: Profiles inject external variables into Jsonnet schema compilation to show/hide fields dynamically
2. **Template-Level Control**: Templates render based on what data agents provide (data-driven rendering)

**Example:**
```jsonnet
// schema.jsonnet - Profile controls what fields exist
local verbosity = std.extVar('verbosity');

local baseSchema = {
  properties: {
    description: {
      type: 'string',
      description: if verbosity == 'detailed' then
        'Comprehensive description with edge cases and implementation details'
      else
        'Brief description of the change'
    }
  }
};
```

## Benefits of Three-Component Architecture

### 1. Separation of Concerns
Each component has single, well-defined responsibility

### 2. Independent Evolution
Components can be updated without cascading changes

### 3. Reusability
Agents, routines, and schemas can be reused across contexts

### 4. Testability
Each component can be tested in isolation

### 5. Clarity
Clear boundaries prevent component overlap and confusion

### 6. Maintainability
Changes are localized to appropriate component

## Related Documentation

- **[Agents](agents.md)** - Detailed guide to agent definition structure and best practices
- **[Processes](processes.md)** - Complete guide to routine and schema design
- **[Structure](structure.md)** - Full directory structure and file organization
- **[Profiles](profiles.md)** - Profile-driven behavior configuration
- **[Decision Framework](decision-framework.md)** - Choosing process types and build modes
- **[Anti-Patterns](anti-patterns.md)** - Common mistakes to avoid

---

The three-component model establishes clear boundaries between WHO (agents), HOW (routines), and WHAT DATA (schemas). This separation enables independent evolution, reusability, and testability while maintaining the Glass Box philosophy of transparent, auditable AI workflows.
