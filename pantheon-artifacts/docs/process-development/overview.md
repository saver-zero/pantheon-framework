---
doc_id: process-development-overview
title: "Process Development Overview"
description: "Introduction to developing Pantheon processes using the Unified Execute Model with operation-specific workflows."
keywords: [process, development, unified-execute-model, create, update, get, workflow]
relevance: "Use this document to understand the overall process development workflow, available operation types, and the tools used for building processes in Pantheon team packages."
---

# Process Development Overview

This guide introduces the core concepts and workflows for creating processes in Pantheon team packages using the **Unified Execute Model**. The framework automatically detects process types based on the files you include in the `artifact/` directory.

## Process Types Overview

The **combination of files in the `artifact/` directory** determines the process type:

- **CREATE**: `content.md` + `placement.jinja` + `naming.jinja` → Generates new artifacts
  - **Optional JSONL Logging**: Add `jsonl_placement.jinja` + `jsonl_naming.jinja` for structured logging
- **UPDATE**: `patch.md` + `locator.jsonnet` + `parser.jsonnet` + `target.jsonnet` → Modifies existing artifacts
- **GET**: `locator.jsonnet` + `parser.jsonnet` + `sections.jsonnet` → Reads existing artifacts

## Process Structure

Each process is a self-contained directory under `processes/<verb-noun>/` with the following components:

### Core Files (Every Process)
- **`routine.md`**: Step-by-step instructions for agents executing the process
- **`permissions.jsonnet`**: Access control rules defining which agents can execute the process
- **`schema.jsonnet`**: Data contract defining expected input structure (optional for GET processes using built-in flags)

### Artifact Files (Operation-Specific)
Files in the `artifact/` directory determine operation type and behavior:

**CREATE Process Files:**
- `content.md` - Jinja2 template for rendering artifact content
- `placement.jinja` - Directory template for artifact placement
- `naming.jinja` - Filename template for artifact naming

**UPDATE Process Files:**
- `patch.md` - Jinja2 template for section replacement content
- `target.jsonnet` - Defines which section to modify
- `locator.jsonnet` - Pattern for locating existing artifacts
- `parser.jsonnet` - Rules for normalizing fuzzy inputs to canonical IDs
- `sections.jsonnet` - Section markers for structured document parsing

**GET Process Files:**
- `locator.jsonnet` - Pattern for locating existing artifacts
- `parser.jsonnet` - Rules for normalizing fuzzy inputs
- `sections.jsonnet` - Section markers for parsing

## Development Tools

### Schema Design with Jsonnet
Schemas use Jsonnet for composition and dynamic adaptation based on team profiles:
- Support for `std.extVar('profile')` to access team profile settings
- Composable schemas using `import` statements
- Dynamic field requirements based on profile configuration

### Template Design with Jinja2
Templates use Jinja2 for rendering with built-in variables:
- `{{ pantheon_actor }}` - Actor executing the process
- `{{ pantheon_timestamp }}` - Current timestamp
- `{{ pantheon_datestamp }}` - Current date
- `{{ pantheon_artifact_id }}` - Sequential artifact ID (CREATE only)
- `{{ pantheon_profile }}` - Active team profile object

### Section Markers
Use HTML comments for structured document parsing:
- `<!-- START_SECTION:name -->` - Section start marker
- `<!-- END_SECTION:name -->` - Section end marker
- `<!-- PLACEHOLDER_SECTION: -->` - Empty section marker

## Testing Your Processes

1. **Validate Schema**: Use `pantheon get schema <process-name>` to check compilation
2. **Test Permissions**: Try execution with different agents
3. **Verify Templates**: Check artifact generation with sample data
4. **Test File Processes**: For UPDATE processes, ensure section replacement works correctly

## Best Practices

### 1. File Organization
- Keep process names descriptive using `verb-noun` convention
- Use consistent naming across related processes
- Share artifact files between UPDATE and GET processes

### 2. Apply DRY Principle with Semantic URIs
- **Reuse schemas**: Use `import "process-schema://base-process"` instead of duplicating
- **Share artifact configuration**: UPDATE processes reference GET counterparts via `import "artifact-locator://get-process"`
- **Leverage redirects**: Create specialized processes using `redirect.md` instead of duplicating routine logic

### 3. Schema Design
- Use Jsonnet's `std.extVar('profile')` for team-specific customization
- Provide clear descriptions for all fields
- Use appropriate validation (patterns, enums, etc.)
- Prefer schema composition via `import` statements over duplication

### 4. Template Design
- Include built-in variables for actor tracking and timestamps
- Use semantic section markers for structured documents
- Keep templates focused and maintainable
- Include section templates via artifact-template:// URIs to eliminate duplication

### 5. Process Composition
- **Create specialized processes** through redirection
- **Build process families** that share common artifact handling
- **Compose complex workflows** by chaining redirects with parameter forwarding
- **Maintain consistency** across related processes through shared references

## Next Steps

- **CREATE Processes**: Learn how to build processes that generate new artifacts
- **UPDATE Processes**: Learn how to build processes that modify existing artifacts
- **GET Processes**: Learn how to build processes that retrieve structured data
- **Schema Design**: Deep dive into Jsonnet patterns and profile integration
- **Template Design**: Master Jinja2 patterns and section management
- **Testing Processes**: Comprehensive testing strategies for process validation

This modular approach ensures consistent behavior while providing the flexibility to create sophisticated workflow automation for your AI team.
