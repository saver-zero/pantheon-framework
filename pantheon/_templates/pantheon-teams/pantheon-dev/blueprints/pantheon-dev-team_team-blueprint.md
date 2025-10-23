<!--
## Welcome to Your Blueprint Journey

Think of this file as a shared workspace that you and the specialist agents shape together. Every time you collaborate with them, each section of the blueprint will be drafted in place of a `SECTION:PLACEHOLDER` tag. Move at your own pace, review the drafts they hand back, and keep iterating until the blueprint feels like it truly represents the team you have in mind.

### Phase 1: Shape the Blueprint Together (Iterative)

This phase is all about conversations and refinement. Each interaction gives the agents more context, and each revision brings the blueprint closer to what you need. For this phase, you need to refer to the blueprint using the blueprint ID (i.e TB123).

1.  **Set the Strategy & Context**
    -   **Who to chat with:** `@pantheon`
    -   **Try asking:** "`@pantheon`, create the strategy and context for a new team based on the workflow in `@docs/workflows/my-new-workflow.md`"
    -   The agent will help bring the `Overall Strategy` and `Project Context` sections to life. Review and provide feedback to @pantheon to make any updates, or make the updates yourself in the doc directly.

2.  **Design the Artifacts**
    -   **Who to chat with:** `@artifact-designer`
    -   **Try asking:** "`@artifact-designer`, design the artifacts for the team described in blueprint TB123
    -   The placeholders under `ARTIFACTS` will evolve into a detailed design you can react to. Review it and provide feedback to the @artifact-designer to make any updates, or make the updates yourself in the doc directly.

3.  **Design the Agents**
    -   **Who to chat with:** `@agent-designer`
    -   **Try asking:** "`@agent-designer`, design the agents for the blueprint TB123
    -   The agent architecture will gradually replace the `AGENTS` section as you iterate together. Review it and provide feedback to the @agent-designer to make any updates, or make the updates yourself in the doc directly.

4.  **Create the Team Readme**
    -   **Who to chat with:** `@team-readme-writer`
    -   **Try asking:** "`@team-readme-writer`, create the team readme for the blueprint TB123
    -   The team-readme-writer will create a team readme. Review and provide feedback to the readme writer to update any flows or usages you'd like to change. And point to the read me to have artifact-designer and agent-designer update their relevant sections of the blueprint.

5.  **Loop, Compare, Refine**
    -   Use what the `@agent-designer` creates to check whether the artifacts still make sense. If anything feels off, circle back to the `@artifact-designer` and explore a revised idea.

6.  **Finish with the Team Profile**
    -   **Who to chat with:** `@profile-designer`
    -   **Try asking:** "`@profile-designer`, design the team profile for the blueprint TB123
    -   Together you will turn the `PROFILE` placeholder into the configuration that ties everything together. Review it and provide feedback to the @profile-designer to make any updates, or make the updates yourself in the doc directly.
    -   You do not have to use or implement any of the profiles or configs, if you prefer to keep things simple. In that case, just delete the profiles and replace with "No profiles or configs needed".

### Phase 2: Bring the Blueprint to Life (Sequential)

Once the blueprint feels complete, you can use it as a script for creating the real team package. These steps happen in order so each piece has what it needs from the previous one. For this phase, you can refer to the blueprint using the full filename (i.e. [TB123]_my-new-team-blueprint.md])

1.  **Create the Team Profile**
    -   The profile carries shared configuration that other components lean on.
    -   Ask @profile-designer to create the team profile from @[TB123]_my-new-team-blueprint.md

2.  **Stand Up the Agents**
    -   Agents need to exist so the later processes know who they are empowering.
    -   For each agent described here, ask @agent-designer to create the agent from the blueprint.
    -   i.e @agent-designer create the planner agent from @[TB123]_my-new-team-blueprint.md
    -   Review it and provide feedback to the @agent-designer to make any updates, or make the updates yourself in the generated agent prompt directly.

3.  **Build the Artifacts & Processes**
    -   This step turns the blueprint’s core workflows into the files your team will actually run.
    -   For each artifact, request the @artifact-designer to build each artifact
    -   i.e @artifact-designer, build the master plan artifact from @[TB123]_my-new-team-blueprint.md
    -   Review it and provide feedback to the @artifact-designer to make any updates, or make the updates yourself in the generated processes and artifact schemas and templates directly.

When you’ve walked through these steps, the new team package is ready for its debut.
-->
<!-- SECTION:START:FOUNDATION -->

# TB24 - pantheon-dev Team Blueprint

## Team Foundation

**Team Name**: pantheon-dev

### Mission Statement

Provide a transparent, auditable, and continuously improving AI development workflow that serves as the default general-purpose team for day-to-day software development tasks under the Glass Box philosophy.

### Strategic Goals
- Demonstrate Glass Box philosophy implementation through fully transparent and auditable AI development workflows
- Establish systematic learning loops that continuously improve team processes based on structured feedback
- Provide profile-based adaptation supporting development contexts from rapid prototyping to production-ready code
- Maintain clear separation of concerns between AI automation and essential human oversight responsibilities

### Key Objectives
- Create comprehensive architecture guides that establish system overview, design patterns, and technical principles
- Generate structured development tickets with complete business context, technical implementation plans, and success criteria
- Implement systematic code review processes that capture lessons learned and maintain quality standards
- Collect and analyze user feedback to generate actionable improvement tickets for continuous team enhancement
- Support profile-based workflow adaptation enabling teams to optimize for specific project requirements

## System Boundary

### Pantheon Framework Responsibilities
- Generate structured tickets with business and technical context
- Create architecture guides and design decision documentation
- Produce code review reports with structured feedback
- Collect and analyze user feedback for continuous improvement
- Generate commit messages and progress logs
- Provide profile-based template adaptation

### Human Operator Responsibilities
- Execute actual code implementation following generated plans
- Run tests and validate functionality
- Commit code to version control systems
- Deploy applications to target environments
- Provide user feedback based on actual system usage
- Make final decisions on architecture guide approval

### High-Leverage Artifacts
- **architecture-guide**: Provides system overview, architecture philosophy, tech stack, and design patterns that establish technical foundation and reduce architectural uncertainty across all development work.
- **ticket**: Comprehensive development artifact containing architectural context, implementation plans, code reviews, and progress logs that ensure complete traceability from business requirements to implementation.
- **design-decision**: Structured logging of architectural decisions with context, alternatives, consequences, and rationale that prevents repeated debates and maintains institutional knowledge.
- **feedback-log**: Systematic collection of user feedback in structured format enabling data-driven continuous improvement and reducing subjective process changes.
- **retro-report** - Actionable improvement reports

### Critical Manual Checkpoints
- Review and approve architecture guides before implementation begins
- Execute code implementation following generated technical plans
- Run tests and verify functionality before marking tickets complete
- Commit code changes using generated commit messages after validation
- Validate that feedback accurately reflects actual user experience before logging
<!-- SECTION:END:FOUNDATION -->

<!-- SECTION:START:CONTEXT -->
## Project Context

The Pantheon Framework implements Retrieval-Augmented Execution (RAE) with a Glass Box philosophy to create transparent, auditable AI development workflows. The framework consists of two main parts: the Pantheon Framework (the 'OS') that orchestrates AI teams, and Team Packages (the 'applications') that are portable, version-controlled AI team definitions. The Pantheon Dev Team serves as the flagship implementation, demonstrating how structured AI workflows can replace ad-hoc interactions with systematic, transparent, and continuously improving processes that maintain human oversight while leveraging AI capabilities effectively.

### Key Concepts

**Glass Box Philosophy**: A development approach emphasizing transparency over opacity, mechanical reliability over prompt elegance, and systematic learning over ad-hoc fixes through fully visible and controllable workflows.

**Retrieval-Augmented Execution (RAE)**: An architectural pattern where AI agents retrieve structured processes, templates, and schemas before executing tasks, ensuring consistent and auditable behavior.

**Team Package**: A portable, version-controlled collection of agent definitions, processes, and templates that define a complete AI team's capabilities and workflows.

**Specialist Agent**: Domain-specific agents (e.g., backend-engineer, frontend-specialist) created by the pantheon agent to handle specific technical implementation areas.

**Systematic Learning Loop**: A feedback-driven improvement process where structured feedback is collected, analyzed, and used to generate actionable improvement tickets for team processes and agents.

**Profile-Based Adaptation**: Configuration system allowing teams to adapt behavior for different contexts (prototype, standard, production, custom) while maintaining consistent core workflows.


### Core Capabilities

- Create and manage structured development tickets with business and technical context
- Generate architecture guides and design decisions with comprehensive documentation
- Implement systematic code review processes with structured feedback collection
- Provide continuous improvement through feedback-driven retro cycles
- Support profile-based workflow adaptation for different development contexts
- Maintain transparent audit trails for all development decisions and processes

### Key Principles

- Transparency Over Opacity: Every workflow step is visible through routines, schemas, and templates
- Mechanical Reliability Over Prompt Elegance: Structured processes using JSON-to-template workflows prevent prompt drift
- Systematic Learning Over Ad-hoc Fixes: Version-controlled processes enable continuous improvement through structured feedback
- Human-in-the-Loop Control: Manual checkpoints ensure human oversight at critical decision points
- Profile-Based Flexibility: Adapt workflows for different contexts while maintaining core consistency
- Artifact-Centric Strategy: Focus on concrete deliverables that materially reduce ambiguity or rework

### References

- **docs/pantheon-framework/05-core-teams/pantheon-dev.md**: Comprehensive documentation of the Pantheon Dev Team including team philosophy, agent definitions, processes, profile configurations, and workflow examples. Serves as the primary reference for understanding Glass Box implementation.
<!-- SECTION:END:CONTEXT -->

<!-- SECTION:START:ARTIFACTS -->

## Artifact Design
updated_at: 2025-09-23 HH:MM PM PDT

### Process Architecture Overview

The Pantheon Dev Team implements a systematic learning loop through interconnected processes that capture feedback, analyze patterns, and generate actionable improvements. The architecture-guide and design-decision artifacts provide foundational technical guidance that supports all development work, while the feedback-log, retro-report, and ticket artifacts create a closed-loop system for continuous improvement. Architecture guides establish system foundations that reduce uncertainty across development work, design decisions maintain institutional knowledge to prevent repeated debates, and the existing feedback-driven processes ensure these foundational artifacts remain current and valuable through structured evolution.

### Core Artifacts

#### architecture-guide Artifact

**Purpose**: Provides system overview, architecture philosophy, tech stack, and design patterns that establish technical foundation and reduce architectural uncertainty across all development work.

**Build Mode**: `complete`

**Source Reference**: Referenced in TB24 foundation as 'Create comprehensive architecture guides that establish system overview, design patterns, and technical principles' and listed in High-Leverage Artifacts as 'architecture-guide: Provides system overview, architecture philosophy, tech stack, and design patterns that establish technical foundation and reduce architectural uncertainty across all development work.'

**Pantheon Commands**
- To get the instructions for creating architecture-guide, use `pantheon get process create-architecture-guide --actor <your_agent_name>`
- To get the instructions for updating system_overview section of architecture-guide, use `pantheon get process update-architecture-guide --id <architecture-guide id> --sections system_overview --actor <your_agent_name>`
- To get the instructions for updating architecture_philosophy section of architecture-guide, use `pantheon get process update-architecture-guide --id <architecture-guide id> --sections architecture_philosophy --actor <your_agent_name>`
- To get the instructions for updating tech_stack section of architecture-guide, use `pantheon get process update-architecture-guide --id <architecture-guide id> --sections tech_stack --actor <your_agent_name>`
- To get the instructions for updating design_patterns section of architecture-guide, use `pantheon get process update-architecture-guide --id <architecture-guide id> --sections design_patterns --actor <your_agent_name>`

**Sections**:
- **system_overview**: Provides high-level system architecture and component relationships to establish shared understanding of system structure..
- **architecture_philosophy**: Documents architectural principles and design philosophy to guide consistent decision-making across development work..
- **tech_stack**: Specifies technology choices, versions, and rationale to standardize development environment and tooling decisions..
- **design_patterns**: Catalogs approved design patterns and implementation approaches to promote consistent code structure and maintainability..

**Section Workflow**:
- **system_overview (create)**: Start with system overview to establish foundational understanding of architecture before diving into specifics.
- **architecture_philosophy (create)**: Define architectural principles after system overview to provide decision-making framework for detailed design.
- **tech_stack (create)**: Document technology choices after philosophy to ensure selections align with architectural principles.
- **design_patterns (create)**: Catalog design patterns last to show how principles and tech stack combine into concrete implementation approaches.
- **system_overview (review)**: Review system overview after other sections to ensure consistency and completeness of architectural documentation.

**Process Operations**:
- **CREATE**: Generates comprehensive architecture guide with system overview, principles, tech stack, and design patterns for new projects.
- **GET**: Retrieves existing architecture guide sections for reference during development and decision-making.
- **UPDATE**: Updates specific architecture guide sections as system evolves or new patterns emerge.

**External Inputs & Canonicalization**:
- System requirements and constraints - canonicalized through structured analysis that captures functional requirements, non-functional requirements, and system constraints in architecture guide format.
- Technology research and evaluation results - canonicalized through structured comparison that documents options, trade-offs, and selection rationale in tech stack section format.

**Manual Operator Actions**:
- Review and approve architecture guide before implementation begins to ensure technical foundation is sound.
- Validate technology choices against actual project constraints and update tech stack section as needed.
- Review design patterns periodically to ensure they remain current and effective for ongoing development.


#### design-decision Artifact

**Purpose**: Structured logging of architectural decisions with context, alternatives, consequences, and rationale that prevents repeated debates and maintains institutional knowledge.

**Build Mode**: `complete`

**Source Reference**: Referenced in TB24 foundation High-Leverage Artifacts as 'design-decision: Structured logging of architectural decisions with context, alternatives, consequences, and rationale that prevents repeated debates and maintains institutional knowledge.'

**Pantheon Commands**
- To get the instructions for creating design-decision, use `pantheon get process create-design-decision --actor <your_agent_name>`
- To get the instructions for updating decision_context section of design-decision, use `pantheon get process update-design-decision --id <design-decision id> --sections decision_context --actor <your_agent_name>`
- To get the instructions for updating decision_details section of design-decision, use `pantheon get process update-design-decision --id <design-decision id> --sections decision_details --actor <your_agent_name>`
- To get the instructions for updating alternatives_considered section of design-decision, use `pantheon get process update-design-decision --id <design-decision id> --sections alternatives_considered --actor <your_agent_name>`
- To get the instructions for updating consequences_and_rationale section of design-decision, use `pantheon get process update-design-decision --id <design-decision id> --sections consequences_and_rationale --actor <your_agent_name>`

**Sections**:
- **decision_context**: Captures the situation, problem, and driving forces that necessitated the architectural decision to provide future context..
- **decision_details**: Documents the specific decision made, key stakeholders involved, and decision date for clear accountability and traceability..
- **alternatives_considered**: Records alternative approaches evaluated with pros/cons analysis to prevent future re-litigation of settled decisions..
- **consequences_and_rationale**: Documents expected outcomes, trade-offs, and reasoning to enable future validation and inform related decisions..

**Section Workflow**:
- **decision_context (create)**: Start by capturing the context and driving forces to establish why a decision is needed before exploring options.
- **alternatives_considered (create)**: Document alternatives after context to show comprehensive evaluation of options within the established constraints.
- **decision_details (create)**: Record the specific decision after alternatives analysis to clearly document what was chosen and by whom.
- **consequences_and_rationale (create)**: Document rationale and expected consequences after decision to capture reasoning for future reference and validation.

**Process Operations**:
- **CREATE**: Generates structured decision record capturing context, alternatives, decision, and rationale for architectural choices.
- **GET**: Retrieves existing design decisions for reference during related architectural discussions and decision-making.

**External Inputs & Canonicalization**:
- Architectural decision triggers from development work - canonicalized through structured decision template that captures context, alternatives, and rationale in consistent format.

**Manual Operator Actions**:
- Identify architectural decision points during development that require structured documentation to prevent future debates.
- Validate decision consequences periodically against actual outcomes to improve future decision-making quality.


#### feedback-log Artifact

**Purpose**: Systematically captures user feedback in a structured format to enable data-driven analysis and continuous improvement of team processes and agent behavior.

**Build Mode**: `complete`

**Source Reference**: Referenced in the TB24 foundation document as 'Collect and analyze user feedback to generate actionable improvement tickets for continuous team enhancement' and 'feedback-log: Systematic collection of user feedback in structured format enabling data-driven continuous improvement and reducing subjective process changes.'

**Pantheon Commands**
- To get the instructions for creating feedback-log, use `pantheon get process create-feedback-log --actor <your_agent_name>`

**Sections**:
- **metadata**: Captures timestamp, target agent, feedback type, severity, and user sentiment for categorization and analysis..
- **situation_context**: Records the situation before the interaction and agent behavior to provide baseline context for feedback analysis..
- **user_feedback**: Documents the actual user feedback with code detection flag to enable comprehensive feedback analysis..
- **agent_response**: Captures what action the agent took after receiving feedback to track response patterns and effectiveness..

**Section Workflow**:
- **metadata (create)**: First populate metadata fields to establish the feedback context and categorization for analysis.
- **situation_context (create)**: Document the baseline situation and agent behavior before feedback to enable comparative analysis.
- **user_feedback (create)**: Record the actual user feedback with code detection to capture the core improvement signal.
- **agent_response (create)**: Document agent actions taken after feedback to track response patterns and measure improvement effectiveness.

**Process Operations**:
- **CREATE**: Generates a new structured feedback log entry for systematic analysis and improvement tracking.
- **GET**: Retrieves existing feedback logs for analysis and retro report generation.

**External Inputs & Canonicalization**:
- User feedback from direct interaction - canonicalized by structured collection form that captures feedback type, severity, sentiment, and context before storage.

**Manual Operator Actions**:
- Validate that feedback accurately reflects actual user experience before logging to ensure data quality.
- Review feedback logs periodically to identify patterns requiring retro analysis.


#### retro-report Artifact

**Purpose**: Analyzes feedback patterns and generates actionable improvement recommendations categorized by the four core action types: updating agent prompts, updating process routines, updating artifact schemas/templates, and updating documentation.

**Build Mode**: `complete`

**Source Reference**: Described in requirements as retro report artifact that designs around 4 core action item types: updating agent prompt, updating routine of a process, updating schema/template of artifact, and updating doc or diagram. Also referenced in foundation as 'retro-report - Actionable improvement reports'.

**Pantheon Commands**
- To get the instructions for creating retro-report, use `pantheon get process create-retro-report --actor <your_agent_name>`
- To get the instructions for updating analysis_summary section of retro-report, use `pantheon get process update-retro-report --id <retro-report id> --sections analysis_summary --actor <your_agent_name>`
- To get the instructions for updating agent_improvements section of retro-report, use `pantheon get process update-retro-report --id <retro-report id> --sections agent_improvements --actor <your_agent_name>`
- To get the instructions for updating process_improvements section of retro-report, use `pantheon get process update-retro-report --id <retro-report id> --sections process_improvements --actor <your_agent_name>`
- To get the instructions for updating artifact_improvements section of retro-report, use `pantheon get process update-retro-report --id <retro-report id> --sections artifact_improvements --actor <your_agent_name>`
- To get the instructions for updating documentation_improvements section of retro-report, use `pantheon get process update-retro-report --id <retro-report id> --sections documentation_improvements --actor <your_agent_name>`

**Sections**:
- **analysis_summary**: Provides high-level patterns identified from feedback analysis and overall team performance assessment..
- **agent_improvements**: Lists specific agent prompt updates needed based on feedback patterns and behavioral issues identified..
- **process_improvements**: Identifies process routine updates required to address workflow inefficiencies or gaps discovered through feedback..
- **artifact_improvements**: Specifies artifact schema and template updates needed to capture missing information or improve structure based on usage patterns..
- **documentation_improvements**: Documents updates needed for guides, diagrams, or reference materials to address knowledge gaps or confusion points..

**Section Workflow**:
- **analysis_summary (create)**: Start with high-level pattern analysis to establish the overall context and scope of improvements needed.
- **agent_improvements (create)**: Identify agent-specific improvements first as they often drive downstream process and artifact changes.
- **process_improvements (create)**: Document process routine updates that address workflow issues identified in the analysis.
- **artifact_improvements (create)**: Specify artifact changes needed to support improved processes and capture better structured data.
- **documentation_improvements (create)**: Finally capture documentation updates that support all other improvements and knowledge transfer.

**Process Operations**:
- **CREATE**: Generates a comprehensive retro report analyzing feedback patterns and providing categorized improvement recommendations.
- **GET**: Retrieves existing retro reports for tracking improvement implementation progress and pattern analysis.

**External Inputs & Canonicalization**:
- Feedback log data - canonicalized through GET operations on feedback-log artifacts to ensure structured analysis of consistent data format.

**Manual Operator Actions**:
- Review retro report recommendations and prioritize improvements based on impact and effort assessment.
- Create tickets for approved improvement items to ensure systematic implementation tracking.


#### ticket Artifact

**Purpose**: Provides comprehensive development artifact containing architectural context, implementation plans, code reviews, and progress logs to ensure complete traceability from business requirements to implementation.

**Build Mode**: `modular`

**Source Reference**: Referenced in the TB24 foundation as 'ticket: Comprehensive development artifact containing architectural context, implementation plans, code reviews, and progress logs that ensure complete traceability from business requirements to implementation' and 'Generate structured development tickets with complete business context, technical implementation plans, and success criteria'.

**Pantheon Commands**
- To get the instructions for creating ticket, use `pantheon get process create-ticket --actor <your_agent_name>`
- To get the instructions for updating description section of ticket, use `pantheon get process update-ticket --id <ticket id> --sections description --actor <your_agent_name>`
- To get the instructions for updating technical_plan section of ticket, use `pantheon get process update-ticket --id <ticket id> --sections technical_plan --actor <your_agent_name>`
- To get the instructions for updating progress_log section of ticket, use `pantheon get process update-ticket --id <ticket id> --sections progress_log --actor <your_agent_name>`
- To get the instructions for updating code_review section of ticket, use `pantheon get process update-ticket --id <ticket id> --sections code_review --actor <your_agent_name>`
- To get the instructions for updating commit_message section of ticket, use `pantheon get process update-ticket --id <ticket id> --sections commit_message --actor <your_agent_name>`

**Sections**:
- **description**: Captures ticket metadata, objective, architectural context, and acceptance criteria to establish complete requirements context..
- **technical_plan**: Documents phased implementation approach with technical analysis and step-by-step execution plan..
- **progress_log**: Tracks completed phases, remaining work, key decisions, and lessons learned throughout implementation..
- **code_review**: Provides structured code review findings with severity assessment and actionable recommendations..
- **commit_message**: Generates conventional commit message with proper formatting and traceability to ticket requirements..

**Section Workflow**:
- **description (create)**: Start with complete requirements definition including metadata, objectives, and acceptance criteria to establish work scope.
- **technical_plan (create)**: Develop detailed technical implementation plan with phased approach after requirements are established.
- **progress_log (update)**: Continuously update progress as phases complete to maintain implementation visibility and capture decisions.
- **code_review (create)**: Generate code review after implementation completion to validate quality and capture lessons learned.
- **commit_message (create)**: Finally create commit message based on completed work and review findings for proper version control integration.

**Process Operations**:
- **CREATE**: Generates a comprehensive development ticket with complete requirements, architectural context, and implementation planning.
- **GET**: Retrieves existing ticket information for progress tracking and context reference.
- **UPDATE**: Updates specific ticket sections like progress logs, code reviews, and commit messages as work progresses.

**External Inputs & Canonicalization**:
- Business requirements - canonicalized through structured requirement gathering that captures objectives, context, and acceptance criteria in ticket description format.
- Code implementation results - canonicalized through structured progress logging that captures decisions, lessons learned, and completion status.

**Manual Operator Actions**:
- Execute actual code implementation following generated technical plans.
- Run tests and validate functionality before marking phases complete.
- Commit code changes using generated commit messages after validation.
- Update progress logs with actual implementation decisions and lessons learned.



### Process Interactions

The architecture-guide and design-decision artifacts provide foundational technical guidance that supports all development work. Architecture guides flow to ticket CREATE process to provide architectural context for implementation planning. Design decisions flow to architecture-guide UPDATE process to maintain consistency with documented choices. The feedback-log CREATE process captures structured user feedback data which flows to retro-report CREATE process for pattern analysis. The retro-report generates improvement recommendations that flow to ticket CREATE process for systematic implementation, and may also trigger architecture-guide and design-decision updates. This creates a closed data loop where foundational guidance supports development while feedback drives continuous improvement through structured Pantheon artifacts.

### Operator Notes

Manual validation ensures both foundational guidance quality and implementation effectiveness. Operators must review and approve architecture guides before implementation begins, validate technology choices against project constraints, identify architectural decision points requiring structured documentation, execute actual code implementation following generated plans, validate functionality before committing changes, and prioritize retro recommendations based on business impact. These manual checkpoints maintain human oversight while leveraging AI-generated structure and analysis to establish sound technical foundations and accelerate improvement cycles.
<!-- SECTION:END:ARTIFACTS -->

<!-- SECTION:START:AGENTS -->

## Agent Architecture
updated_at: 2025-09-24 HH:MM AM PDT

### Team Composition

The Pantheon Dev Team operates through a focused set of six specialized agents that collaborate to create transparent, auditable development workflows. The pantheon agent serves as the intelligent orchestrator, creating specialist agents as needed and providing high-level business context to the architect. The architect prepares comprehensive technical foundations through architecture guides and design decisions, enhanced with PlantUML diagrams for visual system representation. The specialist agents (created by pantheon) handle domain-specific implementation planning within their expertise areas. The code-reviewer ensures quality through systematic code review processes. The retro agent drives continuous improvement through feedback pattern analysis. The scribe captures and structures all feedback interactions for systematic learning. This composition ensures complete coverage from business understanding through technical design to implementation tracking and systematic improvement, with clear handoffs between agent responsibilities and explicit manual operator checkpoints for code execution, validation, and decision approval.

### Agent Definitions

#### pantheon

**Role**: Serves as the intelligent orchestrator who understands business needs and creates specialist agents as needed while providing high-level context to the architect.

**Core Responsibilities**:
- Analyze business requirements and user problems to understand development needs
- Create specialist agents (backend-engineer, frontend-specialist, etc.) as needed for specific implementation areas
- Provide high-level business context and problem framing to the architect
- Coordinate initial project kick-off by establishing the right set of specialist agents
- Assess ongoing project needs and create additional specialist agents ad-hoc when required

**Key Capabilities**:
- Deep understanding of business requirements and user problem analysis
- Specialist agent creation and configuration based on project needs
- Business-to-technical context translation for effective architect collaboration
- Project scope assessment and agent team composition planning

**Pantheon Workflows**:
- **create-agent**: Generates new specialist agent definitions based on project requirements and technical domains needed.

**Manual Handoffs**:
- Operator validates business requirements analysis before specialist agent creation begins
- Operator approves specialist agent composition for project needs
- Operator confirms business context interpretation aligns with actual project goals


#### architect

**Role**: Prepares comprehensive technical foundations by creating architecture guides, design decisions, and PlantUML diagrams that establish system structure and institutional knowledge.

**Core Responsibilities**:
- Create architecture guides with system overview, principles, tech stack, and design patterns
- Generate design decision records with context, alternatives, and rationale
- Create high-level system diagrams using PlantUML to visualize architecture
- Establish technical foundations that reduce architectural uncertainty
- Maintain institutional knowledge to prevent repeated architectural debates

**Key Capabilities**:
- System architecture design and comprehensive documentation
- Technology stack evaluation and selection with rationale
- PlantUML diagram creation for system visualization and communication
- Design pattern cataloging and standardization
- Architectural decision logging with structured alternatives analysis

**Pantheon Workflows**:
- **create-architecture-guide**: Generates comprehensive architecture documentation with system overview, principles, and patterns.
- **create-design-decision**: Documents architectural decisions with context, alternatives, and consequences for institutional knowledge.

**Manual Handoffs**:
- Operator reviews and approves architecture guides before implementation begins
- Operator validates technology choices against actual project constraints and requirements
- Operator reviews PlantUML diagrams for accuracy and completeness of system representation


#### code-reviewer

**Role**: Ensures development quality through systematic code review processes with structured feedback collection and analysis.

**Core Responsibilities**:
- Conduct systematic code reviews with structured feedback collection
- Generate code review reports with severity assessment and actionable recommendations
- Analyze code quality patterns and identify improvement opportunities
- Maintain consistent code quality standards across development work

**Key Capabilities**:
- Systematic code review methodology and quality assessment
- Structured feedback generation with severity classification
- Code quality pattern recognition and analysis
- Best practices enforcement and recommendation generation

**Pantheon Workflows**:
- **update-ticket --sections code_review**: Generates structured code review with findings, severity assessment, and actionable recommendations.

**Manual Handoffs**:
- Operator executes actual code implementation following generated technical plans
- Operator runs tests and validates functionality before code review analysis
- Operator commits code changes after validating review recommendations


#### retro

**Role**: Drives continuous improvement by analyzing feedback patterns and generating actionable improvement recommendations across team processes and agents.

**Core Responsibilities**:
- Analyze feedback logs to identify patterns and improvement opportunities
- Generate retro reports with categorized improvement recommendations
- Track improvement implementation progress and effectiveness
- Drive systematic learning loops for continuous team enhancement

**Key Capabilities**:
- Feedback pattern analysis and trend identification
- Improvement recommendation generation across agent, process, and artifact categories
- Systematic learning loop design and implementation
- Data-driven process optimization and enhancement planning

**Pantheon Workflows**:
- **create-retro-report**: Analyzes feedback patterns and generates categorized improvement recommendations for systematic enhancement.

**Manual Handoffs**:
- Operator reviews retro recommendations and prioritizes improvements based on business impact
- Operator creates tickets for approved improvement items to ensure systematic implementation
- Operator validates improvement effectiveness through actual usage experience


#### scribe

**Role**: Captures and structures feedback interactions to enable systematic learning and continuous improvement through comprehensive feedback logging.

**Core Responsibilities**:
- Capture user feedback in structured format for systematic analysis
- Create feedback logs with proper categorization and metadata
- Maintain comprehensive feedback documentation for retro analysis
- Ensure feedback quality and consistency for effective pattern analysis

**Key Capabilities**:
- Structured feedback collection and categorization
- Comprehensive interaction documentation and logging
- Feedback quality assessment and validation
- Systematic data capture for continuous improvement analysis

**Pantheon Workflows**:
- **create-feedback-log**: Generates structured feedback entries with metadata, context, and analysis tags for systematic improvement.

**Manual Handoffs**:
- Operator validates that feedback accurately reflects actual user experience before logging
- Operator provides context for feedback situations to ensure proper categorization
- Operator confirms feedback interpretation aligns with actual interaction experience



<!-- SECTION:END:AGENTS -->

<!-- SECTION:START:PROFILE -->

## Team Profile Configuration
updated_at: 2025-09-28 HH:MM PM PDT

### Configuration Overview

The pantheon-dev team supports profile-based adaptation to balance development speed with process rigor across different project contexts. Five key properties control workflow enforcement: TDD requirements, documentation updates, diagram maintenance, commit message drafting, and progress logging, with lint tools configured per profile. The prototype profile prioritizes speed with minimal overhead, standard profile provides balanced rigor for typical development, and production profile ensures maximum quality assurance and transparency for critical systems.

### Configuration Properties

#### enforce_tdd

**Type**: boolean

**Description**: When true, requires the technical plan to include a dedicated testing phase as the first implementation step, mechanically enforcing Test-Driven Development practices.

**Options**:
- **true**: Require test-first implementation approach in technical plans
- **false**: Allow flexible testing approach without TDD enforcement

#### update_documentation

**Type**: boolean

**Description**: When true, requires the technical plan to include a documentation update phase specifying affected files and change summaries to prevent documentation drift.

**Options**:
- **true**: Require documentation updates in technical plans to prevent drift
- **false**: Skip documentation update requirements for faster development

#### update_diagram

**Type**: boolean

**Description**: When true, requires the technical plan to include diagram update requirements, ensuring architectural diagrams remain current with implementation changes.

**Options**:
- **true**: Require diagram updates when architectural changes are made
- **false**: Skip diagram update requirements for faster iteration

#### draft_commit_message

**Type**: boolean

**Description**: When true, requires each implementation phase to include commit message drafting requirements using the Pantheon tool to ensure proper message formatting.

**Options**:
- **true**: Include commit message drafting requirements in each phase
- **false**: Skip commit message drafting requirements

#### enable_progress_log

**Type**: boolean

**Description**: When true, requires each implementation phase to include progress logging requirements, ensuring transparent tracking of development progress and decisions.

**Options**:
- **true**: Include progress logging requirements in each implementation phase
- **false**: Skip progress logging requirements for faster execution


### Available Profiles

**Default Profile**: standard

#### prototype
- **profile_description**: Optimized for rapid prototyping and experimentation with minimal process overhead.
- **enforce_tdd**: false
- **update_documentation**: false
- **update_diagram**: false
- **lint_tools**: []
- **draft_commit_message**: false
- **enable_progress_log**: false

#### standard
- **profile_description**: Balanced development profile suitable for most development work with reasonable quality gates.
- **enforce_tdd**: true
- **update_documentation**: true
- **update_diagram**: false
- **lint_tools**: ['ruff check --fix', 'ruff format']
- **draft_commit_message**: true
- **enable_progress_log**: true

#### production
- **profile_description**: Maximum rigor profile ensuring comprehensive quality assurance and documentation for production systems.
- **enforce_tdd**: true
- **update_documentation**: true
- **update_diagram**: true
- **lint_tools**: ['ruff check --fix', 'ruff format', 'mypy --strict']
- **draft_commit_message**: true
- **enable_progress_log**: true


<!-- SECTION:END:PROFILE -->
