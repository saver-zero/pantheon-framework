---
doc_id: creating-update-processes
title: "Creating UPDATE Processes"
description: "Complete guide to building UPDATE processes that modify specific sections of existing artifacts with targeted patches."
keywords: [update, process, patch, target, locator, parser, sections, semantic-uri]
relevance: "Use this document when building processes that modify specific sections of existing artifacts, including section targeting and artifact location patterns."
---

# Creating UPDATE Processes

UPDATE processes modify specific sections of existing artifacts. They require specialized files for locating artifacts, parsing IDs, targeting sections, and generating replacement content.

## Process Structure

```
processes/update-plan/
├── routine.md
├── permissions.jsonnet
├── schema.jsonnet
└── artifact/
    ├── patch.md            # Template for section replacement
    ├── target.jsonnet      # Which section to update
    ├── locator.jsonnet     # Pattern to find tickets
    └── parser.jsonnet      # ID normalization rules
```

## Example: update-plan Process

### Core Files

**routine.md**:
```markdown
# Update Plan Process

**Objective:** Update the implementation plan section of an existing ticket.

## Steps

Step 1. **Get schema:** Use `pantheon get schema update-plan --actor <your_agent_name>` to retrieve the data contract.

Step 2. **Generate plan content:** Create JSON data following the schema description.

Step 3. **Get temp file:** Use `pantheon get tempfile --process update-plan --actor <your_agent_name>` to get the temp file path to save your JSON.

Step 4 (terminate). **Update plan:** Use `pantheon execute update-plan --from-file {tempfile} --actor <your_agent_name>`. You are now done. Report back to the user.
```

**schema.jsonnet** - Consolidated UPDATE schema with section structure:
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
      }
    },
    section_order: {
      type: 'array',
      description: 'Canonical ordering of sections for default workflows',
      items: { type: 'string' },
      default: ['plan']
    }
  },
  required: ['section_updates']
}
```

### Artifact Files

**artifact/patch.md** - Consolidated section template with includes:
```markdown
{% set requested_sections = pantheon_sections if pantheon_sections else section_order %}

{% for section_name in requested_sections %}
  {% set snippet = "sections/" ~ section_name ~ ".md" %}
  {% include snippet ignore missing %}
{% endfor %}
```

**artifact/sections/plan.md** - Individual section template:
```markdown

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

> **Template Variable Access**: Section templates use direct variable names like `{{ implementation_steps }}` and `{{ dependencies }}`. The framework automatically flattens `section_updates.plan.implementation_steps` into `implementation_steps` for each section during rendering, enabling clean template syntax.

> **Include Support**: The consolidated `patch.md` uses `{% include %}` statements to compose multiple sections. The framework uses a FileSystemLoader-enabled Jinja environment to resolve these includes from the `artifact/sections/` directory.

**artifact/target.jsonnet** - Section targeting via import retrieves section markers:
```jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```

**artifact/locator.jsonnet** - Artifact finding pattern:
```jsonnet
import "artifact-locator://get-ticket"
```

**artifact/parser.jsonnet** - ID normalization:
```jsonnet
import "artifact-parser://get-ticket"
```

## Semantic URI Integration

UPDATE processes extensively use semantic URIs to share configuration with GET processes:

### Locator Sharing
```jsonnet
// In processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"
```

This ensures UPDATE and GET processes use identical artifact finding logic.

### Parser Sharing
```jsonnet
// In processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

Both processes normalize IDs (e.g., `T001`, `t1`, `001`) to the same canonical format.

### Section Targeting
```jsonnet
// In processes/update-ticket/artifact/target.jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```

Imports section marker definitions from the GET process.

## Single-Section Process Simplification

The framework implements a **"1 section = no sections"** principle for processes with only one section:

### Single-Section UPDATE Process
```bash
processes/update-simple-readme/:
    - routine.md
    - permissions.jsonnet
    - schema.jsonnet                    # Flat properties, no section_updates
    - artifact/locator.jsonnet          # Shared with GET
    - artifact/parser.jsonnet           # Shared with GET
    - artifact/patch.md                 # Whole document template
```

### Schema Structure Comparison

**Multi-Section Schema:**
```jsonnet
{
  artifact_id: { type: "string" },
  section_updates: {
    type: "object",
    properties: {
      overview: { type: "string" },
      details: { type: "string" }
    }
  }
}
```

**Single-Section Schema (Flat):**
```jsonnet
{
  artifact_id: { type: "string" },
  content: { type: "string" },
  title: { type: "string" }
}
```

## Section-Level Permissions

UPDATE processes support fine-grained section-level permissions:

```jsonnet
{
  allow: ["pantheon"],  // Admin has access to all sections
  sections: {
    "plan": {
      allow: ["backend-engineer", "tech-lead"],
      deny: []
    },
    "code_review": {
      allow: ["code-reviewer", "senior-engineer"],
      deny: []
    }
  }
}
```

## Non-Destructive Updates (Insert Modes)

UPDATE processes support non-destructive section modifications:

```bash
# Append new content to existing section
pantheon execute update-progress --actor developer --id T001 \
  --insert-mode append --from-file progress.json

# Prepend new content to existing section
pantheon execute update-changelog --actor tech-lead --id T001 \
  --insert-mode prepend --from-file update.json
```

Without `--insert-mode`, UPDATE operations replace the entire section content.

## Testing UPDATE Processes

1. **Validate Schema**: `pantheon get schema update-plan --actor <agent>`
2. **Test Artifact Location**: Verify locator finds correct artifacts
3. **Test ID Normalization**: Ensure parser handles fuzzy inputs (T001, t1, 001)
4. **Check Section Targeting**: Verify target.jsonnet identifies correct sections
5. **Test Template Rendering**: Update test artifact with sample data
6. **Verify Permissions**: Test section-level access control
7. **Test Insert Modes**: Verify append/prepend behavior

## Common Patterns

### Multi-Specialist Collaboration
Different agents own different sections:

```jsonnet
{
  allow: ["admin"],
  sections: {
    "technical_design": {
      allow: ["architect", "tech-lead"],
      deny: []
    },
    "implementation_plan": {
      allow: ["senior-developer", "tech-lead"],
      deny: []
    },
    "test_strategy": {
      allow: ["qa-engineer", "test-lead"],
      deny: []
    }
  }
}
```

### Progressive Section Updates
Start with placeholders, fill in over time:

```markdown
## Initial Planning
<!-- START_SECTION:plan -->
_To be filled by assigned developer_
<!-- END_SECTION:plan -->

## Code Review
<!-- START_SECTION:review -->
_To be filled after implementation_
<!-- END_SECTION:review -->
```

### Template Variable Flattening
Section templates access flattened variables:

```jsonnet
// Schema
{
  section_updates: {
    plan: {
      implementation_steps: ["Step 1", "Step 2"],
      dependencies: "None"
    }
  }
}
```

```jinja2
// Template (variables flattened automatically)
{% for step in implementation_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

{{ dependencies }}
```

## Best Practices

1. **Share Artifact Logic**: Use semantic URIs to import locator/parser from GET processes
2. **Section Markers**: Use HTML comments for compatibility (`<!-- START_SECTION:name -->`)
3. **Descriptive Section Names**: Use clear names (plan, status, review, not sec1, sec2)
4. **Placeholder Markers**: Include placeholders for empty sections
5. **Section Permissions**: Define fine-grained access control for collaborative workflows
6. **Template Includes**: Use `{% include %}` for section composition
7. **Variable Flattening**: Leverage automatic variable flattening for clean templates
8. **Insert Modes**: Support non-destructive updates for append/prepend workflows

## Next Steps

- **GET Processes**: Learn how to retrieve sections for UPDATE operations
- **Schema Design**: Master section_updates structure and validation
- **Template Design**: Deep dive into section templates and includes
- **Permissions**: Implement section-level access control
