---
doc_id: scaffolding-workflow
title: Build Process Scaffolding Workflow
description: Technical documentation for the build-team-process scaffolding system including component architecture, five-phase build workflow, section markers, cross-process references, and single-section simplification for intelligent process family generation
keywords: [build process, scaffolding, process family, build-spec, CREATE process, GET process, UPDATE process, section markers, agent routine, schema validation]
relevance: Essential technical reference for understanding how build-team-process generates complete process families from specifications and the intelligent scaffolding logic behind automated process creation
---

# Build Process Scaffolding Workflow

The `pantheon-team-builder` team uses a powerful **`build-team-process`** to generate entire process families from a single specification. Instead of manually creating separate processes for CREATE, GET, and UPDATE operations, an agent defines the core behavior in a `build-spec.json` file, and the framework scaffolds the complete family.

## The Build Workflow: Component Symphony

The agent's workflow for building a process family is a partnership between four components:

### 1. The LLM Agent (The Architect)

The agent's role is creative design. It uses the `build-team-process` routine as its guide to perform high-level design and assemble a complete architectural plan: the `build-spec.json`.

### 2. The Routine (The Scaffold)

The `build-team-process` routine is the agent's user manual. It provides step-by-step cognitive scaffolding, guiding the agent through the design process and pointing it to the tools and information needed at the right time.

### 3. The Schema (The Contract)

The `build-schema.jsonnet` provides the rigid, unambiguous contract for the `build-spec.json`. It validates the agent's final plan, ensuring it is perfectly structured and machine-readable.

### 4. The Framework (The Fabricator)

The framework code acts as the deterministic construction crew. It takes the validated `build-spec.json` and executes the plan, mechanically scaffolding the entire process family.

## Build Specification Structure

After following the routine, the agent produces a `build-spec.json` file containing:

### Core Identity

- **`target_team`**: The team package where processes will be installed
- **`artifact`**: The core noun (e.g., "ticket", "document")
- **`build_mode`**: `complete` (all sections rendered) or `modular` (collaborative building)
- **`include_context`**: `true` for Process Artifacts, `false` for Terminal Artifacts

### Section Definitions

- **`sections`**: Array of section names (e.g., ["description", "plan"])
- **`initial_section`**: Which section creates the artifact
- **`section_template`**: Array of section definitions with schema and template

### Artifact Location

- **`artifact_location`**: Object with `directory` and `filename_template`

### Permissions

- **`permissions`**: Operation-specific access control for `create`, `get`, `update`

### Example Build Spec

```json
{
  "target_team": "pantheon-dev",
  "artifact": "ticket",
  "build_mode": "modular",
  "include_context": true,
  "sections": ["description", "plan"],
  "initial_section": "description",
  "section_template": [
    {
      "section": "description",
      "template": "# {{ title }}\n\n## Business Context\n{{ business_context }}\n\n",
      "schema": {
        "properties": {
          "title": {
            "type": "string",
            "purpose": "Concise, human-readable identifier for the ticket",
            "description_for_schema": "A short, descriptive title for the ticket"
          },
          "business_context": {
            "type": "string",
            "purpose": "High-level 'why' behind the ticket",
            "description_for_schema": "Detailed explanation of business reasons"
          }
        },
        "required": ["title", "business_context"]
      }
    }
  ],
  "artifact_location": {
    "directory": "tickets/",
    "filename_template": "T{{ pantheon_artifact_id }}_{{ title | slugify }}.md"
  },
  "permissions": {
    "create": {"allow": ["tech-lead"], "deny": []},
    "get": {"allow": ["*"], "deny": []},
    "update": {"allow": ["tech-lead"], "deny": []}
  }
}
```

## Intelligent Scaffolding Logic

The framework's BUILD process follows a structured five-phase approach:

### Phase 1: Context Initialization and Validation

**Actions:**
- Extract user parameters, excluding framework built-ins
- Restore original "sections" business parameter from build-spec
- Validate build-spec against `build-schema.jsonnet`
- Create immutable `_BuildContext` containing all state
- Render output directory template for staging location

### Phase 2: CREATE Process Scaffolding

**Generated Files:**
- `artifact/content.md` - Section templates with HTML markers
- `artifact/placement.jinja` - Directory location template
- `artifact/naming.jinja` - Filename generation template
- `schema.jsonnet` - Data contract from initial section
- `permissions.jsonnet` - Access control rules
- `routine.md` - Step-by-step execution instructions

**Template Structure:**
```markdown
<!-- SECTION:START:DESCRIPTION -->
{{ title }}

{{ business_context }}
<!-- SECTION:END:DESCRIPTION -->

<!-- SECTION:START:PLAN -->
<!-- PLACEHOLDER:PLAN -->
<!-- SECTION:END:PLAN -->
```

### Phase 3: GET Process Scaffolding

**Generated Files:**
- `artifact/sections.jsonnet` - Section marker definitions
- `artifact/locator.jsonnet` - Artifact finding pattern
- `artifact/parser.jsonnet` - ID normalization rules
- `permissions.jsonnet` - Access control rules
- `routine.md` - Retrieval instructions

**Sections Configuration:**
```jsonnet
{
  sections: {
    description: {
      start: "<!-- SECTION:START:DESCRIPTION -->",
      end: "<!-- SECTION:END:DESCRIPTION -->",
      description: "Business context and requirements"
    },
    plan: {
      start: "<!-- SECTION:START:PLAN -->",
      end: "<!-- SECTION:END:PLAN -->",
      description: "Technical implementation plan"
    }
  }
}
```

### Phase 4: UPDATE Process Scaffolding

**Generated Files (per non-initial section):**
- `artifact/patch.md` - Section replacement template
- `artifact/target.jsonnet` - Section targeting configuration
- `artifact/locator.jsonnet` - Import from GET process
- `artifact/parser.jsonnet` - Import from GET process
- `schema.jsonnet` - Section-specific data contract
- `permissions.jsonnet` - Access control rules
- `routine.md` - Update instructions

**Cross-Process References:**
```jsonnet
// In update-ticket-plan/artifact/locator.jsonnet
import "artifact-locator://get-ticket"

// In update-ticket-plan/artifact/parser.jsonnet
import "artifact-parser://get-ticket"
```

### Phase 5: Bundle Staging and Summary

**Actions:**
- Save all generated processes to `pantheon-artifacts/pantheon-team-builds/<team>/`
- Generate summary listing all created processes
- Return staging location for review

**Output Structure:**
```
pantheon-artifacts/pantheon-team-builds/pantheon-dev/
├── create-ticket/
├── get-ticket/
└── update-ticket-plan/
```

## Section Marker System

All generated processes use HTML comment markers for structured document parsing:

### Section Markers

```html
<!-- SECTION:START:DESCRIPTION -->
Content here
<!-- SECTION:END:DESCRIPTION -->
```

### Placeholder Markers

```html
<!-- SECTION:START:IMPLEMENTATION -->
<!-- PLACEHOLDER:IMPLEMENTATION -->
<!-- SECTION:END:IMPLEMENTATION -->
```

### Benefits

- **Machine-readable**: Precise section boundaries for parsing
- **Human-readable**: Visible in Markdown source
- **HTML-compatible**: Invisible in rendered output
- **Consistent**: Standard format across all artifacts

## Single-Section Simplification

The build process automatically detects and optimizes single-section artifacts using the **"1 section = no sections"** principle.

### Automatic Detection

When `sections.length === 1`, the builder triggers simplified scaffolding:

- **CREATE**: Simple content template without section markers
- **GET**: Only `locator.jsonnet` and `parser.jsonnet` (no `sections.jsonnet`)
- **UPDATE**: Whole document replacement using `patch.md` (no `target.jsonnet`)

### Example: Multi-Section vs Single-Section

**Multi-Section (Complex Ticket):**
```
create-ticket/          # Initial section only
get-ticket/             # Full section parsing
update-ticket-plan/     # Specific section updates
update-ticket-review/   # Specific section updates
```

**Single-Section (Simple Status):**
```
create-status/          # Complete document
get-status/             # Whole document retrieval
update-status/          # Whole document replacement
```

### Benefits

1. **Simplified File Structure**: Fewer files for simple artifacts
2. **Cleaner Templates**: No section iteration logic
3. **Flatter Schemas**: Direct property access
4. **Reduced Cognitive Load**: Simpler mental model

## Build Modes

### Complete Mode

**Characteristics:**
- Renders every section with real content
- Both CREATE and UPDATE have full templates
- Section schema fragments compiled without `$schema`
- Best for: Simple, self-contained documents

**Use Cases:**
- Agent prompts (all content defined upfront)
- Configuration files
- Brief reports

### Modular Mode

**Characteristics:**
- Renders initial section only (plus optional context)
- Other sections get placeholders
- Incremental collaboration through UPDATE processes
- Best for: Complex, multi-stage documents

**Use Cases:**
- Project tickets (description → plan → review)
- Technical specs (overview → details → implementation)
- Team blueprints (mission → agents → processes)

## ProcessHandler Orchestration

The BUILD process is orchestrated by `ProcessHandler.execute_build_process()`:

### Process Type Detection

Uses `determine_process_type()` to check for `build-schema.jsonnet`, identifying BUILD operation.

### Context Initialization

Calls `_build_init_context()` to validate input and create immutable state.

### Sequential Scaffolding

Executes phases in dependency order:
1. CREATE (base artifact)
2. GET (retrieval mechanism)
3. UPDATE (modification processes)

### Workspace Integration

Uses `PantheonWorkspace` methods:
- `scaffold_create_process()`
- `scaffold_get_process()`
- `scaffold_update_process()`

### Bundle Management

All files written to `PantheonPath` objects under artifacts sandbox.

## Best Practices

### Designing Build Specs

1. **Clear Purpose**: Define artifact's primary goal
2. **Logical Sections**: Break content into coherent parts
3. **Meaningful Names**: Use descriptive section names
4. **Proper Classification**: Distinguish Process vs Terminal artifacts
5. **Complete Schemas**: Define all required properties

### Section Design

1. **Single Responsibility**: Each section has one clear purpose
2. **Orthogonal Content**: Sections don't overlap
3. **Appropriate Granularity**: Not too fine, not too coarse
4. **Clear Descriptions**: Help agents understand section purpose
5. **Consistent Naming**: Follow team conventions

### Template Design

1. **Use Profile Variables**: Support configuration-based customization
2. **Include Framework Variables**: Leverage `pantheon_actor`, `pantheon_timestamp`
3. **Proper Formatting**: Use Markdown best practices
4. **Clear Structure**: Logical content organization
5. **Comment Markers**: Never include section markers in templates

### Testing Generated Processes

1. **Review Staged Output**: Inspect before promotion
2. **Test CREATE Process**: Verify artifact generation
3. **Test GET Process**: Confirm retrieval works
4. **Test UPDATE Process**: Validate section updates
5. **Check Permissions**: Verify access control

This scaffolding workflow transforms process creation from tedious, file-by-file work into declarative, architectural design, ensuring consistency and enforcing best practices across the entire system.
