---
doc_id: routine-templates
title: "Routine Templates"
description: "Guide to creating routine templates with Jinja2 for step-by-step agent instruction generation."
keywords: [routines, templates, jinja2, workflow, instructions, sections, step-numbering]
relevance: "Use this document to understand how to create routine templates that generate dynamic, section-aware agent instructions."
---

# Routine Templates

Routine templates are Jinja2-based templates that generate **step-by-step agent instructions** for process execution. They enable dynamic instruction generation based on context, section selection, and team profile settings.

## Routine Template Location

Routines can be simple static files or dynamic Jinja2 templates:

### Static Routines
**Location:** `processes/<process-name>/routine.md`
**Format:** Plain Markdown with fixed steps

**Example:**
```markdown
# Update Plan Process

**Objective:** Update the implementation plan section of an existing ticket.

## Steps

Step 1. **Get schema:** Use `pantheon get schema update-plan --actor <your_agent_name>`.

Step 2. **Generate plan content:** Create JSON data following the schema.

Step 3. **Get temp file:** Use `pantheon get tempfile --process update-plan --actor <your_agent_name>`.

Step 4 (finish). **Update plan:** Use `pantheon execute update-plan --from-file {tempfile} --actor <your_agent_name>`.
```

### Dynamic Routine Templates
**Location:** `processes/<process-name>/routine.md` (with Jinja2 syntax)
**Format:** Jinja2 template with conditionals and includes

**Example:**
```jinja2
# Update {{ artifact | title }} Process

**Objective:** Update specific sections of the {{ artifact }} artifact.

## Steps

{% if pantheon_sections is defined %}
Step 1. **Process requested sections:** You will update the following sections: {{ pantheon_sections | join(', ') }}.
{% else %}
Step 1. **Process all sections:** You will update sections in this order: {{ section_order | join(', ') }}.
{% endif %}

Step 2. **Get schema:** Use `pantheon get schema update-{{ artifact }} --actor <your_agent_name>`.

Step 3 (finish). **Execute update:** Use `pantheon execute update-{{ artifact }} --from-file {tempfile} --actor <your_agent_name>`.
```

## Section-Based Routine Composition

UPDATE processes commonly use **section-based routine composition** to modularize instructions for different sections:

### Main Routine Template Structure

**Location:** `processes/update-artifact/routine.md`

```jinja2
# Update Artifact Process

**Objective:** Update specific sections of the artifact with new content.

## Steps

Step 1. **Validate inputs:** Ensure required parameters are provided.

{% if pantheon_sections is defined %}
{% for section in pantheon_sections %}
    {% set snippet = "routine/sections/" ~ section ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
{% endif %}

Step {{ pantheon_routine_step.num }} (finish). **Execute update:** Use `pantheon execute update-artifact --from-file {tempfile} --actor <your_agent_name>`.
```

### Section Routine Fragment Structure

**Location:** `processes/update-artifact/routine/sections/<section-name>.md`

**Pattern:**
```jinja2
Step {{ _current_step_index.num }}. **Section Title:** Brief description of what this step accomplishes.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Next Action:** Description of the next step.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

**Example (routine/sections/analysis.md):**
```jinja2
Step {{ _current_step_index.num }}. **Extract Key Metrics:** Identify quantitative data points from the provided context that will inform the analysis.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Identify Patterns:** Look for recurring themes, trends, or anomalies in the data.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Generate Insights:** Synthesize the metrics and patterns into actionable insights.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

## Step Numbering Pattern

Routine templates use the `_current_step_index` namespace variable for seamless step numbering across sections:

### The _current_step_index Variable

**Type:** Jinja2 namespace object with `num` property
**Purpose:** Maintains step counter across template includes
**Usage Pattern:**
```jinja2
Step {{ _current_step_index.num }}. **Step Name:** Description.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

**Note**: Use `_current_step_index = namespace(num=1)` for initialization, not a dict. The namespace object ensures the variable remains mutable across includes.

### Why This Pattern Works

Traditional approach (broken):
```jinja2
{# This breaks with includes - each include resets loop.index #}
{% for step in steps %}
Step {{ loop.index }}. {{ step }}
{% endfor %}
```

Pantheon approach (works):
```jinja2
{# Shared mutable namespace object persists across includes #}
{% set _current_step_index = namespace(num=1) %}

Step {{ _current_step_index.num }}. **Main Step:** Description.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% include 'routine/sections/analysis.md' with context %}

{# Step numbering continues seamlessly after include #}
Step {{ _current_step_index.num }}. **Final Step:** Description.
```

### Complete Example

**Main routine.md:**
```jinja2
# Update Blueprint Process

**Objective:** Update sections of the blueprint document.

## Steps

{% set pantheon_routine_step = {'num': 1} %}

Step {{ pantheon_routine_step.num }}. **Validate inputs:** Ensure ticket ID is provided.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}

{% if pantheon_sections is defined %}
{% for section in pantheon_sections %}
    {% set snippet = "routine/sections/" ~ section ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
{% endif %}

Step {{ pantheon_routine_step.num }} (finish). **Execute update:** Use `pantheon execute update-blueprint --from-file {tempfile}`.
```

**routine/sections/overview.md:**
```jinja2
Step {{ pantheon_routine_step.num }}. **Review current overview:** Read existing overview content.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}

Step {{ pantheon_routine_step.num }}. **Draft new overview:** Write updated overview content.
{% set pantheon_routine_step.num = pantheon_routine_step.num + 1 %}
```

**Rendered output when `--sections overview`:**
```markdown
# Update Blueprint Process

**Objective:** Update sections of the blueprint document.

## Steps

Step 1. **Validate inputs:** Ensure ticket ID is provided.

Step 2. **Review current overview:** Read existing overview content.

Step 3. **Draft new overview:** Write updated overview content.

Step 4 (finish). **Execute update:** Use `pantheon execute update-blueprint --from-file {tempfile}`.
```

## Built-in Template Variables

Routine templates have access to framework-injected variables:

### Common Variables (All Process Types)
- `{{ pantheon_actor }}` - Executing agent name
- `{{ pantheon_timestamp }}` - Full ISO timestamp
- `{{ pantheon_datestamp }}` - Date-only timestamp
- `{{ pantheon_artifact_id }}` - Artifact identifier
- `{{ pantheon_profile }}` - Team profile object

### UPDATE Process Variables
- `{{ section_order }}` - Array of section names in defined order
- `{{ initial_section }}` - First section in `section_order`
- `{{ artifact }}` - Artifact name extracted from process name (e.g., `update-ticket` → `"ticket"`)
- `{{ pantheon_sections }}` - Sections specified via `--sections` flag

### Section Routine Variables
- `{{ _current_step_index }}` - Namespace object with `num` property for step numbering
- All variables from parent routine (via `with context`)

### Example Usage

```jinja2
{% if initial_section %}
Step 1. **Initialize Update:** Begin updating the {{ artifact }} artifact, starting with the {{ initial_section }} section.
{% endif %}

{% if section_order %}
Available sections for this artifact: {{ section_order | join(", ") }}
{% endif %}

{% if pantheon_sections %}
Processing requested sections: {{ pantheon_sections | join(", ") }}
{% endif %}
```

## Conditional Workflow Logic

Routine templates can include conditional logic for different execution paths:

### Conditional Section Processing

```jinja2
{% if pantheon_sections is defined %}
{% for section in pantheon_sections %}
    {# Only include if section routine exists #}
    {% set snippet = "routine/sections/" ~ section ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
{% else %}
{# Default: process all sections in order #}
{% for section in section_order %}
    {% set snippet = "routine/sections/" ~ section ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
{% endif %}
```

### Profile-Aware Instructions

```jinja2
{% if pantheon_profile.verbosity == 'detailed' %}
Step 2. **Comprehensive Analysis:** Perform detailed analysis including:
- Historical context review
- Stakeholder impact assessment
- Risk evaluation
- Alternative approaches consideration
{% else %}
Step 2. **Quick Analysis:** Review key points and proceed with implementation.
{% endif %}
```

### Parameter-Based Branching

```jinja2
{% if pantheon_sections and 'testing' in pantheon_sections %}
Step 3. **Test Strategy:** Since testing section is requested, prepare comprehensive test plan.
{% else %}
Step 3. **Proceed:** Continue with implementation.
{% endif %}
```

## Include Directives

Routine templates use Jinja2 include directives for composition:

### Basic Include
```jinja2
{% include 'routine/sections/analysis.md' %}
```

### Conditional Include
```jinja2
{% include 'routine/sections/optional.md' ignore missing %}
```

The `ignore missing` directive prevents errors if the section routine doesn't exist.

### Include with Context
```jinja2
{% include 'routine/sections/analysis.md' with context %}
```

The `with context` directive passes all parent template variables to the included template, essential for `_current_step_index` continuity.

### Dynamic Include
```jinja2
{% set section_name = "analysis" %}
{% set snippet = "routine/sections/" ~ section_name ~ ".md" %}
{% include snippet ignore missing with context %}
```

## CLI Integration

Routine templates respond to CLI flags:

### --sections Flag

**Command:**
```bash
pantheon execute update-blueprint --sections intro,analysis --actor architect
```

**Template Response:**
```jinja2
{% if pantheon_sections %}
Processing sections: {{ pantheon_sections | join(', ') }}
{# pantheon_sections = ['intro', 'analysis'] #}
{% endif %}
```

### --actor Flag

**Command:**
```bash
pantheon execute create-ticket --actor tech-lead
```

**Template Response:**
```jinja2
Step 1. **Authenticate:** You are executing as {{ pantheon_actor }}.
{# pantheon_actor = 'tech-lead' #}
```

### --id Flag

**Command:**
```bash
pantheon execute get-ticket --id T042 --actor engineer
```

**Template Response:**
```jinja2
Step 1. **Retrieve ticket:** Fetch ticket {{ pantheon_artifact_id }}.
{# pantheon_artifact_id = 'T042' #}
```

## Best Practices

### 1. Use Consistent Step Numbering
**Always use `_current_step_index` pattern:**
```jinja2
Step {{ _current_step_index.num }}. **Step Name:** Description.
{% set _current_step_index.num = _current_step_index.num + 1 %}
```

### 2. Include Context in Includes
**Always use `with context`:**
```jinja2
{% include 'routine/sections/section.md' with context %}
```

This ensures step numbering and other variables flow correctly.

### 3. Use ignore missing for Optional Sections
```jinja2
{% include 'routine/sections/optional.md' ignore missing with context %}
```

Prevents errors for sections that may not exist.

### 4. Provide Clear Objectives
```jinja2
# Process Name

**Objective:** Single sentence describing what this process accomplishes.
```

### 5. Guide Agent Cognition
Break complex tasks into logical cognitive steps:
```jinja2
Step 2. **Analyze Requirements:** Review the business context and technical constraints.

Step 3. **Design Approach:** Based on your analysis, outline the implementation strategy.

Step 4. **Detail Implementation:** Break down the approach into specific steps.
```

### 6. Terminate with (finish) Marker
```jinja2
Step {{ _current_step_index.num }} (finish). **Submit:** Execute the process. You are now done.
```

This signals clear workflow termination to agents.

## Testing Routine Templates

### Manual Testing

**Get rendered routine:**
```bash
pantheon get process update-blueprint --actor architect
```

**Test with sections flag:**
```bash
pantheon get process update-blueprint --sections intro,analysis --actor architect
```

**Verify step numbering:**
Check that steps increment properly across main routine and section includes.

### Common Template Errors

**Undefined Variable:**
```
jinja2.exceptions.UndefinedError: 'pantheon_sections' is undefined
```
**Solution:** Use `{% if pantheon_sections is defined %}` guard

**Step Numbering Reset:**
```
Steps restart at 1 after include
```
**Solution:** Ensure `with context` in include directive

**Include Not Found:**
```
jinja2.exceptions.TemplateNotFound: routine/sections/missing.md
```
**Solution:** Add `ignore missing` or verify file exists

## Related Documentation

- [Templating System Overview](overview.md) - Three-part templating architecture
- [Built-in Variables](built-in-variables.md) - Framework-injected variables reference
- [Creating Routines](../routine-system/authoring-practices.md) - Best practices for routine design
- [Routine System Philosophy](../routine-system/philosophy.md) - Understanding routine structure and syntax

---

Routine templates enable dynamic, context-aware instruction generation that guides agents through complex workflows. By using section-based composition and proper step numbering patterns, you create maintainable, reusable instruction components that adapt to different execution contexts.
