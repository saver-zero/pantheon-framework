---
doc_id: documentation-master-index
title: "Pantheon Framework Documentation Master Index"
description: "Complete catalog of all Pantheon Framework documentation assets organized by topic for optimal discoverability and targeted retrieval"
keywords: [documentation, master-index, catalog, knowledge-base, retrieval-index]
relevance: "Central discovery hub for all framework documentation enabling targeted retrieval by AI agents and systematic navigation by humans"
---

# Pantheon Framework Documentation Master Index

This master index provides a complete catalog of all documentation assets in the Pantheon Framework knowledge base, organized by topic for optimal discoverability and retrieval operations.

## Architecture Guide

- To get the comprehensive framework architecture reference, follow the steps below.
  - **Step 1. Get the list of sections:** Use `pantheon get sections get-architecture-guide --actor <your_agent_name>` to get a list of available sections.
  - **Step 2. Retrieve the releveant sections:** Use `pantheon execute get-architecture-guide --sections <section1,section2...> --actor <your_agent_name>` to get the relevant sections of interest from the architecture guide.

- **[Pantheon Architecture - Container View](architecture-guide/container-view.puml)**: Use this diagram to understand the overall system architecture, component relationships, and key architectural patterns like dependency inversion, facade, and protection proxy

## Process Model

Process types and execution model

- **[Process Model Overview](process-model/overview.md)**: Use this document to understand how Pantheon determines process types (CREATE, UPDATE, GET, BUILD) through convention-based file combinations
- **[Build Process Scaffolding Workflow](process-model/scaffolding-workflow.md)**: Essential technical reference for understanding how build-team-process generates complete process families from specifications and the intelligent scaffolding logic behind automated process creation
- **[BUILD Processes](process-model/build-processes.md)**: Use this document to understand BUILD process structure and how complete process families are generated from build specifications
- **[CREATE Processes](process-model/create-processes.md)**: Use this document to understand CREATE process structure and how new artifacts are generated from templates
- **[GET Processes](process-model/get-processes.md)**: Use this document to understand GET process structure and how existing artifacts are located and parsed
- **[Single-Section Simplification](process-model/single-section-simplification.md)**: Use this document to understand when and how Pantheon simplifies single-section artifacts to eliminate unnecessary complexity
- **[UPDATE Processes](process-model/update-processes.md)**: Use this document to understand UPDATE process structure and how existing artifacts are modified through section targeting
- **[BUILD Process - Update Scaffolding Sequence](process-model/build-process-scaffold-update.puml)**: Use this diagram to understand how BUILD generates consolidated UPDATE processes with section imports, FileSystemLoader templates, and section-order for atomic multi-section operations.
- **[BUILD Process - Process Family Generation](process-model/build-process.puml)**: Use this diagram to understand BUILD operations that generate complete process families from a single build-spec including enhanced ID formats, semantic URIs, and consolidated multi-section UPDATE processes.
- **[Complete CREATE Process Flow](process-model/create-process-complete.puml)**: Use this diagram for the complete CREATE workflow including framework initialization, dependency injection patterns, and all execution phases from command to artifact creation.
- **[CREATE Process Core Flow](process-model/create-process-core.puml)**: Use this diagram to understand CREATE process execution focusing on template rendering with built-in variables, path generation, and optional JSONL logging for analytics.
- **[Create Team Config with Data-Driven Documentation](process-model/create-team-config-sequence.puml)**: Use this diagram to understand team configuration creation with self-documenting YAML output generated from property definitions, including smart to_yaml filter processing.
- **[Complete RETRIEVE Process Flow](process-model/get-process-complete.puml)**: Use this diagram for the complete RETRIEVE workflow including single-section vs multi-section modes, placeholder filtering, and JSON response formatting.
- **[GET Process Core Flow](process-model/get-process-core.puml)**: Use this diagram to understand GET/RETRIEVE operations including ArtifactEngine's find_artifact decomposition, parser.jsonnet transformations, and locator.jsonnet patterns for artifact discovery.
- **[Get Sections Metadata Flow](process-model/get-sections-metadata.puml)**: Use this diagram to understand how pantheon get sections extracts section metadata with names and descriptions, falling back from target.jsonnet to sections.jsonnet, with actor-based permission filtering.
- **[Operation Detection and Schema Validation](process-model/operation-detection.puml)**: Use this diagram to understand how ProcessHandler determines process types (CREATE/UPDATE/RETRIEVE) through efficient 2-call detection and validates inputs against compiled schemas.
- **[UPDATE Process Core Flow](process-model/update-process-core.puml)**: Use this diagram to understand UPDATE operations including mode detection via target.jsonnet, artifact finding with singleton support, and atomic section processing with rollback capability.
- **[Consolidated UPDATE Process Sections URI Resolution](process-model/update-process-sections-uri.puml)**: Use this diagram to understand how consolidated UPDATE processes use semantic URIs to import section markers from GET processes, enabling DRY principle and multi-section atomic updates.
- **[UPDATE Process Singleton Mode Detection](process-model/update-process-singleton-mode.puml)**: Use this diagram to understand how parser.jsonnet presence determines UPDATE mode (singleton vs multi-artifact), artifact_id handling differences, and mode-specific error messages.
- **[Schema Composition Sequence - Profile-Aware](process-model/schema-composition.puml)**: Use this diagram to understand schema composition including import preprocessing, profile context injection via ext_vars, and JSON schema compilation


## Process Development

Guides for creating new processes

- **[Creating CREATE Processes](process-development/creating-create-processes.md)**: Use this document when building processes that generate entirely new artifacts from structured input data, including optional JSONL logging for analytics.
- **[Creating GET Processes](process-development/creating-get-processes.md)**: Use this document when building processes that retrieve structured information from existing artifacts without modifying them.
- **[Creating UPDATE Processes](process-development/creating-update-processes.md)**: Use this document when building processes that modify specific sections of existing artifacts, including section targeting and artifact location patterns.
- **[Process Development Overview](process-development/overview.md)**: Use this document to understand the overall process development workflow, available operation types, and the tools used for building processes in Pantheon team packages.
- **[Testing Processes](process-development/testing-processes.md)**: Use this document when validating process behavior, testing schema compilation, verifying template rendering, and ensuring permission enforcement.
- **[Cross-Process Import Sequence (Preprocessed)](process-development/cross-process-import.puml)**: Use this diagram to understand cross-process schema extension via process-schema:// URIs including both full schema and sub-path section imports
- **[Cross-Process Reference Sequence (Import-Based)](process-development/cross-process-reference.puml)**: Use this diagram to understand cross-process artifact locator reuse via artifact-locator:// semantic URIs and transparent import preprocessing
- **[Direct File Import Sequence (Build Process)](process-development/direct-file-import.puml)**: Use this diagram to understand direct file imports for shared Jsonnet modules with directory traversal protection and recursive content inlining

## Routine System

Routine design and execution patterns

- **[Routine Anti-Patterns](routine-system/anti-patterns.md)**: Use this document to identify and avoid common mistakes when writing routine instructions.
- **[Routine Authoring Best Practices](routine-system/authoring-practices.md)**: Use this document to learn best practices for creating high-quality routine instructions that maximize agent execution reliability.
- **[Cognitive Load Management in Routines](routine-system/cognitive-load-management.md)**: Use this document to learn how to structure routine instructions that reduce cognitive load and improve agent reasoning quality.
- **[Routine System Philosophy](routine-system/philosophy.md)**: Use this document to understand WHY routines use structured syntax and how it ensures reliable agent execution
- **[Routine Testing and Validation](routine-system/testing-validation.md)**: Use this document to learn how to test routine instructions for clarity, completeness, and execution reliability.

## Templating System

Jinja2 templating and artifact generation

- **[Built-in Template Variables](templating-system/built-in-variables.md)**: Use this document to understand all framework-injected variables available in templates and their usage patterns.
- **[Jinja2 Templates Guide](templating-system/jinja2-templates-guide.md)**: Use this document to learn how to create Jinja2 templates for generating artifacts in Pantheon processes.
- **[Jinja2 Syntax Reference](templating-system/jinja2-syntax-reference.md)**: Use this reference when you need to look up Jinja2 syntax, filters, or control structures while writing templates.
- **[JSON Schema Reference](templating-system/json-schema-reference.md)**: Use this reference when you need to look up JSON Schema syntax, keywords, and validation rules for defining data contracts.
- **[Jsonnet Language Reference](templating-system/jsonnet-language-reference.md)**: Use this reference when you need to look up Jsonnet syntax including functions, operators, and standard library methods.
- **[Jsonnet Schemas Guide](templating-system/jsonnet-schemas-guide.md)**: Use this document to learn how to create Jsonnet schemas that define data contracts with dynamic composition and profile-aware behavior.
- **[Routine Templates](templating-system/routine-templates.md)**: Use this document to understand how to create routine templates that generate dynamic, section-aware agent instructions.
- **[Semantic URI Reference](templating-system/semantic-uri-reference.md)**: Use this reference when you need to understand semantic URI schemes for cross-process asset sharing and imports.
- **[Template Composition Patterns](templating-system/template-composition-patterns.md)**: Use this document to understand advanced template composition techniques that eliminate duplication and establish single sources of truth.
- **[Templating System Overview](templating-system/overview.md)**: Use this document to understand Pantheon's three-part templating architecture and how each template type serves different purposes in the framework.

## CLI Interface

Command-line interface reference and usage patterns

- **[CLI Commands Reference](cli-interface/commands.md)**: Essential reference for all CLI operations and command patterns used by agents and developers to interact with the Pantheon Framework
- **[CLI Usage Patterns and Workflows](cli-interface/usage-patterns.md)**: Essential practical guide showing real-world CLI usage patterns for agents executing processes through structured, transparent workflows
- **[Command Audit Logging (CLI → Workspace → JSONL)](cli-interface/command-audit-logging.puml)**: Use this diagram to understand the command audit logging system, including event structure, persistence mechanism, and guardrails against audit directory tampering
- **[Command Processing - Actor Validation & Permission Checking](cli-interface/command-processing.puml)**: Use this diagram to understand how CLI commands are validated, parsed, and prepared for ProcessHandler delegation
- **[Framework Initialization - Project Discovery & Active Team Resolution](cli-interface/framework-init.puml)**: Use this diagram to understand the framework initialization phase, including project root discovery, active team resolution, and profile selection during pantheon init
- **[Project Initialization Sequence](cli-interface/project-init.puml)**: Use this diagram to understand the complete pantheon init workflow including team discovery, scaffolding, team-data directory creation, and optional Claude agent installation
- **[Team Data Operations - Get and Set Commands](cli-interface/team-data-operations.puml)**: Use this diagram to understand team-data get/set operations including type coercion for unquoted values, deep merge for nested updates, and framework-controlled file paths

## Security and Permissions

Actor-based security model and access control

- **[Common Permission Patterns](security-permissions/common-patterns.md)**: Use this document to find proven permission patterns for common scenarios like single-owner processes, admin oversight, public collaboration, and role-based access.
- **[Permission Evaluation Rules](security-permissions/evaluation-rules.md)**: Use this document to understand exactly how the framework evaluates permissions, including the interaction between process-level and section-level rules.
- **[Security & Permissions Overview](security-permissions/overview.md)**: Use this document to understand the foundational security principles and permission architecture that controls access to processes and artifacts.
- **[Permission System Structure](security-permissions/permission-system.md)**: Use this document to understand how to structure permission files for processes, including process-level, section-level, and wildcard permissions.

## Team Packages

Team package structure and management

- **[Team Packages Overview](team-packages/overview.md)**: Use this document to understand the complete Team Packages architecture, including the three-component model and how agents, routines, and schemas work together.
- **[Agent Definitions](team-packages/agents.md)**: Use this document to understand how to structure agent personas effectively and what content belongs in agent definition files.
- **[Routines Development Guide](team-packages/routines-guide.md)**: Use this document to understand how to design routine workflows that guide agent execution through structured, step-by-step instructions.
- **[Schemas Development Guide](team-packages/schemas-guide.md)**: Use this document to understand how to design schema data contracts that define required data structures and validation rules for processes.
- **[Agents & Processes](team-packages/agents-processes.md)**: Use this document to understand how agents and processes work together to create AI teams, including agent definition structure, process types, and the RAE interaction model.
- **[Team Profiles](team-packages/profiles.md)**: Use this document to understand how team profiles control process behavior through schema-level and template-level mechanisms, enabling context-aware process execution.
- **[Team Package Structure](team-packages/structure.md)**: Use this document to understand team package organization, file naming conventions, and the relationship between bundled templates and installed teams.
- **[Process Type Decision Framework](team-packages/decision-framework.md)**: Use this document when you need to determine which process type to create or how to configure process families using build-team-artifact
- **[Process Component Anti-Patterns](team-packages/anti-patterns.md)**: Use this document to identify and avoid common mistakes when organizing process components across agents, routines, and schemas.
- **[Package Bundling - Team Package Inclusion in Distribution](team-packages/package-bundling.puml)**: Use this diagram to understand how production team templates are bundled for distribution while test fixtures remain excluded from the wheel
- **[Team Profile Usage - Smart Schema, Dumb Template Pattern](team-packages/team-profile-usage.puml)**: Use this diagram to understand the smart schema/dumb template pattern where profiles control schema behavior while templates render data without profile-specific logic

## Core Teams

Bundled team package documentation

- **[Pantheon Dev Team](core-teams/pantheon-dev-team.md)**: Essential reference for the primary Pantheon team package implementing Glass Box philosophy for day-to-day software development with transparent, auditable workflows
- **[Pantheon Team Builder](core-teams/pantheon-team-builder-team.md)**: Essential documentation for the meta-team that creates and manages other team packages through blueprint-driven design, artifact scaffolding, and specialized designer agents for recursive framework capabilities
- **[Learning Loop Activity Flow](routine-system/learning-loop-activity.puml)**: Use this diagram to understand the complete learning loop workflow that the Pantheon Dev Team has - from feedback submission through process improvement implementation

## Getting Started

Installation, initialization, and project configuration for end users

- **[Installation and System Requirements](getting-started/installation.md)**: Essential starting point for setting up the Pantheon Framework tool before project initialization and team configuration
- **[Project Initialization Workflow](getting-started/initialization.md)**: Critical workflow documentation for setting up new projects or switching active teams with detailed interactive prompts and configuration steps
- **[Configuration Files and Settings](getting-started/configuration.md)**: Essential reference for all project and team configuration options controlling framework behavior and artifact management
- **[Team Package Management and Switching](getting-started/team-management.md)**: Essential for projects using multiple team packages or switching between different development contexts while preserving team customizations

## Framework Development

Development environment setup, build workflows, and release processes for framework contributors

- **[Development Environment Setup - Developer Onboarding](framework-development/development-environment-setup.puml)**: Use this diagram to understand the development environment setup process including editable installation, CLI verification, and template development workflow
- **[Build and Release Workflow - Complete Release Process](framework-development/build-and-release-workflow.puml)**: Use this diagram to understand the complete release workflow from pre-release checklist through quality gate validation and package distribution
- **[Template Change Propagation - Development vs Test Templates](framework-development/template-change-propagation.puml)**: Use this diagram to understand the different propagation mechanisms for production templates (copy-based) versus test fixtures (direct access)

## Testing

Testing strategies and patterns

- **[E2E Test Architecture - Fixture-Based Isolation System](testing/e2e-test-architecture.puml)**: Use this diagram to understand the E2E test isolation architecture using test teams in fixtures directory with automatic cleanup and production independence
- **[Test Execution Flow - Complete Testing Workflow](testing/test-execution-flow.puml)**: Use this diagram to understand the end-to-end testing workflow including environment setup, CLI verification, test category execution, and debugging techniques
- **[Pantheon Framework Testing Strategy - Three-Tier Pyramid](testing/testing-pyramid.puml)**: Use this diagram to understand the overall testing strategy and the three-tier pyramid approach with isolation levels and execution speeds

## Documentation Standards

This knowledge base follows structured documentation standards for retrieval optimization:

### Structured Metadata

Every asset contains metadata with:
- `doc_id`: Unique identifier for the document
- `title`: Human-readable document title
- `description`: Detailed content summary
- `keywords`: Searchable terms for targeted queries
- `relevance`: One-sentence relevance description answering "When should I use this?"

### Topic Orthogonality

Concepts are organized into non-overlapping directories:
- Each topic has exactly one canonical source of truth
- Related concepts are nested or cross-referenced, not duplicated
- Prevents knowledge fragmentation

### Co-location Principle

All assets for a topic reside in the same directory:
- Text documentation with related diagrams
- Simplifies retrieval operations
- Prevents orphaned knowledge

### Retrieval Optimization

Documentation structure enables precise query patterns:
- **Keyword queries**: Search metadata keywords for concepts
- **Relevance filtering**: Determine applicability before retrieval
- **Cross-referencing**: Navigate between related concepts via relative paths
- **Status filtering**: Query metadata status fields (deprecated, draft, approved)

## Usage Guidelines

### For AI Agents

- Use keyword searches to find relevant documentation
- Read relevance descriptions before full retrieval
- Follow cross-references for related topics
- Respect topic boundaries (avoid duplicating information)

### For Human Readers

- Browse directory structure for topic discovery
- Use this index for quick reference
- Follow links for detailed documentation
- Start with overview documents in each directory

### For Contributors

- Add new documentation to appropriate directory
- Include complete metadata (YAML frontmatter for .md, block comments for .puml)
- Update this master index (or regenerate using rebuild_readme.py)
- Follow co-location principle (keep related assets together)
- Maintain topic orthogonality (avoid duplicating existing content)
