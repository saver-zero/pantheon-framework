---
doc_id: routine-testing-validation
title: "Routine Testing and Validation"
description: "Methods and techniques for testing routine effectiveness and validating agent execution."
keywords: [testing, validation, routines, quality-assurance, verification]
relevance: "Use this document to learn how to test routine instructions for clarity, completeness, and execution reliability."
---

# Routine Testing and Validation

Testing routines ensures they provide clear, complete instructions that guide reliable agent execution. This document covers testing strategies and validation techniques.

## Testing Levels

### 1. Syntax Validation
**Purpose:** Verify routine structure conforms to standards

**Checks:**
- Sequential step numbering
- Proper (finish) markers
- Correct branch notation
- Complete tool commands
- Valid Jinja2 syntax (for templates)

**Manual Review:**
```bash
# Get routine content
pantheon get process create-ticket --actor test-agent

# Check:
# - Steps numbered 1, 2, 3 (not 1, 3, 5)
# - Final step has (finish) marker
# - Branches use "Branch X-Y" format
# - Tool commands include --actor flag
```

### 2. Completeness Validation
**Purpose:** Ensure all necessary information is present

**Checks:**
- Clear objective statement
- All required steps included
- Tool commands are complete
- Parameter placeholders identified
- Cognitive guidance provided for complex steps

**Review Checklist:**
- [ ] Objective clearly states process outcome
- [ ] Schema retrieval step included
- [ ] Data preparation guidance provided
- [ ] File operations specified (CREATE processes)
- [ ] Termination instruction clear

### 3. Execution Testing
**Purpose:** Verify routine guides successful execution

**Method:**
```bash
# Execute process following routine
pantheon get process create-ticket --actor test-agent

# Follow instructions step-by-step
# Note any ambiguities or missing information
# Verify process completes successfully
```

**Success Criteria:**
- Agent can complete all steps
- No ambiguous instructions encountered
- Tool commands execute successfully
- Expected output produced

## Validation Techniques

### Technique 1: Peer Review

**Process:**
1. Have another person read the routine
2. Ask them to explain what each step does
3. Identify unclear or ambiguous instructions
4. Note missing context or guidance

**Questions:**
- Can you execute this step without additional context?
- Is it clear what tool to use and why?
- Do you understand what data to prepare?
- Is the termination condition obvious?

### Technique 2: Dry Run Execution

**Process:**
1. Read routine without executing
2. Mentally simulate each step
3. Identify missing information
4. Note questions that arise

**Common Issues:**
- Missing parameter values
- Unclear file paths
- Ambiguous conditional logic
- Incomplete tool commands

### Technique 3: Agent Execution

**Process:**
```bash
# Real execution with test data
pantheon get process create-ticket --actor test-agent

# Follow routine exactly
# Document any issues:
# - Steps that failed
# - Ambiguous instructions
# - Missing information
# - Unclear guidance
```

**Metrics:**
- First-time success rate
- Number of clarifications needed
- Time to completion
- Output quality

## Common Issues

### Issue 1: Missing Tool Commands

**Symptom:**
```markdown
Step 1. **Get schema:** Retrieve the data contract.
```

**Problem:** No tool command provided

**Fix:**
```markdown
Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>`.
```

### Issue 2: Ambiguous Instructions

**Symptom:**
```markdown
Step 2. **Prepare data:** Get ready to create the JSON.
```

**Problem:** Unclear what "get ready" means

**Fix:**
```markdown
Step 2. **Generate JSON content:** Create the full JSON object following the retrieved schema.
```

### Issue 3: Missing Cognitive Guidance

**Symptom:**
```markdown
Step 3. **Design plan:** Create the implementation plan.
```

**Problem:** No guidance on how to approach design

**Fix:**
```markdown
Step 3. **Design Implementation Plan:** Break down the work:
- Identify components to modify
- Determine sequence of changes
- Consider dependencies
- Estimate effort for each step
```

### Issue 4: Incomplete Branching

**Symptom:**
```markdown
Step 1 (branch). **Check ID:**
- Branch 1-1. **Continue:** If ID provided...
- Branch 1-2. **Stop:** If ID missing...
```

**Problem:** Branch paths incomplete or unclear

**Fix:**
```markdown
Step 1 (branch). **Check ticket ID:** Validate required input:
- Branch 1-1 Step 1. **Continue:** If ticket ID provided, then get schema. Use `pantheon get schema update-plan`.
- Branch 1-2 Step 1 (finish). **Request ID:** If ID not provided, ask user for ticket ID. You are now done.
```

## Testing Checklist

### Pre-Release Validation

**Structure:**
- [ ] Objective statement present and clear
- [ ] Steps numbered sequentially
- [ ] Final step marked with (finish)
- [ ] Branch paths properly formatted
- [ ] No step numbering gaps

**Content:**
- [ ] All tool commands complete
- [ ] Actor flags included
- [ ] Parameter placeholders identified
- [ ] Cognitive guidance for complex steps
- [ ] No data validation in routine

**Execution:**
- [ ] Can be executed start to finish
- [ ] All steps clear and actionable
- [ ] No ambiguous instructions
- [ ] Produces expected output
- [ ] Terminates properly

### Post-Deployment Monitoring

**Track:**
- Success rate of process executions
- Common failure points
- Questions from agents
- Time to completion
- Output quality

**Review Regularly:**
- Execution logs
- Error reports
- Agent feedback
- Success metrics

## Testing Strategies

### Strategy 1: Unit Testing Steps

**Approach:** Test individual steps in isolation

**Example:**
```bash
# Test schema retrieval
pantheon get schema create-ticket --actor test-agent

# Verify output:
# - Valid JSON Schema returned
# - All expected properties present
# - Descriptions clear
```

### Strategy 2: Integration Testing

**Approach:** Test complete workflow end-to-end

**Example:**
```bash
# Follow complete routine
pantheon get process create-ticket --actor test-agent
# [Execute all steps]
pantheon execute create-ticket --from-file test-data.json --actor test-agent

# Verify:
# - Process completes successfully
# - Artifact created correctly
# - All sections present
```

### Strategy 3: Edge Case Testing

**Approach:** Test boundary conditions and error cases

**Examples:**
```bash
# Test missing required parameter
pantheon execute update-plan --actor test-agent  # No --id provided

# Test invalid data
pantheon execute create-ticket --from-file invalid.json --actor test-agent

# Test permission denial
pantheon execute admin-process --actor unauthorized-agent
```

## Continuous Improvement

### Feedback Collection

**Sources:**
- Agent execution logs
- User reports
- Error messages
- Success/failure metrics

**What to Track:**
- Most common failure points
- Unclear instructions
- Missing information
- Performance bottlenecks

### Iterative Refinement

**Process:**
1. **Collect feedback** from executions
2. **Identify patterns** in failures
3. **Update routine** to address issues
4. **Test changes** with real executions
5. **Deploy updates** and monitor

**Example Improvement:**
```markdown
# Original (causing confusion):
Step 2. **Create plan:** Make the implementation plan.

# Improved (after feedback):
Step 2. **Design Implementation Plan:** Break down the work into logical steps:
- Identify components to modify
- Determine sequence of changes
- Consider dependencies
- Estimate effort
```

## Automated Testing

### Schema Validation

**Test:** Routine references correct schema

```bash
# Verify schema exists
pantheon get schema create-ticket --actor test-agent

# Check routine mentions correct process name
pantheon get process create-ticket --actor test-agent | grep "create-ticket"
```

### Command Syntax Validation

**Test:** All tool commands are valid

```bash
# Extract commands from routine
# Verify each command format is correct
# Check all required flags present
```

### Completion Markers

**Test:** Routine has proper termination

```bash
# Verify routine contains (finish) marker
pantheon get process create-ticket --actor test-agent | grep "(finish)"
```

## Related Documentation

- [Authoring Practices](authoring-practices.md) - Best practices for writing routines
- [Structure and Syntax](structure-syntax.md) - Formal routine syntax
- [Anti-Patterns](anti-patterns.md) - Common mistakes to avoid

---

Testing and validation ensure routines provide clear, complete instructions for reliable agent execution. Regular testing and iterative refinement based on feedback creates high-quality routines that guide agents successfully through complex workflows.
