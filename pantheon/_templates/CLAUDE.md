# Pantheon Framework Templates

## Template System Overview

This directory contains the bundled starter templates that ship with the Pantheon Framework, demonstrating **Glass Box** implementation patterns and providing working examples of the **Unified Execute Model**.

### Template Structure

#### Pantheon Skeleton Team (`pantheon-teams/pantheon-skeleton/`)
**Reference implementation** showcasing all three operation types and best practices:

```
pantheon-skeleton/
├── team-profile.yaml              # Central configuration panel
├── team-profile-schema.json       # Profile validation schema
├── agents/                        # Agent persona definitions
│   └── ticket-handler.md          # Example agent with clear responsibilities
└── processes/                     # Demonstrates all operation types
    ├── create-ticket/             # CREATE operation example
    │   ├── routine.md             # Step-by-step workflow
    │   ├── schema.jsonnet         # Input data contract
    │   ├── permissions.jsonnet    # Actor access control
    │   └── artifact/              # CREATE-specific templates
    │       ├── content.md         # Document template
    │       ├── naming.jinja       # Filename generation
    │       └── placement.jinja    # Directory placement
    ├── get-ticket/                # RETRIEVE operation example
    │   ├── routine.md             # Retrieval workflow
    │   ├── permissions.jsonnet    # Access permissions
    │   └── artifact/              # RETRIEVE-specific configs
    │       ├── locator.jsonnet    # Finding pattern
    │       ├── parser.jsonnet     # ID normalization
    │       └── sections.jsonnet   # Section markers
    ├── update-plan/               # UPDATE operation example
    │   ├── routine.md             # Modification workflow
    │   ├── schema.jsonnet         # Update parameters
    │   ├── permissions.jsonnet    # Modification permissions
    │   └── artifact/              # UPDATE-specific templates
    │       ├── patch.md           # Section replacement
    │       ├── target.jsonnet     # Section targeting
    │       ├── locator.jsonnet    # Finding pattern
    │       └── parser.jsonnet     # ID normalization
    └── get-plan/                  # REDIRECT example
        ├── routine.md             # Redirect workflow
        └── redirect.md            # Target redirection
```

## Implementation Patterns

### Unified Execute Model Examples

#### CREATE Process Pattern (`create-ticket/`)
**File Combination**: `content.md` + `placement.jinja` + `naming.jinja`
- **Purpose**: Generate new artifacts with structured content
- **Template variables**: `pantheon_actor`, `pantheon_timestamp`, `pantheon_datestamp`, `pantheon_artifact_id`
- **Workflow**: Schema validation → Template rendering → File placement

#### RETRIEVE Process Pattern (`get-ticket/`)
**File Combination**: `locator.jsonnet` + `parser.jsonnet` + `sections.jsonnet`
- **Purpose**: Find and extract content from existing artifacts
- **Locator logic**: Pattern matching for artifact discovery
- **Parser logic**: ID normalization for consistent addressing
- **Sections logic**: HTML comment markers for structured parsing

#### UPDATE Process Pattern (`update-plan/`)
**File Combination**: `patch.md` + `target.jsonnet` + RETRIEVE files
- **Purpose**: Modify sections within existing artifacts
- **Target logic**: Precise section identification for replacement
- **Patch logic**: New content with template variable support
- **Atomic operations**: Safe modification through temporary files

### Schema Composition Patterns

#### Profile Context Injection
```jsonnet
// Example from schema.jsonnet files
{
  local profile = std.extVar('profile'),
  // Schema adapts based on active team profile
  verbosity: if profile.verbosity then ["verbose"] else [],
  // Conditional fields based on profile settings
}
```

#### Semantic URI References
```jsonnet
// Cross-process component reuse
{
  "$ref": "#/common/validation-rules",  // Internal reference
  "external_ref": "process://other-process/schema#section"  // Cross-process reference
}
```

### Permission Model Examples

#### Actor-Based Access Control
```jsonnet
// From permissions.jsonnet files
{
  allow: ["ticket-handler", "tech-lead"],    // Explicit allow list
  deny: ["guest-user"],                      // Explicit deny list
  default: "deny"                            // Secure by default
}
```

### Template Rendering Examples

#### Jinja2 Template Variables
```markdown
<!-- From content.md templates -->
# Ticket: {{ pantheon_artifact_id }}

Created by: {{ pantheon_actor }}
Date: {{ pantheon_datestamp }}
Timestamp: {{ pantheon_timestamp }}

Profile Context: {{ pantheon_profile.team_name }}
```

#### Section Markers for Structured Documents
```html
<!-- From artifact templates -->
<!-- SECTION: requirements -->
Requirements content here
<!-- /SECTION: requirements -->

<!-- SECTION: implementation -->
Implementation details here  
<!-- /SECTION: implementation -->
```

## Team Profile Configuration

### Central Configuration Panel (`team-profile.yaml`)
```yaml
# Example configuration showing profile structure
team_name: "pantheon-skeleton"
profiles:
  development:
    verbosity: true
    enforce_tdd: false
    test_coverage: 80
  production:
    verbosity: false
    enforce_tdd: true
    test_coverage: 95
```

### Profile Schema Validation (`team-profile-schema.json`)
- **JSON Schema**: Validates profile structure and required fields
- **Type enforcement**: Ensures profile consistency across environments
- **Default values**: Provides fallbacks for optional configuration

## Template Usage Guidelines

### When Creating New Teams

#### 1. Copy Template Structure
```bash
cp -r pantheon/_templates/pantheon-teams/pantheon-skeleton/ pantheon-teams/my-team/
```

#### 2. Customize Team Profile
- Update `team-profile.yaml` with team-specific configuration
- Modify `team-profile-schema.json` if adding custom profile fields
- Set appropriate default profile for team context

#### 3. Define Agents
- Create agent persona files in `agents/` directory
- Use clear, specific role definitions
- Reference agents in process permissions

#### 4. Implement Processes
- Follow `<verb-noun>` naming convention for process directories
- Include all required files: `routine.md`, `permissions.jsonnet`
- Add `schema.jsonnet` for parameterized processes
- Create `artifact/` directory for operation-specific templates

### Template Modification Best Practices

#### Routine Structure
```markdown
# Process: verb-noun

## node: step-1
Clear, actionable step description

## branch: conditional-logic
- **condition**: Specific condition to check
- **true**: Path for true condition
- **false**: Path for false condition

## finish: completion
Final step with clear success criteria
```

#### Schema Design Principles
- **Profile context**: Always include `std.extVar('profile')` access
- **Validation rules**: Define clear input constraints
- **Semantic references**: Use `$ref` for reusable components
- **Documentation**: Include field descriptions and examples

#### Permission Security
- **Principle of least privilege**: Grant minimum necessary access
- **Explicit permissions**: Always define allow/deny lists
- **Agent validation**: Ensure referenced agents exist
- **Regular review**: Update permissions as team structure changes

## Integration with Framework

### Template Discovery
- **Bundled with framework**: Templates ship as part of package installation
- **Runtime copying**: Framework copies templates to project on initialization
- **Version tracking**: Templates versioned with framework releases

### Framework Command Integration
```bash
# Framework uses templates for project initialization
pantheon init --team-template pantheon-skeleton

# Templates work with all framework commands
pantheon execute create-ticket --actor ticket-handler
pantheon get process update-plan --actor tech-lead
```

## Extension Points

### Custom Template Creation
- **Follow established patterns**: Use skeleton as reference implementation
- **Maintain file structure**: Preserve required filenames and directories
- **Test thoroughly**: Validate all operation types work correctly
- **Document clearly**: Provide usage examples and customization guides

### Template Validation
- **Schema compliance**: Ensure all schemas validate correctly
- **Permission testing**: Verify access control works as expected
- **Template rendering**: Test all Jinja2 templates render without errors
- **Process execution**: Validate complete workflows through CLI testing