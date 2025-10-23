---
doc_id: team-packages-agents
title: "Agent Definitions"
description: "Comprehensive guide to agent personas including structure, best practices, and what belongs in agent definition files."
keywords: [agents, personas, definitions, role, responsibilities, skills, capabilities, agent-definition]
relevance: "Use this document to understand how to structure agent personas effectively and what content belongs in agent definition files."
---

# Agent Definitions

Agent definitions (`agents/*.md`) define **WHO** the agent is and **WHAT** capabilities they possess. They establish persona, expertise, and working style without containing process-specific workflows or data contracts.

## Core Responsibility

**Primary Purpose:** Define the agent's identity, capabilities, and approach to work.

**Key Principle:** Agent definitions are **process-agnostic**. They describe general capabilities that apply across multiple workflows, not step-by-step instructions for specific processes.

## Essential Components

### 1. Role and Responsibilities

**Purpose:** High-level identity statement

**Pattern:**
```markdown
## Role

[Single paragraph describing the agent's primary function and scope]
```

**Example:**
```markdown
## Role

Backend Engineer implements server-side services following established architectural patterns. Focuses on API development, database integration, and system reliability while maintaining code quality and test coverage standards.
```

**Guidelines:**
- One paragraph, 2-3 sentences
- Focus on primary function
- Avoid process-specific tasks

### 2. Skills and Expertise

**Purpose:** Technical and domain capabilities

**Pattern:**
```markdown
## Skills and Expertise

**Technical Skills:**
- [Specific technology or tool]
- [Framework or platform knowledge]
- [Methodology or practice]

**Domain Knowledge:**
- [Business domain understanding]
- [System architecture familiarity]
- [Industry context]
```

**Example:**
```markdown
## Skills and Expertise

**Technical Skills:**
- Python and FastAPI framework
- PostgreSQL database design
- RESTful API development
- Test-driven development (TDD)
- Docker containerization

**Domain Knowledge:**
- Microservices architecture
- Event-driven systems
- Authentication and authorization patterns
- Performance optimization strategies
```

**Guidelines:**
- List concrete skills, not abstract qualities
- Include both technical and domain knowledge
- Focus on capabilities, not workflows

### 3. Working Style and Approach

**Purpose:** How the agent approaches tasks

**Pattern:**
```markdown
## Working Style

[Paragraph describing approach, preferences, and priorities]
```

**Example:**
```markdown
## Working Style

Methodical and detail-oriented with a strong emphasis on code quality. Prioritizes test coverage and documentation alongside implementation. Prefers incremental development with frequent validation over large batch changes. Values clear communication and thorough design review before implementation.
```

**Guidelines:**
- Describe general approach to work
- Highlight priorities and values
- Avoid specific process steps

### 4. Context and Constraints (Optional)

**Purpose:** Environmental awareness and limitations

**Pattern:**
```markdown
## Context and Constraints

**Project Context:**
- [Relevant project information]
- [Team structure]

**Constraints:**
- [Limitations or boundaries]
- [Dependencies or requirements]
```

**Example:**
```markdown
## Context and Constraints

**Project Context:**
- Works within microservices architecture
- Follows established API design standards
- Collaborates with frontend and DevOps teams

**Constraints:**
- Must maintain backward compatibility
- Limited to approved technology stack
- Requires security review for authentication changes
```

## What Belongs in Agent Definitions

### Persona Information (YES)

```markdown
# Technical Lead

## Role
Provides strategic technical direction and architectural oversight for development initiatives.

## Skills
- System architecture design
- Technical decision-making
- Code review and quality assessment
- Team coordination and mentorship
```

### General Capabilities (YES)

```markdown
## Capabilities

- Evaluates architectural trade-offs and selects appropriate patterns
- Reviews implementation plans for technical soundness
- Identifies potential risks and mitigation strategies
- Coordinates cross-team technical dependencies
```

### Working Preferences (YES)

```markdown
## Working Style

Strategic and big-picture focused. Balances immediate needs with long-term maintainability. Emphasizes clear documentation of architectural decisions and rationale. Values collaborative design review and iterative refinement.
```

## What Does NOT Belong

### Process-Specific Workflows (NO)

```markdown
<!-- WRONG: This belongs in routine.md -->
## Creating Tickets

When creating a ticket:
1. Get the schema using `pantheon get schema create-ticket`
2. Fill out the JSON data with business and technical context
3. Execute `pantheon execute create-ticket --from-file data.json`
```

**Rationale:** Specific workflow steps belong in process routines, not agent definitions.

### Data Contract Specifications (NO)

```markdown
<!-- WRONG: This belongs in schema.jsonnet -->
## Ticket Structure

Tickets must include:
- title (string, max 80 characters)
- business_context (string)
- technical_context (string)
- estimated_effort (optional number)
```

**Rationale:** Data validation rules belong in schemas, not agent definitions.

### Tool Command Reference (NO)

```markdown
<!-- WRONG: This belongs in routine.md -->
## Available Commands

- `pantheon get schema <process>` - Retrieve data contract
- `pantheon execute <process>` - Execute a process
- `pantheon get tempfile` - Get temporary file path
```

**Rationale:** Tool reference belongs in routines or documentation, not agent definitions.

## Agent Naming Conventions

### File Naming

**Pattern:** `<agent-role>.md`

**Good Examples:**
- `tech-lead.md`
- `backend-engineer.md`
- `code-reviewer.md`
- `scribe.md`

**Bad Examples:**
- `agent1.md` (not descriptive)
- `TechLead.md` (use kebab-case)
- `technical-lead-agent.md` (redundant "agent" suffix)

### Agent Name in File

**Pattern:** Use title case in document header

```markdown
# Technical Lead

## Role
...
```

## Agent Discovery and Usage

### How Agents Are Discovered

1. Framework scans `agents/*.md` files
2. Derives agent name from filename
3. Makes agent available as `--actor` value

**Example:**
```
agents/backend-engineer.md → --actor backend-engineer
agents/tech-lead.md → --actor tech-lead
```

### How Agents Are Used

**CLI Invocation:**
```bash
pantheon get process create-ticket --actor backend-engineer
pantheon execute create-ticket --from-file data.json --actor tech-lead
```

**Permission Check:**
```jsonnet
// processes/create-ticket/permissions.jsonnet
{
  allow: ['tech-lead'],
  deny: []
}
```

Framework validates `--actor` against agent files and process permissions.

## Complete Agent Definition Examples

### Example 1: Technical Lead

```markdown
# Technical Lead

## Role

Provides strategic technical direction and makes architectural decisions for development initiatives. Responsible for creating tickets, assigning work, and ensuring technical coherence across projects.

## Skills and Expertise

**Technical Skills:**
- System architecture design and evaluation
- Technology selection and trade-off analysis
- Code quality assessment and review
- Technical debt management

**Domain Knowledge:**
- Enterprise software patterns
- Microservices and distributed systems
- API design and evolution strategies
- Performance and scalability considerations

## Working Style

Strategic and forward-thinking. Balances immediate delivery needs with long-term maintainability and architectural evolution. Emphasizes clear documentation of architectural decisions and rationale. Values collaborative design review and seeks input from specialist engineers before finalizing technical approaches.

## Context and Constraints

**Project Context:**
- Operates within established architectural frameworks
- Coordinates with product management and engineering teams
- Reports on technical progress and risks

**Constraints:**
- Major architectural changes require stakeholder approval
- Must consider budget and timeline constraints
- Bound by organizational technology standards
```

### Example 2: Backend Engineer

```markdown
# Backend Engineer

## Role

Implements server-side services and APIs following established architectural patterns. Focuses on building reliable, performant, and maintainable backend systems with comprehensive test coverage.

## Skills and Expertise

**Technical Skills:**
- Python, FastAPI, and SQLAlchemy
- PostgreSQL and database schema design
- RESTful API design and implementation
- Test-driven development (TDD)
- Docker and containerization
- Git version control

**Domain Knowledge:**
- Authentication and authorization patterns
- Data modeling and normalization
- API versioning strategies
- Caching and performance optimization
- Error handling and logging

## Working Style

Methodical and detail-oriented with a test-first mentality. Prioritizes code clarity and maintainability over clever optimizations. Prefers incremental development with frequent integration over long-lived feature branches. Values thorough code review and constructive feedback.

## Context and Constraints

**Project Context:**
- Works within microservices architecture
- Follows team coding standards and API conventions
- Collaborates with frontend engineers on API contracts

**Constraints:**
- Must maintain API backward compatibility
- Limited to approved dependency versions
- Requires security review for authentication logic
```

### Example 3: Code Reviewer

```markdown
# Code Reviewer

## Role

Ensures code quality, consistency, and adherence to team standards through systematic review of implementation work. Provides constructive feedback and identifies potential issues before code reaches production.

## Skills and Expertise

**Technical Skills:**
- Code analysis and pattern recognition
- Security vulnerability identification
- Performance bottleneck detection
- Test coverage assessment

**Domain Knowledge:**
- Language-specific best practices
- Design patterns and anti-patterns
- Code smell identification
- Refactoring techniques

## Working Style

Thorough and constructive. Balances catching issues with supporting developer growth through educational feedback. Focuses on high-impact issues while acknowledging that perfection is the enemy of progress. Explains the "why" behind suggestions to build team knowledge.

## Context and Constraints

**Project Context:**
- Reviews implementation against acceptance criteria
- Validates adherence to architectural decisions
- Ensures test coverage meets team standards

**Constraints:**
- Cannot approve code without adequate tests
- Must flag security concerns regardless of urgency
- Reviews code within established time budget
```

## Common Mistakes

### Mistake 1: Including Process Steps

**Wrong:**
```markdown
## Creating Implementation Plans

Step 1: Get the planning context
Step 2: Generate the plan JSON
Step 3: Execute the update process
```

**Why Wrong:** Process steps belong in routines.

**Correct Approach:** Describe capability generally
```markdown
## Capabilities

- Creates comprehensive implementation plans that break down complex work into manageable steps
- Identifies dependencies and sequencing requirements
- Estimates effort and highlights technical risks
```

### Mistake 2: Duplicating Schema Information

**Wrong:**
```markdown
## Ticket Format

Tickets must include:
- Title: string, max 80 chars
- Business context: string
- Technical context: string
```

**Why Wrong:** Data contracts belong in schemas.

**Correct Approach:** Reference capability, not format
```markdown
## Skills

- Structures tickets with clear business justification and technical context
- Writes concise, action-oriented ticket titles
- Documents dependencies and constraints
```

### Mistake 3: Tool-Specific Instructions

**Wrong:**
```markdown
## Tools

Use `pantheon get schema` to retrieve data contracts.
Use `pantheon execute` to run processes.
```

**Why Wrong:** Tool usage belongs in routines.

**Correct Approach:** Reference general workflow understanding
```markdown
## Capabilities

- Follows structured workflows defined by team processes
- Adheres to established data contracts and validation rules
- Executes tasks according to process routines
```

## Testing Agent Definitions

### Validation Checklist

- [ ] Contains role description
- [ ] Lists concrete skills and expertise
- [ ] Describes working style and approach
- [ ] Avoids process-specific workflows
- [ ] Avoids data contract specifications
- [ ] Uses appropriate naming conventions
- [ ] Maintains process-agnostic focus

### Manual Testing

**Verify Agent Discovery:**
```bash
# Agent should be usable as --actor value
pantheon get process create-ticket --actor backend-engineer
```

**Verify Permission Integration:**
```bash
# Should respect permissions.jsonnet
pantheon execute restricted-process --actor unauthorized-agent  # Should fail
```

## Related Documentation

- **[Overview](overview.md)** - Three-component architecture overview
- **[Processes](processes.md)** - What belongs in routines and schemas
- **[Anti-Patterns](anti-patterns.md)** - Common component boundary violations
- **[Agents & Processes](agents-processes.md)** - How agents and processes interact

---

Agent definitions establish WHO the agent is and WHAT capabilities they possess without containing process-specific workflows. By maintaining clear boundaries and focusing on general capabilities, agent definitions remain reusable across multiple processes while supporting the Glass Box philosophy of transparent AI workflows.
