---
doc_id: jinja2-syntax-reference
title: "Jinja2 Syntax Reference"
description: "Quick reference for Jinja2 template syntax including variables, control structures, filters, and includes."
keywords: [jinja2, syntax, reference, filters, loops, conditionals]
relevance: "Use this reference when you need to look up Jinja2 syntax, filters, or control structures while writing templates."
---

# Jinja2 Syntax Reference

This is a quick reference for Jinja2 template syntax used in Pantheon artifact templates. For comprehensive guidance on using templates in processes, see [Jinja2 Templates Guide](./jinja2-templates-guide.md).

## Variable Substitution

Basic variable output and property access:

```jinja2
{{ variable_name }}                    # Simple variable
{{ nested.property }}                  # Nested object property
{{ list_variable[0] }}                # List index access
{{ dictionary['key'] }}               # Dictionary key access
```

**Examples:**
```jinja2
{{ title }}
{{ pantheon_active_profile.team_name }}
{{ implementation_steps[0] }}
{{ metadata['status'] }}
```

## Control Structures

### Conditionals

If/elif/else statements for conditional content:

```jinja2
{% if condition %}
Content when true
{% elif other_condition %}
Content when other is true
{% else %}
Content when false
{% endif %}
```

**Examples:**
```jinja2
{% if dependencies %}
## Dependencies
{{ dependencies }}
{% endif %}

{% if pantheon_active_profile.verbosity == 'detailed' %}
## Detailed Context
{{ detailed_context }}
{% elif pantheon_active_profile.verbosity == 'minimal' %}
{{ summary }}
{% else %}
{{ standard_content }}
{% endif %}
```

**Common Conditions:**
```jinja2
{% if variable %}                      # Truthy check
{% if not variable %}                  # Falsy check
{% if variable == 'value' %}           # Equality
{% if variable != 'value' %}           # Inequality
{% if variable in list %}              # Membership
{% if variable and other %}            # Logical AND
{% if variable or other %}             # Logical OR
```

### Loops

Iterate over lists and dictionaries:

**List Iteration:**
```jinja2
{% for item in items %}
- {{ item }}
{% endfor %}
```

**Dictionary Iteration:**
```jinja2
{% for key, value in dictionary.items() %}
{{ key }}: {{ value }}
{% endfor %}
```

**Loop Variables:**
```jinja2
{% for item in items %}
{{ loop.index }}. {{ item }}          # 1-based index
{{ loop.index0 }}. {{ item }}         # 0-based index
{{ loop.first }}                      # True on first iteration
{{ loop.last }}                       # True on last iteration
{{ loop.length }}                     # Total number of items
{% endfor %}
```

**Example:**
```jinja2
{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% if loop.last %}
Total steps: {{ loop.length }}
{% endif %}
{% endfor %}
```

## Filters

Filters transform variable output using the pipe (`|`) operator.

### Text Transformation

```jinja2
{{ title | lower }}                   # Lowercase: "hello world"
{{ title | upper }}                   # Uppercase: "HELLO WORLD"
{{ title | capitalize }}              # Capitalize first letter: "Hello world"
{{ title | title }}                   # Title Case: "Hello World"
{{ text | trim }}                     # Remove whitespace
{{ title | replace(' ', '-') }}       # String replacement
```

**Example:**
```jinja2
T{{ artifact_id }}_{{ title | lower | replace(' ', '-') | replace('/', '-') }}.md
```

### Default Values

Provide fallback values for undefined or empty variables:

```jinja2
{{ optional_field | default('N/A') }}
{{ optional_field | default('N/A', true) }}  # Also for empty strings
```

**Examples:**
```jinja2
**Priority**: {{ priority | default('medium') }}
**Estimated Effort**: {{ effort | default('TBD') }}
```

### List Operations

```jinja2
{{ items | join(', ') }}              # Join list items: "a, b, c"
{{ items | length }}                  # List length: 3
{{ items | first }}                   # First item
{{ items | last }}                    # Last item
{{ items | sort }}                    # Sort list
{{ items | reverse }}                 # Reverse list
```

**Examples:**
```jinja2
**Tags**: {{ tags | join(', ') }}
**Total Items**: {{ items | length }}
```

### Chaining Filters

Apply multiple filters in sequence:

```jinja2
{{ title | lower | replace(' ', '-') | trim }}
{{ text | default('N/A') | upper }}
{{ items | sort | join(', ') }}
```

### Common Filter Combinations

**Filename sanitization:**
```jinja2
{{ title | lower | replace(' ', '-') | replace('/', '-') | replace('\\', '-') }}
```

**Safe display with fallback:**
```jinja2
{{ description | default('No description provided') | trim }}
```

**List formatting:**
```jinja2
{% if tags %}
**Tags**: {{ tags | sort | join(', ') }}
{% endif %}
```

## Includes

Include other templates for composition and reuse.

### Basic Include

```jinja2
{% include 'sections/header.md' %}
```

### Conditional Include

Ignore errors if template doesn't exist:

```jinja2
{% include 'sections/optional.md' ignore missing %}
```

### Include with Context

Pass variables to included template:

```jinja2
{% include 'sections/details.md' with context %}
```

### Dynamic Include

Construct template path at runtime:

```jinja2
{% set template_name = "sections/" ~ section ~ ".md" %}
{% include template_name ignore missing %}
```

### Semantic URI Includes

Include templates from other processes:

```jinja2
{% include 'artifact-template://update-guide/sections/overview' %}
{% include 'artifact-template://shared/common-footer' %}
```

See [Semantic URI Reference](./semantic-uri-reference.md) for complete URI documentation.

## Comments

Comments are removed from template output:

**Single-line comment:**
```jinja2
{# This is a comment and will not appear in output #}
```

**Multi-line comment:**
```jinja2
{#
Multi-line comment
for longer explanations
#}
```

**Example with inline comments:**
```jinja2
{% set _include_plan = true %}  {# Enable plan section #}
```

## Variable Assignment

Set local template variables:

```jinja2
{% set variable_name = value %}
{% set path = "sections/" ~ section ~ ".md" %}
{% set enabled = true %}
```

**Examples:**
```jinja2
{% set _include_technical_plan = false %}
{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}
{% set template_path = "artifact-template://update-guide/sections/" ~ section_name %}
```

## Whitespace Control

Control whitespace in template output:

```jinja2
{% if condition -%}           # Remove whitespace after
No leading whitespace
{%- endif %}                  # Remove whitespace before

{% for item in items -%}
{{ item }}
{%- endfor %}
```

## Escaping

Output Jinja2 syntax literally:

```jinja2
{% raw %}
{{ variable }}  # This will appear as-is, not substituted
{% endraw %}
```

**Example:**
```jinja2
{% raw %}
To use a variable in Jinja2, write {{ variable_name }}
{% endraw %}
```

## Built-in Tests

Use tests with `is` keyword:

```jinja2
{% if variable is defined %}
{{ variable }}
{% endif %}

{% if variable is undefined %}
Default content
{% endif %}

{% if items is empty %}
No items available
{% endif %}
```

**Common tests:**
- `is defined` - Variable is defined
- `is undefined` - Variable is not defined
- `is none` - Variable is None
- `is empty` - Variable is empty (list, dict, string)
- `is number` - Variable is a number
- `is string` - Variable is a string

## Quick Reference Summary

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ var }}` | Output variable | `{{ title }}` |
| `{% if %}` | Conditional | `{% if condition %}...{% endif %}` |
| `{% for %}` | Loop | `{% for item in items %}...{% endfor %}` |
| `{{ var \| filter }}` | Apply filter | `{{ title \| lower }}` |
| `{% include %}` | Include template | `{% include 'path.md' %}` |
| `{# comment #}` | Comment | `{# Note: This is hidden #}` |
| `{% set %}` | Variable assignment | `{% set x = 5 %}` |

## Common Patterns

### Conditional List Rendering
```jinja2
{% if items %}
**Items**:
{% for item in items %}
- {{ item }}
{% endfor %}
{% else %}
No items available
{% endif %}
```

### Safe Section Rendering
```jinja2
{% if estimated_effort %}
**Estimated Effort**: {{ estimated_effort }}
{% endif %}
```

### Dynamic Section Inclusion
```jinja2
{% for section_name in requested_sections %}
  {% set snippet = "sections/" ~ section_name ~ ".md" %}
  {% include snippet ignore missing with context %}
{% endfor %}
```

### Filename Generation
```jinja2
{{ pantheon_artifact_id }}_{{ title | lower | replace(' ', '-') }}.md
```

## Related Documentation

- [Jinja2 Templates Guide](./jinja2-templates-guide.md) - Comprehensive guide to templates in Pantheon
- [Template Composition Patterns](./template-composition-patterns.md) - Advanced composition techniques
- [Semantic URI Reference](./semantic-uri-reference.md) - URI schemes for cross-process includes

---

This reference covers the most commonly used Jinja2 syntax in Pantheon templates. For detailed usage patterns and best practices, see the [Jinja2 Templates Guide](./jinja2-templates-guide.md).
