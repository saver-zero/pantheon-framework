---
doc_id: pantheon-dev-team
title: Pantheon Development Team Package
description: Complete documentation for the default pantheon-dev team including Glass Box philosophy, agent roster, core processes, profile system, workflow examples, and systematic learning loop for transparent software development
keywords: [pantheon-dev, default team, glass box, development workflow, tech-lead, backend-engineer, code-reviewer, scribe, retro, team profile, learning loop]
relevance: Essential reference for the primary Pantheon team package implementing Glass Box philosophy for day-to-day software development with transparent, auditable workflows
---
# Pantheon Development Team

The **Pantheon Development Team**, located at `pantheon-teams/pantheon-dev/`, is the primary manifestation of the **"Glass Box"** philosophy. It is the default, general-purpose team designed for day-to-day software development tasks and serves as the flagship example of transparent, auditable AI development workflows.

## Team Philosophy and Purpose

The Pantheon Development Team embodies the Glass Box philosophy through:

- **Deep Transparency:** Every development step is visible through structured routines, human-readable process definitions, comprehensive artifacts (architecture guides, design decisions, tickets, feedback logs, retro reports), and systematic progress tracking.
- **Systemic Learning Loop:** Team processes are version-controlled artifacts that improve continuously through structured feedback collection, retro analysis, and systematic enhancement. This solves the "almost right" problem at its root by making process improvement mechanical rather than ad-hoc.
- **Glass Box Operations:** All workflows are visible, controllable, and systematically improvable. From business context capture through specialist agent creation to code review and retrospective analysis, every step follows structured processes that can be audited, analyzed, and enhanced.
- **Business-to-Technical Translation:** The team bridges stakeholder intent and technical implementation through explicit artifacts that preserve context, rationale, and decisions throughout the development lifecycle.

The framework's RAE architecture enables this team to operate with mechanical reliability, systematic improvement, and complete transparency while maintaining human oversight at critical decision points.

## Team Agents

The Pantheon Development Team includes the following agents organized by their primary responsibilities:

### Core Management Agents

- **`pantheon-dev`**: The intelligent orchestrator who translates stakeholder intent into staffed agent teams. Creates domain-specific specialist agents (backend-engineer, frontend-specialist, devops-engineer, etc.) based on project technical requirements. Authors project kickoff tickets with rich business context, success criteria, and architectural foundation for the tech-lead. Maintains the business-context handshake with the tech lead by creating and updating tickets with comprehensive business objectives and acceptance boundaries.

- **`tech-lead`**: The delivery-minded technical lead who owns the architecture and backlog. Creates comprehensive architecture guides establishing system overview, principles, tech stack, and design patterns. Documents architectural decisions through structured design decision records. Creates PlantUML diagrams for system visualization. Translates business context into sequenced backlog with clear technical notes and dependencies.

### Quality and Process Agents

- **`code-reviewer`**: Ensures development quality through systematic code review with structured feedback collection. Conducts comprehensive reviews examining security, performance, maintainability, and architectural alignment. Generates structured feedback with severity classification, specific findings, and actionable recommendations. Identifies quality patterns and helps establish coding standards.

- **`retro`**: Drives continuous improvement by analyzing feedback patterns and generating actionable recommendations. Examines feedback logs to identify patterns and trends across team processes and agent performance. Generates specific improvement recommendations for process routine updates and artifact schema/template updates. Creates retro reports with analysis summary and categorized improvements for systematic implementation.

### Specialist Agents

- **`routine-designer`**: Expert in creating clear, effective step-by-step procedural guides following the RAE pattern. Designs routines using proper node types (node, branch, branchnode, branchfinishnode, finish) to create robust control flow. Balances cognitive steps for reasoning with tool steps for execution. Ensures all routines embody Glass Box principles with transparency, mechanical reliability, and systematic learning.

### Dynamically Created Specialists

The team composition adapts to project needs through specialist agents created by `pantheon-dev`:

- **Backend Engineers**: Handle server-side logic, APIs, and database integration
- **Frontend Specialists**: Focus on user interfaces, client-side interactions, and visual design
- **DevOps Engineers**: Manage infrastructure, deployment, and system reliability
- **Domain-Specific Specialists**: Created based on unique project requirements (mobile, ML, security, etc.)

Each specialist agent is configured with appropriate expertise, workflows following the mandatory RAE pattern (Get Instructions, Follow Instructions), and domain-specific competencies aligned with project technical requirements.

## Team Processes

The Pantheon Development Team provides comprehensive processes organized by functional area. All processes follow the RAE pattern where agents retrieve structured routines before execution.

### Agent and Team Management

- **`create-agent`**: Creates domain-specific specialist agents based on project technical requirements. Used by `pantheon-dev` to staff the team with appropriate expertise (backend-engineer, frontend-specialist, devops-engineer, etc.). Each agent is configured with specific competencies, workflows, and RAE-compliant operation protocols.

### Architecture and Design

- **`create-architecture-guide`**: Establishes comprehensive technical foundations with system overview, architecture principles, tech stack specifications, and design patterns. Used by `tech-lead` at project kickoff to reduce architectural uncertainty and guide consistent development decisions.

- **`get-architecture-guide`**: Retrieves existing architecture guide content, optionally filtered by sections (project_context, high-level-overview, core-principles, tech-stack, design-patterns). Enables agents to access architectural context for informed decision-making.

- **`update-architecture-guide`**: Modifies specific sections of the architecture guide as system architecture evolves, new patterns emerge, or technology choices need updates based on project experience.

- **`create-design-decision`**: Documents architectural decisions with structured format capturing context, alternatives considered, decision details, and consequences/rationale. Prevents repeated debates and maintains institutional knowledge.

- **`get-design-decision`**: Retrieves existing design decision records for reference during development planning and architectural discussions.

- **`update-design-decision`**: Updates design decisions to reflect new context, additional alternatives considered, or validation of consequences against actual outcomes.

- **`create-documentation`**: Creates documentation following established standards with proper metadata (doc_id, title, description, keywords, relevance) for optimal retrieval-friendliness. To keep documentation more flexible, the create-documentation process only has a routine to guide the agent to create the doc, without a schema or an artifact template.

### Ticket Management

- **`create-kickoff-ticket`**: Creates special project kickoff ticket for `tech-lead` to establish comprehensive architecture guide and initial backlog. Used by `pantheon-dev` during project initialization to provide rich business context and success criteria.

- **`create-ticket`**: Creates structured tickets with business context, technical foundation, and acceptance criteria. Used primarily by `tech-lead` and `pantheon-dev` to translate requirements into executable work items with clear objectives and architectural alignment.

- **`get-ticket`**: Retrieves ticket content, optionally filtered by sections (description, technical_plan, progress_log, code_review, commit_message, lessons_learned). Returns all non-empty sections if no sections specified.

- **`update-ticket`**: Modifies specific sections of existing tickets to update business context, technical plans, code reviews, commit messages, or lessons learned as work progresses and requirements evolve.

- **`update-kickoff-ticket`**: Updates the special kickoff ticket to reflect architecture guide progress, backlog refinement, or changes to project scope and priorities.

### Feedback and Learning Loop

- **`create-feedback-log`**: Creates structured feedback logs capturing user feedback with context, sentiment analysis, classification, and severity assessment. Used by the main LLM agent (not a dedicated scribe) to submit feedback during development workflows for continuous improvement analysis.

- **`get-feedback-log`**: Retrieves logged feedback for analysis by `retro` agent. Returns structured feedback data for pattern identification and improvement recommendation generation.

- **`create-retro-report`**: Generates comprehensive retrospective reports analyzing feedback patterns with categorized improvements for process routines and artifact templates. Used by `retro` agent to drive systematic team enhancement.

- **`get-retro-report`**: Retrieves existing retro reports for reference, follow-up analysis, or validation of improvement implementation effectiveness.

- **`update-retro-report`**: Updates retro reports to reflect additional feedback analysis, refinement of improvement recommendations, or validation of consequences against actual implementation experience.

### Routine Design

- **`create-custom-routine`**: Creates detailed, structured step-by-step process routines using proper RAE node types and control flow. Used by `routine-designer` to design new workflows that embody Glass Box principles with transparency and mechanical reliability.

*Note: The team focuses on planning and quality assurance. Actual code implementation is performed by human operators or the main LLM agent following generated technical plans. This separation ensures systematic planning while maintaining flexibility in execution.*

## Team Profile Configuration

The Pantheon Development Team uses a comprehensive profile system to adapt workflow rigor and quality gates for different development contexts. The active profile is configured in `team-profile.yaml` and influences process behavior through dynamic schema composition and template rendering.

### Available Profiles

The team provides four pre-configured profiles designed to be instantly understandable, each clearly stating its core philosophy and its position on the velocity vs. reliability spectrum.

#### Vibe-Coding
*   **Philosophy:** Go with the flow. This is for pure, unconstrained creation where the goal is to translate an idea into code as fast as possible. It prioritizes intuition and speed above all else.
*   **Use Case:** Rapid prototyping, brainstorming, scratchpad experiments, and work you intend to throw away.

```yaml
vibe-coding:
  profile_description: Optimized for rapid vibe coding. Auto commits and leaves a progress log, with no other checks
  enforce_tdd: false
  run_and_fix_tests: false
  perform_code_review: false
  draft_commit_message: true
  auto_commit_each_phase: true
  enable_progress_log: true
  read_documentation: false
  update_documentation: false
  update_diagram: false
  lint_tools: []
```

#### run-some-tests
*   **Philosophy:** Trust the agent to do good work, but verify it with automated checks. This profile balances speed with a crucial, non-blocking safety net.
*   **Use Case:** Standard day-to-day feature development. It's fast, but not reckless, relying on tests and linters to catch issues.

```yaml
run-some-tests:
  profile_description: Run some tests and read existing docs, along with progress logging and auto commits.
  enforce_tdd: false
  run_and_fix_tests: true
  perform_code_review: false
  draft_commit_message: true
  auto_commit_each_phase: true
  enable_progress_log: true
  read_documentation: true
  update_documentation: false
  update_diagram: false
  lint_tools: []
```

#### plan-and-review (Default)
*   **Philosophy:** A second pair of eyes prevents mistakes. This profile introduces mandatory planning (TDD) and review to ensure high quality for important changes.
*   **Use Case:** Core features, complex bug fixes, or any code that would benefit from collaborative review.

```yaml
plan-and-review:
  profile_description: Recommended profile for reliable long term execution with high quality planning and review. Enforces TDD, reads and keeps documentation updated, and keeps track of commit for code review.
  enforce_tdd: true
  run_and_fix_tests: true
  perform_code_review: true
  draft_commit_message: true
  auto_commit_each_phase: true
  enable_progress_log: true
  read_documentation: true
  update_documentation: true
  update_diagram: false
  lint_tools: []
```

#### Check-Everything
*   **Philosophy:** The code is only one part of the system. This profile enforces the highest level of rigor, ensuring that all surrounding documentation and architectural artifacts are kept perfectly in sync with the code.
*   **Use Case:** Mission-critical systems, public APIs, or foundational modules where long-term maintainability and a complete system record are paramount.

```yaml
check-everything:
  profile_description: Also updates diagrams for better visualization of the code and architecture. Recommended for complex systems, and easier review of the overall code flow via diagrams.
  enforce_tdd: true
  run_and_fix_tests: true
  perform_code_review: true
  draft_commit_message: true
  auto_commit_each_phase: true
  enable_progress_log: true
  read_documentation: true
  update_documentation: true
  update_diagram: true
  lint_tools: []
```

### Profile Configuration Options

Each profile supports the following configuration options:

- **`enforce_tdd`**: When `true`, requires technical plans to include a dedicated testing phase as the first implementation step, mechanically enforcing Test-Driven Development practices.

- **`run_and_fix_tests`**: When `true`, requires running tests and fixing failures as part of the implementation workflow.

- **`perform_code_review`**: When `true`, stores the baseline commit info for code review later.

- **`draft_commit_message`**: When `true`, requires each implementation phase to include commit message drafting using Pantheon tools for proper formatting, that can be copy-pasted manually or auto-commited.

- **`auto_commit_each_phase`**: When `true`, automatically commits code after each implementation phase. When `false`, requires manual operator to commit.

- **`enable_progress_log`**: When `true`, requires each implementation phase to include progress logging for transparent tracking of development decisions.

- **`read_documentation`**: When `true`, technical plans must include reading existing documentation to establish architectural context before implementation.

- **`update_documentation`**: When `true`, requires technical plans to include documentation update phases specifying affected files and change summaries to prevent documentation drift.

- **`update_diagram`**: When `true`, requires technical plans to include diagram update requirements, ensuring architectural diagrams remain current with implementation changes.

- **`lint_tools`**: Array of lint and formatting tools to include in technical plans for code quality enforcement (e.g., `ruff check --fix`, `ruff format`, `mypy --strict`).

### Profile Impact on Behavior

Profiles influence team behavior through multiple mechanisms:

**Process Schema Adaptation**: Profile settings inject into process schemas via `std.extVar('profile')` in Jsonnet, enabling conditional field requirements and validation rules based on active profile.

**Template Rendering**: Profile configuration affects template content through `pantheon_profile` variable, adjusting routine complexity, documentation verbosity, and required steps dynamically.

**Quality Gate Enforcement**: Profiles mechanically enforce quality standards by requiring specific phases in technical plans (testing, code review, documentation updates, diagram synchronization) based on configuration.

**Workflow Automation**: Profile settings control automation level from fully automated commits (prototype) to manual approval gates (production), balancing speed with oversight.

### Changing Active Profile

Update the `active_profile` setting in `team-profile.yaml` to switch between profiles:

```yaml
active_profile: plan-and-review  # Switch to production profile
```

All subsequent process executions will use the new profile's configuration until changed again.

## Workflow Examples

### Workflow Example 1: Project Kickoff

A complete project initialization workflow demonstrating business-to-technical translation:

**Step 1: Stakeholder Intake and Specialist Team Creation**
```bash
# pantheon-dev analyzes requirements and creates specialist agents
pantheon get process create-agent --actor pantheon-dev
# Creates backend-engineer specialist
pantheon execute create-agent --from-file backend-engineer.json --actor pantheon-dev
# Creates frontend-specialist
pantheon execute create-agent --from-file frontend-specialist.json --actor pantheon-dev
```

**Step 2: Kickoff Ticket Creation**
```bash
# pantheon-dev creates kickoff ticket with rich business context
pantheon get process create-kickoff-ticket --actor pantheon-dev
pantheon execute create-kickoff-ticket --from-file kickoff.json --actor pantheon-dev
# Output: Ticket K001 created with business objectives and success criteria
```

**Step 3: Architecture Foundation**
```bash
# tech-lead creates comprehensive architecture guide
pantheon get process create-architecture-guide --actor tech-lead
pantheon execute create-architecture-guide --from-file architecture.json --actor tech-lead
# Output: Architecture guide established with system overview, principles, tech stack
```

**Step 4: Initial Backlog Creation**
```bash
# tech-lead creates sequenced backlog tickets
pantheon execute create-ticket --from-file ticket-auth.json --actor tech-lead
pantheon execute create-ticket --from-file ticket-api.json --actor tech-lead
pantheon execute create-ticket --from-file ticket-ui.json --actor tech-lead
```

### Workflow Example 2: Ticket Development Lifecycle

A typical development workflow showing the complete ticket lifecycle:

**Step 1: Specialist Reviews Ticket Context**
```bash
# Specialist agent retrieves full ticket context
pantheon execute get-ticket --ticket T001 --actor backend-engineer
# Returns: Business context, architectural alignment, acceptance criteria
```

**Step 2: Specialist Creates Technical Plan**
```bash
# Specialist updates ticket with detailed technical plan
pantheon get process update-ticket --sections technical_plan --actor backend-engineer
pantheon execute update-ticket --from-file plan.json --actor backend-engineer
# Output: Technical plan with phased implementation, testing strategy, dependencies
```

**Step 3: Human Operator Implements Code via Agent of Choice**
```bash
# Agent follows technical plan
# Implements features according to phased approach
# Runs tests as specified in plan
```

**Step 4: Code Review**
```bash
# code-reviewer conducts systematic review
pantheon get process update-ticket --sections code_review --actor code-reviewer
pantheon execute update-ticket --from-file review.json --actor code-reviewer
# Output: Structured feedback with severity classification and recommendations
```

**Step 5: Commit and Document**
```bash
# Agent updates commit message based on work completed
pantheon execute update-ticket --sections commit_message --from-file commit.json --actor backend-engineer
# Operator commits code with generated message
```

**Step 6: Capture Learnings**
```bash
# Agent documents lessons learned
pantheon execute update-ticket --sections lessons_learned --from-file lessons.json --actor backend-engineer
```

### Workflow Example 3: Continuous Improvement Loop

The systematic learning workflow that drives team enhancement:

**Step 1: Feedback Collection During Development**
```bash
# Main LLM agent submits feedback when issues arise and human operator instructs it to log feedback
pantheon get process create-feedback-log --actor main-agent
# Output: Structured feedback log with context, sentiment, classification, severity
```

**Step 2: Periodic Retrospective Analysis**
```bash
# retro agent is instruccted to create a retro report
# retro analyzes patterns and generates improvement recommendations
pantheon get process create-retro-report --actor retro
# Output: Retro report with categorized improvements for routines and templates
```

**Step 3: Improvement Implementation**
```bash
# human operator uses appropriate agents (pantheon-dev, routine-designer, or the main LLM agent) to make improvements by
# updating/adding agents, updating schema, updating template, or updating a routine,
# either by leveraging pre-defined pantheon process, or by making direct edits to the relevant team package files (i.e routine.md, schema.json, content.md)
# this results in a concrente, permanent, systematic update to the process based on the feedback and retro
```

### Workflow Example 4: Architectural Decision Making

Documenting architectural decisions for institutional knowledge:

**Step 1: Capture Decision Context**
```bash
# tech-lead documents major architectural choice
pantheon get process create-design-decision --actor tech-lead
# Output: Design decision DD001 with context, alternatives, rationale
```

## Benefits of the Glass Box Approach

The Pantheon Development Team demonstrates the Glass Box philosophy's advantages through systematic, transparent, and continuously improving workflows:

### Deep Transparency

Every development step is visible, auditable, and understandable:

- **Structured Artifacts**: Architecture guides, design decisions, tickets, feedback logs, and retro reports create complete audit trails from business requirements through implementation.
- **Process Visibility**: All workflows follow explicit routines that can be inspected, validated, and understood by both humans and AI agents.
- **Context Preservation**: Business objectives, architectural rationale, and technical decisions are preserved in structured formats that prevent knowledge loss.
- **Progress Tracking**: Systematic progress logging provides real-time visibility into agent activities, decisions, and workflow execution.

### Systematic Learning and Improvement

The team improves mechanically through structured feedback loops:

- **Structured Feedback Collection**: Feedback logs capture context, sentiment, classification, and severity for systematic analysis rather than ad-hoc commentary.
- **Pattern-Based Analysis**: Retro agent identifies recurring issues, process inefficiencies, and improvement opportunities through data-driven examination of feedback patterns.
- **Actionable Recommendations**: Improvements target specific process routines and artifact templates, making enhancement systematic rather than theoretical.
- **Continuous Evolution**: Process definitions and quality gates evolve based on real-world usage, solving the "almost right" problem through version-controlled iteration.

See: [Learning Loop Activity Diagram](learning-loop-activity.puml)

### Quality Assurance Through Mechanical Reliability

Quality is enforced mechanically through structured processes and profiles:

- **Multi-Stage Reviews**: Code review processes with structured feedback ensure systematic quality assessment across security, performance, maintainability, and architectural alignment.
- **Profile-Based Quality Gates**: Team profiles mechanically enforce appropriate rigor levels (TDD, testing, documentation, diagram updates) based on development context.
- **Consistent Standards**: Structured templates and schemas ensure consistent quality across all artifacts regardless of which agent or human produces them.
- **Early Issue Detection**: Systematic planning and review phases catch problems during design rather than after implementation.

### Knowledge Preservation and Institutional Memory

Organizational knowledge persists as structured, queryable artifacts:

- **Version-Controlled Processes**: All team processes, routines, and templates are version-controlled, enabling rollback, comparison, and systematic improvement.
- **Architectural Decision Records**: Design decisions capture context, alternatives, and rationale, preventing repeated debates and maintaining institutional knowledge.
- **Reusable Templates**: Process templates codify proven workflows and best practices into reusable patterns that transcend individual contributors.
- **Retrieval-Friendly Documentation**: Architecture guides and design decisions use structured metadata for precise retrieval by both humans and AI agents.

### Business-Technical Alignment

The team maintains clear connections between business intent and technical implementation:

- **Context Handoffs**: Explicit artifacts (kickoff tickets, architecture guides, tickets) preserve business context through technical planning and implementation.
- **Traceability**: Every technical decision traces back to business objectives, acceptance criteria, and success measures through structured ticket sections.
- **Stakeholder Communication**: High-level artifacts (architecture guides, design decisions) provide stakeholder-accessible documentation of technical direction and trade-offs.
- **Adaptive Team Composition**: Specialist agent creation aligns team capabilities with project technical requirements while maintaining business context awareness.

### Human Oversight and Control

The Glass Box approach maintains human control at critical decision points:

- **Approval Gates**: Profile settings enable manual approval for commits, architectural changes, and major decisions based on risk tolerance.
- **Transparent Operations**: All agent actions follow visible routines, enabling human intervention when workflows deviate from expectations.
- **Systematic Escalation**: Structured error handling and feedback collection ensure problems surface to human operators for resolution.
- **Flexible Execution**: Human operators perform actual code implementation, maintaining creative control while benefiting from systematic planning and review.

The Pantheon Development Team demonstrates how the Glass Box philosophy transforms AI development from ad-hoc prompt engineering into a systematic, transparent, and continuously improving engineering discipline that maintains human oversight while leveraging AI capabilities for planning, review, and knowledge management.

---

**Next:** Learn about [Pantheon Team Builder](pantheon-team-builder-team.md) or explore [CLI Commands](../cli-interface/commands.md).