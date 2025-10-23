---
doc_id: creating-get-processes
title: "Creating GET Processes"
description: "Complete guide to building GET processes that find and parse existing artifacts, returning structured JSON data."
keywords: [get, retrieve, process, locator, parser, sections, structured-data]
relevance: "Use this document when building processes that retrieve structured information from existing artifacts without modifying them."
---

# Creating GET Processes

GET processes find and parse existing artifacts, returning structured JSON data. They operate using built-in CLI flags (`--id`, `--sections`) without requiring custom schemas.

## Process Structure

```
processes/get-ticket/
├── routine.md
├── permissions.jsonnet
└── artifact/
    ├── locator.jsonnet     # Pattern to find tickets
    ├── parser.jsonnet      # ID normalization
    └── sections.jsonnet    # Section markers
```

## Example: get-ticket Process

### Core Files

**routine.md**:
```markdown
# Get Ticket Process

**Objective:** Retrieve structured information from an existing ticket.

## Steps

Step 1. **Execute retrieval:** Use `pantheon execute get-ticket --id <ticket_id> --sections plan,status --actor <your_agent_name>`.

The process will return JSON data with the requested ticket sections. You are now done. Report back to the user.
```

**No schema.jsonnet required** - GET processes can operate using built-in CLI flags (`--id`, `--sections`) without custom schemas.

### Artifact Files

**artifact/locator.jsonnet** - Uses external variables from CLI flags:
```jsonnet
{
  // Directory to search for ticket files
  directory: "tickets",

  // Get the artifact ID from external variable (--id flag)
  local id = std.extVar("pantheon_artifact_id"),

  // Regex pattern to find ticket files by specific ID
  pattern: "^" + id + "-.*[.]md$"
}
```

**artifact/parser.jsonnet** - ID normalization rules:
```jsonnet
[
  {
    pattern: "^\\s+|\\s+$",
    replacement: ""
  },
  {
    pattern: "^[Tt]?(\\d{3})$",
    replacement: "T$1"
  }
]
```

**artifact/sections.jsonnet** - Section markers:
```jsonnet
{
  "sections": {
    "status": {
      "start": "<!-- SECTION:START:STATUS -->",
      "end": "<!-- SECTION:END:STATUS -->",
      "description": "Current ticket status and progress tracking"
    },
    "plan": {
      "start": "<!-- SECTION:START:PLAN -->",
      "end": "<!-- SECTION:END:PLAN -->",
      "description": "Detailed implementation plan with steps and dependencies"
    }
  },
  "placeholder": "<!-- SECTION:PLACEHOLDER -->"
}
```

## Built-in CLI Flags

GET processes leverage framework-provided flags:

### --id Flag
Specifies which artifact to retrieve:
```bash
pantheon execute get-ticket --actor engineer --id T001
```

The ID is normalized using `parser.jsonnet` rules to handle fuzzy inputs:
- `T001`, `t001`, `001` → All normalized to `T001`
- Whitespace is trimmed
- Case-insensitive matching

### --sections Flag
Specifies which sections to retrieve:
```bash
# Get specific sections
pantheon execute get-ticket --actor engineer --id T001 --sections plan,status

# Get all sections (default)
pantheon execute get-ticket --actor engineer --id T001
```

## Discovering Available Sections

Use `pantheon get sections` to discover section metadata:

```bash
pantheon get sections get-ticket --actor developer
```

**Returns:**
```json
[
  {
    "name": "plan",
    "description": "Detailed implementation plan with steps and dependencies"
  },
  {
    "name": "status",
    "description": "Current ticket status and progress tracking"
  }
]
```

## ID Normalization Patterns

Parser rules enable flexible ID input:

### Whitespace Trimming
```jsonnet
{
  pattern: "^\\s+|\\s+$",
  replacement: ""
}
```
Handles: ` T001 ` → `T001`

### Case-Insensitive Prefix
```jsonnet
{
  pattern: "^[Tt]?(\\d{3})$",
  replacement: "T$1"
}
```
Handles: `t001`, `T001`, `001` → `T001`

### Custom Formats
```jsonnet
{
  pattern: "^TICKET-(\\d+)$",
  replacement: "T$1"
}
```
Handles: `TICKET-123` → `T123`

## Placeholder Section Filtering

Sections containing placeholder markers are automatically filtered from results:

```markdown
## Implementation Plan
<!-- SECTION:START:PLAN -->
<!-- SECTION:PLACEHOLDER -->
_Implementation plan will be added here_
<!-- SECTION:END:PLAN -->
```

This section won't appear in GET results until it contains real content.

## Section Metadata

Section definitions include descriptions for discoverability:

```jsonnet
{
  "sections": {
    "overview": {
      "start": "<!-- SECTION:START:OVERVIEW -->",
      "end": "<!-- SECTION:END:OVERVIEW -->",
      "description": "High-level overview and purpose of the ticket"
    },
    "technical_context": {
      "start": "<!-- SECTION:START:TECHNICAL_CONTEXT -->",
      "end": "<!-- SECTION:END:TECHNICAL_CONTEXT -->",
      "description": "Technical background, constraints, and architectural considerations"
    }
  }
}
```

## Single-Section GET Process

For artifacts with only one section, omit `sections.jsonnet`:

```bash
processes/get-simple-readme/:
    - routine.md
    - permissions.jsonnet
    - artifact/locator.jsonnet          # Find README files
    - artifact/parser.jsonnet           # Normalize IDs
```

Framework returns entire content instead of parsing sections.

## Testing GET Processes

1. **Test Artifact Location**: Verify locator finds correct artifacts
2. **Test ID Normalization**: Try fuzzy inputs (T001, t1, 001)
3. **Verify Section Parsing**: Check section extraction accuracy
4. **Test Placeholder Filtering**: Ensure empty sections are excluded
5. **Validate Permissions**: Test access control
6. **Check Section Discovery**: Verify `get sections` returns correct metadata

## Common Patterns

### Context Retrieval for Planning
```bash
pantheon execute get-ticket --actor backend-engineer \
  --id T004 --sections context,requirements
```

### Full Ticket Retrieval
```bash
pantheon execute get-ticket --actor code-reviewer --id T004
```

### Specialized Section Access
```bash
# Only get implementation plan
pantheon execute get-ticket --actor developer --id T004 --sections plan
```

## Integration with UPDATE Processes

GET processes provide the foundation for UPDATE operations:

```jsonnet
// UPDATE process imports section markers from GET
import "artifact-sections://get-ticket?data=sections.plan"
```

This ensures UPDATE and GET processes use identical section definitions.

## Best Practices

1. **Descriptive Section Names**: Use clear, semantic names (plan, context, not sec1)
2. **Rich Metadata**: Include helpful descriptions for all sections
3. **Fuzzy ID Support**: Implement robust parser rules for flexible input
4. **Placeholder Filtering**: Use placeholder markers for empty sections
5. **Shared Logic**: UPDATE processes should import locator/parser from GET
6. **Permission Design**: Consider who needs read access to sensitive sections
7. **Testing**: Validate with various ID formats and section combinations

## Next Steps

- **UPDATE Processes**: Learn how GET processes support UPDATE operations
- **Schema Design**: Understand when custom schemas are needed
- **Permissions**: Implement section-level read access control
- **Testing**: Comprehensive GET process validation strategies
