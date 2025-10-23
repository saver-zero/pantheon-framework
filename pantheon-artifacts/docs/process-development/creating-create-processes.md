---
doc_id: creating-create-processes
title: "Creating CREATE Processes"
description: "Complete guide to building CREATE processes that generate new artifacts with structured content and metadata."
keywords: [create, process, artifact, content-template, placement, naming, jsonl]
relevance: "Use this document when building processes that generate entirely new artifacts from structured input data, including optional JSONL logging for analytics."
---

# Creating CREATE Processes

CREATE processes generate entirely new artifacts from structured input data. They require three specific files in the `artifact/` directory and optionally support JSONL logging for analytics.

## Process Structure

```
processes/create-ticket/
├── routine.md
├── permissions.jsonnet
├── schema.jsonnet
└── artifact/
    ├── content.md          # Template for ticket content
    ├── placement.jinja     # Where to save tickets
    └── naming.jinja        # How to name ticket files
```

## Example: create-ticket Process

### Core Files

**routine.md** - Instructions for agents:
```markdown
# Create Ticket Process

**Objective:** Generate a new project ticket with structured content.

## Steps

Step 1. **Get schema:** Use `pantheon get schema create-ticket --actor <your_agent_name>` to retrieve the data contract.

Step 2. **Generate ticket content:** Create JSON data following the schema description.

Step 3. **Get temp file:** Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>` to get the temp file path to save your JSON.

Step 4 (terminate). **Create ticket:** Use `pantheon execute create-ticket --from-file {tempfile} --actor <your_agent_name>`. You are now done. Report back to the user.
```

**schema.jsonnet** - Data contract:
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
  required: ['id', 'title', 'business_context', 'technical_context']
}
```

**permissions.jsonnet** - Access control:
```jsonnet
{
  allow: ['tech-lead'],
  deny: []
}
```

### Artifact Files

**artifact/content.md** - Content template:
```markdown
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

**artifact/placement.jinja** - Directory template:
```
tickets/
```

**artifact/naming.jinja** - Filename template:
```
T{{ artifact_id }}_{{ title | lower | replace(' ', '-') | replace('/', '-') }}.md
```

## Optional JSONL Logging

For processes requiring structured logging (analytics, audit trails), add JSONL templates:

**artifact/jsonl_placement.jinja** - JSONL directory template:
```
logs/{{ pantheon_actor }}
```

**artifact/jsonl_naming.jinja** - JSONL filename template:
```
{{ pantheon_datestamp }}_tickets.jsonl
```

JSONL logging creates entries like:
```json
{"title":"Fix auth bug","business_context":"Users can't login","timestamp":"2024-01-15T10:30:00Z"}
```

## Built-in Template Variables

All CREATE process templates have access to:

- `{{ pantheon_actor }}` - The actor executing the process
- `{{ pantheon_timestamp }}` - Current timestamp in ISO format
- `{{ pantheon_datestamp }}` - Current date in YYYY-MM-DD format
- `{{ pantheon_artifact_id }}` - Sequential artifact ID (auto-generated)
- `{{ pantheon_profile }}` - Active team profile object

## Profile-Driven Schema Adaptation

Use profile settings to dynamically adjust schema requirements:

```jsonnet
local profile = std.extVar('profile');

local baseSchema = {
  properties: {
    ticket_id: { type: 'string' },
    description: { type: 'string' }
  },
  required: ['ticket_id', 'description']
};

// Conditionally add TDD requirements based on profile
local tddFields = if profile.enforce_tdd then {
  properties+: {
    test_file: {
      type: 'string',
      description: 'Path to the failing test file (required for TDD)'
    }
  },
  required+: ['test_file']
} else {};

baseSchema + tddFields
```

## Testing CREATE Processes

1. **Validate Schema**: `pantheon get schema create-ticket --actor <agent>`
2. **Test Permissions**: Try execution with different agents
3. **Check Template Rendering**: Create test artifact with sample data
4. **Verify File Placement**: Ensure artifacts are created in correct location
5. **Validate JSONL Logging**: If enabled, check log entries are correctly formatted

## Common Patterns

### Single-Section CREATE Process
For simple artifacts without sections:

```bash
processes/create-simple-readme/:
    - routine.md
    - permissions.jsonnet
    - schema.jsonnet
    - artifact/content.md               # Simple template without sections
    - artifact/placement.jinja
    - artifact/naming.jinja
```

### Multi-Section CREATE Process
For complex documents with structured sections:

```markdown
# {{ title }}

## Overview
{{ overview }}

## Technical Details
<!-- START_SECTION:details -->
{{ technical_details }}
<!-- END_SECTION:details -->

## Implementation Notes
<!-- START_SECTION:notes -->
{{ implementation_notes }}
<!-- END_SECTION:notes -->
```

### Template Includes for Section Reuse
CREATE processes can include section templates from UPDATE processes:

```jinja2
# Architecture Guide for {{ project_name }}

## Core Principles
{% include 'artifact-template://update-architecture-guide/sections/core-principles' %}

## High-Level Overview
{% include 'artifact-template://update-architecture-guide/sections/high-level-overview' %}
```

This eliminates duplication and establishes UPDATE processes as the single source of truth for section content.

## Best Practices

1. **Clear Naming**: Use descriptive `verb-noun` convention (e.g., `create-ticket`, `create-architecture-doc`)
2. **Minimal Required Fields**: Only require fields that are truly essential for artifact creation
3. **Profile Integration**: Use profile settings to adapt schema for different development contexts
4. **Section Markers**: Include section markers for future UPDATE operations
5. **Built-in Variables**: Always include actor tracking and timestamps
6. **Template Includes**: Reuse section templates from UPDATE processes via semantic URIs
7. **JSONL Logging**: Enable for processes where analytics or audit trails are valuable

## Next Steps

- **UPDATE Processes**: Learn how to modify artifacts created by CREATE processes
- **Schema Design**: Deep dive into Jsonnet patterns and composition
- **Template Design**: Master Jinja2 patterns and section management
