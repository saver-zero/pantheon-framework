---
doc_id: jsonnet-schemas-guide
title: "Jsonnet Schemas Guide"
description: "Comprehensive guide to using Jsonnet for dynamic schema composition, validation, and profile-aware data contracts in Pantheon processes."
keywords: [jsonnet, schemas, validation, composition, profile-aware, data-contracts, schema-inheritance, semantic-uri]
relevance: "Use this document to understand how to create Jsonnet schemas with dynamic composition, profile-aware behavior, and schema inheritance for Pantheon data contracts."
---

# Jsonnet Schemas Guide

Jsonnet schemas are the **data contract layer** of the Pantheon Framework. They define what data agents must provide when executing processes, with support for dynamic composition, profile-aware validation, and schema inheritance.

## Why Jsonnet Over Static JSON?

Pantheon uses **Jsonnet** instead of static JSON Schema files for three key reasons:

### 1. Profile-Aware Composition
Schemas can adapt based on team profile settings:
```jsonnet
local profile = std.extVar('profile');

{
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

### 2. Schema Inheritance and Reuse
Schemas can import and extend other schemas:
```jsonnet
local baseSchema = import "process-schema://create-ticket";

baseSchema + {
  properties+: {
    additional_field: { type: 'string' }
  }
}
```

### 3. Programmatic Composition
Schemas can use functions, variables, and conditional logic:
```jsonnet
local enforce_tdd = std.extVar('enforce_tdd');

local tddFields = if enforce_tdd then {
  properties+: {
    test_file: { type: 'string', description: 'Path to test file' }
  },
  required+: ['test_file']
} else {};

baseSchema + tddFields
```

## Schema Structure

### Basic Schema Pattern

```jsonnet
{
  type: 'object',
  properties: {
    field_name: {
      type: 'string',
      description: 'Human-readable description for agents'
    },
    another_field: {
      type: 'number',
      minimum: 0,
      description: 'Numeric field with validation'
    }
  },
  required: ['field_name']
}
```

### Profile-Aware Schema Pattern

```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    title: {
      type: 'string',
      maxLength: 80,
      description: 'Brief, action-oriented ticket title'
    },
    business_context: {
      type: 'string',
      description: 'Why this work is needed from business perspective'
    },
    technical_context: {
      type: 'string',
      description: if profile.verbosity == 'detailed' then
        'Comprehensive technical background and constraints'
      else
        'Key technical considerations and approach'
    }
  },
  required: ['title', 'business_context', 'technical_context']
}
```

## Schema Composition Patterns

### Profile-Based Conditional Fields

**Pattern: Optional Field Based on Profile**
```jsonnet
local profile = std.extVar('profile');

local baseProperties = {
  title: { type: 'string', description: 'Title' },
  description: { type: 'string', description: 'Description' }
};

local detailedProperties = if profile.verbosity == 'detailed' then {
  technical_notes: {
    type: 'string',
    description: 'Detailed technical implementation notes'
  },
  architectural_context: {
    type: 'string',
    description: 'Broader architectural considerations'
  }
} else {};

{
  type: 'object',
  properties: baseProperties + detailedProperties,
  required: ['title', 'description']
}
```

**Pattern: Conditional Required Fields**
```jsonnet
local profile = std.extVar('profile');
local enforce_tdd = std.extVar('enforce_tdd');

local baseRequired = ['title', 'description'];
local tddRequired = if enforce_tdd then ['test_file'] else [];

{
  type: 'object',
  properties: {
    title: { type: 'string' },
    description: { type: 'string' },
    test_file: { type: 'string', description: 'Path to test file' }
  },
  required: baseRequired + tddRequired
}
```

### Schema Inheritance via Imports

**Base Schema (processes/create-ticket/schema.jsonnet):**
```jsonnet
{
  type: 'object',
  properties: {
    title: { type: 'string', maxLength: 80 },
    business_context: { type: 'string' },
    technical_context: { type: 'string' }
  },
  required: ['title', 'business_context', 'technical_context']
}
```

**Extended Schema (processes/update-ticket/schema.jsonnet):**
```jsonnet
import "process-schema://create-ticket"
```

This imports the entire schema from the CREATE process, ensuring data contract consistency.

**Extended Schema with Additions:**
```jsonnet
local baseSchema = import "process-schema://create-ticket";

baseSchema + {
  properties+: {
    update_notes: {
      type: 'string',
      description: 'Notes about this update'
    }
  }
}
```

### Section-Based Schema Composition

**UPDATE Process Consolidated Schema:**
```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    section_updates: {
      type: 'object',
      additionalProperties: false,
      properties: {
        plan: {
          type: 'object',
          properties: {
            implementation_steps: {
              type: 'array',
              items: { type: 'string' },
              description: 'Ordered list of implementation steps'
            },
            dependencies: {
              type: 'string',
              description: 'Dependencies and prerequisites'
            }
          },
          required: ['implementation_steps']
        },
        status: {
          type: 'object',
          properties: {
            current_status: {
              type: 'string',
              enum: ['planning', 'implementation', 'testing', 'complete']
            }
          },
          required: ['current_status']
        }
      }
    },
    section_order: {
      type: 'array',
      description: 'Canonical ordering of sections',
      items: { type: 'string' },
      default: ['plan', 'status']
    }
  },
  required: ['section_updates']
}
```

**Individual Section Schema Fragment (artifact/sections/plan.schema.jsonnet):**
```jsonnet
// Note: No $schema header in section fragments
{
  type: 'object',
  properties: {
    implementation_steps: {
      type: 'array',
      items: { type: 'string' },
      description: 'Ordered list of implementation steps'
    },
    dependencies: {
      type: 'string',
      description: 'Dependencies and prerequisites'
    },
    estimated_effort: {
      type: 'string',
      description: 'Time estimate for completion'
    }
  },
  required: ['implementation_steps']
}
```

**Consolidated Schema Importing Fragments:**
```jsonnet
local planSchema = import 'sections/plan.schema.jsonnet';
local statusSchema = import 'sections/status.schema.jsonnet';

{
  type: 'object',
  properties: {
    section_updates: {
      type: 'object',
      properties: {
        plan: planSchema,
        status: statusSchema
      }
    }
  }
}
```

### Section Composition with Enabled Flags

**Use Case:** CREATE process with configurable optional sections that import schemas from UPDATE process

This pattern enables easy human configuration of which sections to include in the final schema. BUILD processes automatically generate this structure.

```jsonnet
// Define sections array with enabled flags
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
  },
  {
    name: "commit_message",
    schema: import "process-schema://update-ticket/sections/commit_message",
    enabled: false
  }
];

// Fold enabled section properties into combined properties object
local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.schema.properties else acc,
  sections,
  {}
);

// Fold enabled section required fields into combined required array
local required = std.foldl(
  function(acc, sec)
    if sec.enabled && std.objectHas(sec.schema, 'required')
    then acc + sec.schema.required
    else acc,
  sections,
  []
);

// Final schema contains only enabled sections
{
  type: 'object',
  properties: properties,
  required: required
}
```

**Pattern Benefits:**

1. **Single Source of Truth**: Section schemas defined in UPDATE process, imported via semantic URIs
2. **Easy Configuration**: Toggle `enabled` boolean to include/exclude sections
3. **Automatic Composition**: `std.foldl` combines enabled sections dynamically
4. **No Duplication**: Schemas defined once, reused across CREATE and UPDATE processes
5. **Maintainability**: Changes to section schemas propagate automatically

**Configuration Workflow:**

To enable a section:
```jsonnet
{
  name: "technical_plan",
  schema: import "process-schema://update-ticket/sections/technical_plan",
  enabled: true  // Changed from false
}
```

To disable a section:
```jsonnet
{
  name: "progress_log",
  schema: import "process-schema://update-ticket/sections/progress_log",
  enabled: false  // Changed from true
}
```

**Coordination with Templates:**

This schema pattern coordinates with template composition patterns. When enabling/disabling sections:

1. **Update schema.jsonnet**: Change `enabled` flag
2. **Update artifact/content.md**: Change corresponding `{% set _include_section_name = ... %}` variable

See [Jinja2 Templates Guide](jinja2-templates-guide.md) for template coordination details.

## Smart Schema, Dumb Template Pattern

Pantheon follows the **Smart Schema, Dumb Template** architectural pattern for profile-aware behavior:

### The Pattern
- **Profile properties control schema behavior** (what agents are prompted for)
- **Templates remain data-driven** (render whatever data was provided)
- **Profile logic is centralized in schemas** rather than spread across both layers

### Flow
```
Profile → Schema → Agent Response → Template
```

### Example: Controlling Fields via Schema

**Schema (Smart - Contains Profile Logic):**
```jsonnet
local verbosity = std.extVar('verbosity');
local enforce_tdd = std.extVar('enforce_tdd');

local baseSchema = {
  properties: {
    ticket_id: { type: 'string' }
  },
  required: ['ticket_id']
};

local tddFields = if enforce_tdd then {
  properties+: {
    test_file: { type: 'string', description: 'Path to failing test' },
    test_code: { type: 'string', description: 'Test implementation' }
  },
  required+: ['test_file', 'test_code']
} else {};

baseSchema + tddFields
```

**Template (Dumb - Data-Driven):**
```jinja2
# Implementation Plan: {{ ticket_id }}

{% if test_file %}
## Test-First Development
**Failing Test:**
```python
# {{ test_file }}
{{ test_code }}
```
{% endif %}
```

**Rationale:**
- Template checks for data presence (`{% if test_file %}`), not profile settings
- Profile logic lives in one place (schema), not two (schema + template)
- Templates are easier to test with mock data
- Better separation of concerns

### Exceptional Cases
Direct profile access in templates (`{{ pantheon_profile }}`) is acceptable for **pure formatting changes** that schemas cannot control:

```jinja2
{% if pantheon_profile.output_format == 'json' %}
{{ data | tojson(indent=2) }}
{% else %}
{{ data }}
{% endif %}
```

## Semantic URI Resolution

Pantheon's Workspace resolves semantic URIs for cross-process schema references:

### Supported URI Schemes

**process-schema://process-name**
Imports complete schema from another process:
```jsonnet
import "process-schema://create-ticket"
```
Resolves to: `processes/create-ticket/schema.jsonnet`

**artifact-sections://process-name?data=path**
Extracts section data from another process's sections.jsonnet:
```jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```
Resolves to: `processes/get-ticket/artifact/sections.jsonnet` with data extraction at `sections.plan`

### Benefits
- **DRY Principle**: No schema duplication across processes
- **Consistency**: UPDATE processes inherit CREATE process contracts
- **Maintainability**: Schema changes propagate automatically
- **Testability**: Single source of truth for validation

## Validation Behavior

### Schema Validation Flow
1. Agent requests schema: `pantheon get schema <process-name>`
2. Framework evaluates Jsonnet with profile context
3. Framework returns compiled JSON Schema
4. Agent prepares data conforming to schema
5. Framework validates data against schema before execution
6. Invalid data returns validation errors to agent

### Common Validation Patterns

**Required Fields:**
```jsonnet
{
  properties: {
    required_field: { type: 'string' }
  },
  required: ['required_field']
}
```

**Conditional Requirements:**
```jsonnet
{
  properties: {
    field_a: { type: 'string' },
    field_b: { type: 'string' }
  },
  if: {
    properties: { field_a: { const: 'specific_value' } }
  },
  then: {
    required: ['field_b']
  }
}
```

**Pattern Validation:**
```jsonnet
{
  type: 'string',
  pattern: '^T[0-9]{3}$',  // Matches T001, T002, etc.
  description: 'Ticket ID in format T###'
}
```

## Best Practices

### 1. Centralize Profile Logic in Schemas
**Good:**
```jsonnet
local profile = std.extVar('profile');

{
  properties: {
    field: {
      type: 'string',
      description: if profile.detailed then 'Long description' else 'Short'
    }
  }
}
```

**Bad:**
```jinja2
{% if pantheon_profile.detailed %}
{{ long_description }}
{% else %}
{{ short_description }}
{% endif %}
```

### 2. Provide Clear Descriptions
```jsonnet
{
  implementation_steps: {
    type: 'array',
    items: { type: 'string' },
    description: 'Ordered list of implementation steps, starting with "Step 1:", "Step 2:", etc.'
  }
}
```

Good descriptions guide agents on expected data format and content.

### 3. Use Appropriate Validation
```jsonnet
{
  title: {
    type: 'string',
    minLength: 10,
    maxLength: 80,
    description: 'Concise, action-oriented title (10-80 characters)'
  }
}
```

### 4. Leverage Schema Composition
```jsonnet
import "process-schema://base-process"
```
Prefer imports over duplication for consistency.

### 5. Section Fragments Without $schema
```jsonnet
// artifact/sections/plan.schema.jsonnet
// No $schema header - imported by consolidated schema
{
  type: 'object',
  properties: {
    steps: { type: 'array' }
  }
}
```

### 6. Use additionalProperties: false
```jsonnet
{
  type: 'object',
  properties: {
    defined_field: { type: 'string' }
  },
  additionalProperties: false  // Reject unexpected fields
}
```

## Testing Schemas

### Manual Testing
```bash
# Compile and view schema
pantheon get schema create-ticket --actor test-agent

# Test with sample data
pantheon execute create-ticket --from-file test-data.json --actor test-agent
```

### Common Schema Errors

**Jsonnet Compilation Error:**
```
RUNTIME ERROR: Field does not exist: profile
```
**Solution:** Check external variable spelling, ensure profile is injected

**Invalid JSON Schema:**
```
Invalid schema: 'type' is required
```
**Solution:** Ensure all property definitions have `type` field

**Validation Failure:**
```
Validation error: 'required_field' is a required property
```
**Solution:** Check required fields list matches property names

## Related Documentation

- **[Templating System Overview](./overview.md)** - Three-part templating architecture
- **[Jinja2 Templates Guide](./jinja2-templates-guide.md)** - Content generation layer
- **[JSON Schema Reference](./json-schema-reference.md)** - Data types and validation constraints
- **[Jsonnet Language Reference](./jsonnet-language-reference.md)** - Jsonnet language features
- **[Semantic URI Protocol](./semantic-uri-protocol.md)** - Cross-process asset sharing
- **[Built-in Variables](./built-in-variables.md)** - Framework-injected variables

---

Jsonnet schemas provide the data contract layer that ensures agents provide valid, complete data for process execution. By leveraging profile-aware composition and schema inheritance, you create flexible, maintainable validation that adapts to team-specific requirements while maintaining consistency across process families.
