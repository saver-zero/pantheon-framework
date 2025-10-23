---
doc_id: team-packages-schemas-guide
title: "Schemas Development Guide"
description: "Comprehensive guide to designing schema data contracts including property definitions, validation constraints, profile-aware composition, and testing strategies."
keywords: [schemas, data-contracts, validation, jsonnet, json-schema, profile-aware-schemas, schema-composition]
relevance: "Use this document to understand how to design schema data contracts that define required data structures and validation rules for processes."
---

# Schemas Development Guide

Schemas (`processes/*/schema.jsonnet`) define **WHAT DATA** is required for process execution through structured validation rules. They specify data contracts without containing workflow steps or agent capabilities.

## Process Architecture Context

A complete process consists of:

```
processes/<verb-noun>/
├── routine.md          # HOW: Step-by-step workflow instructions
├── schema.jsonnet      # WHAT DATA: Data contract and validation
├── permissions.jsonnet # WHO: Access control
└── artifact/           # Operation-specific files
```

**See also:** [Routines Development Guide](./routines-guide.md) for workflow instructions.

## Core Responsibility

**Primary Purpose:** Define the data contract that agents must satisfy when executing a process.

**Key Principle:** Schemas are **data-focused**. They specify types, constraints, and validation rules for input data, not workflow procedures or agent personas.

## Essential Schema Components

### 1. Property Definitions

**Purpose:** Specify what fields are required and their types

**Pattern:**
```jsonnet
{
  type: 'object',
  properties: {
    field_name: {
      type: 'string|number|boolean|array|object',
      description: 'Human-readable description for agents'
    }
  }
}
```

**Example:**
```jsonnet
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
      description: 'Key technical considerations and implementation approach'
    }
  }
}
```

### 2. Required Fields

**Pattern:**
```jsonnet
{
  properties: { ... },
  required: ['field1', 'field2']
}
```

### 3. Validation Constraints

**Purpose:** Define acceptable values and formats

**Pattern:**
```jsonnet
{
  field_name: {
    type: 'string',
    minLength: 1,
    maxLength: 100,
    pattern: '^[A-Z]',  // Regex
    enum: ['option1', 'option2']
  }
}
```

**Example:**
```jsonnet
{
  status: {
    type: 'string',
    enum: ['planning', 'implementation', 'testing', 'complete'],
    description: 'Current project status'
  },
  priority: {
    type: 'integer',
    minimum: 1,
    maximum: 5,
    description: 'Priority level from 1 (lowest) to 5 (highest)'
  }
}
```

### 4. Profile-Aware Composition

**Purpose:** Adapt schema based on team profile settings

**Pattern:**
```jsonnet
local profile = std.extVar('profile');

local baseSchema = { ... };

local conditionalFields = if profile.some_setting then {
  properties+: { additional_field: { ... } }
} else {};

baseSchema + conditionalFields
```

**Example:**
```jsonnet
local profile = std.extVar('profile');
local enforce_tdd = std.extVar('enforce_tdd');

local baseSchema = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    description: { type: 'string' }
  },
  required: ['title', 'description']
};

local tddFields = if enforce_tdd then {
  properties+: {
    test_file: {
      type: 'string',
      description: 'Path to failing test file'
    },
    test_code: {
      type: 'string',
      description: 'Failing test implementation'
    }
  },
  required+: ['test_file', 'test_code']
} else {};

baseSchema + tddFields
```

## What Belongs in Schemas

**YES - Data Type Specifications:**
```jsonnet
{
  title: { type: 'string' },
  priority: { type: 'integer' },
  is_urgent: { type: 'boolean' },
  tags: {
    type: 'array',
    items: { type: 'string' }
  }
}
```

**YES - Validation Rules:**
```jsonnet
{
  title: {
    type: 'string',
    minLength: 10,
    maxLength: 80,
    pattern: '^[A-Z]',
    description: 'Capitalized title, 10-80 characters'
  }
}
```

**YES - Field Descriptions:**
```jsonnet
{
  technical_context: {
    type: 'string',
    description: 'Key technical considerations including architecture, dependencies, risks, and implementation approach'
  }
}
```

**YES - Profile-Based Conditional Fields:**
```jsonnet
local profile = std.extVar('profile');

{
  properties: {
    field1: { type: 'string' }
  } + if profile.verbosity == 'detailed' then {
    detailed_notes: { type: 'string' }
  } else {}
}
```

**NO - Workflow Steps:**
```jsonnet
// WRONG: This belongs in routine.md
{
  title: {
    type: 'string',
    description: 'First, get the schema. Then generate this title field by...'
  }
}
```

**NO - Agent Capabilities:**
```jsonnet
// WRONG: This belongs in agent definition
{
  '$schema': 'http://json-schema.org/draft-07/schema#',
  agent_role: 'backend-engineer',
  agent_skills: ['Python', 'FastAPI']
}
```

## Schema Structure Patterns

### Pattern: Basic CREATE Schema

```jsonnet
{
  type: 'object',
  properties: {
    title: {
      type: 'string',
      maxLength: 80,
      description: 'Brief, action-oriented title'
    },
    description: {
      type: 'string',
      description: 'Detailed description of the work'
    }
  },
  required: ['title', 'description']
}
```

### Pattern: UPDATE Schema with Sections

```jsonnet
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
              items: { type: 'string' }
            },
            dependencies: { type: 'string' }
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
          }
        }
      }
    },
    section_order: {
      type: 'array',
      items: { type: 'string' },
      default: ['plan', 'status']
    }
  },
  required: ['section_updates']
}
```

### Pattern: Schema with Imports

```jsonnet
local baseSchema = import "process-schema://create-ticket";

baseSchema + {
  properties+: {
    update_timestamp: { type: 'string', format: 'date-time' },
    update_notes: { type: 'string' }
  }
}
```

## Smart Schema, Dumb Template Pattern

### Profile Logic Belongs in Schemas

**Good:**
```jsonnet
// Schema controls what fields exist
local enforce_tdd = std.extVar('enforce_tdd');

local baseSchema = {
  properties: {
    implementation: { type: 'string' }
  },
  required: ['implementation']
};

local tddFields = if enforce_tdd then {
  properties+: {
    test_file: { type: 'string' },
    test_code: { type: 'string' }
  },
  required+: ['test_file', 'test_code']
} else {};

baseSchema + tddFields
```

**Template is Data-Driven:**
```jinja2
## Implementation
{{ implementation }}

{% if test_file %}
## Test Strategy
Test file: {{ test_file }}
```
{{ test_code }}
```
{% endif %}
```

**Rationale:** Profile logic centralized in schemas prevents duplication across schemas and templates.

## Validation Constraint Reference

### String Constraints
```jsonnet
{
  type: 'string',
  minLength: 1,
  maxLength: 100,
  pattern: '^[A-Z]',  // Starts with capital letter
  format: 'email' | 'date' | 'date-time' | 'uri'
}
```

### Numeric Constraints
```jsonnet
{
  type: 'number',
  minimum: 0,
  maximum: 100,
  exclusiveMinimum: 0,  // > 0, not >= 0
  multipleOf: 5
}
```

### Array Constraints
```jsonnet
{
  type: 'array',
  items: { type: 'string' },
  minItems: 1,
  maxItems: 10,
  uniqueItems: true
}
```

### Object Constraints
```jsonnet
{
  type: 'object',
  properties: { ... },
  required: ['field1', 'field2'],
  additionalProperties: false  // Reject unexpected fields
}
```

## Complete Schema Examples

### Example 1: CREATE Process Schema

**Schema (schema.jsonnet):**
```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    title: {
      type: 'string',
      minLength: 10,
      maxLength: 80,
      description: 'Brief, action-oriented ticket title'
    },
    business_context: {
      type: 'string',
      minLength: 20,
      description: 'Why this work is needed from business perspective'
    },
    technical_context: {
      type: 'string',
      description: if profile.verbosity == 'detailed' then
        'Comprehensive technical background and constraints'
      else
        'Key technical considerations and approach'
    },
    priority: {
      type: 'integer',
      minimum: 1,
      maximum: 5,
      description: 'Priority level from 1 (lowest) to 5 (highest)'
    }
  },
  required: ['title', 'business_context', 'technical_context']
}
```

### Example 2: UPDATE Process Schema

**Schema (schema.jsonnet):**
```jsonnet
local planSchema = import 'sections/plan.schema.jsonnet';
local statusSchema = import 'sections/status.schema.jsonnet';

{
  type: 'object',
  properties: {
    section_updates: {
      type: 'object',
      additionalProperties: false,
      properties: {
        plan: planSchema,
        status: statusSchema
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

## Common Mistakes

### Mistake 1: Including Workflow Instructions in Schemas

**Wrong:**
```jsonnet
{
  title: {
    type: 'string',
    description: 'First, ask the user for the task description. Then, create a brief title by extracting key words from their description. Capitalize the first letter.'
  }
}
```

**Correct:**
```jsonnet
{
  title: {
    type: 'string',
    maxLength: 80,
    pattern: '^[A-Z]',
    description: 'Brief, action-oriented ticket title (capitalized, 10-80 characters)'
  }
}
```

## Testing Schemas

### Manual Testing

**View Compiled Schema:**
```bash
pantheon get schema create-ticket --actor test-agent
```

**Test Validation:**
```bash
# Create test JSON conforming to schema
# Execute process to trigger validation
pantheon execute create-ticket --from-file test-data.json --actor test-agent
```

**Test Profile Variations:**
```bash
# Modify team profile settings
# Re-retrieve schema to verify conditional fields
pantheon get schema create-ticket --actor test-agent
```

## Related Documentation

- **[Process Development Overview](./overview.md)** - Three-component architecture overview
- **[Routines Development Guide](./routines-guide.md)** - Workflow instructions
- **[Jsonnet Schema Templates](../templating-system/jsonnet-schemas-guide.md)** - Advanced Jsonnet composition patterns
- **[Decision Framework](./decision-framework.md)** - Choosing process types and patterns
- **[Anti-Patterns](../routine-system/anti-patterns.md)** - Common boundary violations to avoid

---

Schemas define WHAT DATA is required for process execution through structured validation rules. By maintaining clear boundaries between data contracts, workflow instructions, and agent capabilities, schemas enable reliable, transparent AI workflows that support the Glass Box philosophy.
