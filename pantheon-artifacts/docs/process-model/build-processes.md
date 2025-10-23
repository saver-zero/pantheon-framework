---
doc_id: process-model-build
title: "BUILD Processes"
description: "BUILD process behavior and workflow for scaffolding complete process families from declarative specifications"
keywords: [build, process-model, scaffolding, process-generation, build-schema]
relevance: "Use this document to understand BUILD process structure and how complete process families are generated from build specifications"
---

# BUILD Processes

BUILD processes generate complete process families (CREATE, GET, UPDATE) from declarative specifications.

## File Requirements

### Required Files
- **`build-schema.jsonnet`** - Schema for build specification (at process root, not in artifact/)
- **`routine.md`** - Instructions for creating build specifications
- **`permissions.jsonnet`** - Access control for BUILD operations

### Optional Files
- **`directory.jinja`** - Template for bundle output location

## Process Detection

A process is considered BUILD if `build-schema.jsonnet` exists at the **process root level** (not in `artifact/` subdirectory).

## Build Specification Structure

Build specifications define:
- **Artifact metadata**: Name, description, type
- **Sections**: Array of section definitions (name, description, schema properties)
- **Permissions**: Access control rules for generated processes
- **Templates**: Initial content for sections (complete vs modular mode)

## Workflow

1. Agent retrieves schema: `pantheon get schema build-team-process --actor pantheon`
2. Agent creates comprehensive build-spec.json
3. Agent executes: `pantheon execute build-team-process --from-file build-spec.json --actor pantheon`
4. Framework validates build specification
5. Framework creates immutable `_BuildContext`
6. Framework scaffolds processes in dependency order:
   - **Phase 2**: CREATE process with section markers
   - **Phase 3**: GET process with section definitions
   - **Phase 4**: Consolidated UPDATE process with section schemas
7. Framework writes bundle to `pantheon-artifacts/` for review
8. User manually copies validated processes to `pantheon-teams/<team>/processes/`

## Single-Section Detection

If `sections.length === 1`, framework automatically uses simplified structure:
- CREATE: No section markers in content.md
- GET: No sections.jsonnet file
- UPDATE: No target.jsonnet, no sections/ subdirectory
- Schemas: Flat structure without section_updates wrapper

## Complete vs Modular Mode

The `build_mode` parameter controls the **default toggle values** in generated processes, determining which sections are enabled by default in both schemas (`enabled` flags) and templates (`_include_*` variables).

### Complete Mode (`build_mode: "complete"`)
- Sets all section `enabled` flags to `true` in generated schemas
- Sets all `_include_*` template variables to `true` in generated templates
- Renders all section content during CREATE operations
- Generates fully populated initial artifacts
- Best for artifacts created once with all content

### Modular Mode (`build_mode: "modular"`)
- Sets only initial section `enabled` flag to `true`, others to `false`
- Sets only initial `_include_*` variable to `true`, others to `false`
- CREATE renders initial section with full content, placeholders for others
- UPDATE process used to populate remaining sections later
- Best for collaborative multi-step workflows with staged completion

### Post-Generation Flexibility

The `build_mode` parameter determines **initial defaults only**. After generation, you can modify section toggle values to change rendering behavior without regenerating the process:

1. Edit `enabled` flags in the generated `schema.jsonnet`
2. Edit `_include_*` variables in the generated `artifact/content.md`
3. Test the modified process behavior

This separation between user intent (`build_mode` parameter) and implementation mechanism (toggle pattern) provides runtime flexibility while maintaining backward compatibility.

## Generated Patterns

### Section Enabling/Disabling Structure

BUILD processes automatically generate a sophisticated pattern for managing optional sections in CREATE processes. The `build_mode` parameter determines the initial state of these toggles, but the pattern itself is always generated regardless of mode. This pattern combines:

1. **Schema composition** with semantic URI imports and `enabled` flags
2. **Template composition** with conditional includes using local variables
3. **Easy human configuration** through boolean flag toggles
4. **Build mode integration** where `build_mode` parameter sets initial toggle defaults

#### How build_mode Sets Toggle Defaults

When generating a BUILD process:
- `build_mode: "complete"` sets all `enabled` flags to `true` and all `_include_*` variables to `true`
- `build_mode: "modular"` sets only the initial section's flags to `true`, others to `false`

The toggle pattern structure is identical in both modes - only the default boolean values differ.

**Generated Schema Structure (CREATE):**
```jsonnet
// build_mode parameter determines enabled flag defaults:
// - build_mode="complete": all enabled flags set to true
// - build_mode="modular": only initial section enabled=true, others false
local sections = [
  {
    name: "initial_section",
    schema: import "process-schema://update-artifact/sections/initial_section",
    enabled: true  // Always true for initial section
  },
  {
    name: "second_section",
    schema: import "process-schema://update-artifact/sections/second_section",
    enabled: true  // true for complete, false for modular
  },
  // ... more sections with enabled set by build_mode
];

local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.schema.properties else acc,
  sections,
  {}
);

local required = std.foldl(
  function(acc, sec)
    if sec.enabled && std.objectHas(sec.schema, 'required')
    then acc + sec.schema.required
    else acc,
  sections,
  []
);

{
  type: 'object',
  properties: properties,
  required: required
}
```

**Generated Template Structure (CREATE):**
```jinja2
{# build_mode parameter determines _include_* variable defaults:
   - build_mode="complete": all _include_* variables set to true
   - build_mode="modular": only initial section _include_*=true, others false #}
{% set _include_initial_section = true %}  {# Always true for initial section #}
{% set _include_second_section = true %}  {# true for complete, false for modular #}

<!-- SECTION:START:INITIAL_SECTION -->
{% if _include_initial_section %}
{% include 'artifact-template://update-artifact/sections/initial_section' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:INITIAL_SECTION -->

<!-- SECTION:START:SECOND_SECTION -->
{% if _include_second_section %}
{% include 'artifact-template://update-artifact/sections/second_section' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:SECOND_SECTION -->
```

**Configuration Workflow:**

The `build_mode` parameter sets initial toggle defaults during generation. To modify section inclusion after generation:

1. Edit `enabled` flags in the generated `schema.jsonnet`
2. Edit `_include_*` variables in the generated `artifact/content.md`
3. Test the modified process execution

**Key Architectural Insight:** The `build_mode` parameter controls **what the defaults are** (input parameter layer), not **how rendering works** (implementation layer). This separation enables:
- Transparent behavior through visible toggle flags
- Runtime flexibility without regeneration
- Single canonical pattern (toggle-based) for all BUILD processes
- Easy modification of section inclusion post-generation

See [Jinja2 Templates Guide](../templating-system/jinja2-templates-guide.md) and [Template Composition Patterns](../templating-system/template-composition-patterns.md) for detailed documentation of this pattern.

## Benefits

- **Rapid Development**: Generate entire process family from specification
- **Consistency**: Ensures CREATE, GET, UPDATE work together seamlessly
- **Glass Box**: All generated code staged for review before integration
- **DRY Principle**: Single source of truth for artifact structure
- **Easy Configuration**: Generated patterns support simple boolean toggles for section management

---

**Related:** [Process Model Overview](overview.md) | [CREATE Processes](create-processes.md) | [UPDATE Processes](update-processes.md) | [GET Processes](get-processes.md)
