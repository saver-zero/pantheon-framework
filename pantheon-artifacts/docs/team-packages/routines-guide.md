---
doc_id: team-packages-routines-guide
title: "Routines Development Guide"
description: "Comprehensive guide to designing routine workflows including step sequences, cognitive guidance, conditional logic, and testing strategies."
keywords: [routines, workflows, process-workflows, step-sequences, cognitive-guidance, conditional-branching, routine-testing]
relevance: "Use this document to understand how to design routine workflows that guide agent execution through structured, step-by-step instructions."
---

# Routines Development Guide

Routines (`processes/*/routine.md`) define **HOW** to execute a specific process through structured, step-by-step instructions. They guide agent execution without defining agent capabilities or data validation rules.

## Process Architecture Context

A complete process consists of:

```
processes/<verb-noun>/
├── routine.md          # HOW: Step-by-step workflow instructions
├── schema.jsonnet      # WHAT DATA: Data contract and validation
├── permissions.jsonnet # WHO: Access control
└── artifact/           # Operation-specific files
```

**See also:** [Schemas Development Guide](./schemas-guide.md) for data contract specifications.

## Core Responsibility

**Primary Purpose:** Provide the procedural, step-by-step workflow for process execution.

**Key Principle:** Routines are **process-specific**. They contain concrete steps and tool commands for one particular workflow, not general agent capabilities or data contracts.

## Essential Routine Components

### 1. Process Objective

**Purpose:** Single-sentence statement of what the routine accomplishes

**Pattern:**
```markdown
# Process Name

**Objective:** [One sentence describing the process outcome]
```

**Example:**
```markdown
# Update Implementation Plan

**Objective:** Update the implementation plan section of an existing ticket with detailed steps and timeline.
```

### 2. Step Sequence

**Purpose:** Structured, sequential instructions for execution

**Pattern:**
```markdown
## Steps

Step 1. **Step Name:** Description of what to do. Use `pantheon command` if tool execution required.

Step 2. **Next Step:** Description of next action.

Step N (finish). **Final Step:** Description of completion action. You are now done.
```

**Example:**
```markdown
## Steps

Step 1. **Get schema:** Retrieve the data contract for plan updates. Use `pantheon get schema update-plan --actor <your_agent_name>`.

Step 2. **Generate plan content:** Create JSON data following the schema, including implementation steps, dependencies, and estimated effort.

Step 3. **Get temp file:** Obtain temporary file path for atomic operations. Use `pantheon get tempfile --process update-plan --actor <your_agent_name>`.

Step 4 (finish). **Execute update:** Submit the plan update. Use `pantheon execute update-plan --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

### 3. Cognitive Guidance (Optional)

**Purpose:** Guide agent reasoning for complex steps

**Pattern:**
```markdown
Step N. **Cognitive Task:** [Guidance on how to think about the task]
```

**Example:**
```markdown
Step 2. **Analyze Requirements:** Review the business context and technical constraints to understand the scope. Consider:
- What problem needs solving
- What existing systems are affected
- What technical approaches are viable
- What risks or dependencies exist
```

### 4. Conditional Logic (Optional)

**Purpose:** Branch execution based on conditions

**Pattern:**
```markdown
Step N (branch). **Decision Point:** Perform a branch condition check. [Condition description]:
- Branch N-1 Step 1. **Path Name:** If [condition], then [action]. Use `command`.
- Branch N-1 Step 2. **Continue:** [Next action in this path].
- Branch N-2 Step 1. **Alternate Path:** If [other condition], then [action].
- Branch N-2 Step 2 (finish). **Terminate:** [Final action]. You are now done.
```

## What Belongs in Routines

**YES - Workflow Steps:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema.

Step 3 (finish). **Submit ticket:** Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`.
```

**YES - Tool Commands:**
```markdown
Step 1. **Retrieve planning context:** Use `pantheon execute get-planning-context --actor <your_agent_name> --ticket {ticket_id}`.
```

**YES - Cognitive Guidance:**
```markdown
Step 2. **Design Implementation Approach:** Based on the technical context, outline the implementation strategy:
- Identify the core components affected
- Determine the sequence of changes
- Consider testing requirements
- Note any dependencies or blockers
```

**NO - Agent Capabilities:**
```markdown
<!-- WRONG: This belongs in agent definition -->
You are a backend engineer skilled in Python and FastAPI.
You prioritize test-driven development and code quality.
```

**NO - Data Contract Specifications:**
```markdown
<!-- WRONG: This belongs in schema.jsonnet -->
The title field must be a string with maximum 80 characters.
The business_context field is required and must be a non-empty string.
```

## Routine Structure Best Practices

### 1. One Instruction Per Step

**Bad:**
```markdown
Step 3. Generate JSON content and then get a temp file.
```

**Good:**
```markdown
Step 3. **Generate JSON content:** Create the full JSON object following the schema.

Step 4. **Get temp file:** Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.
```

### 2. Use Explicit Termination

**Bad:**
```markdown
Step 5. **Submit:** Use `pantheon execute create-ticket --from-file {tempfile}`.
```

**Good:**
```markdown
Step 5 (finish). **Submit:** Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

### 3. Include Tool Commands

**Bad:**
```markdown
Step 1. **Get the schema:** Retrieve the data contract.
```

**Good:**
```markdown
Step 1. **Get schema:** Retrieve the data contract. Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

## Dynamic Routines with Templates

Routines can use Jinja2 templates for dynamic content:

### Profile-Aware Instructions

```jinja2
{% if pantheon_profile.verbosity == 'detailed' %}
Step 2. **Comprehensive Analysis:** Perform detailed analysis including:
- Historical context review
- Stakeholder impact assessment
- Risk evaluation matrix
- Alternative approaches with trade-offs
{% else %}
Step 2. **Analysis:** Review key requirements and constraints.
{% endif %}
```

## Complete Routine Examples

### Example 1: CREATE Process

**Routine (routine.md):**
```markdown
# Create Ticket Process

**Objective:** Generate a new project ticket with structured business and technical context.

## Steps

Step 1. **Get schema:** Retrieve the data contract for ticket creation. Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated with relevant business and technical context.

Step 3. **Get temp file:** Obtain a temporary file path for atomic operations. Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.

Step 4 (finish). **Submit ticket:** Execute the ticket creation process. Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

### Example 2: UPDATE Process with Branching

**Routine (routine.md):**
```markdown
# Update Implementation Plan

**Objective:** Update the implementation plan section of an existing ticket with detailed steps and timeline.

## Steps

Step 1 (branch). **Check ticket availability:** Perform a branch condition check. Validate required ticket id:
- Branch 1-1 Step 1. **Continue:** If ticket id was provided, then get the schema. Use `pantheon get schema update-plan --actor <your_agent_name>`.
- Branch 1-1 Step 2. **Retrieve context:** Get planning context for the provided ticket. Use `pantheon execute get-planning-context --actor <your_agent_name> --ticket {ticket_id}`.
- Branch 1-2 Step 1. **Ask for ticket id:** If ticket id was not provided, then report to the user that a ticket id is required.
- Branch 1-2 Step 2 (finish). **Stop:** Explain that a ticket id is required before proceeding. You are now done.

Step 2. **Design Plan:** Create implementation plan with:
- Ordered implementation steps
- Dependencies and prerequisites
- Estimated effort for completion
- Potential risks or blockers

Step 3. **Generate JSON:** Create the full JSON object following the schema with your designed plan.

Step 4. **Get temp file:** Use `pantheon get tempfile --process update-plan --actor <your_agent_name>`.

Step 5 (finish). **Submit plan:** Use `pantheon execute update-plan --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

## Common Mistakes

### Mistake 1: Including Agent Persona in Routines

**Wrong:**
```markdown
# Create Ticket

You are a technical lead responsible for creating tickets.
You have expertise in project planning and task breakdown.

## Steps
...
```

**Correct:**
```markdown
# Create Ticket Process

**Objective:** Generate a new project ticket.

## Steps
...
```

### Mistake 2: Specifying Data Validation in Routines

**Wrong:**
```markdown
Step 2. **Generate JSON:** Create JSON with:
- title (string, max 80 characters)
- business_context (required string)
- technical_context (optional but recommended)
```

**Correct:**
```markdown
Step 2. **Generate JSON:** Create the full JSON object following the retrieved schema.
```

## Testing Routines

### Manual Testing

**View Routine:**
```bash
pantheon get process create-ticket --actor backend-engineer
```

**Verify Step Structure:**
- Check step numbering sequential
- Verify finish markers present
- Confirm tool commands correct

## Related Documentation

- **[Process Development Overview](./overview.md)** - Three-component architecture overview
- **[Schemas Development Guide](./schemas-guide.md)** - Data contract specifications
- **[Agents Guide](./agents.md)** - What belongs in agent definitions
- **[Decision Framework](./decision-framework.md)** - Choosing process types and patterns
- **[Anti-Patterns](../routine-system/anti-patterns.md)** - Common boundary violations to avoid

---

Routines define HOW to execute specific processes through structured workflows. By maintaining clear boundaries between workflow instructions, data contracts, and agent capabilities, routines enable reliable, transparent AI workflows that support the Glass Box philosophy.
