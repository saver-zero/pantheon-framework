---
doc_id: templating-built-in-variables
title: "Built-in Template Variables"
description: "Comprehensive reference for framework-injected variables available in Jinja2 artifact templates, Jsonnet schemas, and routine templates."
keywords: [variables, templates, built-in, pantheon, framework, context, injection]
relevance: "Use this document to understand all framework-injected variables available in templates and their usage patterns."
---

# Built-in Template Variables

The Pantheon Framework automatically injects variables into templates during rendering. These built-in variables provide access to execution context, metadata, and framework state without requiring manual configuration.

## Variable Categories

Variables are organized into three categories based on availability:

### 1. Common Variables (All Template Types)
Available in artifact templates, routine templates, and accessible via profile in schemas

### 2. UPDATE Process Variables
Available only in UPDATE process routines and templates

### 3. Section Routine Variables
Available only in section-based routine fragments

## Common Variables

These variables are available in **all templates** regardless of process type:

### pantheon_actor
**Type:** `string`
**Description:** The name of the agent executing the process
**Source:** `--actor` CLI flag
**Use Cases:** Audit trails, authorship tracking, conditional logic based on agent role

**Example (Artifact Template):**
```jinja2
**Created By:** {{ pantheon_actor }}
**Last Modified By:** {{ pantheon_actor }}
```

**Example (Routine Template):**
```jinja2
Step 1. **Authenticate:** You are executing as {{ pantheon_actor }}.
```

### pantheon_timestamp
**Type:** `string` (ISO 8601 format)
**Description:** Full timestamp when the process was invoked
**Format:** `YYYY-MM-DDTHH:MM:SS.ffffffZ`
**Example Value:** `2024-01-15T10:30:45.123456Z`

**Use Cases:** Audit trails, version tracking, temporal ordering

**Example:**
```jinja2
**Created:** {{ pantheon_timestamp }}
**Last Updated:** {{ pantheon_timestamp }} by {{ pantheon_actor }}
```

### pantheon_datestamp
**Type:** `string` (ISO 8601 date format)
**Description:** Date-only timestamp when the process was invoked
**Format:** `YYYY-MM-DD`
**Example Value:** `2024-01-15`

**Use Cases:** Daily logs, date-based file organization, summaries

**Example (File Naming):**
```jinja2
logs/{{ pantheon_actor }}/{{ pantheon_datestamp }}_activity.jsonl
```

**Example (Content):**
```jinja2
## Daily Summary - {{ pantheon_datestamp }}

Activity performed by {{ pantheon_actor }}
```

### pantheon_artifact_id
**Type:** `string`
**Description:** Unique identifier for the artifact being created or updated
**Source:** `--id` CLI flag or auto-generated counter
**Format:** Typically numeric (e.g., `"042"`) or alphanumeric based on configuration

**Use Cases:** File naming, cross-references, artifact identification

**Example (File Naming):**
```jinja2
T{{ pantheon_artifact_id }}_{{ title | lower | replace(' ', '-') }}.md
```

**Example (Content):**
```jinja2
**ID:** T{{ pantheon_artifact_id }}
**Reference:** Use T{{ pantheon_artifact_id }} to reference this ticket
```

### pantheon_active_profile
**Type:** `object`
**Description:** Team profile settings object with all configuration properties
**Access:** Direct property access via dot notation
**Available In:** Artifact templates, routine templates (limited use in schemas via `std.extVar('profile')`)

**Note**: The actual variable name in templates is `pantheon_active_profile`, not `pantheon_profile`. This distinguishes the runtime active profile from the profile configuration structure.

**Common Properties:**
- `pantheon_active_profile.team_name` - Team identifier
- `pantheon_active_profile.verbosity` - Verbosity level (`'concise'`, `'detailed'`)
- `pantheon_active_profile.output_format` - Preferred output format
- Custom properties defined in `team-profile.yaml`

**Use Cases:** Conditional formatting, team-specific content, output customization

**Example (Conditional Content):**
```jinja2
{% if pantheon_active_profile.verbosity == 'detailed' %}
## Detailed Technical Context
{{ technical_context }}

## Implementation Notes
{{ implementation_notes }}
{% else %}
## Technical Context
{{ technical_context }}
{% endif %}
```

**Example (Custom Properties):**
```jinja2
{% if pantheon_active_profile.include_metadata %}
**Team:** {{ pantheon_active_profile.team_name }}
**Profile:** {{ pantheon_active_profile.verbosity }}
{% endif %}
```

**Best Practice:** Prefer controlling behavior via schemas rather than templates (see Smart Schema, Dumb Template pattern). Use `pantheon_active_profile` in templates only for pure formatting changes.

## UPDATE Process Variables

These variables are automatically injected into **UPDATE process routines** by analyzing the process schema:

### section_order
**Type:** `array` of `string`
**Description:** Ordered list of section names for the artifact
**Source:** Extracted from schema's `section_order.default` property or keys of `section_updates.properties`
**Use Cases:** Displaying available sections, default section processing order

**Example:**
```jinja2
{% if section_order %}
Available sections for this artifact: {{ section_order | join(", ") }}
{# Output: Available sections for this artifact: plan, analysis, conclusion #}
{% endif %}
```

### initial_section
**Type:** `string`
**Description:** The first section in `section_order`
**Source:** Automatically set to `section_order[0]`
**Use Cases:** Default section operations, initial processing guidance

**Example:**
```jinja2
{% if initial_section %}
Step 1. **Initialize Update:** Begin updating the {{ artifact }} artifact, starting with the {{ initial_section }} section.
{% endif %}
```

### artifact
**Type:** `string`
**Description:** Artifact name extracted from the process name
**Source:** Process name pattern `update-{artifact}` → `artifact` value
**Example:** `update-ticket` → `artifact = "ticket"`

**Use Cases:** Dynamic routine text, referencing artifact type

**Example:**
```jinja2
# Update {{ artifact | title }} Process

**Objective:** Update specific sections of the {{ artifact }} artifact.
```

### pantheon_sections
**Type:** `array` of `string` (optional)
**Description:** List of sections requested via `--sections` CLI flag
**Source:** `--sections` CLI parameter
**Availability:** Only present when `--sections` flag is used
**Use Cases:** Selective section processing, conditional workflow logic

**Example:**
```jinja2
{% if pantheon_sections %}
Processing requested sections: {{ pantheon_sections | join(", ") }}
{% else %}
Processing all sections in default order: {{ section_order | join(", ") }}
{% endif %}
```

**Example (Conditional Include):**
```jinja2
{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}

{% for section_name in requested_sections %}
    {% set snippet = "routine/sections/" ~ section_name ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
```

## Section Routine Variables

These variables are available in **section routine fragments** (`routine/sections/*.md`):

### _current_step_index
**Type:** `namespace` object with `num` property
**Description:** Jinja2 namespace object for maintaining step numbering across section boundaries
**Properties:**
- `_current_step_index.num` - Current step number (integer)

**Note**: Actual implementation uses `_current_step_index` (with namespace) rather than `pantheon_routine_step` (with dict). The namespace approach is the correct Jinja2 pattern for mutable values in includes.

**Use Cases:** Seamless step numbering in modular routines

**Pattern:**
```jinja2
Step {{ _current_step_index.num }}. **Step Name:** Description.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

**Complete Example:**

**Main routine.md:**
```jinja2
{% set _current_step_index = namespace(num=1) %}

Step {{ _current_step_index.num }}. **Main Step:** Description.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% include 'routine/sections/analysis.md' with context %}

Step {{ _current_step_index.num }} (finish). **Final Step:** Complete.
```

**routine/sections/analysis.md:**
```jinja2
Step {{ _current_step_index.num }}. **Analyze:** Perform analysis.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Synthesize:** Create synthesis.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

**Rendered Output:**
```markdown
Step 1. **Main Step:** Description.

Step 2. **Analyze:** Perform analysis.

Step 3. **Synthesize:** Create synthesis.

Step 4 (finish). **Final Step:** Complete.
```

## Variable Injection Mechanism

### When Variables Are Injected

**Common Variables:**
- Injected during all template rendering operations
- Available immediately when template engine initializes

**UPDATE Process Variables:**
- Injected during routine retrieval in `RaeEngine._enrich_update_context()`
- Extracted from schema before routine rendering

**Section Routine Variables:**
- Initialized in main routine template
- Passed to section templates via `with context` directive

### How to Access Variables

**In Jinja2 Templates (Artifact, Routine):**
```jinja2
{{ variable_name }}
{{ pantheon_active_profile.property_name }}
{{ _current_step_index.num }}
```

**In Jsonnet Schemas:**
```jsonnet
local profile = std.extVar('profile');

{
  description: if profile.verbosity == 'detailed' then 'Long' else 'Short'
}
```

**Checking Variable Existence:**
```jinja2
{% if variable_name is defined %}
Variable exists: {{ variable_name }}
{% else %}
Variable not defined
{% endif %}
```

## Variable Usage Patterns

### Audit Trail Pattern
```jinja2
**Created:** {{ pantheon_timestamp }} by {{ pantheon_actor }}
**Last Modified:** {{ pantheon_timestamp }} by {{ pantheon_actor }}
**Artifact ID:** {{ pantheon_artifact_id }}
```

### File Naming Pattern
```jinja2
{{ pantheon_datestamp }}_{{ pantheon_actor }}_{{ artifact_type }}.md
T{{ pantheon_artifact_id }}_{{ title | slugify }}.md
```

### Conditional Processing Pattern
```jinja2
{% if pantheon_sections %}
Processing only: {{ pantheon_sections | join(', ') }}
{% else %}
Processing all sections: {{ section_order | join(', ') }}
{% endif %}
```

### Step Numbering Pattern
```jinja2
{% set _current_step_index = namespace(num=1) %}

Step {{ _current_step_index.num }}. **Action:** Do something.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

### Profile-Aware Formatting Pattern
```jinja2
{% if pantheon_active_profile.output_format == 'json' %}
{{ data | tojson(indent=2) }}
{% elif pantheon_active_profile.output_format == 'yaml' %}
{{ data | toyaml }}
{% else %}
{{ data }}
{% endif %}
```

## Common Pitfalls

### 1. Using Profile in Templates for Business Logic

**Bad:**
```jinja2
{% if pantheon_active_profile.enforce_tdd %}
## Test Strategy
{{ test_strategy }}
{% endif %}
```

**Good (Control via Schema):**
```jsonnet
// In schema.jsonnet
local enforce_tdd = std.extVar('enforce_tdd');

{
  properties: if enforce_tdd then {
    test_strategy: { type: 'string' }
  } else {}
}
```

```jinja2
// In template
{% if test_strategy %}
## Test Strategy
{{ test_strategy }}
{% endif %}
```

### 2. Not Using with context in Includes

**Bad:**
```jinja2
{% include 'routine/sections/analysis.md' %}
{# _current_step_index not passed to include #}
```

**Good:**
```jinja2
{% include 'routine/sections/analysis.md' with context %}
{# All variables including _current_step_index passed #}
```

### 3. Assuming Optional Variables Exist

**Bad:**
```jinja2
Sections: {{ pantheon_sections | join(', ') }}
{# Fails if --sections not provided #}
```

**Good:**
```jinja2
{% if pantheon_sections %}
Sections: {{ pantheon_sections | join(', ') }}
{% else %}
All sections will be processed.
{% endif %}
```

### 4. Hardcoding Values Available as Variables

**Bad:**
```jinja2
**Created:** 2024-01-15 by admin
```

**Good:**
```jinja2
**Created:** {{ pantheon_timestamp }} by {{ pantheon_actor }}
```

## Testing Variable Access

### List Available Variables in Template
```jinja2
{# Temporary debug output #}
<!-- DEBUG VARIABLES
Actor: {{ pantheon_actor }}
Timestamp: {{ pantheon_timestamp }}
Artifact ID: {{ pantheon_artifact_id }}
Active Profile: {{ pantheon_active_profile }}
{% if section_order %}Section Order: {{ section_order }}{% endif %}
{% if pantheon_sections %}Requested Sections: {{ pantheon_sections }}{% endif %}
-->
```

### Test with Different Flags
```bash
# Test with sections flag
pantheon get process update-blueprint --sections intro --actor test-agent

# Test with id flag
pantheon execute get-ticket --id T042 --actor test-agent

# Test with different actors
pantheon execute create-ticket --from-file data.json --actor tech-lead
pantheon execute create-ticket --from-file data.json --actor engineer
```

## Variable Reference Summary

| Variable | Type | Availability | Source |
|----------|------|--------------|--------|
| `pantheon_actor` | string | All templates | `--actor` flag |
| `pantheon_timestamp` | string | All templates | Framework clock |
| `pantheon_datestamp` | string | All templates | Framework clock |
| `pantheon_artifact_id` | string | All templates | `--id` flag or counter |
| `pantheon_active_profile` | object | All templates | Team profile config |
| `section_order` | array | UPDATE routines | Schema analysis |
| `initial_section` | string | UPDATE routines | Schema analysis |
| `artifact` | string | UPDATE routines | Process name parsing |
| `pantheon_sections` | array | UPDATE routines | `--sections` flag |
| `_current_step_index` | namespace | Section routines | Template initialization |

## Related Documentation

- [Templating System Overview](overview.md) - Three-part templating architecture
- [Jinja2 Templates Guide](./jinja2-templates-guide.md) - Artifact content templates
- [Routine Templates](routine-templates.md) - Routine instruction templates
- [Jsonnet Schemas Guide](./jsonnet-schemas-guide.md) - Schema composition

---

Built-in variables provide essential context and metadata to templates, enabling dynamic content generation, audit trails, and conditional logic. Understanding variable availability and proper usage patterns ensures templates leverage framework capabilities effectively while maintaining clean separation of concerns.
