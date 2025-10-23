---
doc_id: team-packages-profiles
title: "Team Profiles"
description: "Comprehensive guide to team profile configuration, schema-driven behavior control, and dynamic process adaptation through profile settings."
keywords: [team-packages, profiles, configuration, schema, jsonnet, dynamic-behavior, team-profile-yaml]
relevance: "Use this document to understand how team profiles control process behavior through schema-level and template-level mechanisms, enabling context-aware process execution."
---

# Team Profiles

While the Framework Core is the engine and the Team Package is the brain, the **Team Profile** acts as the team's central control panel. It's a single, human-readable YAML file (`team-profile.yaml`) stored at the root of the Team Package that defines and controls the team's high-level operational behavior.

## Purpose and Function

The Team Profile serves two primary purposes:

1.  **Defines Available Profiles:** It contains the definitions for pre-packaged "profiles" (e.g., `prototype`, `production`). Each profile is a named collection of settings that configures the team for a specific context, such as rapid development or production-grade stability.
2.  **Sets the Active Profile:** It specifies which profile is currently active for the team. The framework reads this active profile at runtime to dynamically adjust its behavior.

## How Team Profiles Actually Control Behavior

Team profile settings control behavior through **two distinct mechanisms** that work at different stages of process execution:

### 1. Schema-Level Control (Smart Schema, Dumb Template)
The active profile's configuration is injected as **external variables** into Jsonnet schema compilation. This allows schemas to dynamically show/hide fields, change validation rules, and modify field descriptions based on profile settings.

**How it works:**
- Each property in the active profile becomes a Jsonnet external variable
- Schemas use `std.extVar('property_name')` to access profile values
- This affects what fields agents see and how they're prompted to fill them

**Example Schema (`schema.jsonnet`):**
```jsonnet
local verbosity = std.extVar('verbosity');        // From active profile
local enforce_tdd = std.extVar('enforce_tdd');    // From active profile

local baseSchema = {
  properties: {
    ticket_id: { type: 'string' },
    description: { type: 'string' }
  },
  required: ['ticket_id', 'description']
};

// Conditionally add TDD requirements based on profile
local tddFields = if enforce_tdd then {
  properties+: {
    test_file: {
      type: 'string',
      description: 'Path to the failing test file (required for TDD)'
    }
  },
  required+: ['test_file']
} else {};

// Adjust description detail based on verbosity
local descriptionDetail = {
  properties+: {
    description+: {
      description: if verbosity == 'detailed' then
        'Provide comprehensive description including edge cases and implementation details'
      else
        'Brief description of the change'
    }
  }
};

baseSchema + tddFields + descriptionDetail
```

### 2. Template-Level Control (Data-Driven Rendering)
Templates should be "dumb" and primarily render based on what data was actually provided by the agent, rather than checking profile settings directly.

**How it works:**
- Profile controls schema → schema controls what agent provides → template renders what's provided
- Templates use `{% if variable_name %}` to check for data presence
- Profile is only accessed directly in exceptional cases where pure rendering changes are needed

**Example Template (`content.md`):**
```jinja2
# Implementation Plan: {{ ticket_id }}

## Overview
{{ description }}

{% if implementation_steps %}
## Implementation Steps
{% for step in implementation_steps %}
### {{ step.title }}
{% if step.rationale %}
{{ step.rationale }}

**Implementation approach:** {{ step.details }}
{% endif %}
{% endfor %}
{% endif %}

{% if error_handling_strategy %}
## Error Handling Strategy
{{ error_handling_strategy }}
{% endif %}

{% if edge_cases %}
## Edge Cases Considered
{% for case in edge_cases %}
- **{{ case.scenario }}:** {{ case.mitigation }}
{% endfor %}
{% endif %}

{% if test_file %}
## Test-First Development

**Failing Test:**
```python
# {{ test_file }}
{{ test_code }}
```

This test must be written and failing before implementing the feature.
{% endif %}
```

**Note:** The template doesn't check `pantheon_profile.verbosity` or `pantheon_profile.enforce_tdd`. Instead, it renders based on whether the schema (driven by profile) caused the agent to provide `step.rationale`, `error_handling_strategy`, `edge_cases`, or `test_file` data.

## The Clean Control Flow

```
User Input → Schema (with profile) → Agent Response → Template (data-driven) → Final Artifact
            ↑                                         ↑
            Smart Schema                              Dumb Template
            (controls what agent sees)                (renders what's provided)
```

This creates the clean architectural pattern: **Smart Schema, Dumb Template**
- The schema becomes "smart" by adapting to profile settings, controlling what the agent is prompted for
- The template remains "dumb" and simply renders whatever data was provided, without needing to check profiles

**Benefits of this approach:**
- **Separation of concerns:** Profile logic is centralized in schemas
- **Template simplicity:** Templates don't need to understand profile semantics
- **Easier testing:** Template behavior is purely data-driven
- **Better maintainability:** Profile changes only require schema updates

**When to use direct profile access in templates (rare exceptions):**
- Pure rendering format changes (e.g., markdown vs HTML output)
- Content styling that doesn't affect data structure
- Execution preferences that don't affect data structure (e.g., lint tools, build commands)
- Cases where schema cannot capture the rendering difference

## Built-in Template Variables

Templates automatically have access to several built-in framework variables, including the active profile configuration:

### Available Built-in Variables

- **`pantheon_actor`** - The actor executing the process (from `--actor` flag)
- **`pantheon_active_profile`** - The active profile configuration object (for templates)
- **`pantheon_full_profile`** - The complete profile structure (for schema compilation)
- **`pantheon_timestamp`** - Current timestamp in ISO format
- **`pantheon_datestamp`** - Current date in YYYY-MM-DD format
- **`pantheon_artifact_id`** - Sequential artifact ID (CREATE operations only)
- **`pantheon_process`** - Name of the current process

### Using `pantheon_active_profile` in Templates

The `pantheon_active_profile` variable contains only the active profile configuration, allowing direct access to any profile property:

```jinja2
{% if pantheon_active_profile.lint_tool %}
- **Run lint**: After implementation, run `{{ pantheon_active_profile.lint_tool }}` to check for lint errors and formatting issues.
{% endif %}

<!-- Format-specific rendering -->
{% if pantheon_active_profile.output_format == "html" %}
<div class="implementation-steps">
{% else %}
## Implementation Steps
{% endif %}
```

### Profile Variable Types

The framework provides two profile variables with different purposes:

- **`pantheon_active_profile`**: Contains only the active profile's configuration (e.g., `{verbosity: "detailed", enforce_tdd: false}`)
  - **Use in templates** for simple property access
  - **Clean and direct**: `{{ pantheon_active_profile.enforce_tdd }}`

- **`pantheon_full_profile`**: Contains the complete profile structure with `active_profile` and `profiles` sections
  - **Used internally** for schema compilation with `std.extVar()`
  - **Not typically needed** in templates unless accessing metadata

### Best Practices for Direct Profile Access

**Use direct profile access for:**
- **Execution commands**: Tools, scripts, or commands that vary by environment
- **Rendering preferences**: Output format, styling, or presentation choices
- **Simple hardcoded configurations**: Environment-specific settings that don't affect data structure

**Example: Environment-specific lint tools**
```yaml
# team-profile.yaml
profiles:
  development:
    lint_tool: "ruff check --fix && ruff format"
  production:
    lint_tool: "ruff check --fix && ruff format && mypy --strict"
```

```jinja2
<!-- template usage -->
- **Run lint**: After implementation, run `{{ pantheon_active_profile.lint_tool }}` to check for lint errors.
```

**Avoid direct profile access for:**
- **Data requirements**: Use schema-driven approach instead (e.g., verbosity levels should control what fields appear in schemas)
- **Complex business logic**: Keep templates simple and data-focused
- **Validation rules**: These belong in schemas, not templates
- **Content that affects data structure**: Use profile-driven schemas to control what agents provide

## Understanding Profile Properties

Profile properties are **not arbitrary** - they must be designed to work with the framework's two control mechanisms. When designing profile properties, consider:

### Schema-First Properties (Primary Use)
Most profile properties should control schema behavior, letting templates be data-driven:
- **Boolean flags** (`enforce_tdd: true/false`) - Enable/disable required fields
- **Enum values** (`verbosity: brief|standard|detailed`) - Change field descriptions and add/remove optional fields
- **Numeric thresholds** (`max_complexity: 10`) - Set validation limits
- **Lists of options** (`allowed_frameworks: [react, vue, angular]`) - Define enum constraints

### Template-Only Properties (Rare Exceptions)
These properties only affect template rendering and should be used sparingly:
- **Pure format preferences** (`output_format: markdown|html`) - Change rendering format without affecting data structure
- **Styling options** (`code_theme: light|dark`) - Visual presentation that schemas can't control

### Anti-Patterns to Avoid
- **Complex nested objects** - Hard to use in Jsonnet external variables
- **Dynamic property names** - Cannot be referenced reliably in schemas
- **Runtime-dependent values** - Profiles should be static configuration

## Data-Driven YAML Generation

For processes that generate `team-profile.yaml` files (like a `create-team-config` process), profile properties are documented using a data-driven approach. The input data for such a process includes a special `property_definitions` section that describes the schema for each profile property.

The `to_yaml` Jinja2 filter intelligently detects this `property_definitions` key in the input data. It uses this information to automatically generate a comprehensive documentation header, then excludes the `property_definitions` key from the final YAML output.

```jinja2
{{ input_data | to_yaml }}
```

This creates a clean, self-documenting `team-profile.yaml` file where the documentation is derived directly from the design input provided to the process.

## Real-World Profile Properties

Here are proven profile property patterns that work well with the framework's control mechanisms:

### Development Workflow Controls
- **`verbosity: brief|standard|detailed`** - Controls schema field descriptions and template content depth
- **`enforce_tdd: true|false`** - Adds/removes required test fields in schemas and test sections in templates
- **`review_level: peer|senior|architect`** - Changes validation requirements and template review sections

### Content Generation Controls
- **`include_examples: true|false`** - Shows/hides example sections in generated artifacts
- **`format: markdown|restructured_text|html`** - Controls template output format
- **`documentation_style: minimal|standard|comprehensive`** - Affects schema requirements and template sections

### Quality and Compliance
- **`security_level: basic|enhanced|strict`** - Adds security-related required fields and template sections
- **`compliance_standards: [gdpr, hipaa, sox]`** - Enables compliance-specific validation and content
- **`code_standards: relaxed|standard|strict`** - Controls complexity thresholds and style requirements

### Process Behavior
- **`approval_required: true|false`** - Adds approval workflow fields to schemas
- **`auto_assign: true|false`** - Controls automatic assignment logic in templates
- **`notification_level: none|critical|all`** - Affects notification-related template sections

## Profile Selection During Initialization

When running `pantheon init`, the framework provides an interactive profile selection step that helps users choose the most appropriate profile for their project needs. This selection occurs immediately after team selection and before project configuration is created.

### Profile Selection User Experience

**Multiple Profiles Available:**

When a team defines multiple profiles, users see a numbered list with profile names and descriptions:

```
Available profiles:
  1. prototype
     Optimized for rapid prototyping and experimentation with minimal process overhead.
  2. standard
     Balanced development profile suitable for most development work with reasonable quality gates.
  3. production
     Maximum rigor profile ensuring comprehensive quality assurance and documentation for production systems.
Select a profile (1, 2, 3) [1]:
```

Users can:
- Enter a number to select a specific profile
- Press Enter to accept the default (first profile, shown in brackets)
- The default provides a smart choice for users in a hurry

**Single Profile Available:**

When a team has exactly one profile, the framework auto-selects it and displays a confirmation message:

```
Using profile: standard - Balanced development profile suitable for most development work with reasonable quality gates.
```

No user interaction is required - the initialization proceeds automatically with the only available profile.

**No Profiles Defined:**

Teams without a `profiles` section in `team-profile.yaml` are fully supported. The initialization completes without profile selection, and no `active_profile` line is added to `.pantheon_project`. This maintains backward compatibility with teams that don't use the profile system.

### Profile Information Display

The profile selection interface follows the **progressive disclosure** principle:

- **Primary information**: Profile name and `profile_description` are always shown
- **Scannable format**: Numbered list with clear visual hierarchy
- **No technical jargon**: Descriptions use accessible language for all skill levels
- **Complete configuration hidden**: Full profile properties aren't displayed to avoid overwhelming users

This approach ensures users can make informed decisions without analysis paralysis, supporting both quick defaults and thoughtful selection.

### Configuration Impact

The selected profile is written to `.pantheon_project` as the `active_profile`:

```yaml
# Pantheon project configuration
active_team: pantheon-dev
active_profile: standard
artifacts_root: pantheon-artifacts
```

The `active_profile` setting:
- Determines which profile context is injected into process schemas via `std.extVar('profile')`
- Controls process behavior through profile-specific properties
- Can be changed later by editing `.pantheon_project` (though `pantheon init` with team switching is recommended)

### Error Handling

Profile selection handles various edge cases gracefully:

- **Missing team-profile.yaml**: Returns `None`, skips profile selection
- **Malformed YAML**: Logs warning, skips profile selection
- **Missing profiles section**: Skips profile selection, no error shown
- **User cancellation**: Raises `BadInputError` with clear message

All errors maintain the framework's robustness principle - the init workflow degrades gracefully rather than failing hard.

## Configuration and Discovery

To empower the user as the architect, the `Team Package` is fully self-contained with a simple, transparent configuration approach.

- **`team-profile.yaml`**: The human-readable file where the user defines and selects profiles. This file is copied from bundled templates during `pantheon init`.

**Schema Validation**: When teams need processes to create or modify team profiles (such as `create-team-config`), those processes can include `schema.jsonnet` files that define the validation rules for team profile creation. This provides validation where it's needed while keeping the core configuration system simple and transparent.

### Team Description Display During Initialization

The `team_description` field in `team-profile.yaml` serves a dual purpose: it configures the team's identity and provides user-facing information during project initialization. When running `pantheon init`, the framework loads and displays the `team_description` from each bundled team's profile to help users make informed decisions about which team package best fits their project needs.

**Display Format:**

When multiple teams are available:
```
Available starter teams:
  1. pantheon-dev - Provide a transparent, auditable, and continuously improving AI development workflow...
  2. pantheon-ops - Specialized team for infrastructure and deployment automation...
  3. mobile-team - A specialized team focused on mobile application development with CI/CD integration.
```

When a single team is available:
```
Using available team: pantheon-dev - Provide a transparent, auditable, and continuously improving AI development workflow...
```

**Error Handling:**

The initialization process gracefully handles missing or malformed team descriptions:
- If `team-profile.yaml` is missing, the team is still listed with "No description available"
- If the YAML is malformed or `team_description` field is absent, "No description available" is shown
- All errors are logged as warnings for debugging while keeping the user experience clean

This approach ensures that the init workflow never fails due to description loading issues, maintaining the framework's robustness while providing helpful context when available.

## Example Configuration

### team-profile.yaml

When generated using the data-driven `to_yaml` filter, the team profile includes a comprehensive documentation header derived from the `property_definitions` in the process input:

```yaml
# Profile Properties Documentation:
#
# verbosity:
#   Description: Level of detail in generated artifacts
#   Type: string
#   Options: brief, standard, detailed
#
# enforce_tdd:
#   Description: Whether to enforce TDD practices
#   Type: boolean (true/false)
#
# test_type:
#   Description: Types of tests to write
#   Type: string
#   Options: unit_test_only, integration_test_only, unit_and_integration_test

team_name: Mobile Development Team
team_description: A specialized team focused on mobile application development with CI/CD integration.
active_profile: development
profiles:
  development:
    verbosity: detailed
    enforce_tdd: false
    test_type: unit_test_only
  production:
    verbosity: brief
    enforce_tdd: true
    test_type: unit_and_integration_test
```

**Key Features:**
- **Documentation Header**: Complete field descriptions, types, and available options documented once at the top.
- **No Repetition**: The generated YAML is clean and readable.
- **Data-Driven**: The documentation is generated from the input data provided to the creation process, not a static schema.

## Context-Aware Schema Composition

The most powerful feature of Team Profiles is their ability to dynamically alter process schemas. Instead of requiring separate schema files for each profile, the framework injects the active profile's configuration object directly into the Jsonnet evaluation context.

### The Process

When `pantheon get schema <process-name>` is called:

1.  **Identify Active Profile:** The engine reads `team-profile.yaml` to identify the `active_profile` and extracts the entire configuration object for that profile.
2.  **Invoke Jsonnet with Context:** The engine invokes the Jsonnet compiler on the process's `schema.jsonnet` file, passing the active profile's configuration object as an **external variable** named `profile`.
3.  **Evaluate and Return Schema:** The `schema.jsonnet` file uses the injected `profile` variable to conditionally construct the schema.

---

**Cross-References:**
- [Agents & Processes](./agents-processes.md) - Understanding how agents use profiles
- [Jsonnet Schemas Guide](../templating-system/jsonnet-schemas-guide.md) - Schema composition mechanics
