---
doc_id: jinja2-templates-guide
title: "Jinja2 Templates Guide"
description: "Comprehensive guide to using Jinja2 templates for artifact content generation in CREATE and UPDATE processes."
keywords: [jinja2, templates, artifacts, create, update, tutorial, guide]
relevance: "Use this document to learn how to create Jinja2 templates for generating artifacts in Pantheon processes."
---

# Jinja2 Templates Guide

Jinja2 templates are the **content generation layer** of the Pantheon Framework. They transform structured JSON data (validated by schemas) into formatted artifacts like Markdown documents, configuration files, or any text-based output.

## Template Types by Process Operation

### CREATE Process Templates

CREATE processes use three Jinja2 template files to generate and place new artifacts:

#### artifact/content.md
**Purpose:** Defines the complete content structure of new artifacts

**Example:**
```jinja2
# {{ title }}

**ID**: T{{ artifact_id }}
**Created**: {{ timestamp }}
**Author**: {{ actor }}

## Business Context

{{ business_context }}

## Technical Context

{{ technical_context }}

## Implementation Plan

<!-- START_SECTION:plan -->
_Implementation plan will be added here_
<!-- END_SECTION:plan -->

## Status

- [ ] Planning
- [ ] Implementation
- [ ] Testing
- [ ] Review
- [ ] Complete
```

**Key Features:**
- Access to all schema-defined properties (e.g., `{{ title }}`, `{{ business_context }}`)
- Built-in framework variables (e.g., `{{ artifact_id }}`, `{{ timestamp }}`, `{{ actor }}`)
- Section markers for future UPDATE operations
- Placeholder content for sections to be populated later

#### artifact/placement.jinja
**Purpose:** Determines the directory where artifacts are saved

**Example:**
```jinja2
tickets/
```

**Advanced Example (Dynamic Placement):**
```jinja2
{% if pantheon_active_profile.organize_by_status %}
tickets/{{ status | lower }}/
{% else %}
tickets/
{% endif %}
```

**Key Features:**
- Simple static paths for most cases
- Profile-aware dynamic paths when needed
- Relative to the configured artifacts root directory

#### artifact/naming.jinja
**Purpose:** Generates meaningful filenames for artifacts

**Example:**
```jinja2
T{{ artifact_id }}_{{ title | lower | replace(' ', '-') | replace('/', '-') }}.md
```

**Key Features:**
- Jinja2 filters for text transformation (`lower`, `replace`, `trim`)
- Artifact ID inclusion for uniqueness
- Human-readable titles for discoverability
- Extension specification (`.md`, `.json`, `.yaml`, etc.)

**Common Naming Patterns:**
```jinja2
# ID-based naming
T{{ artifact_id }}.md

# ID with title
{{ artifact_id }}_{{ title | slugify }}.md

# Date-based organization
{{ pantheon_datestamp }}_{{ artifact_type }}.md

# Actor-scoped naming
{{ pantheon_actor }}_{{ artifact_id }}.md
```

### UPDATE Process Templates

UPDATE processes modify existing artifacts using section-based templates:

#### artifact/patch.md
**Purpose:** Orchestrates section replacement by including section templates

**Basic Pattern (Single Section):**
```jinja2
## Implementation Steps

{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

{% if dependencies %}
## Dependencies

{{ dependencies }}
{% endif %}

**Plan Updated**: {{ timestamp }} by {{ actor }}
```

**Advanced Pattern (Multi-Section with Includes):**
```jinja2
{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}

{% for section_name in requested_sections %}
  {% set snippet = "sections/" ~ section_name ~ ".md" %}
  {% include snippet ignore missing %}
{% endfor %}
```

**Key Features:**
- Access to flattened section data (e.g., `{{ implementation_steps }}` from `section_updates.plan.implementation_steps`)
- Dynamic section inclusion based on `--sections` parameter
- `ignore missing` directive for optional sections
- Framework handles section targeting via `target.jsonnet`

#### artifact/sections/<name>.md
**Purpose:** Define individual section content for modular composition

**Example: artifact/sections/plan.md**
```jinja2

## Implementation Steps

{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

{% if dependencies %}
## Dependencies

{{ dependencies }}
{% endif %}

{% if estimated_effort %}
**Estimated Effort**: {{ estimated_effort }}
{% endif %}

**Plan Updated**: {{ timestamp }} by {{ actor }}

```

**Variable Access Pattern:**
The framework automatically flattens nested schema properties for section templates. Given schema structure:
```json
{
  "section_updates": {
    "plan": {
      "implementation_steps": [...],
      "dependencies": "..."
    }
  }
}
```

Section templates access variables directly:
```jinja2
{{ implementation_steps }}  # NOT {{ section_updates.plan.implementation_steps }}
{{ dependencies }}          # NOT {{ section_updates.plan.dependencies }}
```

## Section Markers for Structured Documents

Section markers enable UPDATE operations to target specific portions of documents:

### Standard Section Marker Pattern
```markdown
<!-- SECTION:START:SECTION_NAME -->
Section content goes here
<!-- SECTION:END:SECTION_NAME -->
```

**Important**: Section names in markers are UPPERCASE, while section names in schema properties use lowercase with underscores.

**Example Mapping**:
- Schema property: `ticket_description`
- Section marker: `SECTION:START:TICKET_DESCRIPTION` and `SECTION:END:TICKET_DESCRIPTION`

### Placeholder Markers
For sections not yet populated:
```markdown
<!-- SECTION:PLACEHOLDER -->
```

**Framework Behavior:**
- GET operations automatically filter sections with placeholder markers
- First UPDATE to a placeholder section performs full replacement
- Placeholder markers never persist in the final artifact
- Placeholder markers are section-scoped (placed between START and END markers)

**Example with Placeholder**:
```markdown
<!-- SECTION:START:TECHNICAL_PLAN -->
<!-- SECTION:PLACEHOLDER -->
<!-- SECTION:END:TECHNICAL_PLAN -->
```

### Section Marker Guidelines

**Use Descriptive Names:**
```markdown
<!-- SECTION:START:PLAN -->              # Good
<!-- SECTION:START:SECTION1 -->          # Bad (not descriptive)
```

**HTML Comment Format:**
```markdown
<!-- SECTION:START:NAME -->              # Good (HTML comment)
[SECTION:START:NAME]                     # Bad (not HTML comment)
```

**Consistent Naming:**
- Use UPPERCASE for section marker names
- Use underscores (not hyphens or spaces) in marker names
- Schema properties use lowercase_with_underscores
- Match section names in `sections.jsonnet` and `target.jsonnet` (lowercase)
- Framework automatically converts between lowercase schema names and UPPERCASE markers

## Built-in Variables

All Jinja2 artifact templates have access to framework-injected variables:

### Common Variables (All Process Types)
- `{{ pantheon_actor }}` - The executing agent's name
- `{{ pantheon_timestamp }}` - Full ISO 8601 timestamp
- `{{ pantheon_datestamp }}` - Date-only timestamp (YYYY-MM-DD)
- `{{ pantheon_artifact_id }}` - Unique artifact identifier
- `{{ pantheon_active_profile }}` - Team profile settings object

### UPDATE Process Variables
- `{{ section_order }}` - Array of section names in defined order
- `{{ initial_section }}` - First section in order
- `{{ artifact }}` - Artifact name from process name
- `{{ pantheon_sections }}` - Requested sections from `--sections` flag

**Example Usage:**
```jinja2
**Created**: {{ pantheon_timestamp }}
**Author**: {{ pantheon_actor }}
**Artifact ID**: {{ pantheon_artifact_id }}

{% if pantheon_active_profile.include_metadata %}
**Team**: {{ pantheon_active_profile.team_name }}
**Profile**: {{ pantheon_active_profile.verbosity }}
{% endif %}
```

## Template Composition Patterns

### Semantic URI Includes

Templates can include content from other processes using semantic URIs:

```jinja2
# Architecture Guide for {{ project_name }}

## Core Principles
{% include 'artifact-template://update-architecture-guide/sections/core-principles' %}

## High-Level Overview
{% include 'artifact-template://update-architecture-guide/sections/high-level-overview' %}
```

**Benefits:**
- Single source of truth for section content
- Automatic propagation of updates
- Consistent content across CREATE and UPDATE processes

**URI Resolution:**
`artifact-template://process-name/sections/section-name` resolves to:
`processes/process-name/artifact/sections/section-name.md`

For complete details on semantic URIs, see [Semantic URI Reference](./semantic-uri-reference.md).

### Conditional Section Rendering

```jinja2
{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}

{% for section_name in requested_sections %}
  {% if section_name in ['plan', 'analysis'] %}
    {% set snippet = "sections/" ~ section_name ~ ".md" %}
    {% include snippet ignore missing with context %}
  {% endif %}
{% endfor %}
```

### Profile-Aware Formatting

```jinja2
{% if pantheon_active_profile.verbosity == 'detailed' %}
## Detailed Technical Context
{{ technical_context }}

## Detailed Implementation Notes
{{ implementation_notes }}
{% else %}
## Technical Context
{{ technical_context }}
{% endif %}
```

### Section Enabling/Disabling Pattern

CREATE processes can enable or disable optional sections using local Jinja2 variables combined with semantic URI includes. This pattern is auto-generated by BUILD processes and provides easy human configuration.

**Pattern Overview:**

**Schema Layer** (schema.jsonnet):
```jsonnet
local sections = [
  {
    name: "ticket_description",
    schema: import "process-schema://update-ticket/sections/ticket_description",
    enabled: true
  },
  {
    name: "technical_plan",
    schema: import "process-schema://update-ticket/sections/technical_plan",
    enabled: false
  },
  {
    name: "progress_log",
    schema: import "process-schema://update-ticket/sections/progress_log",
    enabled: false
  }
];

local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.schema.properties else acc,
  sections,
  {}
);

local required = std.foldl(
  function(acc, sec)
    if sec.enabled && std.objectHas(sec.schema, 'required')
    then acc + sec.schema.required
    else acc,
  sections,
  []
);

{
  type: 'object',
  properties: properties,
  required: required
}
```

**Template Layer** (artifact/content.md):
```jinja2
---
created_at: {{ pantheon_timestamp }}
---
{% set _include_ticket_description = true %}
<!-- SECTION:START:TICKET_DESCRIPTION -->
{% if _include_ticket_description %}
{% include 'artifact-template://update-ticket/sections/ticket_description' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TICKET_DESCRIPTION -->

{% set _include_technical_plan = false %}
<!-- SECTION:START:TECHNICAL_PLAN -->
{% if _include_technical_plan %}
{% include 'artifact-template://update-ticket/sections/technical_plan' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:TECHNICAL_PLAN -->

{% set _include_progress_log = false %}
<!-- SECTION:START:PROGRESS_LOG -->
{% if _include_progress_log %}
{% include 'artifact-template://update-ticket/sections/progress_log' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:PROGRESS_LOG -->
```

**Pattern Benefits:**

1. **Single Source of Truth**: Section content defined in UPDATE process, imported by CREATE
2. **Easy Configuration**: Toggle boolean flags to enable/disable sections
3. **Automatic Synchronization**: Schema and template work together - enabled sections appear in schema and render content
4. **Placeholder Support**: Disabled sections insert placeholders for future updates
5. **Profile-Aware**: Can combine with profile conditionals for environment-specific sections

**How It Works:**

**Schema Composition**:
- Array of section objects with `name`, `schema` (semantic URI import), and `enabled` flag
- `std.foldl` iterates sections and combines properties/required fields from enabled sections
- Only enabled sections appear in the final schema

**Template Composition**:
- Local Jinja2 variables (`_include_section_name`) control rendering
- When `true`: Includes section template via semantic URI
- When `false`: Inserts placeholder comment
- Section markers present for all sections (enabled or disabled) for future updates

**Human Configuration Workflow:**

To enable a section:

1. **Update schema.jsonnet**: Change `enabled: false` to `enabled: true` for the section
2. **Update content.md**: Change `{% set _include_section_name = false %}` to `{% set _include_section_name = true %}`
3. **Test**: Execute CREATE process to verify section renders correctly

**Profile-Based Section Control:**

Combine with profile conditionals for environment-specific sections:

```jinja2
{% if pantheon_active_profile.enable_progress_log %}

## Progress Log
{% set _include_progress_log = false %}
<!-- SECTION:START:PROGRESS_LOG -->
{% if _include_progress_log %}
{% include 'artifact-template://update-ticket/sections/progress_log' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:PROGRESS_LOG -->
{% endif %}
```

The outer `{% if pantheon_active_profile.enable_progress_log %}` controls whether the section structure appears at all, while the inner `_include_progress_log` variable controls whether initial content is rendered or a placeholder is used.

## Best Practices

### 1. Keep Templates Data-Driven
**Good:**
```jinja2
{% if dependencies %}
## Dependencies
{{ dependencies }}
{% endif %}
```

**Bad:**
```jinja2
{% if pantheon_active_profile.require_dependencies %}
## Dependencies
{{ dependencies }}
{% endif %}
```

**Rationale:** Profile logic belongs in schemas (controlling what data is prompted for), not templates (rendering provided data).

### 2. Use Meaningful Section Names
```jinja2
<!-- START_SECTION:implementation_plan -->    # Good
<!-- START_SECTION:plan -->                   # Good
<!-- START_SECTION:section_2 -->              # Bad
```

### 3. Include Update Metadata
```jinja2
**Last Updated**: {{ pantheon_timestamp }} by {{ pantheon_actor }}
```

This provides auditability for all artifact modifications.

### 4. Use Filters for Safe Text Transformation
```jinja2
{{ title | lower | replace(' ', '-') | replace('/', '-') }}
```

Always sanitize user-provided text used in filenames or URLs.

### 5. Handle Missing Optional Fields
```jinja2
{% if estimated_effort %}
**Estimated Effort**: {{ estimated_effort }}
{% endif %}
```

Use conditionals to prevent rendering empty sections.

### 6. Keep Includes Modular
```jinja2
{% include 'sections/header.md' %}
{% include 'sections/body.md' %}
{% include 'sections/footer.md' %}
```

Break complex templates into focused, reusable components.

## Testing Templates

### Manual Testing
```bash
# Get schema to understand required data
pantheon get schema create-ticket --actor test-agent

# Create test JSON file with sample data
# Execute process to verify template rendering
pantheon execute create-ticket --from-file test-data.json --actor test-agent
```

### Common Template Errors

**Undefined Variable:**
```
jinja2.exceptions.UndefinedError: 'field_name' is undefined
```
**Solution:** Check schema definition or use `{{ field_name | default('') }}`

**Template Not Found:**
```
jinja2.exceptions.TemplateNotFound: sections/missing.md
```
**Solution:** Verify file exists or add `ignore missing` directive

**Syntax Error:**
```
jinja2.exceptions.TemplateSyntaxError: unexpected '}'
```
**Solution:** Check for unmatched braces, missing `endif`, or `endfor`

## Related Documentation

- [Templating System Overview](overview.md) - Three-part templating architecture
- [Jinja2 Syntax Reference](./jinja2-syntax-reference.md) - Quick reference for Jinja2 syntax
- [Semantic URI Reference](./semantic-uri-reference.md) - URI schemes for cross-process includes
- [Jsonnet Schemas Guide](./jsonnet-schemas-guide.md) - Data contract definitions
- [Template Composition Patterns](template-composition-patterns.md) - Advanced reuse patterns

---

Jinja2 artifact templates are the final rendering layer that transforms validated data into meaningful, well-formatted artifacts. By keeping templates data-driven and composable, you create maintainable content generation that adapts to different team profiles and workflow requirements.
