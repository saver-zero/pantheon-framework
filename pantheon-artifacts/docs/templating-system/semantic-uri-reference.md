---
doc_id: semantic-uri-reference
title: "Semantic URI Reference"
description: "Complete reference for semantic URI schemes used in Pantheon for cross-process asset sharing including process-schema, artifact-template, artifact-locator, and other URI protocols."
keywords: [semantic-uri, uri-schemes, process-schema, artifact-template, artifact-locator, artifact-parser, artifact-sections, cross-process-imports]
relevance: "Use this document as a reference for all semantic URI schemes available in Pantheon when sharing assets between processes."
---

# Semantic URI Reference

Pantheon uses **semantic URIs** to reference assets within team packages while maintaining sandboxing boundaries. This document provides a complete reference for all supported URI schemes.

## URI Schemes Overview

| Scheme | Purpose | Resolves To |
|--------|---------|-------------|
| `process-schema://` | Import schemas from other processes | `processes/<process-name>/schema.jsonnet` |
| `process-routine://` | Import routines from other processes | `processes/<process-name>/routine.md` |
| `artifact-locator://` | Import artifact finding configuration | `processes/<process-name>/artifact/locator.jsonnet` |
| `artifact-parser://` | Import ID normalization rules | `processes/<process-name>/artifact/parser.jsonnet` |
| `artifact-sections://` | Import section configuration with data extraction | `processes/<process-name>/artifact/sections.jsonnet` |
| `artifact-template://` | Include Jinja2 templates from other processes | `processes/<process-name>/artifact/<relative-path>.md` |

## process-schema://

**Purpose:** Import schemas from other processes

**Pattern:** `process-schema://<process-name>`

**Resolves To:** `processes/<process-name>/schema.jsonnet`

### Basic Example

```jsonnet
// processes/update-ticket/schema.jsonnet
import "process-schema://create-ticket"
```

### Use Cases

1. **UPDATE processes inheriting CREATE schemas**
   ```jsonnet
   // UPDATE uses same data contract as CREATE
   import "process-schema://create-ticket"
   ```

2. **Shared base schemas across process families**
   ```jsonnet
   local baseSchema = import "process-schema://base-artifact";

   baseSchema + {
     properties+: {
       specialized_field: { type: 'string' }
     }
   }
   ```

3. **Schema composition and extension**
   ```jsonnet
   local createSchema = import "process-schema://create-ticket";

   createSchema + {
     properties+: {
       update_timestamp: { type: 'string', format: 'date-time' }
     }
   }
   ```

## process-routine://

**Purpose:** Import routines from other processes

**Pattern:** `process-routine://<process-name>`

**Resolves To:** `processes/<process-name>/routine.md`

### Basic Example

```markdown
<!-- processes/get-ticket-plan/redirect.md -->
process://get-ticket?pantheon_sections=plan
```

### Use Cases

1. **Process redirection**
   ```markdown
   process://get-ticket?pantheon_sections=plan,status
   ```

2. **Specialized process variants**
   ```markdown
   <!-- Get only the plan section from tickets -->
   process://get-ticket?pantheon_sections=plan
   ```

3. **Routine reuse**
   - Specialized processes delegate to general processes
   - Parameter forwarding maintained

## artifact-locator://

**Purpose:** Import artifact finding configuration

**Pattern:** `artifact-locator://<process-name>`

**Resolves To:** `processes/<process-name>/artifact/locator.jsonnet`

### Basic Example

```jsonnet
// processes/update-ticket/artifact/locator.jsonnet
import "artifact-locator://get-ticket"
```

### Use Cases

1. **UPDATE processes reusing GET locators**
   ```jsonnet
   // UPDATE and GET use identical artifact finding logic
   import "artifact-locator://get-ticket"
   ```

2. **Consistent artifact finding logic**
   - Single source of truth for locating artifacts
   - Changes propagate to all dependent processes

3. **Shared search patterns**
   ```jsonnet
   // GET process defines locator
   // processes/get-ticket/artifact/locator.jsonnet
   {
     directory: "tickets",
     local id = std.extVar("pantheon_artifact_id"),
     pattern: "^" + id + "-.*[.]md$"
   }

   // UPDATE imports same locator
   // processes/update-ticket/artifact/locator.jsonnet
   import "artifact-locator://get-ticket"
   ```

### Benefits
- Guaranteed consistency between GET and UPDATE
- Single location for finding logic changes
- No duplication of search patterns

## artifact-parser://

**Purpose:** Import ID normalization rules

**Pattern:** `artifact-parser://<process-name>`

**Resolves To:** `processes/<process-name>/artifact/parser.jsonnet`

### Basic Example

```jsonnet
// processes/update-ticket/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

### Use Cases

1. **Consistent ID parsing across process families**
   ```jsonnet
   // GET process defines parser
   // processes/get-ticket/artifact/parser.jsonnet
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

   // UPDATE imports same parser
   // processes/update-ticket/artifact/parser.jsonnet
   import "artifact-parser://get-ticket"
   ```

2. **Shared normalization rules**
   - ID format normalization (e.g., "001" → "T001")
   - Whitespace trimming
   - Case normalization

3. **UPDATE/GET alignment**
   - Both processes use identical ID parsing
   - No inconsistency in artifact identification

## artifact-sections://

**Purpose:** Import section configuration with data extraction

**Pattern:** `artifact-sections://<process-name>?data=<json-path>`

**Resolves To:** `processes/<process-name>/artifact/sections.jsonnet` with data extraction

### Basic Example

```jsonnet
// processes/update-ticket/artifact/target.jsonnet
import "artifact-sections://get-ticket?data=sections.plan"
```

### Use Cases

1. **UPDATE processes targeting sections from GET**
   ```jsonnet
   // GET process defines sections
   // processes/get-ticket/artifact/sections.jsonnet
   {
     "sections": {
       "plan": {
         "start": "<!-- START_SECTION:plan -->",
         "end": "<!-- END_SECTION:plan -->"
       },
       "status": {
         "start": "<!-- START_SECTION:status -->",
         "end": "<!-- END_SECTION:status -->"
       }
     }
   }

   // UPDATE targets specific section
   // processes/update-ticket/artifact/target.jsonnet
   import "artifact-sections://get-ticket?data=sections.plan"
   ```

2. **Section marker consistency**
   - UPDATE targets exact section markers defined in GET
   - Single source of truth for section boundaries

3. **Extraction of specific section data**
   - `?data=sections.plan` extracts only the plan section
   - Flexible data path queries

### Data Path Syntax

```jsonnet
// Extract root sections object
import "artifact-sections://get-ticket?data=sections"

// Extract specific section
import "artifact-sections://get-ticket?data=sections.plan"

// Extract nested data
import "artifact-sections://get-ticket?data=sections.plan.start"
```

## artifact-template://

**Purpose:** Include Jinja2 templates from other processes

**Pattern:** `artifact-template://<process-name>/<relative-path>`

**Resolves To:** `processes/<process-name>/artifact/<relative-path>.md`

### Basic Example

```jinja2
{% include 'artifact-template://update-guide/sections/overview' %}
```

### Use Cases

1. **CREATE processes including UPDATE section templates**
   ```jinja2
   <!-- processes/create-guide/artifact/content.md -->
   # {{ title }}

   {% include 'artifact-template://update-guide/sections/overview' %}
   {% include 'artifact-template://update-guide/sections/details' %}
   {% include 'artifact-template://update-guide/sections/conclusion' %}
   ```

2. **Shared section content**
   - Section templates defined once in UPDATE process
   - CREATE and UPDATE use identical section formatting
   - Changes to sections propagate automatically

3. **Template fragment reuse**
   ```jinja2
   <!-- Reuse common section formatting -->
   {% include 'artifact-template://shared/implementation-section' %}
   ```

### Advanced Example with Conditionals

```jinja2
{% set _include_technical_plan = true %}
{% if _include_technical_plan %}
{% include 'artifact-template://update-ticket/sections/technical_plan' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
```

## Workspace Resolution

The Pantheon Workspace automatically resolves semantic URIs using conventions:

### Convention Mapping

```
process-schema://create-ticket
  → processes/create-ticket/schema.jsonnet

artifact-template://update-guide/sections/overview
  → processes/update-guide/artifact/sections/overview.md

artifact-locator://get-ticket
  → processes/get-ticket/artifact/locator.jsonnet

artifact-parser://get-ticket
  → processes/get-ticket/artifact/parser.jsonnet

artifact-sections://get-ticket?data=sections.plan
  → processes/get-ticket/artifact/sections.jsonnet (with data extraction)
```

### No Configuration Required
- No registration of imports
- No manifest files
- Runtime discovery via conventions

## Custom Jinja2 Loader

The framework provides a `SemanticUriLoader` that:
- Resolves `artifact-template://` URIs
- Maintains architectural boundaries
- Integrates with Workspace for path resolution
- Enables transparent cross-process includes

## Best Practices

### 1. Use Semantic URIs Over Relative Paths

**Good:**
```jsonnet
import "process-schema://create-ticket"
```

**Bad:**
```jsonnet
import "../create-ticket/schema.jsonnet"
```

**Rationale:** Semantic URIs are portable and maintain abstraction

### 2. Establish Single Sources of Truth

**Pattern:**
- UPDATE process sections are canonical
- CREATE includes from UPDATE
- GET/UPDATE share artifact configuration

### 3. Document URI Dependencies

```markdown
<!-- This template includes:
- artifact-template://update-guide/sections/overview
- artifact-template://update-guide/sections/details
-->
```

### 4. Use ignore missing for Optional Components

```jinja2
{% include 'artifact-template://optional/section' ignore missing %}
```

Prevents errors when optional templates don't exist

### 5. Use with context in Template Includes

```jinja2
{% include 'artifact-template://update-guide/sections/overview' with context %}
```

Ensures variables propagate correctly

## Testing Semantic URIs

### Verify Import Resolution

```bash
# Test schema import
pantheon get schema update-ticket --actor test-agent

# Verify template includes render
pantheon execute create-guide --from-file test-data.json --actor test-agent
```

### Test Cross-Process Consistency

```bash
# CREATE and UPDATE should use same section formatting
pantheon execute create-ticket --from-file create-data.json --actor test-agent
pantheon execute update-plan --from-file update-data.json --actor test-agent

# Compare section content structure
```

### Validate URI Resolution

```bash
# Test process with imports
pantheon execute update-ticket --from-file data.json --actor test-agent

# Check logs for resolution errors
```

## Related Documentation

- **[Template Composition Patterns](./template-composition-patterns.md)** - Advanced composition techniques
- **[Jsonnet Schemas Guide](./jsonnet-schemas-guide.md)** - Schema composition patterns
- **[Jinja2 Templates Guide](./jinja2-templates-guide.md)** - Template development
- **[Semantic URI Protocol](./semantic-uri-protocol.md)** - Detailed protocol documentation

---

Semantic URIs enable cross-process asset sharing while maintaining architectural boundaries and sandboxing. By using consistent URI schemes, you create maintainable, DRY processes that automatically propagate changes across process families.
