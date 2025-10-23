---
doc_id: template-composition-patterns
title: "Template Composition Patterns"
description: "Advanced patterns for template reuse, semantic URIs, DRY principles, and cross-process asset sharing."
keywords: [composition, DRY, semantic-uris, includes, imports, reuse, patterns]
relevance: "Use this document to understand advanced template composition techniques that eliminate duplication and establish single sources of truth."
---

# Template Composition Patterns

Template composition enables code reuse across processes by leveraging semantic URIs, includes, and imports. These patterns implement the DRY (Don't Repeat Yourself) principle while maintaining clear architectural boundaries.

## The DRY Principle in Pantheon

### Problem: Template Duplication
Without composition, process families duplicate content:

```
processes/create-ticket/artifact/content.md:
    ## Implementation Plan
    {% for step in implementation_steps %}
    {{ loop.index }}. {{ step }}
    {% endfor %}

processes/update-plan/artifact/sections/plan.md:
    ## Implementation Plan
    {% for step in implementation_steps %}
    {{ loop.index }}. {{ step }}
    {% endfor %}
```

**Issues:**
- Changes must be applied in multiple places
- Inconsistency risk when templates diverge
- Maintenance burden increases with process count

### Solution: Single Source of Truth
Establish one canonical template and reference it:

```
processes/update-plan/artifact/sections/plan.md:
    ## Implementation Plan
    {% for step in implementation_steps %}
    {{ loop.index }}. {{ step }}
    {% endfor %}

processes/create-ticket/artifact/content.md:
    {% include 'artifact-template://update-plan/sections/plan' %}
```

**Benefits:**
- One location to update
- Automatic propagation of changes
- Guaranteed consistency

## Semantic URI Overview

Pantheon uses **semantic URIs** to reference assets within team packages while maintaining sandboxing boundaries. For complete URI scheme details, see [Semantic URI Reference](./semantic-uri-reference.md).

**Key URI Schemes:**
- `process-schema://` - Import schemas from other processes
- `artifact-template://` - Include Jinja2 templates
- `artifact-locator://` - Share artifact finding configuration
- `artifact-parser://` - Share ID normalization rules
- `artifact-sections://` - Import section configuration

**Example:**
```jinja2
{% include 'artifact-template://update-guide/sections/overview' %}
```

For schema composition patterns and Jsonnet usage, see [Jsonnet Schemas Guide](./jsonnet-schemas-guide.md).

## Artifact Configuration Reuse

### Pattern: Shared Locator and Parser

**Use Case:** UPDATE and GET use identical artifact finding logic

**GET Process:**
```jsonnet
// processes/get-ticket/artifact/locator.jsonnet
{
  directory: "tickets",
  local id = std.extVar("pantheon_artifact_id"),
  pattern: "^" + id + "-.*[.]md$"
}
```

```jsonnet
// processes/get-ticket/artifact/parser.jsonnet
[
  {
    pattern: "^\\s+|\\s+$",
    replacement: ""
  },
  {
    pattern: "^[Tt]?(\\d{3})$",
    replacement: "T$1"
  }
}
```

**UPDATE Process (Reuses GET Configuration):**
```jsonnet
// processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"
```

```jsonnet
// processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

**Benefits:**
- Guaranteed consistency between GET and UPDATE
- Single location for finding logic changes
- No duplication of search patterns

### Pattern: Section Target Import

**Use Case:** UPDATE targets sections defined in GET

**GET Process:**
```jsonnet
// processes/get-ticket/artifact/sections.jsonnet
{
  "sections": {
    "plan": {
      "start": "<!-- START_SECTION:plan -->",
      "end": "<!-- END_SECTION:plan -->"
    },
    "status": {
      "start": "<!-- START_SECTION:status -->",
      "end": "<!-- END_SECTION:status -->"
    }
  }
}
```

**UPDATE Process:**
```jsonnet
// processes/update-ticket/artifact/target.jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```

**Result:** UPDATE targets exact section markers defined in GET

## Template Include Patterns

### Pattern: Section Template Includes

**Use Case:** CREATE includes section templates from UPDATE

**UPDATE Process Section Template:**
```jinja2
<!-- processes/update-guide/artifact/sections/overview.md -->

## Overview

{{ overview_text }}

**Key Points:**
{% for point in key_points %}
- {{ point }}
{% endfor %}

**Updated:** {{ pantheon_timestamp }} by {{ pantheon_actor }}
```

**CREATE Process Content Template:**
```jinja2
<!-- processes/create-guide/artifact/content.md -->
# {{ title }}

**Created:** {{ pantheon_timestamp }} by {{ pantheon_actor }}

{% include 'artifact-template://update-guide/sections/overview' %}

{% include 'artifact-template://update-guide/sections/details' %}

{% include 'artifact-template://update-guide/sections/conclusion' %}
```

**Benefits:**
- Section content defined once in UPDATE process
- CREATE and UPDATE use identical section formatting
- Changes to sections propagate automatically

### Pattern: Section Enabling/Disabling with Semantic URIs

**Use Case:** CREATE process with configurable optional sections that maintain single source of truth via semantic URI imports

This sophisticated pattern combines schema composition with template composition to provide easy human configuration of which sections to enable in CREATE processes. BUILD processes auto-generate this structure.

**Schema Layer (processes/create-ticket/schema.jsonnet):**
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

// Combine properties from enabled sections only
local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.schema.properties else acc,
  sections,
  {}
);

// Combine required fields from enabled sections only
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

**Template Layer (processes/create-ticket/artifact/content.md):**
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

1. **DRY Principle**: Section content defined once in UPDATE process, imported via semantic URIs
2. **Synchronized Configuration**: Schema and template stay in sync - both use boolean flags
3. **Easy Human Configuration**: Toggle `enabled` flag in schema and `_include_*` variable in template
4. **Placeholder Support**: Disabled sections get placeholders for future UPDATE operations
5. **Maintainability**: Changes to section content automatically propagate to CREATE process
6. **Profile Integration**: Can wrap section blocks with profile conditionals for environment-specific behavior

**Configuration Workflow:**

To enable a section, update both files:

1. **Schema**: Change `enabled: false` to `enabled: true`
2. **Template**: Change `{% set _include_section_name = false %}` to `{% set _include_section_name = true %}`

**Why Two Flags?**

- **Schema flag (`enabled`)**: Controls whether section fields appear in data contract
- **Template flag (`_include_*`)**: Controls whether initial content is rendered or placeholder is used

This separation allows for scenarios where:
- Section structure exists (schema enabled) but starts empty (template disabled) → placeholder for later updates
- Section is fully populated initially (both enabled) → content rendered on CREATE

**Auto-Generation:**

BUILD processes automatically generate this pattern when scaffolding process families. See [BUILD Processes](../process-model/build-processes.md) and [Jinja2 Templates Guide](./jinja2-templates-guide.md) for implementation details.

### Pattern: Conditional Include

**Use Case:** Optional sections based on data presence

```jinja2
{% if technical_details %}
{% include 'artifact-template://shared/technical-section' %}
{% endif %}

{% if testing_notes %}
{% include 'artifact-template://shared/testing-section' %}
{% endif %}
```

### Pattern: Dynamic Include with Loop

**Use Case:** Include multiple sections dynamically

```jinja2
{% for section_name in section_order %}
    {% set template_path = "artifact-template://update-guide/sections/" ~ section_name %}
    {% include template_path ignore missing with context %}
{% endfor %}
```

## Routine Composition Patterns

### Pattern: Section Routine Includes

**Use Case:** Modular routine instructions for different sections

**Main Routine:**
```jinja2
<!-- processes/update-blueprint/routine.md -->
# Update Blueprint Process

**Objective:** Update specific sections of the blueprint.

## Steps

{% set pantheon_routine_step = {'num': 1} %}

Step {{ pantheon_routine_step.num }}. **Validate:** Ensure required inputs provided.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}

{% if pantheon_sections %}
{% for section in pantheon_sections %}
    {% include 'routine/sections/' ~ section ~ '.md' ignore missing with context %}
{% endfor %}
{% endif %}

Step {{ pantheon_routine_step.num }} (finish). **Execute:** Complete update.
```

**Section Routine:**
```jinja2
<!-- processes/update-blueprint/routine/sections/analysis.md -->
Step {{ pantheon_routine_step.num }}. **Extract Metrics:** Gather quantitative data.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}

Step {{ pantheon_routine_step.num }}. **Identify Patterns:** Find trends.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}
```

**Benefits:**
- Section-specific instructions modularized
- Reusable across different workflows
- Selective execution via `--sections` flag

### Pattern: Process Redirection

**Use Case:** Specialized process delegates to general process

**Redirect File:**
```markdown
<!-- processes/get-plan/redirect.md -->
process://get-ticket?pantheon_sections=plan
```

**Result:** Executing `get-plan` automatically executes `get-ticket` with `--sections plan`

**Benefits:**
- No routine duplication
- Specialized processes built from general ones
- Parameter forwarding maintained

## Multi-Level Composition

### Pattern: Layered Template Composition

**Use Case:** Complex documents with nested includes

**Level 1 (Main Template):**
```jinja2
<!-- processes/create-report/artifact/content.md -->
# {{ report_title }}

{% include 'artifact-template://shared/report-header' %}

{% include 'artifact-template://shared/report-body' %}

{% include 'artifact-template://shared/report-footer' %}
```

**Level 2 (Body Template):**
```jinja2
<!-- processes/shared/artifact/report-body.md -->
## Executive Summary
{% include 'artifact-template://shared/summary-section' %}

## Detailed Analysis
{% include 'artifact-template://shared/analysis-section' %}
```

**Level 3 (Section Templates):**
```jinja2
<!-- processes/shared/artifact/summary-section.md -->
{{ executive_summary }}

**Key Findings:**
{% for finding in key_findings %}
- {{ finding }}
{% endfor %}
```

**Benefits:**
- Deep composition hierarchy
- Highly reusable components
- Flexible document assembly

### Pattern: Schema Composition Chains

**Use Case:** Hierarchical schema inheritance

**Base Schema:**
```jsonnet
// processes/base-artifact/schema.jsonnet
{
  type: 'object',
  properties: {
    id: { type: 'string' },
    title: { type: 'string' }
  },
  required: ['id', 'title']
}
```

**Intermediate Schema:**
```jsonnet
// processes/document-artifact/schema.jsonnet
local baseSchema = import "process-schema://base-artifact";

baseSchema + {
  properties+: {
    content: { type: 'string' },
    author: { type: 'string' }
  },
  required+: ['content']
}
```

**Specialized Schema:**
```jsonnet
// processes/technical-document/schema.jsonnet
local documentSchema = import "process-schema://document-artifact";

documentSchema + {
  properties+: {
    technical_level: {
      type: 'string',
      enum: ['beginner', 'intermediate', 'advanced']
    }
  }
}
```

**Result:** `technical-document` inherits from `document-artifact` which inherits from `base-artifact`

## Convention Over Configuration

### Workspace Resolution

The Pantheon Workspace automatically resolves semantic URIs using conventions:

**Convention Mapping:**
```
process-schema://create-ticket
  → processes/create-ticket/schema.jsonnet

artifact-template://update-guide/sections/overview
  → processes/update-guide/artifact/sections/overview.md

artifact-locator://get-ticket
  → processes/get-ticket/artifact/locator.jsonnet
```

**No Configuration Required:**
- No registration of imports
- No manifest files
- Runtime discovery via conventions

### Custom Jinja2 Loader

The framework provides a `SemanticUriLoader` that:
- Resolves `artifact-template://` URIs
- Maintains architectural boundaries
- Integrates with Workspace for path resolution
- Enables transparent cross-process includes

## Best Practices

### 1. Establish Single Sources of Truth
**Pattern:**
- UPDATE process sections are canonical
- CREATE includes from UPDATE
- GET/UPDATE share artifact configuration

### 2. Use Semantic URIs Over Relative Paths
**Good:**
```jsonnet
import "process-schema://create-ticket"
```

**Bad:**
```jsonnet
import "../create-ticket/schema.jsonnet"
```

**Rationale:** Semantic URIs are portable and maintain abstraction

### 3. Section Schemas Without $schema Header
```jsonnet
// Section fragments for import only
{
  type: 'object',
  properties: { ... }
}
```

### 4. Always Use with context in Routine Includes
```jinja2
{% include 'routine/sections/analysis.md' with context %}
```

Ensures variables like `pantheon_routine_step` propagate correctly

### 5. Use ignore missing for Optional Components
```jinja2
{% include 'artifact-template://optional/section' ignore missing %}
```

Prevents errors when optional templates don't exist

### 6. Document Composition Dependencies
```markdown
<!-- This template includes:
- artifact-template://update-guide/sections/overview
- artifact-template://update-guide/sections/details
-->
```

## Testing Composition

### Verify Import Resolution
```bash
# Test schema import
pantheon get schema update-ticket --actor test-agent

# Verify includes render
pantheon execute create-guide --from-file test-data.json --actor test-agent
```

### Test Cross-Process Consistency
```bash
# CREATE and UPDATE should use same section formatting
pantheon execute create-ticket --from-file create-data.json --actor test-agent
pantheon execute update-plan --from-file update-data.json --actor test-agent

# Compare section content structure
```

### Validate Semantic URI Resolution
```bash
# Test process with imports
pantheon execute update-ticket --from-file data.json --actor test-agent

# Check logs for resolution errors
```

## Related Documentation

- [Templating System Overview](overview.md) - Three-part templating architecture
- [Semantic URI Reference](./semantic-uri-reference.md) - Complete URI scheme documentation
- [Jsonnet Schemas Guide](./jsonnet-schemas-guide.md) - Schema composition patterns
- [Jinja2 Templates Guide](./jinja2-templates-guide.md) - Artifact content templates (once created)
- [Routine Templates](routine-templates.md) - Routine instruction templates

---

Template composition patterns eliminate duplication and establish single sources of truth across process families. By leveraging semantic URIs, includes, and imports, you create maintainable, consistent processes that adapt to changes automatically while maintaining clear architectural boundaries.
