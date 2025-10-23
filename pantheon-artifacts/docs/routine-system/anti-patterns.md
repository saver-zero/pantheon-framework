---
doc_id: routine-anti-patterns
title: "Routine Anti-Patterns"
description: "Common mistakes and bad practices to avoid when creating routine instructions."
keywords: [anti-patterns, mistakes, routines, bad-practices, errors]
relevance: "Use this document to identify and avoid common mistakes when writing routine instructions."
---

# Routine Anti-Patterns

This document catalogs common mistakes when creating routine instructions. Understanding these anti-patterns helps avoid pitfalls and create effective routines.

## Instruction Anti-Patterns

### Anti-Pattern: Multiple Instructions Per Step

**Symptom:** Steps combine multiple distinct actions

**Example:**
```markdown
Step 3. Generate the JSON content and then get a temp file and write the JSON to it.
```

**Why Wrong:**
- Unclear which action to do first
- Can't track progress granularly
- Harder to debug failures
- Violates single responsibility

**Correct:**
```markdown
Step 3. **Generate JSON:** Create the JSON object following the schema.

Step 4. **Get temp file:** Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.

Step 5. **Write JSON:** Save the JSON to the temp file.
```

### Anti-Pattern: Vague Instructions

**Symptom:** Steps lack specificity or actionable guidance

**Example:**
```markdown
Step 2. **Prepare:** Get ready to create the ticket.
```

**Why Wrong:**
- Unclear what "get ready" means
- No actionable guidance
- Agent doesn't know what to do

**Correct:**
```markdown
Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated with relevant context.
```

### Anti-Pattern: Missing Tool Commands

**Symptom:** Steps mention actions but don't provide commands

**Example:**
```markdown
Step 1. **Get schema:** Retrieve the data contract.
```

**Why Wrong:**
- Agent doesn't know which command to use
- Ambiguous about how to execute
- Reduces reliability

**Correct:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

### Anti-Pattern: Incomplete Tool Commands

**Symptom:** Commands missing required flags or parameters

**Example:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket`.
```

**Why Wrong:**
- Missing `--actor` flag
- Command will fail
- Forces agent to infer missing parameters

**Correct:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

## Cognitive Guidance Anti-Patterns

### Anti-Pattern: No Cognitive Guidance

**Symptom:** Complex tasks lack thinking framework

**Example:**
```markdown
Step 2. **Design plan:** Create the implementation plan.
```

**Why Wrong:**
- No guidance on how to approach task
- Agent may miss important considerations
- Inconsistent output quality

**Correct:**
```markdown
Step 2. **Design Implementation Plan:** Break down the work:
- Identify components to modify
- Determine sequence of changes
- Consider dependencies between steps
- Estimate effort for each step
- Note any risks or unknowns
```

### Anti-Pattern: Over-Prescriptive Guidance

**Symptom:** Instructions dictate exact outputs rather than thinking process

**Example:**
```markdown
Step 2. **Design plan:** Create exactly 5 steps. The first step must be "Analyze requirements". The second step must be "Design approach". Use only these exact phrases.
```

**Why Wrong:**
- Removes agent autonomy
- May not fit actual task
- Stifles appropriate reasoning
- Reduces quality

**Correct:**
```markdown
Step 2. **Design Implementation Plan:** Break down the work into logical phases:
- Start with analysis and design
- Define implementation steps
- Include validation checkpoints
- End with testing and deployment
```

## Structure Anti-Patterns

### Anti-Pattern: Missing Termination

**Symptom:** Final step lacks (finish) marker

**Example:**
```markdown
Step 5. **Submit:** Use `pantheon execute create-ticket --from-file {tempfile}`.
```

**Why Wrong:**
- Agent may continue unnecessarily
- Unclear when workflow is complete
- No explicit termination signal

**Correct:**
```markdown
Step 5 (finish). **Submit:** Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

### Anti-Pattern: Non-Sequential Numbering

**Symptom:** Step numbers skip or restart

**Example:**
```markdown
Step 1. **Get schema:** ...
Step 3. **Generate JSON:** ...  <!-- Missing step 2 -->
Step 4. **Submit:** ...
```

**Why Wrong:**
- Confusing to follow
- Suggests missing steps
- Breaks flow

**Correct:**
```markdown
Step 1. **Get schema:** ...
Step 2. **Generate JSON:** ...
Step 3. **Get temp file:** ...
Step 4. **Submit:** ...
```

### Anti-Pattern: Incomplete Branching

**Symptom:** Branch paths unclear or malformed

**Example:**
```markdown
Step 1 (branch). **Check ID:**
- If ID provided, continue
- If ID missing, stop
```

**Why Wrong:**
- Missing branch numbering
- No specific actions
- Unclear structure

**Correct:**
```markdown
Step 1 (branch). **Check ticket ID:** Validate required input:
- Branch 1-1 Step 1. **Continue:** If ticket ID provided, then get schema. Use `pantheon get schema update-plan --actor <your_agent_name>`.
- Branch 1-2 Step 1 (finish). **Request ID:** If ID not provided, ask user for ticket ID. You are now done.
```

## Boundary Violation Anti-Patterns

### Anti-Pattern: Data Validation in Routines

**Symptom:** Routine specifies field types and constraints

**Example:**
```markdown
Step 2. **Generate JSON:** Create JSON with:
- title (string, max 80 characters)
- business_context (required string)
- priority (integer, 1-5)
```

**Why Wrong:**
- Validation belongs in schemas
- Duplicates schema information
- Creates maintenance burden

**Correct:**
```markdown
Step 2. **Generate JSON:** Create the full JSON object following the retrieved schema.
```

### Anti-Pattern: Agent Persona in Routines

**Symptom:** Routine defines agent capabilities

**Example:**
```markdown
# Create Ticket Process

You are a technical lead skilled in project planning.

## Steps
...
```

**Why Wrong:**
- Agent persona belongs in agent definitions
- Routine should be agent-agnostic
- Violates separation of concerns

**Correct:**
```markdown
# Create Ticket Process

**Objective:** Generate a new project ticket.

## Steps
...
```

### Anti-Pattern: Implementation Code

**Symptom:** Routine contains code snippets

**Example:**
```markdown
Step 3. **Parse JSON:** Use this code:
```python
import json
data = json.loads(content)
```
```

**Why Wrong:**
- Routines guide execution, don't implement
- Implementation belongs in framework
- Reduces portability

**Correct:**
```markdown
Step 3. **Load JSON:** Read the generated JSON from the temp file for processing.
```

## Complexity Anti-Patterns

### Anti-Pattern: Cognitive Overload

**Symptom:** Single step requires multiple complex decisions

**Example:**
```markdown
Step 2. **Complete Analysis:** Analyze business context, evaluate technical approaches, identify risks, estimate effort, and create complete plan with testing strategy and rollback approach.
```

**Why Wrong:**
- Too many cognitive tasks
- Overwhelming complexity
- Reduced quality
- High error rate

**Correct:**
```markdown
Step 2. **Analyze Business Context:** Review business requirements and constraints.

Step 3. **Evaluate Technical Approaches:** Consider implementation options and trade-offs.

Step 4. **Identify Risks:** Document potential issues and mitigations.

Step 5. **Estimate Effort:** Provide time estimates for implementation.

Step 6. **Design Testing Strategy:** Define verification approach.
```

### Anti-Pattern: Nested Conditionals

**Symptom:** Multiple levels of conditional logic

**Example:**
```markdown
Step 1. If ID provided, check if valid, if valid check if permissions, if permissions check if file exists, if exists proceed...
```

**Why Wrong:**
- Extremely high cognitive load
- Error-prone
- Hard to follow
- Difficult to debug

**Correct:**
```markdown
Step 1 (branch). **Validate Prerequisites:** Check all required conditions:
- Branch 1-1 Step 1. **Proceed:** If all prerequisites met, get schema.
- Branch 1-2 Step 1 (finish). **Request Missing:** If any prerequisite not met, report which are missing. You are now done.
```

## Format Anti-Patterns

### Anti-Pattern: Missing Command Backticks

**Symptom:** Commands not formatted with backticks

**Example:**
```markdown
Step 1. Use pantheon get schema create-ticket --actor test-agent.
```

**Why Wrong:**
- Harder to identify as command
- Inconsistent formatting
- Reduces clarity

**Correct:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

### Anti-Pattern: Inconsistent Placeholders

**Symptom:** Different placeholder formats used

**Example:**
```markdown
Step 1. Use `pantheon get schema create-ticket --actor [agent]`.
Step 2. Use `pantheon execute create-ticket --actor $AGENT`.
Step 3. Use `pantheon get tempfile --actor AGENT_NAME`.
```

**Why Wrong:**
- Confusing placeholder format
- Inconsistent style
- Unclear substitution

**Correct:**
```markdown
Step 1. Use `pantheon get schema create-ticket --actor <your_agent_name>`.
Step 2. Use `pantheon execute create-ticket --actor <your_agent_name>`.
Step 3. Use `pantheon get tempfile --actor <your_agent_name>`.
```

## Template Anti-Patterns

### Anti-Pattern: Missing with context

**Symptom:** Template includes don't pass context

**Example:**
```jinja2
{% include 'routine/sections/analysis.md' %}
{# pantheon_routine_step not passed #}
```

**Why Wrong:**
- Step numbering breaks
- Variables not available
- Include can't function properly

**Correct:**
```jinja2
{% include 'routine/sections/analysis.md' with context %}
```

### Anti-Pattern: Hardcoded Step Numbers

**Symptom:** Template uses fixed numbers instead of variable

**Example:**
```jinja2
Step 1. **First Step:** ...
Step 2. **Second Step:** ...

{% include 'routine/sections/analysis.md' with context %}

Step 3. **Next Step:** ...  <!-- Wrong if include has steps -->
```

**Why Wrong:**
- Numbering breaks with includes
- Can't insert sections dynamically
- Maintenance nightmare

**Correct:**
```jinja2
{% set pantheon_routine_step = {'num': 1} %}

Step {{ pantheon_routine_step.num }}. **First Step:** ...
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}

{% include 'routine/sections/analysis.md' with context %}

Step {{ pantheon_routine_step.num }}. **Next Step:** ...
```

## Refactoring Anti-Patterns

### Pattern: Split Combined Steps

**Before:**
```markdown
Step 2. Get schema, generate JSON, and write to file.
```

**After:**
```markdown
Step 2. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 3. **Generate JSON:** Create JSON following schema.

Step 4. **Write to file:** Save JSON to temp file.
```

### Pattern: Add Cognitive Structure

**Before:**
```markdown
Step 2. **Design plan:** Create the implementation plan.
```

**After:**
```markdown
Step 2. **Design Implementation Plan:** Break down the work:
- Identify components to modify
- Determine sequence of changes
- Consider dependencies
- Estimate effort
```

### Pattern: Complete Tool Commands

**Before:**
```markdown
Step 1. Get the schema.
```

**After:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

## Related Documentation

- [Authoring Practices](authoring-practices.md) - Best practices for routines
- [Structure and Syntax](structure-syntax.md) - Formal routine structure
- [Cognitive Load Management](cognitive-load-management.md) - Managing complexity

---

Avoiding these anti-patterns creates clear, reliable routine instructions that guide effective agent execution. When in doubt, favor clarity, specificity, and proper structure over brevity or assumed knowledge.
