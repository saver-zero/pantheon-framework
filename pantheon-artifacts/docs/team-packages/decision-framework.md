---
doc_id: process-components-decision-framework
title: "Process Type Decision Framework"
description: "Decision trees and guidelines for selecting appropriate process types (CREATE, UPDATE, GET) and choosing between build modes, artifact classifications, and section strategies"
keywords: [process-types, decision-framework, CREATE, UPDATE, GET, build-mode, artifact-classification, single-section, multi-section]
relevance: "Use this document when you need to determine which process type to create or how to configure process families using build-team-artifact"
---

# Process Type Decision Framework

## Overview

The Pantheon Framework provides three fundamental process types (CREATE, UPDATE, GET) with multiple configuration options. This document provides decision trees and guidelines for selecting the appropriate approach for your workflow needs.

## Process Type Selection

### Primary Decision Tree

```
Start: What is the primary goal?
├─ Generate NEW artifact
│  └─ Use CREATE process
│     Files: content.md + placement.jinja + naming.jinja
│
├─ Modify EXISTING artifact
│  └─ Use UPDATE process
│     Files: patch.md + locator.jsonnet + parser.jsonnet + target.jsonnet
│
└─ Read EXISTING artifact
   └─ Use GET process
      Files: locator.jsonnet + parser.jsonnet + sections.jsonnet
```

### Process Type Characteristics

| Process Type | Creates Files | Modifies Files | Returns Data | Use Case |
|--------------|---------------|----------------|--------------|----------|
| **CREATE** | ✓ | ✗ | ✗ | Generate new tickets, documents, configs |
| **UPDATE** | ✗ | ✓ | ✗ | Modify sections, update status, patch content |
| **GET** | ✗ | ✗ | ✓ | Retrieve context, extract data, query artifacts |

---

## CREATE Process Design Decisions

### Question 1: Single Document or Multiple Sections?

**Single Document** (simpler):
- Entire content created at once
- No section markers needed
- Flat schema structure
- Example: Configuration files, simple READMEs

**Multiple Sections** (structured):
- Document composed of distinct parts
- Section markers for targeted updates
- Nested schema with `section_updates`
- Example: Tickets, architecture docs, blueprints

### Question 2: Is Structured Logging Required?

**Yes** - Add JSONL templates:
```
artifact/
├── content.md
├── placement.jinja
├── naming.jinja
├── jsonl_placement.jinja  ← Add this
└── jsonl_naming.jinja     ← Add this
```

**No** - Standard templates only:
```
artifact/
├── content.md
├── placement.jinja
└── naming.jinja
```

**Use JSONL when**: Analytics, audit trails, compliance tracking needed

### Question 3: Should Built-in Variables Be Used?

Available built-in template variables:
- `{{ pantheon_timestamp }}` - ISO 8601 timestamp
- `{{ pantheon_datestamp }}` - YYYY-MM-DD date
- `{{ pantheon_actor }}` - Agent name executing process
- `{{ pantheon_artifact_id }}` - Generated artifact ID
- `{{ pantheon_profile }}` - Active team profile data

**Best Practice**: Always include `pantheon_timestamp` and `pantheon_actor` for auditability

---

## UPDATE Process Design Decisions

### Question 1: Whole Document or Section Updates?

**Whole Document Replacement**:
- Missing `target.jsonnet` signals whole replacement
- Simpler for single-section artifacts
- Example: Simple README updates

**Section-Level Updates**:
- Include `target.jsonnet` pointing to sections
- Enables granular modifications
- Example: Updating ticket plan without changing status

### Question 2: Should Artifact Config Be Shared?

**Recommended Pattern** - Share with GET process:
```jsonnet
// update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"

// update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

**Benefits**:
- Guaranteed consistency in artifact finding
- Reduced duplication
- Single source of truth

### Question 3: Should Schema Be Inherited?

**Recommended Pattern** - Import from CREATE:
```jsonnet
// update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

**Benefits**:
- Same validation rules
- Automatic schema propagation
- Prevents validation mismatches

---

## GET Process Design Decisions

### Question 1: Retrieve Entire Content or Specific Sections?

**Entire Content**:
- Missing `sections.jsonnet` signals full retrieval
- Returns complete artifact content
- Example: Simple config file retrieval

**Specific Sections**:
- Include `sections.jsonnet` with markers
- Supports `--sections` parameter
- Example: Get only plan from ticket

### Question 2: Is ID Normalization Required?

**Yes** - Include `parser.jsonnet`:
```jsonnet
[
  {
    pattern: "^\\s+|\\s+$",
    replacement: ""  // Trim whitespace
  },
  {
    pattern: "^[Tt]?(\\d{3})$",
    replacement: "T$1"  // Normalize to T001 format
  }
]
```

**No** - Omit parser, use raw IDs

**Use normalization when**: Users might provide IDs in various formats (T001, t001, 001)

---

## Build Mode Selection (build-team-artifact)

### Decision Tree

```
Start: How is artifact created?
├─ Single session, all content at once
│  └─ Use "complete" mode
│     - All sections rendered in CREATE
│     - No placeholders
│     - Example: Agent definitions, configs
│
└─ Multiple sessions, progressive development
   └─ Use "modular" mode
      - Initial section + placeholders in CREATE
      - Remaining sections via UPDATE
      - Example: Team blueprints, specifications
```

### Complete Mode

**Choose when**:
- Document created by single actor
- All content available at creation
- Simplicity preferred over granularity
- Updates require full regeneration

**Behavior**:
- CREATE includes ALL sections with real content
- UPDATE provides consolidated section updates
- Merged permissions in CREATE process
- Example: `create-agent` with persona + capabilities rendered immediately

**Generated Structure**:
```
processes/
├── create-{artifact}/
│   ├── routine.md          (all-in-one creation)
│   ├── schema.jsonnet      (merged from all sections)
│   └── artifact/
│       ├── content.md      (all sections rendered)
│       ├── placement.jinja
│       └── naming.jinja
├── get-{artifact}/
└── update-{artifact}/
    ├── schema.jsonnet      (section_updates structure)
    └── artifact/
        ├── patch.md        (consolidated sections)
        └── sections/       (individual templates)
```

---

### Modular Mode

**Choose when**:
- Multiple collaborators involved
- Content developed over time
- Different permission requirements per section
- Granular update control needed

**Behavior**:
- CREATE renders initial section + context only
- Remaining sections start as placeholders
- UPDATE fills in sections progressively
- Separate permissions for CREATE vs UPDATE

**Generated Structure**:
```
processes/
├── create-{artifact}/
│   ├── routine.md          (initial section only)
│   ├── schema.jsonnet      (initial section schema)
│   └── artifact/
│       ├── content.md      (initial + placeholders)
│       ├── placement.jinja
│       └── naming.jinja
├── get-{artifact}/
└── update-{artifact}/
    ├── schema.jsonnet      (all sections)
    └── artifact/
        ├── patch.md        (section assembly)
        └── sections/       (section templates)
```

---

## Artifact Classification

### Decision Tree

```
Start: Who is the primary audience?
├─ Agents or team members doing subsequent work
│  └─ Process Artifact (include_context: true)
│     - Include context section
│     - Stable background information
│     - Example: Planning docs, design briefs
│
└─ End-users or downstream systems
   └─ Terminal Artifact (include_context: false)
      - No context section
      - Self-contained deliverable
      - Example: Client deliverables, generated code
```

### Process Artifacts

**Characteristics**:
- Internal planning documents
- Guide subsequent agent work
- Include context/metadata sections
- Not intended for external consumption

**Examples**:
- Project tickets
- Architecture guides
- Design decision docs
- Team blueprints

---

### Terminal Artifacts

**Characteristics**:
- Final deliverables
- Consumed by end-users or systems
- Clean, context-free output
- Production-ready format

**Examples**:
- Client reports
- Generated source code
- Published documentation
- API responses

---

## Section Strategy

### Single-Section Simplification

**"1 section = no sections" Principle**

The framework automatically simplifies single-section artifacts:

**Detection Logic**:
- **BUILD**: Analyzes `sections.length === 1`
- **GET**: Missing `sections.jsonnet`
- **UPDATE**: Missing `target.jsonnet`

**Automatic Simplifications**:
- Omits section markers
- Uses flat schema properties
- Produces cleaner documents
- Fewer required files

**Ideal for**:
- Simple READMEs
- Configuration files
- Single-purpose docs
- Status reports

---

### Multi-Section Strategy

**Use when document has**:
- Multiple logical topics
- Different update permissions per section
- Progressive development needs
- Complex content structure

**Examples**:
- Tickets: context + plan + status + review
- Architecture docs: principles + overview + components
- Specifications: requirements + design + testing

**Section Design Guidelines**:
1. Each section should be independently updateable
2. Sections should be orthogonal (non-overlapping)
3. Use semantic section names (plan, status, review)
4. Include descriptive `section_description` for discovery

---

## Decision Matrix: Quick Reference

| Scenario | Process Type | Build Mode | Classification | Sections |
|----------|--------------|------------|----------------|----------|
| Create new ticket | CREATE | modular | process | multi |
| Update ticket plan | UPDATE | N/A | process | section-level |
| Generate config file | CREATE | complete | terminal | single |
| Read ticket context | GET | N/A | process | section-level |
| Create agent definition | CREATE | complete | process | multi |
| Update documentation | UPDATE | N/A | terminal | section-level |
| Query team data | GET | N/A | N/A | full |

---

## Common Anti-Patterns

### Anti-Pattern 1: Duplicating Artifact Configuration

**Problem**:
```jsonnet
// update-ticket/artifact/locator.jsonnet
{
  directory: "tickets",
  pattern: "^T\\d{3}-.*[.]md$"  // Duplicated from get-ticket
}
```

**Solution**:
```jsonnet
// update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"  // Share configuration
```

---

### Anti-Pattern 2: Using Multi-Section for Simple Content

**Problem**: Creating section markers for single-topic documents

**Solution**: Use single-section simplification
- Omit `sections.jsonnet` in GET
- Omit `target.jsonnet` in UPDATE
- Use flat schema structure

---

### Anti-Pattern 3: Complete Mode for Collaborative Docs

**Problem**: Using complete mode for team blueprints developed over time

**Solution**: Use modular mode
- Initial section rendered
- Progressive section development
- Granular permissions

---

## Validation Checklist

Before finalizing process design, verify:

- [ ] Process type matches primary goal (create/modify/read)
- [ ] File combination matches intended operation
- [ ] Schema inheritance uses semantic URIs where appropriate
- [ ] Artifact configuration shared between GET and UPDATE
- [ ] Build mode aligns with creation workflow
- [ ] Classification matches audience (process vs terminal)
- [ ] Section strategy matches content complexity
- [ ] Permissions grant access to appropriate agents

---

## Related Documentation

- **[Semantic URI Reference](../templating-system/semantic-uri-reference.md)**: Asset sharing
- **[Jsonnet Schemas Guide](../templating-system/jsonnet-schemas-guide.md)**: Data contract patterns

---

## Summary

Process design requires strategic decisions about:

1. **Process Type**: CREATE for new, UPDATE for modifications, GET for retrieval
2. **Build Mode**: Complete for all-at-once, modular for progressive
3. **Classification**: Process for internal, terminal for deliverables
4. **Sections**: Single for simple, multi for complex documents

Use this framework to make informed decisions that align with your workflow requirements.
