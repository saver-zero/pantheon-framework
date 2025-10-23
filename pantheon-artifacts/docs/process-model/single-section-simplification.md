---
doc_id: process-model-single-section
title: "Single-Section Simplification"
description: "The '1 section = no sections' principle that automatically simplifies artifacts with only one section"
keywords: [single-section, simplification, process-model, schema-structure, template-structure]
relevance: "Use this document to understand when and how Pantheon simplifies single-section artifacts to eliminate unnecessary complexity"
---

# Single-Section Simplification

The Pantheon Framework implements a powerful "**1 section = no sections**" principle that automatically simplifies artifacts with only one section, eliminating unnecessary complexity and providing a cleaner, more intuitive experience.

## Core Principle

When an artifact has only one logical section, the framework treats it as a **simple document** rather than a **sectioned document**, removing all section-related infrastructure and complexity.

### Benefits

1. **Reduced Complexity**: Fewer files, simpler schemas, cleaner directory structure
2. **More Intuitive**: Single documents behave like simple templates without section markers
3. **Less Boilerplate**: No nested `section_updates` schemas or section marker comments
4. **Cleaner Artifacts**: Output documents don't contain HTML section comments
5. **Backward Compatible**: Existing multi-section processes remain unchanged

## Detection Logic

The framework automatically determines single vs multi-section behavior:

### During BUILD Process
- **Input**: `sections` array in build specification
- **Logic**: If `sections.length === 1` → single-section mode
- **Result**: Generated processes use simplified structure

### During UPDATE Execution
- **Detection**: Presence/absence of `target.jsonnet` file
- **Logic**:
  - No `target.jsonnet` → single-section (whole document replacement)
  - Has `target.jsonnet` → multi-section (sectioned updates)

### During GET Execution
- **Detection**: Presence/absence of `sections.jsonnet` file
- **Logic**:
  - No `sections.jsonnet` → single-section (return entire content)
  - Has `sections.jsonnet` → multi-section (can parse specific sections)

## Single-Section Process Structure

### CREATE Process (Single-Section)
```bash
processes/create-document/
├── routine.md
├── permissions.jsonnet
├── schema.jsonnet                    # Flat schema structure
└── artifact/
    ├── content.md                    # No section markers
    ├── placement.jinja
    └── naming.jinja
```

**Key Characteristics:**
- `content.md` has no section markers
- Schema uses direct properties (not nested in `section_updates`)
- Template variables accessed directly: `{{ title }}`, `{{ description }}`

### GET Process (Single-Section)
```bash
processes/get-document/
├── routine.md
├── permissions.jsonnet
└── artifact/
    ├── locator.jsonnet
    └── parser.jsonnet
    # No sections.jsonnet file
```

**Key Characteristics:**
- No `sections.jsonnet` file
- Returns entire document content as single unit
- `--sections` flag not applicable

### UPDATE Process (Single-Section)
```bash
processes/update-document/
├── routine.md
├── permissions.jsonnet
├── schema.jsonnet                    # Flat schema structure
└── artifact/
    ├── locator.jsonnet
    ├── parser.jsonnet
    └── patch.md                      # Simple replacement template
    # No target.jsonnet file
    # No sections/ subdirectory
```

**Key Characteristics:**
- No `target.jsonnet` file
- No `sections/` subdirectory
- Flat schema structure (no `section_updates` wrapper)
- Performs complete document replacement

## Schema Structure Comparison

### Single-Section Schema
```jsonnet
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Document title"
    },
    "content": {
      "type": "string",
      "description": "Main document content"
    }
  },
  "required": ["title", "content"]
}
```

### Multi-Section Schema
```jsonnet
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "section_updates": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "overview": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"}
          }
        },
        "details": {
          "type": "object",
          "properties": {
            "content": {"type": "string"}
          }
        }
      }
    }
  },
  "required": ["section_updates"]
}
```

## Best Practices

### When to Use Single-Section
- Simple documents with unified content
- Configuration files
- Basic templates or prompts
- Reports with single logical flow
- Any artifact that doesn't benefit from independent section updates

### When to Use Multi-Section
- Complex documents built collaboratively
- Documents with independent update workflows
- Artifacts where different agents update different parts
- Long documents with distinct logical sections
- Documents requiring granular version control

### Design Considerations
- Start with single-section for simplicity
- Add sections only when you need independent update workflows
- Consider the cognitive load on agents using the processes
- Evaluate whether section complexity adds real value to your workflow

---

**Related:** [Process Model Overview](overview.md) | [UPDATE Processes](update-processes.md) | [GET Processes](get-processes.md)
