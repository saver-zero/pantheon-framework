---
doc_id: routine-authoring-practices
title: "Routine Authoring Best Practices"
description: "Comprehensive guide to writing effective, reliable routine instructions that guide LLM execution."
keywords: [routines, authoring, best-practices, instructions, workflows, design]
relevance: "Use this document to learn best practices for creating high-quality routine instructions that maximize agent execution reliability."
---

# Routine Authoring Best Practices

Writing effective routines is critical to reliable agent execution. This document compiles best practices for creating clear, unambiguous instructions that guide LLMs through complex workflows.

## Core Principles

### 1. One Instruction Per Step

**Principle:** Each step should represent a single, focused instruction.

**Bad:**
```markdown
Step 3. Generate JSON content and then get a temp file.
```

**Good:**
```markdown
Step 3. **Generate JSON content:** Create the full JSON object following the retrieved schema.

Step 4. **Get temp file:** Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.
```

**Rationale:**
- Single instruction reduces ambiguity
- Clear breakpoints for execution flow
- Easier debugging and validation

### 2. Separate Cognition from Action

**Principle:** Distinguish between thinking steps and doing steps.

**Bad:**
```markdown
Step 2. **Design and implement:** Think about the approach and then execute the command.
```

**Good:**
```markdown
Step 2. **Design Approach:** Outline the implementation strategy considering technical constraints and dependencies.

Step 3. **Implement:** Execute the implementation using the designed approach.
```

**Rationale:**
- Clear cognitive guidance
- Separates planning from execution
- Supports better decision-making

### 3. Guide the Chain of Thought

**Principle:** For complex tasks, break reasoning into logical substeps.

**Bad:**
```markdown
Step 2. **Analyze:** Analyze the requirements.
```

**Good:**
```markdown
Step 2. **Analyze Requirements:** Review the business context and technical constraints:
- What problem needs solving
- What existing systems are affected
- What technical approaches are viable
- What risks or dependencies exist
- What success criteria must be met
```

**Rationale:**
- Structured reasoning improves quality
- Reduces cognitive load
- Provides thinking framework

## Step Instruction Patterns

### Pattern: Tool Execution Step

**Template:**
```markdown
Step N. **Action Name:** Brief description of what the tool does. Use `pantheon command --flag value --actor <your_agent_name>`.
```

**Example:**
```markdown
Step 1. **Get schema:** Retrieve the data contract for ticket creation. Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

**Guidelines:**
- Start with action name in bold
- Provide brief context
- Include complete tool command
- Use placeholder `<your_agent_name>` for actor

### Pattern: Cognitive Step

**Template:**
```markdown
Step N. **Cognitive Task:** [Guidance on how to approach the task]
- [Specific consideration 1]
- [Specific consideration 2]
- [Specific consideration 3]
```

**Example:**
```markdown
Step 2. **Design Implementation Plan:** Break down the work into logical phases:
- Identify the components to modify
- Determine the sequence of changes
- Consider dependencies between steps
- Identify testing requirements
- Estimate effort for each phase
- Note any risks or unknowns
```

**Guidelines:**
- Provide thinking framework
- Use bullet points for substeps
- Focus on "how to think" not "what to output"
- Avoid prescribing specific content

### Pattern: Data Preparation Step

**Template:**
```markdown
Step N. **Prepare Data:** Create the [data structure] following the retrieved schema, ensuring all required fields are populated with [content guidance].
```

**Example:**
```markdown
Step 3. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated with relevant business context, technical implementation details, and estimated effort.
```

**Guidelines:**
- Reference schema for structure
- Provide content guidance
- Mention key field categories
- Avoid repeating validation rules

### Pattern: Termination Step

**Template:**
```markdown
Step N (finish). **Action Name:** [Final action description]. Use `pantheon command`. You are now done.
```

**Example:**
```markdown
Step 5 (finish). **Submit ticket:** Execute the ticket creation process. Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

**Guidelines:**
- Always mark with (finish)
- Include clear termination language
- Provide final tool command
- End with "You are now done"

## Branching and Conditional Logic

### Pattern: Simple Branch

**Template:**
```markdown
Step N (branch). **Decision Point:** Perform a branch condition check. [Condition description]:
- Branch N-1 Step 1. **Path Name:** If [condition], then [action]. Use `command`.
- Branch N-2 Step 1. **Alternate Path:** If [other condition], then [action].
- Branch N-2 Step 2 (finish). **Terminate:** [Final action]. You are now done.
```

**Example:**
```markdown
Step 1 (branch). **Check ticket availability:** Perform a branch condition check. Validate required ticket id:
- Branch 1-1 Step 1. **Continue:** If ticket id was provided, then get the schema. Use `pantheon get schema update-plan --actor <your_agent_name>`.
- Branch 1-2 Step 1. **Ask for ticket id:** If ticket id was not provided, then report to the user that a ticket id is required.
- Branch 1-2 Step 2 (finish). **Stop:** Explain that a ticket id is required. You are now done.
```

**Guidelines:**
- State condition clearly in branch description
- Use "If X, then Y" format for branchstartnode
- Number branches consistently (N-1, N-2, etc.)
- Terminate alternate paths explicitly

## Cognitive Guidance Techniques

### Technique: Structured Questioning

**Pattern:**
```markdown
Step N. **Task Name:** [Description]. Consider:
- [Question 1]?
- [Question 2]?
- [Question 3]?
```

**Example:**
```markdown
Step 2. **Evaluate Technical Approach:** Assess the implementation strategy:
- What are the core components affected?
- What is the optimal sequence of changes?
- What dependencies exist between components?
- What testing strategy will verify correctness?
- What risks could impact delivery?
```

### Technique: Decision Framework

**Pattern:**
```markdown
Step N. **Task Name:** [Description]. For each option:
1. Identify alternatives
2. Evaluate trade-offs
3. Select approach
4. Document rationale
```

**Example:**
```markdown
Step 3. **Select Architecture Pattern:** Choose the appropriate pattern:
1. List viable architectural patterns
2. Evaluate each against requirements (performance, maintainability, complexity)
3. Select the pattern that best balances trade-offs
4. Document why this pattern was chosen over alternatives
```

### Technique: Progressive Refinement

**Pattern:**
```markdown
Step N. **Task Name:** [Description]:
- Draft: [Initial version guidance]
- Review: [Self-review criteria]
- Refine: [Improvement guidance]
```

**Example:**
```markdown
Step 4. **Draft Implementation Plan:**
- Draft: Create initial plan with high-level steps
- Review: Check for missing dependencies, unclear steps, or unrealistic estimates
- Refine: Add detail, clarify ambiguous steps, adjust estimates based on review
```

## Command Formatting Best Practices

### 1. Include Complete Commands

**Bad:**
```markdown
Step 1. **Get schema:** Use the get schema command.
```

**Good:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

### 2. Use Placeholders Consistently

**Pattern:** `<your_agent_name>` for actor, `{variable_name}` for user-provided values

**Example:**
```markdown
Use `pantheon execute get-ticket --id {ticket_id} --actor <your_agent_name>`.
```

### 3. Format with Backticks

**Always use backticks for commands:**
```markdown
Use `pantheon get schema create-ticket`.
```

**Not:**
```markdown
Use pantheon get schema create-ticket.
```

### 4. Include Actor Flag

**Always specify the actor flag in commands:**
```markdown
Use `pantheon get process create-ticket --actor <your_agent_name>`.
```

## Step Numbering Best Practices

### 1. Sequential Numbering

**Use sequential step numbers:**
```markdown
Step 1. **First Step:** ...
Step 2. **Second Step:** ...
Step 3. **Third Step:** ...
```

**Not:**
```markdown
Step 1. **First Step:** ...
Step 3. **Third Step:** ...  <!-- Missing step 2 -->
```

### 2. Branch Numbering

**Use Branch X-Y format:**
```markdown
Step 2 (branch). **Check condition:**
- Branch 2-1 Step 1. **Path A:** ...
- Branch 2-1 Step 2. **Continue A:** ...
- Branch 2-2 Step 1. **Path B:** ...
- Branch 2-2 Step 2 (finish). **Terminate B:** ...
```

### 3. Dynamic Step Numbering in Templates

**Use pantheon_routine_step for templates:**
```jinja2
Step {{ pantheon_routine_step.num }}. **Step Name:** Description.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}
```

## Process Objectives

### Pattern: Clear Objective Statement

**Template:**
```markdown
# Process Name

**Objective:** [Single sentence describing the process outcome]
```

**Good:**
```markdown
# Update Implementation Plan

**Objective:** Update the implementation plan section of an existing ticket with detailed steps, dependencies, and timeline.
```

**Bad:**
```markdown
# Update Implementation Plan

This process updates plans.
```

**Guidelines:**
- One clear sentence
- Focus on outcome
- Mention key deliverables
- Avoid implementation details

## Common Pitfalls

### Pitfall 1: Vague Instructions

**Bad:**
```markdown
Step 2. **Do the work:** Complete the required work.
```

**Good:**
```markdown
Step 2. **Generate Implementation Steps:** Break down the work into specific, actionable steps with clear dependencies and acceptance criteria.
```

### Pitfall 2: Missing Tool Commands

**Bad:**
```markdown
Step 1. **Get the schema:** Retrieve the data contract.
```

**Good:**
```markdown
Step 1. **Get schema:** Retrieve the data contract. Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

### Pitfall 3: Combining Instructions

**Bad:**
```markdown
Step 3. **Generate JSON and get temp file:** Create the JSON and then get a temp file path.
```

**Good:**
```markdown
Step 3. **Generate JSON:** Create the full JSON object following the schema.

Step 4. **Get temp file:** Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.
```

### Pitfall 4: Missing Termination

**Bad:**
```markdown
Step 5. **Submit:** Use `pantheon execute create-ticket --from-file {tempfile}`.
```

**Good:**
```markdown
Step 5 (finish). **Submit:** Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

### Pitfall 5: Over-Specifying Data

**Bad:**
```markdown
Step 2. **Generate JSON:** Create JSON with:
- title (string, max 80 chars)
- business_context (required string)
- technical_context (optional string)
```

**Good:**
```markdown
Step 2. **Generate JSON:** Create the full JSON object following the retrieved schema.
```

**Rationale:** Data specifications belong in schemas, not routines.

## Testing Your Routines

### Manual Review Checklist

- [ ] Each step has single instruction
- [ ] Cognitive steps provide thinking framework
- [ ] Tool commands are complete and correct
- [ ] Termination steps marked with (finish)
- [ ] Step numbering is sequential
- [ ] Branch paths are properly structured
- [ ] Objective is clear and focused
- [ ] No data validation rules in routine
- [ ] No agent persona in routine

### Execution Testing

**Test with actual agent:**
```bash
# Get routine
pantheon get process create-ticket --actor test-agent

# Verify clarity and completeness
# Check for ambiguous instructions
# Validate tool commands are correct
```

**Test edge cases:**
```bash
# Test branch conditions
# Test missing required parameters
# Test section-specific execution
```

## Complete Example

```markdown
# Create Ticket Process

**Objective:** Generate a new project ticket with structured business and technical context.

## Steps

Step 1. **Get schema:** Retrieve the data contract for ticket creation. Use `pantheon get schema create-ticket --actor <your_agent_name>`.

Step 2. **Analyze Requirements:** Review the business need and technical landscape:
- What business problem needs solving?
- What technical systems are affected?
- What implementation approach is appropriate?
- What risks or dependencies exist?
- What success criteria define completion?

Step 3. **Generate JSON content:** Create the full JSON object following the retrieved schema, ensuring all required fields are populated with relevant business justification, technical implementation details, and effort estimation.

Step 4. **Get temp file:** Obtain a temporary file path for atomic operations. Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.

Step 5. **Write JSON to temp file:** Save the generated JSON content to the temp file path obtained in the previous step.

Step 6 (finish). **Submit ticket:** Execute the ticket creation process. Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done.
```

## Related Documentation

- [Routine System Philosophy](philosophy.md) - Understanding routine structure and syntax
- [Cognitive Load Management](cognitive-load-management.md) - Breaking down complex tasks
- [Routine Anti-Patterns](anti-patterns.md) - Common mistakes to avoid
- [Routines Development Guide](../team-packages/routines-guide.md) - What belongs in routines

---

Effective routine authoring combines clear instructions, cognitive guidance, and proper structure. By following these best practices, you create routines that reliably guide agent execution while maintaining clarity and maintainability.
