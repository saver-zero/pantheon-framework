---
doc_id: cli-usage-patterns
title: CLI Usage Patterns and Workflows
description: Practical examples demonstrating common CLI workflow patterns including agent planning, code review, feedback loops, and team management with step-by-step command sequences showing Glass Box philosophy in action
keywords: [usage examples, workflows, agent patterns, planning workflow, code review, feedback loop, team management, rae loop, process execution]
relevance: Essential practical guide showing real-world CLI usage patterns for agents executing processes through structured, transparent workflows
---

# CLI Usage Patterns and Workflows

This document provides practical examples of how agents and users interact with the Pantheon Framework to accomplish real development tasks. These examples demonstrate the Glass Box philosophy in action.

## Example 1: Planning Agent Creates Technical Plan

**Scenario:** A backend engineer has been assigned ticket "T004" and needs to create a detailed technical implementation plan.

### Step 1: Agent Gets Process Instructions (RAE Loop)

```bash
pantheon get process update-plan --actor backend-engineer
```

**Framework Returns the Routine:**
```markdown
Step 1 (branch). **Check ticket id availability:** Perform a branch condition check. Validate required ticket id:
    - Branch 1-1 Step 1. **Continue:** If ticket id was provided, get the schema needed for update-plan. Use `pantheon get schema update-plan --actor backend-engineer`.
    - Branch 1-2 Step 1 (terminate). **Ask for ticket id:** If ticket id was not provided, report to the user that a ticket id is required. You are now done, report back to the user.
Step 2. **Get planning context:** Retrieve planning context from the user provided ticket id. Use `pantheon execute get-planning-context --ticket T004 --actor backend-engineer`
Step 3. **Generate the JSON content:** Create the full JSON object in-memory, ensuring it strictly follows the retrieved schema.
Step 4. **Get temp file path:** Obtain absolute path for temporary JSON file creation to ensure atomic operations. Use `pantheon get tempfile --process update-plan --actor backend-engineer`
Step 5. **Write the JSON to the temp file:** Save the generated JSON content to the `{tempfile}`
Step 6 (terminate). **Submit implementation plan:** Execute file-based plan submission using the temporary file. Use `pantheon execute update-plan --from-file {tempfile} --actor backend-engineer`. You are now done, report back to the user.
```

### Step 2: Agent Follows the Routine Step-by-Step

```bash
# Step 1: Get the data contract
pantheon get schema update-plan --actor backend-engineer

# Step 2: Get context from existing ticket
pantheon execute get-planning-context --ticket T004 --actor backend-engineer

# Returns: JSON with business context, technical requirements, constraints, etc.

# Step 3: Agent analyzes the requirements and prepares JSON data structure

# Step 4: Get temporary file for atomic operations
pantheon get tempfile --process update-plan --actor backend-engineer
# Returns: /project/pantheon-artifacts/tmp/update-plan_456.json

# Step 5: Agent writes structured JSON to the temporary file

# Step 6: Submit the plan
pantheon execute update-plan --from-file /project/pantheon-artifacts/tmp/update-plan_456.json --actor backend-engineer
```

**Result:** A formatted technical plan is generated and saved to the appropriate location, with all sections properly structured and cross-referenced with the original ticket.

## Example 2: Tech Lead Creates Initial Project Ticket

**Scenario:** Starting a new feature that requires coordination across multiple team members.

### Agent Workflow

```bash
# 1. Get the process instructions
pantheon get process create-ticket --actor tech-lead

# 2. Get the schema to understand required data
pantheon get schema create-ticket --actor tech-lead

# 3. Gather project context (this might involve external research)

# 4. Prepare structured ticket data
pantheon get tempfile --process create-ticket --actor tech-lead

# 5. Create the initial ticket
pantheon execute create-ticket --from-file /tmp/ticket_789.json --actor tech-lead
```

**Generated Ticket Structure:**
```markdown
# T005: Implement User Authentication System

## Business Context
Enable secure user login and registration to support the upcoming premium features rollout...

## Technical Context
Current system uses session-based auth. Need to migrate to JWT tokens for API scalability...

## Acceptance Criteria
- [ ] User registration with email validation
- [ ] Secure password hashing (bcrypt)
- [ ] JWT token generation and validation
- [ ] Integration with existing user database

<!-- PANTHEON:SECTION:PLACEHOLDER -->
## Implementation Plan
(To be filled by assigned developer)

<!-- PANTHEON:SECTION:PLACEHOLDER -->
## Code Review
(To be filled after implementation)
```

## Example 3: Code Review Workflow

**Scenario:** After implementation, code needs to be reviewed and feedback provided.

### Reviewer Workflow

```bash
# 1. Get review process instructions
pantheon get process update-code-review --actor code-reviewer

# 2. Get current ticket state including implementation plan
pantheon execute get-ticket --ticket T005 --sections context,plan --actor code-reviewer

# 3. Review the actual code changes (external to Pantheon)

# 4. Prepare structured review feedback
pantheon get tempfile --process update-code-review --actor code-reviewer

# 5. Submit code review
pantheon execute update-code-review --from-file /tmp/review_123.json --actor code-reviewer
```

**Generated Review Section:**
```markdown
## Code Review

**Reviewer:** code-reviewer
**Date:** 2025-08-29 2:15 PM PDT
**Status:** Approved with Minor Issues

### Findings

#### Security - PASS
- Password hashing implementation using bcrypt is correct
- JWT secret properly stored in environment variables
- Input validation prevents SQL injection

#### Performance - MINOR ISSUES
- Database queries could benefit from connection pooling
- Consider adding caching layer for frequent token validations

#### Code Quality - PASS
- Functions are well-documented and follow team conventions
- Error handling is comprehensive and user-friendly
- Test coverage meets team standards (87%)

### Recommendations
1. Implement connection pooling in database layer
2. Add Redis cache for JWT token validation
3. Consider rate limiting for authentication endpoints

**Overall Assessment:** Code is production-ready with minor optimizations recommended.
```

## Example 4: Feedback Loop and Continuous Improvement

**Scenario:** User provides feedback on the development process that needs to be captured for systematic improvement.

### Feedback Collection

```bash
# 1. Scribe agent captures user feedback
pantheon get process submit-feedback --actor scribe

# 2. Structure and submit feedback
pantheon get tempfile --process submit-feedback --actor scribe
pantheon execute submit-feedback --from-file /tmp/feedback_456.json --actor scribe
```

### Retrospective Analysis

```bash
# 1. Retro agent analyzes collected feedback
pantheon get process create-agent-update-ticket --actor retro

# 2. Retrieve accumulated feedback
pantheon execute get-feedback --agent backend-engineer --actor retro

# 3. Create improvement tickets based on patterns
pantheon get tempfile --process create-agent-update-ticket --actor retro
pantheon execute create-agent-update-ticket --from-file /tmp/improvement_789.json --actor retro
```

**Generated Improvement Ticket:**
```markdown
# T006: Update Backend Engineer Agent - Improve Database Query Planning

## Retro Context
Analysis of 5 feedback entries shows consistent pattern: backend-engineer creates plans that don't consider database performance implications until code review stage.

## Recommended Changes
Update backend-engineer agent prompt to include database performance considerations during planning phase...

## Success Criteria
- Plans include database performance analysis
- Fewer database-related issues found during code review
- Reduced implementation rework due to performance concerns
```

## Example 5: Team Management and Agent Updates

**Scenario:** Based on retro feedback, the team needs to add a new specialist agent.

### Agent Creation Workflow

```bash
# 1. Pantheon agent gets instructions for agent management
pantheon get process update-agent-prompt --actor pantheon

# 2. Create new agent definition
pantheon get tempfile --process update-agent-prompt --actor pantheon

# 3. Add the new agent to the team
pantheon execute update-agent-prompt --from-file /tmp/new_agent_123.json --actor pantheon

# 4. Verify team composition
pantheon execute get-team-info --actor pantheon
```

## Example 6: Non-Destructive Section Updates

**Scenario:** Agent needs to append progress updates to existing ticket without losing historical data.

### Append Workflow

```bash
# 1. Get available sections to understand update targets
pantheon get sections update-progress --actor developer

# 2. Prepare progress update data
pantheon get tempfile --process update-progress --actor developer

# 3. Append new progress without replacing existing content
pantheon execute update-progress --actor developer --id T001 \
  --insert-mode append --from-file /tmp/progress_data.json
```

**Result:** New progress entries are added at the end of the existing progress section, preserving all historical updates.

### Prepend Workflow

```bash
# 1. Prepare changelog entry for latest release
pantheon get tempfile --process update-changelog --actor tech-lead

# 2. Prepend latest entry for immediate visibility
pantheon execute update-changelog --actor tech-lead --id T001 \
  --insert-mode prepend --from-file /tmp/changelog_entry.json
```

**Result:** Latest changelog entry appears at the top of the section, with older entries preserved below.

## Example 7: Build Process Family from Specification

**Scenario:** Team builder needs to scaffold a complete process family for a new artifact type.

### Build Workflow

```bash
# 1. Get build process instructions
pantheon get process build-team-process --actor pantheon

# 2. Get schema to understand build specification structure
pantheon get schema build-team-process --actor pantheon

# 3. Design the artifact structure and sections

# 4. Prepare build specification JSON
pantheon get tempfile --process build-team-process --actor pantheon

# 5. Execute build to generate process family
pantheon execute build-team-process --actor pantheon \
  --from-file /tmp/build_spec_123.json
```

**Generated Process Family:**
```
pantheon-artifacts/pantheon-team-builds/my-team/processes/
├── create-report/
│   ├── routine.md
│   ├── schema.jsonnet
│   ├── permissions.jsonnet
│   └── artifact/
│       ├── content.md
│       ├── placement.jinja
│       └── naming.jinja
├── get-report/
│   ├── routine.md
│   ├── permissions.jsonnet
│   └── artifact/
│       ├── locator.jsonnet
│       ├── parser.jsonnet
│       └── sections.jsonnet
└── update-report/
    ├── routine.md
    ├── schema.jsonnet
    ├── permissions.jsonnet
    └── artifact/
        ├── patch.md
        ├── target.jsonnet
        ├── locator.jsonnet
        └── parser.jsonnet
```

## Key Benefits Demonstrated

### Transparency
- Every step is visible and auditable
- Decision rationale is captured in structured format
- Process improvements are systematically tracked

### Consistency
- All agents follow the same structured approach
- Templates ensure uniform output quality
- Schemas prevent data inconsistencies

### Learning Loop
- Feedback is systematically collected and analyzed
- Improvements are implemented at the process level
- Benefits propagate to all future executions

### Accountability
- Actor identification enables full traceability
- Permissions ensure appropriate access control
- Error handling provides clear feedback

## Common Workflow Patterns

### The Standard RAE Loop

1. **Retrieve Instructions**: `pantheon get process <process-name>`
2. **Retrieve Schema**: `pantheon get schema <process-name>`
3. **Retrieve Context**: `pantheon execute get-<artifact> --id <id>`
4. **Prepare Data**: Agent creates structured JSON matching schema
5. **Get Temp File**: `pantheon get tempfile --process <process-name>`
6. **Execute Process**: `pantheon execute <process-name> --from-file <tempfile>`

### The Section-Aware Update Pattern

1. **List Sections**: `pantheon get sections <update-process>`
2. **Retrieve Current Content**: `pantheon execute get-<artifact> --sections <target-section>`
3. **Prepare Updates**: Agent creates update data
4. **Choose Insert Mode**: Decide between `replace` (default), `append`, or `prepend`
5. **Execute Update**: `pantheon execute <update-process> --insert-mode <mode>`

### The Team Data Management Pattern

1. **Check Current State**: `pantheon get team-data`
2. **Query Specific Keys**: `pantheon get team-data --key <path>`
3. **Prepare Updates**: Determine new values and deprecated keys
4. **Atomic Update**: `pantheon set team-data --set <key>=<value> --del <old-key>`

These examples show how the Pantheon Framework transforms ad-hoc AI interactions into a systematic, transparent, and continuously improving development workflow that maintains human oversight while leveraging AI capabilities effectively.
