---
doc_id: process-components-anti-patterns
title: "Process Component Anti-Patterns"
description: "Common mistakes and boundary violations when structuring agents, routines, and schemas."
keywords: [anti-patterns, mistakes, boundaries, violations, agents, routines, schemas]
relevance: "Use this document to identify and avoid common mistakes when organizing process components across agents, routines, and schemas."
---

# Process Component Anti-Patterns

This document catalogs common mistakes and boundary violations when structuring Team Package components. Understanding these anti-patterns helps maintain clean separation of concerns and prevents component overlap.

## The Fundamental Anti-Pattern: Role Confusion

**The single most critical mistake in team package development is not understanding the distinct roles of agents, routines, and schemas, and placing similar or identical information in multiple places.**

### The Core Principle

**Remember: Two Dimensions of Separation**

**Dimension 1: Responsibility (WHO / HOW / WHAT)**
- **Agents define WHO** - Identity, capabilities, working style
- **Routines define HOW** - Sequential workflow steps and tool commands
- **Schemas define WHAT DATA** - Data contracts, validation rules, field definitions

**Dimension 2: Abstraction Level (Team / Process / Field)**
- **Agents = TEAM level** (highest) - How to operate in general across all processes
- **Routines = PROCESS level** (mid) - How to approach this specific workflow
- **Schemas = FIELD level** (lowest) - Individual data fields and constraints

**Examples of Each Level:**
- TEAM level: "Prioritize business value and user impact" (applies to all work)
- PROCESS level: "Think through: What business problem does this solve?" (specific to this workflow)
- FIELD level: "title: Brief, action-oriented ticket title (max 80 chars)" (individual field)

When you violate these boundaries, you create:
- **Information duplication** - Same content in multiple files
- **Maintenance nightmares** - Changes must be synchronized across files
- **Confusion** - Unclear single source of truth
- **Fragility** - Updates break because information is scattered
- **Abstraction violations** - Mixing team-level, process-level, and field-level concerns

### Quick Self-Check

Before adding content to any file, ask:

**Check 1: Responsibility (WHO / HOW / WHAT)**
1. **Is this about WHO performs the work?** → Agent file
2. **Is this about HOW to perform the work?** → Routine file
3. **Is this about WHAT DATA is involved?** → Schema file

**Check 2: Abstraction Level (Team / Process / Field)**
1. **Does this apply to ALL processes the agent performs?** → Agent file (TEAM level)
2. **Does this apply to THIS SPECIFIC workflow?** → Routine file (PROCESS level)
3. **Does this describe an INDIVIDUAL FIELD?** → Schema file (FIELD level)

**Red Flags:**
- Copying similar content between files → Role boundary violation
- Listing individual fields in a routine → Abstraction level violation (PROCESS → FIELD)
- Describing team-wide behaviors in a routine → Abstraction level violation (PROCESS → TEAM)
- Workflow steps in a schema → Abstraction level violation (FIELD → PROCESS)

### Common Symptoms of Role Confusion

**Responsibility Violations (WHO/HOW/WHAT):**
- Agent files contain step-by-step instructions (belongs in routines)
- Routine files contain validation rules (belongs in schemas)
- Schema files contain workflow guidance (belongs in routines)
- Same validation rules appear in both routines and schemas
- Agent capabilities are redefined in routine files
- Tool commands appear in agent definitions instead of routines

**Abstraction Level Violations (Team/Process/Field):**
- Routines enumerate individual fields one-by-one (FIELD level content in PROCESS level file)
- Routines describe team-wide values like "always prioritize quality" (TEAM level content in PROCESS level file)
- Schemas contain workflow instructions like "First do X, then Y" (PROCESS level content in FIELD level file)
- Agent files describe process-specific steps (PROCESS level content in TEAM level file)
- Agent files define specific field constraints (FIELD level content in TEAM level file)

### Impact

Role confusion is the root cause of most team package maintenance problems:
- **40-60% increase in maintenance effort** from synchronized updates
- **Higher error rates** from inconsistent information across files
- **Slower onboarding** because there's no clear place to find information
- **Process drift** as different files diverge over time

**Fix role confusion first.** All other anti-patterns are symptoms of this fundamental problem.

---

## Anti-Pattern Categories

1. **Boundary Violations:** Placing content in the wrong component
2. **Duplication:** Repeating information across components
3. **Over-Specification:** Including unnecessary implementation details
4. **Under-Specification:** Omitting essential information

## Boundary Violation Anti-Patterns

### Anti-Pattern: Process Steps in Agent Definitions

**Symptom:** Agent files contain specific workflow instructions

**Example (WRONG):**
```markdown
# Backend Engineer

## Role
Implements backend services.

## Creating Tickets

When creating a ticket:
1. Get the schema using `pantheon get schema create-ticket`
2. Fill out the JSON with business and technical context
3. Execute `pantheon execute create-ticket --from-file data.json`
```

**Why Wrong:**
- Workflow steps belong in routines, not agent definitions
- Agent definitions should be process-agnostic
- Changes to process require updating agent file

**Correct Approach:**
```markdown
# Backend Engineer (agents/backend-engineer.md)

## Role
Implements backend services following established patterns.

## Skills
- Task planning and breakdown
- Business context analysis
- Technical implementation design
```

```markdown
# Create Ticket Process (processes/create-ticket/routine.md)

Step 1. Get schema: Use `pantheon get schema create-ticket`
Step 2. Generate JSON: Create data following schema
Step 3 (finish). Submit: Use `pantheon execute create-ticket --from-file data.json`
```

### Anti-Pattern: Listing Schema Fields in Routines

**Symptom:** Routines enumerate individual fields and their constraints instead of guiding thinking

**Example (WRONG):**
```markdown
# Create Ticket Process

Step 2. **Generate JSON:** Create JSON with:
- title (string, max 80 characters)
- business_context (required string, min 20 characters)
- technical_context (string)
- priority (integer, 1-5)
- acceptance_criteria (array of strings)
- estimated_effort (string)

Make sure title starts with a capital letter.
Ensure business_context explains the business value.
Priority should reflect urgency.
```

**Why Wrong:**
- **Duplicates schema information** - Field types and constraints are already defined in schema
- **Creates maintenance burden** - When fields change, both schema AND routine must be updated
- **Violates DRY principle** - Single source of truth is broken
- **Misses the routine's purpose** - Should guide THINKING, not list fields
- **Brittle** - Adding/removing schema fields breaks routine instructions
- **Cognitive overload** - Forces agent to track field-level details instead of workflow

**What Happens When Schema Changes:**
If you add a new field `risk_assessment` to the schema, you must:
1. Update schema.jsonnet (correct place)
2. Update routine.md (unnecessary if done right)
3. Keep descriptions synchronized (error-prone)

**Correct Approach:**
```markdown
# Create Ticket Process (processes/create-ticket/routine.md)

Step 2. **Generate JSON:** Create the full JSON object following the retrieved schema.

Think through:
- What business problem does this solve?
- What are the technical considerations?
- What are the success criteria?
- What is the implementation approach?

The schema defines all required fields and validation rules.
```

**Schema Remains Single Source of Truth:**
```jsonnet
// processes/create-ticket/schema.jsonnet
{
  properties: {
    title: {
      type: 'string',
      maxLength: 80,
      pattern: '^[A-Z]',
      description: 'Brief, action-oriented ticket title'
    },
    business_context: {
      type: 'string',
      minLength: 20,
      description: 'Why this work is needed from business perspective'
    },
    technical_context: {
      type: 'string',
      description: 'Key technical considerations and implementation approach'
    },
    priority: {
      type: 'integer',
      minimum: 1,
      maximum: 5,
      description: 'Priority level from 1 (lowest) to 5 (highest)'
    }
  },
  required: ['title', 'business_context', 'priority']
}
```

**Key Principle:** Routines guide the THINKING PROCESS. Schemas define the DATA CONTRACT. When you find yourself listing fields in a routine, ask: "Am I duplicating the schema or guiding cognitive process?"

### Anti-Pattern: Agent Persona in Routines

**Symptom:** Routines define agent capabilities or identity

**Example (WRONG):**
```markdown
# Update Plan Process

You are a technical lead responsible for creating implementation plans.
You have expertise in task breakdown and effort estimation.

## Steps
...
```

**Why Wrong:**
- Agent persona belongs in agent definitions
- Routine should be agent-agnostic
- Multiple agents may execute same routine

**Correct Approach:**
```markdown
# Update Plan Process (processes/update-plan/routine.md)

**Objective:** Update implementation plan section with detailed steps.

## Steps
...
```

Agent personas stay in `agents/*.md` files.

### Anti-Pattern: Workflow Steps in Schemas

**Symptom:** Schema descriptions contain procedural instructions

**Example (WRONG):**
```jsonnet
{
  title: {
    type: 'string',
    description: 'First, ask the user for the task description. Then, create a brief title by extracting key words from their description. Capitalize the first letter.'
  }
}
```

**Why Wrong:**
- Schemas define data contracts, not workflows
- Procedural logic belongs in routines
- Violates separation of concerns

**Correct Approach:**
```jsonnet
// processes/create-ticket/schema.jsonnet
{
  title: {
    type: 'string',
    maxLength: 80,
    pattern: '^[A-Z]',
    description: 'Brief, action-oriented ticket title (capitalized, 10-80 characters)'
  }
}
```

Workflow guidance stays in routine.md.

## Duplication Anti-Patterns

### Anti-Pattern: Duplicating Schema Information

**Symptom:** Multiple processes define identical schemas

**Example (WRONG):**
```jsonnet
// processes/create-ticket/schema.jsonnet
{
  properties: {
    title: { type: 'string', maxLength: 80 },
    business_context: { type: 'string' }
  }
}

// processes/update-ticket/schema.jsonnet
{
  properties: {
    title: { type: 'string', maxLength: 80 },
    business_context: { type: 'string' }
  }
}
```

**Why Wrong:**
- Violates DRY principle
- Changes must be applied multiple times
- Risk of schema divergence

**Correct Approach:**
```jsonnet
// processes/update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

Use schema imports for consistency.

### Anti-Pattern: Duplicating Artifact Configuration

**Symptom:** UPDATE and GET processes have identical locator/parser files

**Example (WRONG):**
```jsonnet
// processes/get-ticket/artifact/locator.jsonnet
{
  directory: "tickets",
  pattern: "^T[0-9]{3}-.*\\.md$"
}

// processes/update-ticket/artifact/locator.jsonnet
{
  directory: "tickets",
  pattern: "^T[0-9]{3}-.*\\.md$"
}
```

**Why Wrong:**
- Duplicates artifact finding logic
- Changes must be synchronized manually
- Risk of inconsistent behavior

**Correct Approach:**
```jsonnet
// processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"

// processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

Reuse artifact configuration via imports.

### Anti-Pattern: Duplicating Section Templates

**Symptom:** CREATE and UPDATE have identical section content

**Example (WRONG):**
```jinja2
<!-- processes/create-ticket/artifact/content.md -->
## Implementation Plan
{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

<!-- processes/update-plan/artifact/sections/plan.md -->
## Implementation Plan
{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
```

**Why Wrong:**
- Duplicates template logic
- Changes must be synchronized
- Violates DRY principle

**Correct Approach:**
```jinja2
<!-- processes/create-ticket/artifact/content.md -->
{% include 'artifact-template://update-plan/sections/plan' %}
```

Include section templates from UPDATE process (single source of truth).

## Over-Specification Anti-Patterns

### Anti-Pattern: Implementation Code in Routines

**Symptom:** Routines contain code snippets or detailed algorithms

**Example (WRONG):**
```markdown
Step 3. **Parse JSON:** Use this Python code:
```python
import json
with open(tempfile, 'r') as f:
    data = json.loads(f.read())
title = data['title']
```
```

**Why Wrong:**
- Routines guide execution, don't implement
- Implementation details belong in framework/code
- Reduces portability across implementations

**Correct Approach:**
```markdown
Step 3. **Load JSON:** Read the generated JSON from the temp file.
```

Keep routines at instruction level, not implementation level.

### Anti-Pattern: Default Values for User Input

**Symptom:** Schemas provide defaults for fields agents should populate

**Example (WRONG):**
```jsonnet
{
  author: {
    type: 'string',
    default: 'unknown'
  },
  priority: {
    type: 'integer',
    default: 3
  }
}
```

**Why Wrong:**
- Agents should provide meaningful values
- Defaults hide missing data
- Framework injects `pantheon_actor` for authorship

**Correct Approach:**
```jsonnet
{
  author: {
    type: 'string',
    description: 'Agent identifier (automatically injected as pantheon_actor)'
  },
  priority: {
    type: 'integer',
    minimum: 1,
    maximum: 5,
    description: 'Priority level from 1 (lowest) to 5 (highest)'
  },
  required: ['priority']  // Make it required instead of defaulting
}
```

Use framework-injected variables instead of defaults.

### Anti-Pattern: Tool Reference Documentation in Agents

**Symptom:** Agent definitions list available CLI commands

**Example (WRONG):**
```markdown
# Backend Engineer

## Available Tools

- `pantheon get schema <process>` - Retrieve data contract
- `pantheon execute <process>` - Execute process
- `pantheon get tempfile` - Get temp file path
- `pantheon get process` - Get routine instructions
```

**Why Wrong:**
- Tool documentation belongs in framework docs
- Agent definitions should be capability-focused
- Routine provides tool commands when needed

**Correct Approach:**
```markdown
# Backend Engineer

## Capabilities

- Follows structured workflows defined by team processes
- Adheres to established data contracts
- Executes tasks according to process routines
- Validates work against schemas before submission
```

Reference capabilities, not tool commands.

## Under-Specification Anti-Patterns

### Anti-Pattern: Missing Field Descriptions

**Symptom:** Schema properties lack descriptions

**Example (WRONG):**
```jsonnet
{
  properties: {
    title: { type: 'string' },
    context: { type: 'string' },
    details: { type: 'string' }
  }
}
```

**Why Wrong:**
- Agents don't understand expected content
- Field purpose unclear
- Reduces data quality

**Correct Approach:**
```jsonnet
{
  properties: {
    title: {
      type: 'string',
      maxLength: 80,
      description: 'Brief, action-oriented ticket title'
    },
    business_context: {
      type: 'string',
      description: 'Why this work is needed from business perspective'
    },
    technical_context: {
      type: 'string',
      description: 'Key technical considerations and implementation approach'
    }
  }
}
```

Always provide clear, descriptive field descriptions.

### Anti-Pattern: Vague Step Instructions

**Symptom:** Routine steps lack specificity

**Example (WRONG):**
```markdown
Step 1. **Get ready:** Prepare for the task.
Step 2. **Do the work:** Complete the required work.
Step 3. **Finish up:** Wrap things up.
```

**Why Wrong:**
- Instructions too vague to execute
- No tool commands provided
- Ambiguous about what to do

**Correct Approach:**
```markdown
Step 1. **Get schema:** Retrieve the data contract. Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated.

Step 3 (finish). **Submit ticket:** Execute the ticket creation process. Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`.
```

Provide concrete, actionable instructions with tool commands.

### Anti-Pattern: Missing Agent Role

**Symptom:** Agent definitions lack clear role statement

**Example (WRONG):**
```markdown
# Backend Engineer

## Skills
- Python
- FastAPI
- PostgreSQL
```

**Why Wrong:**
- No context for agent's purpose
- Unclear when to use this agent
- Missing identity definition

**Correct Approach:**
```markdown
# Backend Engineer

## Role
Implements server-side services and APIs following established architectural patterns. Focuses on building reliable, performant backend systems with comprehensive test coverage.

## Skills
- Python and FastAPI framework
- PostgreSQL database design
- RESTful API development
```

Always start with clear role definition.

## Pattern Violation Detection

### Checklist for Agents

- [ ] Contains role description
- [ ] Lists skills and expertise
- [ ] Describes working style
- [ ] Does NOT contain process-specific steps
- [ ] Does NOT contain data validation rules
- [ ] Does NOT contain tool command reference

### Checklist for Routines

- [ ] States clear objective
- [ ] Provides sequential steps
- [ ] Includes tool commands
- [ ] Uses (finish) markers
- [ ] Does NOT contain agent persona
- [ ] Does NOT contain validation rules
- [ ] Does NOT contain implementation code

### Checklist for Schemas

- [ ] Defines property types
- [ ] Specifies required fields
- [ ] Provides field descriptions
- [ ] Includes validation constraints
- [ ] Does NOT contain workflow steps
- [ ] Does NOT contain agent capabilities
- [ ] Does NOT default user-provided values

## Refactoring Anti-Patterns

### Pattern: Extract Process Steps from Agent

**Before:**
```markdown
# Tech Lead (agents/tech-lead.md)

## Creating Tickets
1. Get schema
2. Generate JSON
3. Execute create
```

**After:**
```markdown
# Tech Lead (agents/tech-lead.md)

## Capabilities
- Creates well-structured tickets with business justification

# Create Ticket (processes/create-ticket/routine.md)

Step 1. Get schema: Use `pantheon get schema...`
Step 2. Generate JSON: Create data...
Step 3 (finish). Execute: Use `pantheon execute...`
```

### Pattern: Extract Validation from Routine

**Before:**
```markdown
# Create Ticket (routine.md)

Step 2. Generate JSON with:
- title (string, max 80 chars)
- context (required string)
```

**After:**
```markdown
# Create Ticket (routine.md)

Step 2. Generate JSON following the schema.

# Schema (schema.jsonnet)

{
  properties: {
    title: { type: 'string', maxLength: 80 },
    context: { type: 'string' }
  },
  required: ['context']
}
```

### Pattern: Consolidate Duplicate Schemas

**Before:**
```jsonnet
// create-ticket/schema.jsonnet
{ properties: { title: {...} } }

// update-ticket/schema.jsonnet
{ properties: { title: {...} } }
```

**After:**
```jsonnet
// create-ticket/schema.jsonnet
{ properties: { title: {...} } }

// update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

## Related Documentation

- [Process Components Overview](overview.md) - Three-component architecture
- [Agent Definition Role](agent-definition-role.md) - What belongs in agents
- [Routine Role](routine-role.md) - What belongs in routines
- [Schema Role](schema-role.md) - What belongs in schemas

---

Avoiding these anti-patterns maintains clean separation of concerns, enables component reuse, and supports the Glass Box philosophy of transparent, maintainable AI workflows. When in doubt, refer to the core principle: agents define WHO, routines define HOW, and schemas define WHAT DATA.
