---
doc_id: templating-system-overview
title: "Templating System Overview"
description: "Comprehensive guide to Pantheon's three-part templating system for artifact generation, schema composition, and routine rendering with quick reference tables and detailed documentation links."
keywords: [templating, jinja2, jsonnet, templates, schemas, routines, overview, quick-reference]
relevance: "Use this document to understand Pantheon's three-part templating architecture and how each template type serves different purposes in the framework."
---

# Templating System Overview

The Pantheon Framework employs a **three-part templating system** designed to separate concerns and enable dynamic, profile-aware content generation across different layers of the workflow architecture.

## Documentation in This Section

### Core Template Types
- **[Jinja2 Templates Guide](./jinja2-templates-guide.md):** Comprehensive guide to using Jinja2 templates for artifact content generation in CREATE and UPDATE processes, including section markers, variable substitution, and template composition patterns.
- **[Jinja2 Syntax Reference](./jinja2-syntax-reference.md):** Quick reference for Jinja2 syntax, filters, and control structures.
- **[Jsonnet Schemas Guide](./jsonnet-schemas-guide.md):** Guide to using Jsonnet for dynamic schema composition, validation, and profile-aware data contracts with schema inheritance and composition patterns.
- **[Jsonnet Language Reference](./jsonnet-language-reference.md):** Quick reference for Jsonnet syntax, functions, and standard library.
- **[JSON Schema Reference](./json-schema-reference.md):** Quick reference for JSON Schema validation keywords and patterns.
- **[Routine Templates](./routine-templates.md):** Guide to creating routine templates with Jinja2 for step-by-step agent instruction generation, including section-based composition and dynamic step numbering patterns.

### Template Variables and Composition
- **[Built-in Template Variables](./built-in-variables.md):** Comprehensive reference for framework-injected variables available in Jinja2 artifact templates, Jsonnet schemas, and routine templates.
- **[Template Composition Patterns](./template-composition-patterns.md):** Advanced patterns for template reuse, semantic URIs, DRY principles, and cross-process asset sharing to eliminate duplication and establish single sources of truth.
- **[Semantic URI Reference](./semantic-uri-reference.md):** Cross-process asset referencing using semantic URIs for schema composition, artifact reuse, and template includes within team packages.

## The Three Template Types

Pantheon uses three distinct template engines, each optimized for its specific role:

### 1. Jinja2 Artifact Templates
**Purpose:** Generate formatted artifact content
**File Types:** `content.md`, `patch.md`, section templates, `placement.jinja`, `naming.jinja`
**Use Cases:**
- CREATE processes: Generating complete artifact content
- UPDATE processes: Rendering section replacement content
- File placement: Determining directory structure
- File naming: Creating meaningful, sortable filenames

**Example:**
```jinja2
# {{ title }}

**ID**: T{{ artifact_id }}
**Created**: {{ timestamp }}
**Author**: {{ actor }}

## Business Context
{{ business_context }}
```

### 2. Jsonnet Schema Templates
**Purpose:** Define data contracts with dynamic composition
**File Types:** `schema.jsonnet`, section schema fragments
**Use Cases:**
- Input validation for process execution
- Profile-aware field requirements
- Schema composition and inheritance
- Dynamic field descriptions based on team settings

**Example:**
```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    technical_context: {
      type: 'string',
      description: if profile.verbosity == 'detailed' then
        'Comprehensive technical background and constraints'
      else
        'Key technical considerations'
    }
  }
}
```

### 3. Routine Templates
**Purpose:** Create step-by-step agent instructions
**File Types:** `routine.md`, section routine fragments
**Use Cases:**
- Defining process workflows
- Section-specific instructions
- Dynamic step generation based on context
- Conditional workflow branching

**Example:**
```jinja2
Step {{ pantheon_routine_step.num }}. **Section Analysis:** Examine the {{ section }} section content.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}
```

## Design Philosophy

### Separation of Concerns
Each template type serves a distinct purpose in the workflow:
- **Jinja2 templates** handle final content generation (output layer)
- **Jsonnet schemas** manage data contracts and validation (contract layer)
- **Routine templates** guide agent execution (instruction layer)

This separation enables independent evolution of each layer without coupling.

### Convention Over Configuration
Templates follow standardized locations and naming conventions:
- Artifact templates: `artifact/content.md`, `artifact/patch.md`
- Schema files: `schema.jsonnet`, `artifact/sections/<name>.schema.jsonnet`
- Routine files: `routine.md`, `routine/sections/<name>.md`

The framework discovers and resolves these files automatically through the Workspace abstraction.

### Profile-Aware Composition
All three template types can access team profile settings:
- **Schemas** use `std.extVar('profile')` for conditional logic
- **Artifact templates** access `{{ pantheon_profile }}` for formatting
- **Routine templates** receive section metadata extracted from schemas

This enables team-specific customization without duplicating process definitions.

## Template Interaction Flow

The three template types work together in a coordinated workflow:

### CREATE Process Flow
1. **Agent retrieves routine** → Framework renders routine template with context
2. **Agent requests schema** → Framework evaluates Jsonnet schema with profile
3. **Agent prepares data** → Validated against schema contract
4. **Agent executes process** → Framework renders Jinja2 artifact template with data
5. **Framework saves artifact** → Uses `placement.jinja` and `naming.jinja` for location

### UPDATE Process Flow
1. **Agent retrieves routine** → Routine template includes section-specific steps
2. **Agent requests schema** → Consolidated schema imports section fragments
3. **Agent prepares section data** → Validated against section schema
4. **Agent executes process** → Framework renders `patch.md` with section templates
5. **Framework updates artifact** → Replaces targeted sections in existing file

### GET Process Flow
1. **Agent retrieves routine** → Simple retrieval instructions
2. **Agent executes process** → Framework uses `locator.jsonnet` and `parser.jsonnet`
3. **Framework returns data** → Structured JSON output to stdout

## Built-in Variables

All templates have access to framework-injected variables:

### Common Variables (All Templates)
- `pantheon_actor` - The executing agent's name
- `pantheon_timestamp` - Full ISO timestamp
- `pantheon_datestamp` - Date-only timestamp
- `pantheon_artifact_id` - Unique artifact identifier
- `pantheon_profile` - Team profile settings object

### UPDATE Process Variables
- `section_order` - Ordered list of section names
- `initial_section` - First section in order
- `artifact` - Artifact name extracted from process name
- `pantheon_sections` - Requested sections (from `--sections` flag)

### Section Routine Variables
- `pantheon_routine_step` - Object with `num` property for step numbering
- Section-specific context inherited from parent routine

## Template Composition Patterns

### DRY Principle via Semantic URIs
Templates can reference assets from other processes using semantic URIs:

**Schema Composition:**
```jsonnet
import "process-schema://create-ticket"
```

**Artifact Template Includes:**
```jinja2
{% include 'artifact-template://update-guide/sections/overview' %}
```

**Artifact Configuration Reuse:**
```jsonnet
import "artifact-locator://get-ticket"
import "artifact-parser://get-ticket"
```

### Section-Based Modularity
Complex artifacts use section-based composition:
- Individual section schemas: `artifact/sections/<name>.schema.jsonnet`
- Individual section templates: `artifact/sections/<name>.md`
- Individual section routines: `routine/sections/<name>.md`
- Consolidated orchestration files import/include section files

This modular approach enables:
- Independent section development
- Reusable section components
- Selective section updates via `--sections` parameter
- Focused testing of individual sections

## Benefits of the Three-Part System

### Type-Specific Optimization
Each template engine is optimized for its purpose:
- **Jinja2**: Rich text generation with includes, filters, and formatting
- **Jsonnet**: Programmatic composition with functions and conditionals
- **Routine templates**: Step numbering and workflow structure

### Clear Boundaries
Template types enforce architectural boundaries:
- Schemas define contracts, not content
- Artifact templates render content, not validation logic
- Routines provide instructions, not data structures

### Testability
Each template type can be tested independently:
- Schema validation can be unit tested
- Template rendering can be tested with mock data
- Routine structure can be validated against syntax rules

### Extensibility
New capabilities can be added to each layer independently:
- New Jinja2 filters for content generation
- New Jsonnet functions for schema composition
- New routine node types for workflow patterns

## Quick Reference

### Template Types by Purpose

| Template Type | File Extensions | Purpose | Key Features |
|---------------|----------------|---------|--------------|
| **Jinja2 Artifact** | `.md`, `.jinja` | Generate formatted artifact content | Variable substitution, filters, loops, includes, section markers |
| **Jsonnet Schema** | `.jsonnet` | Define data contracts with dynamic composition | Profile-aware validation, schema inheritance, programmatic composition |
| **Routine Template** | `routine.md` | Create step-by-step agent instructions | Dynamic step numbering, section-based composition, conditional workflows |

### Common Built-in Variables

| Variable | Availability | Type | Description |
|----------|-------------|------|-------------|
| `pantheon_actor` | All templates | string | Executing agent name |
| `pantheon_timestamp` | All templates | string | Full ISO 8601 timestamp |
| `pantheon_datestamp` | All templates | string | Date-only timestamp (YYYY-MM-DD) |
| `pantheon_artifact_id` | All templates | string | Unique artifact identifier |
| `pantheon_active_profile` | All templates | object | Team profile settings |
| `section_order` | UPDATE routines | array | Ordered list of section names |
| `pantheon_sections` | UPDATE routines | array | Requested sections from CLI |
| `_current_step_index` | Section routines | namespace | Step numbering object |

### Semantic URI Schemes

| URI Scheme | Resolves To | Use Case |
|------------|-------------|----------|
| `process-schema://name` | `processes/name/schema.jsonnet` | Import schemas from other processes |
| `process-schema://name/sections/sec` | `processes/name/artifact/sections/sec.schema.jsonnet` | Import section schema fragments |
| `artifact-template://name/sections/sec` | `processes/name/artifact/sections/sec.md` | Include section templates |
| `artifact-locator://name` | `processes/name/artifact/locator.jsonnet` | Share artifact finding configuration |
| `artifact-parser://name` | `processes/name/artifact/parser.jsonnet` | Share ID normalization rules |
| `artifact-sections://name?data=path` | `processes/name/artifact/sections.jsonnet` | Reference section markers with data extraction |

### Section Marker Format

Actual implementation uses `SECTION:START:` and `SECTION:END:` patterns:

```markdown
<!-- SECTION:START:SECTION_NAME -->
Section content here
<!-- SECTION:END:SECTION_NAME -->
```

**Important**: Section names in markers are UPPERCASE, while schema properties use lowercase_with_underscores. The framework automatically converts between these formats.

## Related Documentation

- **[Process Development](../process-development/):** Documentation on creating new processes
- **[Process Model](../process-model/):** Documentation on process types and execution patterns
- **[Team Packages](../team-packages/):** Documentation on team package organization and conventions

---

This three-part templating architecture enables the Glass Box philosophy by making all content generation transparent, testable, and version-controlled while providing the flexibility needed for profile-aware customization across different team workflows.
