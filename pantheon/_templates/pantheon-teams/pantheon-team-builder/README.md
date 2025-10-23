---
created_at: 2025-10-13 HH:MM PM PDT
---
<!-- SECTION:START:OVERVIEW -->
# pantheon-team-builder Team

## Mission

The pantheon-team-builder is a meta-team that creates, configures, and documents new Pantheon team packages through a blueprint-driven design process.

## Value Proposition

Building a new AI team requires careful coordination of multiple components: agent personas, artifact schemas, process workflows, configuration profiles, and user documentation. The pantheon-team-builder eliminates guesswork by providing specialized agents who guide you through systematic team design, ensuring all components work together cohesively. You get complete, production-ready team packages with consistent quality and comprehensive documentation.

## Key Capabilities

- **Team Blueprint Design**: Create comprehensive team blueprints that define mission, context, artifacts, agents, and configuration before any implementation begins.
- **Artifact Scaffolding**: Generate complete artifact families with CREATE, GET, and UPDATE processes including schemas, templates, and permission controls.
- **Agent Implementation**: Create AI agent personas with clear roles, competencies, technical understanding, and RAE-compliant workflows.
- **Profile Configuration**: Design team profiles with properties that control schema validation and template rendering for different operational modes.
- **Routine Development**: Build structured step-by-step routines with cognitive guidance, branching logic, and proper control flow for reliable agent execution.
- **Documentation Generation**: Produce user-friendly README files that explain team capabilities, agent interactions, and workflow examples in accessible language.

## When to Use This Team

Use the pantheon-team-builder when you need to create a new Pantheon team package from scratch. This is ideal when you have a workflow or domain that requires specialized AI assistance with custom artifacts, processes, and agents. The team-builder works for any artifact-driven workflow across diverse domains-from software development (architecture decisions, code reviews, deployment planning) to content creation (blog writing, documentation, editorial workflows) to business processes (project planning, risk assessment, decision tracking).

<!-- SECTION:END:OVERVIEW -->

<!-- SECTION:START:GETTING_STARTED -->
## Getting Started

Ready to create your first Pantheon team? The process is straightforward and guided by specialized agents who handle all technical details. You'll start with a blueprint, refine the design with specialists, then implement components systematically.

Note that the team building process isn't meant to be a one-shot process. Rather, it's an **auditable** and **iterative** human-in-the-loop process, where you work with the Pantheon Team Builder agents to refine the team design and create the custom team you want. You can review each team blueprint design, make updates directly or give feedback to agents to update, until the team design is satisfactory before building the team.

### End-to-End Overview

Here's what the complete workflow looks like from idea to deployed team:

1. **Share your idea** with the pantheon-team-builder agent ("I need a team that manages blog posts with drafts, reviews, and publishing workflows")
2. **The agent creates a team blueprint** defining your team's mission, artifacts, agents, and configuration-all in a structured markdown document
3. **Refine the blueprint** by working with specialized agents (artifact-designer for artifacts, agent-designer for agent roles)
4. **Generate all components** by asking the agents to build artifacts/processes, create agents, and generate the team profile
5. **Review the staged output** in `pantheon-artifacts/pantheon-team-builds/<your-team>/` to ensure everything meets your requirements
6. **Deploy the team** by copying the generated files to `pantheon-teams/<your-team>/`
7. **Activate the team** by updating `.pantheon_project` to set the active team to your newly installed team

For Claude Code,
8. **Install agents for Claude Code** by copying the agent files to `.claude/agents/<your-team>/` (this makes the agents available as subagents in Claude Code), and restart Claude Code.

For OpenCode,
8. **Install agents for OpenCode** by copying the agent files to `.opencode/agent/<your-team>/` (this makes the agents available as subagents in OpenCode), and restart OpenCode. OpenCode's agent name follows the file name, so rename the agent definition file as needed.

That's it! Your custom team is now ready to use. You can start interacting with its agents and creating artifacts immediately.

### Prerequisites

- Pantheon Framework installed and initialized in your project
- Clear understanding of the workflow or domain your new team will handle
- Examples or descriptions of artifacts the team should produce
- Basic familiarity with the Pantheon CLI and agent interaction

### Model Configuration Note

When running in Claude Code, the pantheon-team-builder, artifact-designer, and agent-designer agents are configured to use **Claude Sonnet** as their default model.

However, for complex teams and workflows, Opus may provide superior performance for these agents due to:

1. **Complex reasoning requirements**: Blueprint design and artifact scaffolding require sophisticated architectural thinking and pattern recognition across multiple interconnected components.
2. **Schema and template generation**: Creating valid Jsonnet schemas and Jinja2 templates with proper syntax, error handling, and edge cases benefits from Opus's stronger code generation capabilities.
3. **Design consistency**: Maintaining coherent design patterns across agents, artifacts, and processes requires the deeper contextual understanding that Opus provides.

**Cost consideration**: Opus is more token-intensive from a pricing perspective. If performance is a concern, you can modify the agent configurations to use Opus instead. For most team creation workflows, Sonnet will produce good results. For complex teams, Opus may be better. You can modify the model to be sonnet/opus in the agent definition files.

### Your First Interaction

**Step 1: Create Your Team Blueprint**

Start by working with the pantheon-team-builder agent to create the initial blueprint. Describe your team's purpose, the artifacts it should produce, and the types of agents needed. The agent will ask clarifying questions and generate a comprehensive blueprint document.

Example:

```

You: 'pantheon-team-builder, I need a team that manages code reviews. It should create review artifacts with sections for findings, recommendations, and approval status.'

```

💡 **Tip**: Be specific about your workflow and the artifacts you envision, but don't worry about technical implementation details yet.

**Step 2: Refine Blueprint Sections**

Collaborate with specialized agents to refine specific blueprint sections. Work with artifact-designer on artifact definitions, agent-designer on agent roles, and profile-designer on configuration if needed. Iterate until each section is clear and complete.

**Every blueprint has a 'how to use' section in the top comment block of the doc. When unsure, follow the steps outlined in the doc.**

Example:

```

You: 'artifact-designer, please review the artifacts section of blueprint TB01 and add detailed section definitions for the code-review artifact.'

```

💡 **Tip**: This is Phase 1 where you focus entirely on design. Take time to get the blueprint right before implementing anything.

**Step 3: Build Team Components**

Once the blueprint is complete, systematically implement components in Phase 2. Build artifacts with artifact-designer, create agents with agent-designer, generate routines with routine-builder, and create the profile with profile-designer if needed. Each agent uses the blueprint as its specification.

Example:

```

You: 'artifact-designer, build the code-review artifact from blueprint TB01.'

```

💡 **Tip**: Implement components sequentially rather than in parallel, and test each component as it's generated.

**Step 4: Generate Documentation**

After all components are implemented and tested, work with team-readme-writer to generate user documentation. Share the blueprint and generated components as context, and the agent will create comprehensive README documentation.

Example:

```

You: 'team-readme-writer, create documentation for the code-review team based on blueprint TB01 and the implemented components.'

```

💡 **Tip**: Review the generated README to ensure it accurately reflects your team's capabilities and makes the team accessible to users.


### What Happens Next

After your first successful team creation, explore more advanced capabilities like designing artifacts with complex lifecycle sections, creating agents with sophisticated workflows, or adding configuration profiles for different operational modes. Consider building additional teams for other workflows in your project, applying the lessons learned from your first team. Review the generated components to understand the patterns and conventions used, which will help you design better blueprints for future teams. If you need to extend or modify your team later, you can update the blueprint and regenerate specific components rather than starting from scratch.

### Common Questions

**Q: Do I need to know Jsonnet or Jinja2 to create a team?**

A: No. The specialized agents handle all schema and template creation. You describe what you need in plain language, and the agents generate technically correct implementations following framework patterns.

**Q: How long does it take to create a new team?**

A: Blueprint design (Phase 1) typically takes one to several iterations depending on team complexity. Implementation (Phase 2) is systematic and moves quickly once the blueprint is complete. If you have a clear idea in mind, creating a new team is just a matter of having a few conversations with the Pantheon Team Builder agents and reviewing the output.

**Q: Can I modify a team after it's created?**

A: Yes. You can update the team blueprint and regenerate specific components. The modular structure allows you to add new artifacts, create additional agents, or modify existing processes without rebuilding the entire team. You can also make direct edits to the files if that's easier, either by yourself, or with the help of agents. Note that bigger changes are better done through the predefined workflows and processes to ensure structurual integrity and reliable execution.

**Q: What if I'm not sure what artifacts my team needs?**

A: Start with the workflow you want to support and identify the key deliverables or decision points. Each significant deliverable or checkpoint is a candidate for an artifact. The pantheon-team-builder agent can help you think through artifact needs during blueprint creation.

**Q: How do I know if my team needs configuration profiles?**

A: Most teams don't need profiles initially. Add them only if you have clearly different operational modes (like verbose vs concise outputs, or development vs production settings). The profile-designer will help determine if configuration is truly necessary for your use case.

**Q: Is Pantheon a task management system?**

A: No, Pantheon doesn't position itself as a task management system, nor dictate a specific task management system. You can integrate any task management system of your choice simply by creating tasks based on the created artifacts.<!-- SECTION:END:GETTING_STARTED -->

<!-- SECTION:START:WORKING_WITH_AGENTS -->
## Working with pantheon-team-builder Agents

The pantheon-team-builder team operates through natural conversation with agents, not technical commands. Each agent is an expert in their domain who understands your goals and translates them into concrete artifacts: Team Blueprint, Build Specifications, Agent Definitions, Process Families, Team Profile, Team README.

You communicate directly with agents using plain language about what you want to accomplish. Working through the agents eliminates the cognitive overhead of remembering complex procedures and technical syntax.

Agents maintain consistent behavior through structured processes provided by the Pantheon framework, ensuring reliable results every time. This systematic approach creates clear accountability and traceability, so it’s always obvious what was done and why.

With every action documented in structured artifacts and audit trails, you gain full transparency, while staying focused on high-level direction and decision-making.

### Your Role

As a human collaborating with the pantheon-team-builder, your role is to provide strategic vision and domain expertise. You define what the new team should accomplish, what artifacts it should produce, and how agents should specialize. The team-builder agents handle all technical implementation details including schema design, template creation, and file generation. You make high-level decisions about team structure and capabilities, while the agents ensure technical correctness, consistency, and compliance with framework patterns. Throughout the process, you review generated components and provide feedback to refine the design, but you never need to write Jsonnet schemas, Jinja2 templates, or routine files yourself.

Once you have the artifacts, direct the primary LLM agent outside of Pantheon (i.e. Claude Code, GPT Codex, Gemini) to execute based on the artifact (i.e. implement code based on plan, write blog post based on outline). This allows for a flexible collaboration between the main LLM agent based on the artifacts created: Team Blueprint, Build Specifications, Agent Definitions, Process Families, Team Profile, Team README .

### Communication Best Practices

- **Start with the Blueprint**: Always begin by creating a comprehensive team blueprint with the pantheon-team-builder agent before implementing any components.
- **Iterate in Phase 1**: Refine blueprint sections collaboratively with specialized agents until the design is complete before moving to implementation.
- **Be Specific About Artifacts**: Clearly describe what each artifact should contain, its purpose, and how it fits into the team's workflow.
- **Define Clear Agent Boundaries**: Ensure each agent has a focused specialty with minimal overlap to create a cohesive team with clear responsibilities.
- **Review Generated Components**: Inspect all generated files in the staging area before deploying them to ensure they meet your requirements.
<!-- SECTION:END:WORKING_WITH_AGENTS -->

<!-- SECTION:START:AGENTS -->
## Available Agents

The pantheon-team-builder includes six specialized agents, each focused on a specific aspect of team creation. You'll work with different agents depending on which component you're designing or implementing.

### pantheon-team-builder

**Expertise**: Lead architect specializing in high-level team strategy, mission definition, and comprehensive blueprint creation.

**When to Engage**: Engage this agent when starting a new team package or updating the foundational strategy and context sections of an existing blueprint. This agent establishes the team's identity, core principles, and key terminology.

**How to Interact**:

Start by describing your project's goals and how the new team will contribute. Share context about the domain, workflow, or problem space. The agent will ask clarifying questions about mission, scope, and key concepts before creating the blueprint. You can say things like 'Create a blueprint for a team that manages code reviews' or 'Update the foundation section to emphasize security compliance'.

**What pantheon-team-builder Delivers**:
- Team blueprint documents
- Foundation and strategy sections
- Context and terminology definitions

### artifact-designer

**Expertise**: Specialist in artifact data models, JSON schemas, lifecycle sections, and complete process family generation.

**When to Engage**: Work with this agent when designing artifacts for the blueprint or implementing artifacts with their full CREATE, GET, and UPDATE process families. This agent handles schema design, template creation, and artifact scaffolding.

**How to Interact**:

Describe the artifact you need, its purpose, and what information it should contain. Explain the artifact's lifecycle stages if it will be updated over time. Provide examples of similar artifacts if available. You can request things like 'Design a code-review artifact with sections for findings and recommendations' or 'Build the ticket artifact from the blueprint'.

**What artifact-designer Delivers**:
- Artifact section designs
- JSON schemas with validation
- Complete process families
- Content and patch templates

### agent-designer

**Expertise**: Specialist in AI agent persona design, competency definition, technical understanding sections, and RAE workflow creation.

**When to Engage**: Engage this agent when designing agent roles for the blueprint or creating agent definition files. This agent ensures agents have clear identities, focused expertise, and reliable workflows.

**How to Interact**:

Describe the agent's purpose, what problems it should solve, and what specialized knowledge it needs. Explain how it differs from other agents on the team. Share the processes the agent will handle. You can say things like 'Design an agent that specializes in security reviews' or 'Create the security-reviewer agent from the blueprint'.

**What agent-designer Delivers**:
- Agent role definitions
- Agent persona files
- Competency and philosophy sections
- RAE-compliant workflows

### profile-designer

**Expertise**: Specialist in team configuration design, profile properties, schema-template integration, and operational mode translation.

**When to Engage**: Work with this agent when your team needs configuration properties that control different operational modes or when creating the team profile file. This agent designs properties that work in both schemas and templates.

**How to Interact**:

Describe the different operational modes your team needs (like development vs production settings) and what should vary between them. Explain what behaviors should be configurable. The agent will determine if configuration is truly needed and design minimal, effective properties. You can request things like 'Design profiles for detailed and concise report modes'.

**What profile-designer Delivers**:
- Profile property definitions
- Team profile YAML files
- Profile schemas
- Configuration documentation

### routine-builder

**Expertise**: Expert in RAE pattern implementation, structured routine creation, cognitive guidance design, and proper node-based control flow.

**When to Engage**: Engage this agent when creating routine files for processes, whether basic boilerplate routines for simple processes or custom routines with sophisticated logic and branching for complex workflows.

**How to Interact**:

Describe the process the routine guides, including key decision points, required context, and success criteria. Explain any conditional logic or branching needed. Share the associated schema so the routine aligns with expected data. You can say things like 'Create a custom routine for the review process with approval workflows' or 'Generate a basic routine for ticket creation'.

**What routine-builder Delivers**:
- Basic routine files
- Custom routines with branching
- Cognitive guidance steps
- Process-specific guardrails

### team-readme-writer

**Expertise**: Documentation specialist who creates comprehensive, user-friendly README files explaining team capabilities, agent interactions, and workflow examples.

**When to Engage**: Work with this agent after implementing all team components to generate user documentation, or when updating specific sections of existing README files to reflect changes in team capabilities.

**How to Interact**:

Share the team blueprint, agent definitions, and process information. Describe your target audience and their technical background. The agent will create documentation that makes your team accessible to users without exposing technical complexity. You can request things like 'Create the team README' or 'Update the workflow examples section with the new approval process'.

**What team-readme-writer Delivers**:
- Complete team README files
- Agent interaction guides
- Workflow examples
- Getting started documentation

<!-- SECTION:END:AGENTS -->

<!-- SECTION:START:ARTIFACTS -->
## Understanding Team Artifacts

The pantheon-team-builder produces several types of artifacts during the team creation process. These artifacts serve as both planning documents and implementation specifications, ensuring all team components work together cohesively.

### Artifact Types

#### Team Blueprint

**Purpose**: The central planning document that defines team foundation, context, artifacts, agents, and profile configuration before any implementation.

**Format**: Structured markdown document with five main sections: foundation, context, artifacts, agents, and profile.

**How to Use**:

Start every new team project by creating a team blueprint with the pantheon-team-builder agent. Use this blueprint as the single source of truth throughout design and implementation. Update specific sections as the design evolves by working with specialized agents. Reference the blueprint when implementing components to ensure consistency. You can retrieve the blueprint anytime using its ID (e.g., TB01) to review or share with other agents.


#### Build Specifications

**Purpose**: Technical specifications that define how to generate complete artifact families with CREATE, GET, and UPDATE processes.

**Format**: JSON documents with artifact structure, section definitions, schema specifications, and template requirements.

**How to Use**:

The artifact-designer creates build specifications when implementing artifacts from the blueprint. You typically don't create these manually but may review them before execution. Once created, pass the build specification to the artifact-designer to generate the complete process family. The generated files appear in the staging area for review before deployment.


#### Agent Definitions

**Purpose**: Complete agent persona files with role, competencies, philosophy, technical understanding, and workflows.

**Format**: Markdown files with structured sections following agent prompt template format.

**How to Use**:

After designing agent roles in the blueprint, work with the agent-designer to create agent definition files. Review the generated agent files to ensure they capture the intended persona and capabilities. Agent definitions become part of your team package and guide how agents behave when users interact with them.


#### Process Families

**Purpose**: Complete sets of CREATE, GET, and UPDATE processes for each artifact, including schemas, routines, templates, and permissions.

**Format**: Directory structures with multiple files per process following Pantheon conventions.

**How to Use**:

Process families are generated automatically by the artifact-designer from build specifications. Review the generated process directories in the staging area, checking schemas for data validation, templates for content structure, and routines for workflow logic. Test each process type before deploying to ensure complete artifact lifecycle support.


#### Team Profile

**Purpose**: Configuration file defining team properties, operational profiles, and default settings for schema and template control.

**Format**: YAML file with properties section and multiple named profiles.

**How to Use**:

If your team needs configurable behavior, work with the profile-designer to create the team profile file. Review property definitions to ensure they're simple and necessary. Test each profile configuration to verify schemas and templates behave as expected. Most teams can start without profiles and add them later if operational flexibility is needed.


#### Team README

**Purpose**: User-facing documentation that explains team purpose, capabilities, agents, artifacts, and provides workflow examples.

**Format**: Comprehensive markdown document with standardized sections for onboarding and reference.

**How to Use**:

Generate the team README after all components are implemented using the team-readme-writer agent. Share this README with users to help them understand and interact with your team. Update specific sections when team capabilities change rather than regenerating the entire README. The README serves as the primary entry point for users learning about your team.



### Integrating Artifacts into Your Workflow

Team packages created by the pantheon-team-builder integrate seamlessly with your development workflow through the Pantheon CLI. After generating a team package, initialize it using 'pantheon init' to activate the team in your project. Once active, interact with the team's agents naturally through conversational requests, and the agents will internally handle all Pantheon CLI commands and process execution. The artifacts produced by your custom team (like tickets, reviews, or plans) are stored in the pantheon-artifacts directory and can be retrieved, updated, and referenced throughout your project lifecycle. When working with other AI assistants like Claude or implementation LLMs, you can share artifact content as context to inform their work, creating a smooth handoff between planning activities managed by your Pantheon team and implementation activities performed by coding assistants. The framework maintains a clear separation between strategic planning artifacts created through Pantheon processes and implementation code managed by version control and deployment systems.

### Tips for Artifact Consumption

- **Staged Review**: All generated components appear in pantheon-artifacts/pantheon-team-builds/<team-name>/ before deployment. Review schemas, templates, and routines in this staging area to ensure they meet your requirements before copying to the team directory.
- **Incremental Testing**: Test each component type as it's generated rather than waiting until everything is complete. Validate CREATE processes first, then GET processes, then UPDATE processes to catch issues early.
- **Blueprint as Reference**: Keep the team blueprint accessible throughout implementation and refer back to it when reviewing generated components to ensure alignment with the original design intent.
- **Documentation Last**: Generate the team README after all agents, artifacts, and processes are implemented and tested so the documentation accurately reflects the final team capabilities.
<!-- SECTION:END:ARTIFACTS -->

<!-- SECTION:START:WORKFLOW_EXAMPLES -->
## Workflow Examples

These examples show complete workflows for creating different types of teams, demonstrating how you collaborate with the pantheon-team-builder agents from initial concept through implementation.

### Example 1: Creating a Code Review Team

**Scenario**: You need a team that helps manage code reviews by creating review artifacts with structured findings, recommendations, and approval workflows. The team should have agents specializing in different review aspects like security, performance, and architecture.

**Step-by-Step Process**:

1. **Request initial blueprint**
   - Engage the pantheon-team-builder agent to create the foundation blueprint for your code review team.
   - Sample prompt: "pantheon-team-builder, I need to create a team for managing code reviews. The team should produce code-review artifacts that guide reviewers through security, performance, and architectural assessments. Each review should result in findings, recommendations, and an approval decision."
   - Expected outcome: The agent creates blueprint TB01 with initial foundation, context, and placeholder sections for artifacts and agents.

2. **Design artifact structure**
   - Collaborate with artifact-designer to define the code-review artifact with appropriate lifecycle sections.
   - Sample prompt: "artifact-designer, please design the code-review artifact for blueprint TB01. It should have sections for security findings, performance findings, architecture findings, recommendations, and approval status."
   - Expected outcome: The agent updates the blueprint's artifacts section with detailed code-review artifact definition including section purposes and update patterns.

3. **Define specialized agents**
   - Work with agent-designer to specify the agent roles needed for the team.
   - Sample prompt: "agent-designer, design three specialized agents for blueprint TB01: security-reviewer focusing on security vulnerabilities, performance-reviewer analyzing efficiency concerns, and review-coordinator managing the overall review process and approval."
   - Expected outcome: The blueprint's agents section is updated with three agent definitions including their responsibilities and which artifact sections they manage.

4. **Build the code-review artifact**
   - Have artifact-designer generate the complete process family for the code-review artifact.
   - Sample prompt: "artifact-designer, build the code-review artifact from blueprint TB01 with modular build mode so each agent can update their sections independently."
   - Expected outcome: Complete process family generated in staging area: create-code-review, get-code-review, and update processes for each section.

5. **Create agent definitions**
   - Generate the agent persona files for each specialized agent.
   - Sample prompt: "agent-designer, create the security-reviewer, performance-reviewer, and review-coordinator agents from blueprint TB01."
   - Expected outcome: Three agent definition files generated in staging area with complete personas, competencies, and workflows.

6. **Generate documentation**
   - Create the team README to help users understand and interact with the code review team.
   - Sample prompt: "team-readme-writer, create comprehensive documentation for the code-review team based on blueprint TB01 and all implemented components."
   - Expected outcome: Complete README file generated explaining team purpose, agent specialties, and workflow examples for conducting code reviews.


**Final Result**: A production-ready code-review team package with complete artifact processes, three specialized agents, and comprehensive documentation, staged for review and ready to deploy to your team directory.

### Example 2: Building a Deployment Planning Team

**Scenario**: You want a team that creates deployment plans with environment configuration, rollback procedures, and verification checklists. The team should support both simple and complex deployment scenarios through configurable profiles.

**Step-by-Step Process**:

1. **Create blueprint with context**
   - Work with pantheon-team-builder to establish the deployment planning team foundation.
   - Sample prompt: "pantheon-team-builder, create a blueprint for a deployment planning team. It should produce deployment-plan artifacts with sections for environment config, deployment steps, rollback procedures, and verification checklists."
   - Expected outcome: Blueprint TB02 created with foundation defining deployment planning mission and context explaining deployment concepts and terminology.

2. **Design configurable artifacts**
   - Collaborate with artifact-designer and profile-designer to create artifacts that adapt to deployment complexity.
   - Sample prompt: "artifact-designer, design the deployment-plan artifact with sections that scale from simple deployments to complex multi-stage rollouts. profile-designer, create profiles for 'simple' and 'complex' deployment modes that control validation strictness and required sections."
   - Expected outcome: Artifact definition with conditional sections and profile properties that control schema validation based on deployment complexity.

3. **Define planning agents**
   - Specify agents that handle different deployment planning aspects.
   - Sample prompt: "agent-designer, design agents for blueprint TB02: deployment-planner for creating initial plans, environment-specialist for configuration details, and rollback-designer for recovery procedures."
   - Expected outcome: Agent definitions added to blueprint with clear specialization boundaries and workflows for different plan sections.

4. **Implement components systematically**
   - Build artifacts, create agents, generate routines, and create profiles in sequence.
   - Sample prompt: "artifact-designer, build the deployment-plan artifact from TB02. agent-designer, create all three agents. routine-builder, create custom routines for the planning processes. profile-designer, create the team profile."
   - Expected outcome: All team components generated in staging area, ready for review and testing.

5. **Create team documentation**
   - Generate README that explains both simple and complex deployment planning workflows.
   - Sample prompt: "team-readme-writer, document the deployment-planning team including examples for both simple and complex deployment scenarios using different profiles."
   - Expected outcome: README with workflow examples showing how to create deployment plans for different complexity levels using profile configuration.


**Final Result**: A complete deployment-planning team with configurable complexity levels, specialized agents for different planning aspects, and documentation that helps users create appropriate plans for their deployment scenarios.

### Example 3: Extending an Existing Team

**Scenario**: You have an existing ticket management team and need to add a new risk-assessment artifact and corresponding agent to handle risk analysis for high-priority tickets.

**Step-by-Step Process**:

1. **Retrieve existing blueprint**
   - Get the current team blueprint to understand existing structure.
   - Sample prompt: "pantheon-team-builder, retrieve blueprint TB05 for the ticket management team so we can extend it."
   - Expected outcome: Complete blueprint content showing existing artifacts, agents, and configuration.

2. **Add new artifact to blueprint**
   - Update the artifacts section with the risk-assessment artifact definition.
   - Sample prompt: "artifact-designer, update the artifacts section of blueprint TB05 to add a risk-assessment artifact with sections for risk identification, impact analysis, mitigation strategies, and risk score."
   - Expected outcome: Blueprint updated with new artifact definition that complements existing ticket artifacts.

3. **Add risk analyst agent**
   - Update the agents section to include the new specialized agent.
   - Sample prompt: "agent-designer, update the agents section of blueprint TB05 to add a risk-analyst agent who creates and updates risk-assessment artifacts for high-priority tickets."
   - Expected outcome: Agent definition added to blueprint with clear role boundaries and workflows for risk assessment.

4. **Implement new components**
   - Build the risk-assessment artifact and create the risk-analyst agent.
   - Sample prompt: "artifact-designer, build the risk-assessment artifact from TB05. agent-designer, create the risk-analyst agent."
   - Expected outcome: New artifact processes and agent definition generated in staging area alongside existing team components.

5. **Update team documentation**
   - Refresh the README to include the new risk assessment capability.
   - Sample prompt: "team-readme-writer, update the agents and workflow examples sections of the ticket-management team README to include risk assessment capabilities."
   - Expected outcome: README updated with risk-analyst profile and workflow examples showing how to assess ticket risks.


**Final Result**: The existing ticket management team extended with risk assessment capabilities, maintaining consistency with original team design while adding new specialized functionality.

<!-- SECTION:END:WORKFLOW_EXAMPLES -->
