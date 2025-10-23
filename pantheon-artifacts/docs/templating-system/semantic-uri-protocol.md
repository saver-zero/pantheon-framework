---
doc_id: templating-system-semantic-uri-protocol
title: "Semantic URI Protocol for Asset Sharing"
description: "Cross-process asset referencing using semantic URIs for schema composition, artifact reuse, and template includes within team packages"
keywords: [semantic-uri, import, reuse, DRY, schema-composition, artifact-locator, template-includes, process-redirection]
relevance: "Use this document when you need to understand how to share schemas, artifact configurations, or templates between processes using semantic URI imports"
---

# Semantic URI Protocol for Asset Sharing

## Overview

The Pantheon Framework provides **semantic URIs** to reference process assets within the same team package, enabling code reuse while maintaining sandboxing boundaries. This protocol allows processes to share schemas, artifact configurations, and templates without duplication.

## Purpose and Benefits

### Why Semantic URIs Exist

Without semantic URIs, team packages would suffer from:
- **Schema duplication**: UPDATE processes copying CREATE schemas verbatim
- **Artifact configuration drift**: Different processes using inconsistent locator/parser logic
- **Template inconsistency**: Section templates diverging between CREATE and UPDATE processes
- **Maintenance burden**: Changes requiring updates across multiple files

### Core Benefits

1. **DRY Principle**: Single source of truth for shared assets
2. **Consistency Guarantees**: Shared logic ensures identical behavior across processes
3. **Reduced Maintenance**: Updates propagate automatically to all importers
4. **Composability**: Build specialized processes by combining existing ones

## Semantic URI Types

The framework supports five semantic URI schemes for intra-team referencing:

### 1. process-schema://

**Purpose**: Reference another process's data contract or section schema fragments

**Syntax**:
- `import "process-schema://process-name"` (full schema)
- `import "process-schema://process-name/sections/section-name"` (section fragment)

**Use Cases**:
- UPDATE processes inheriting CREATE process schemas
- CREATE processes importing UPDATE section schemas for composition

**Example (Full Schema Import)**:
```jsonnet
// In processes/update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

**Example (Section Fragment Import)**:
```jsonnet
// In processes/create-ticket/schema.jsonnet
local sections = [
  {
    name: "ticket_description",
    schema: import "process-schema://update-ticket/sections/ticket_description",
    enabled: true
  }
];
```

This ensures UPDATE and CREATE processes use identical data contracts, preventing validation mismatches.

---

### 2. process-routine://

**Purpose**: Reference another process's routine instructions

**Syntax**: `import "process-routine://process-name"`

**Use Case**: Creating process variants with shared logic

**Example**:
```jsonnet
// In processes/get-detailed-context/routine.md
import "process-routine://get-context"
```

This enables building specialized processes that extend base workflows.

---

### 3. artifact-locator://

**Purpose**: Reference artifact finding configuration

**Syntax**: `import "artifact-locator://process-name"`

**Use Case**: UPDATE processes reusing GET process locators

**Example**:
```jsonnet
// In processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"
```

This guarantees UPDATE and GET processes find artifacts identically.

---

### 4. artifact-parser://

**Purpose**: Reference ID normalization rules

**Syntax**: `import "artifact-parser://process-name"`

**Use Case**: UPDATE processes reusing GET process parsers

**Example**:
```jsonnet
// In processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

This ensures consistent ID normalization across artifact operations.

---

### 5. artifact-sections://

**Purpose**: Reference section marker configuration with optional data extraction

**Syntax**: `import "artifact-sections://process-name?data=path.to.data"`

**Use Case**: UPDATE processes targeting specific sections from GET definitions

**Example**:
```jsonnet
// In processes/update-plan/artifact/target.jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```

The `?data=` query parameter enables extracting specific subsections from the sections configuration.

---

### 6. artifact-template://

**Purpose**: Include section templates from other processes

**Syntax**: `{% include 'artifact-template://process-name/sections/section-name' %}`

**Use Case**: CREATE processes reusing UPDATE section templates

**Example**:
```jinja2
<!-- In processes/create-architecture-guide/artifact/content.md -->
# Architecture Guide for {{ project_name }}

## Core Principles
{% include 'artifact-template://update-architecture-guide/sections/core-principles' %}

## High-Level Overview
{% include 'artifact-template://update-architecture-guide/sections/high-level-overview' %}
```

**Convention Mapping**:
- `artifact-template://update-guide/sections/core-principles`
- → `processes/update-guide/artifact/sections/core-principles.md`

**Benefits**:
- Section templates maintained in one location (UPDATE process)
- CREATE and UPDATE use identical section content
- Updates propagate automatically

**Note**: Section template includes do NOT automatically add the `with context` directive. Include it explicitly when needed for variable propagation: `{% include 'artifact-template://process/sections/section' with context %}`

---

## Common Usage Patterns

### Pattern 1: CREATE-UPDATE Schema Inheritance

**Problem**: UPDATE process needs same validation as CREATE

**Solution**:
```jsonnet
// processes/update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

**Result**: Schema changes in CREATE automatically apply to UPDATE

---

### Pattern 2: GET-UPDATE Artifact Sharing

**Problem**: UPDATE process must find artifacts identically to GET

**Solution**:
```jsonnet
// processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"

// processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

**Result**: Guaranteed consistency in artifact discovery and ID handling

---

### Pattern 3: Section Template Reuse

**Problem**: CREATE process needs same section content as UPDATE

**Solution**:
```jinja2
<!-- processes/create-blueprint/artifact/content.md -->
## Overview
{% include 'artifact-template://update-blueprint/sections/overview' %}

## Architecture
{% include 'artifact-template://update-blueprint/sections/architecture' %}
```

**Result**: Single source of truth for section templates

---

### Pattern 4: Process Redirection

**Problem**: Need specialized process for subset of functionality

**Solution**:
```markdown
<!-- processes/get-plan/redirect.md -->
process://get-ticket?pantheon_sections=plan
```

**Result**: Specialized process without duplicating routine logic

---

## Technical Implementation

### Resolution Process

1. **Import Detection**: Jsonnet/Jinja2 parser encounters semantic URI
2. **Convention Mapping**: Framework maps URI to physical file path using Workspace conventions
3. **Boundary Enforcement**: Workspace validates access within team sandbox
4. **Content Retrieval**: Framework loads referenced asset content
5. **Inline Substitution**: Content replaces import statement

### File Path Conventions

The framework uses these mapping rules:

| Semantic URI | Physical Path |
|--------------|---------------|
| `process-schema://name` | `processes/name/schema.jsonnet` |
| `process-routine://name` | `processes/name/routine.md` |
| `artifact-locator://name` | `processes/name/artifact/locator.jsonnet` |
| `artifact-parser://name` | `processes/name/artifact/parser.jsonnet` |
| `artifact-sections://name` | `processes/name/artifact/sections.jsonnet` |
| `artifact-template://name/sections/sec` | `processes/name/artifact/sections/sec.md` |

### Custom Jinja2 Loader

The framework implements `SemanticUriLoader` to handle `artifact-template://` URIs:

- Intercepts Jinja2 `{% include %}` statements
- Resolves semantic URIs through Workspace
- Returns template content for rendering
- Maintains sandboxing boundaries

---

## Best Practices

### When to Use Semantic URIs

**Use semantic URIs when**:
- UPDATE process needs same schema as CREATE
- Multiple processes target same artifact type
- Section content must stay synchronized
- Specialized processes extend base workflows

**Avoid semantic URIs when**:
- Processes have genuinely different requirements
- Coupling would create maintenance complexity
- Cross-team references are needed (not supported)

### Versioning Considerations

Semantic URIs create tight coupling:
- Breaking changes in referenced assets affect all importers
- Test thoroughly after modifying imported assets
- Consider deprecation strategies for major changes

### Debugging Import Issues

If imports fail:
1. Verify referenced process exists in same team package
2. Check file naming follows conventions exactly
3. Ensure referenced asset file exists at expected location
4. Review Workspace resolution logs for path mapping errors

---

## Advanced: Process Redirection

### Redirection Protocol

Processes can redirect execution to other processes using `redirect.md`:

**Simple Redirection**:
```markdown
<!-- processes/get-simple-context/redirect.md -->
process://get-ticket
```

**Parameterized Redirection**:
```markdown
<!-- processes/get-plan/redirect.md -->
process://get-ticket?pantheon_sections=plan
```

**Multi-Section Redirection**:
```markdown
<!-- processes/get-detailed-plan/redirect.md -->
process://get-ticket?pantheon_sections=plan,description,acceptance_criteria
```

### Parameter Merging

When redirection includes parameters:
1. User-provided parameters are collected
2. Redirect parameters are applied
3. Redirect parameters take precedence for security
4. Merged parameters passed to target process

### Use Cases

- **Section extraction**: Get specific sections from multi-section artifacts
- **Simplified interfaces**: Hide complexity behind simpler process names
- **Workflow composition**: Chain redirects to build complex operations

---

## Related Documentation

- **[Jsonnet Schemas Guide](./jsonnet-schemas-guide.md)**: Data contract design patterns
- **[Template Composition Patterns](./template-composition-patterns.md)**: DRY principles and code reuse strategies

---

## Summary

Semantic URIs provide a structured protocol for asset sharing within team packages:

- **Five URI schemes** for different asset types
- **Convention-based mapping** from URIs to file paths
- **DRY compliance** through single source of truth
- **Sandboxed security** within team boundaries
- **Automatic propagation** of changes to importers

Use semantic URIs to eliminate duplication and ensure consistency across your process families.
