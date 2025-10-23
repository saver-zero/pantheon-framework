---
doc_id: testing-processes
title: "Testing Processes"
description: "Comprehensive guide to testing Pantheon processes with validation strategies for schemas, templates, permissions, and end-to-end workflows."
keywords: [testing, validation, schema, template, permissions, workflow, integration]
relevance: "Use this document when validating process behavior, testing schema compilation, verifying template rendering, and ensuring permission enforcement."
---

# Testing Processes

Comprehensive testing ensures processes behave correctly across different actors, profiles, and data inputs. This guide covers validation strategies for all process components.

## Testing Philosophy

- **Schema Validation**: Ensure schemas compile and enforce correct data contracts
- **Template Validation**: Verify templates render correctly with various data inputs
- **Permission Validation**: Confirm access control works as designed
- **Integration Testing**: Test complete workflows with real data
- **Profile Testing**: Validate behavior across different profile configurations

## Schema Testing

### Validate Schema Compilation

```bash
# Check schema compiles without errors
pantheon get schema create-ticket --actor tech-lead

# Verify profile integration
# Change profile in team-profile.yaml, then test
pantheon get schema create-ticket --actor tech-lead
```

### Expected Results

**Valid Schema Output:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Brief ticket title"
    }
  },
  "required": ["title"]
}
```

**Schema Errors to Watch For:**
- Jsonnet syntax errors
- Undefined external variables
- Invalid JSON Schema structure
- Missing required properties
- Type mismatches

### Profile-Driven Schema Testing

Test schema changes across profiles:

```bash
# Standard profile (enforce_tdd: false)
pantheon get schema create-ticket --actor tech-lead
# Should NOT require test_file field

# Production profile (enforce_tdd: true)
# Change profile in team-profile.yaml
pantheon get schema create-ticket --actor tech-lead
# Should require test_file field
```

### Schema Validation Checklist

- [ ] Schema compiles without errors
- [ ] All required fields are present
- [ ] Profile-driven fields adapt correctly
- [ ] Field descriptions are clear
- [ ] Validation rules (min/max, patterns) work
- [ ] Semantic URIs resolve correctly

## Template Testing

### Manual Template Testing

```bash
# 1. Get tempfile path
pantheon get tempfile --process create-ticket --actor tech-lead
# Returns: /project/pantheon-artifacts/tmp/create-ticket_123.json

# 2. Write test data to tempfile
# Create JSON with test data

# 3. Execute process
pantheon execute create-ticket --from-file /tmp/create-ticket_123.json --actor tech-lead

# 4. Inspect generated artifact
cat pantheon-artifacts/tickets/T001_test-ticket.md
```

### Test Data Examples

**Minimal Data:**
```json
{
  "title": "Test Ticket",
  "business_context": "Test context",
  "technical_context": "Test technical details"
}
```

**Complete Data:**
```json
{
  "title": "Complex Test Ticket",
  "business_context": "Comprehensive business context",
  "technical_context": "Detailed technical background",
  "implementation_steps": [
    "Step 1: Design solution",
    "Step 2: Implement changes",
    "Step 3: Test thoroughly"
  ],
  "dependencies": "No external dependencies",
  "estimated_effort": "3 days"
}
```

**Edge Cases:**
```json
{
  "title": "Special/Characters-Test_Ticket",
  "business_context": "Context with\nmultiple\nlines",
  "technical_context": "Context with \"quotes\" and 'apostrophes'"
}
```

### Template Validation Checklist

- [ ] Required fields render correctly
- [ ] Optional fields conditionally render
- [ ] Section markers are properly placed
- [ ] Built-in variables (actor, timestamp) appear
- [ ] Profile-driven content adapts
- [ ] Special characters are escaped properly
- [ ] Whitespace and formatting are clean
- [ ] Template includes resolve correctly

## Permission Testing

### Process-Level Permission Testing

```bash
# Allowed actor
pantheon execute create-ticket --actor tech-lead --from-file test.json
# Expected: Success

# Denied actor
pantheon execute create-ticket --actor junior-dev --from-file test.json
# Expected: Permission denied error
```

### Section-Level Permission Testing

```bash
# Allowed for specific section
pantheon execute update-plan --actor backend-engineer \
  --id T001 --from-file plan.json
# Expected: Success

# Denied for specific section
pantheon execute update-plan --actor frontend-engineer \
  --id T001 --from-file plan.json
# Expected: Section permission denied error
```

### Permission Validation Checklist

- [ ] Allowed actors can execute process
- [ ] Denied actors are blocked
- [ ] Wildcard permissions work correctly
- [ ] Section-level permissions enforce correctly
- [ ] Explicit deny overrides allow
- [ ] Unknown actors are rejected
- [ ] Error messages are clear

## GET Process Testing

### Artifact Location Testing

```bash
# Test with various ID formats
pantheon execute get-ticket --actor developer --id T001
pantheon execute get-ticket --actor developer --id t001
pantheon execute get-ticket --actor developer --id 001
# All should find the same ticket
```

### Section Retrieval Testing

```bash
# Get all sections
pantheon execute get-ticket --actor developer --id T001

# Get specific sections
pantheon execute get-ticket --actor developer --id T001 --sections plan,status

# Get non-existent section
pantheon execute get-ticket --actor developer --id T001 --sections invalid_section
# Expected: Empty or error
```

### GET Validation Checklist

- [ ] Locator finds correct artifacts
- [ ] Parser normalizes IDs correctly
- [ ] Section extraction is accurate
- [ ] Placeholder sections are filtered
- [ ] Missing artifacts return clear errors
- [ ] Section discovery works (`get sections`)

## UPDATE Process Testing

### Section Update Testing

```bash
# Update specific section
pantheon execute update-plan --actor backend-engineer \
  --id T001 --from-file plan.json

# Verify update
pantheon execute get-ticket --actor developer \
  --id T001 --sections plan
```

### Insert Mode Testing

```bash
# Append to section
pantheon execute update-progress --actor developer \
  --id T001 --insert-mode append --from-file progress.json

# Prepend to section
pantheon execute update-changelog --actor tech-lead \
  --id T001 --insert-mode prepend --from-file changes.json

# Verify content order
pantheon execute get-ticket --actor developer \
  --id T001 --sections progress,changelog
```

### UPDATE Validation Checklist

- [ ] Section targeting works correctly
- [ ] Template rendering is accurate
- [ ] Append mode preserves existing content
- [ ] Prepend mode adds content at start
- [ ] Replace mode overwrites correctly
- [ ] Section permissions enforce
- [ ] Updates preserve artifact structure

## Integration Testing

### Complete Workflow Testing

**Ticket Lifecycle:**
```bash
# 1. Create ticket
pantheon execute create-ticket --actor tech-lead --from-file ticket.json

# 2. Get ticket context
pantheon execute get-ticket --actor backend-engineer --id T001 --sections context

# 3. Update plan
pantheon execute update-plan --actor backend-engineer --id T001 --from-file plan.json

# 4. Review code
pantheon execute update-code-review --actor code-reviewer --id T001 --from-file review.json

# 5. Verify final state
pantheon execute get-ticket --actor developer --id T001
```

### Multi-Actor Collaboration

```bash
# Tech lead creates ticket
pantheon execute create-ticket --actor tech-lead --from-file ticket.json

# Backend engineer plans
pantheon execute update-plan --actor backend-engineer --id T001 --from-file plan.json

# Code reviewer reviews
pantheon execute update-code-review --actor code-reviewer --id T001 --from-file review.json

# Each actor sees their permitted sections
```

### Integration Validation Checklist

- [ ] Complete workflows execute successfully
- [ ] Artifacts maintain consistency across updates
- [ ] Multi-actor collaboration works
- [ ] Section dependencies are preserved
- [ ] Error recovery is graceful
- [ ] Audit trails are complete

## Profile Testing

### Profile Variation Testing

**Standard Profile:**
```yaml
# team-profile.yaml
active_profile: standard
profiles:
  standard:
    verbosity: standard
    enforce_tdd: true
```

```bash
# Test with standard profile
pantheon get schema create-ticket --actor tech-lead
# Should require test_file if enforce_tdd: true
```

**Production Profile:**
```yaml
active_profile: production
profiles:
  production:
    verbosity: detailed
    enforce_tdd: true
    test_type: unit_and_integration_test
```

```bash
# Test with production profile
pantheon get schema create-ticket --actor tech-lead
# Should require comprehensive fields
```

### Profile Validation Checklist

- [ ] Schema adapts to profile settings
- [ ] Templates render profile-specific content
- [ ] Required fields change based on profile
- [ ] Descriptions adapt to verbosity levels
- [ ] Process behavior matches profile intent

## Error Testing

### Invalid Input Testing

```bash
# Missing required field
echo '{"title": "Test"}' > test.json
pantheon execute create-ticket --actor tech-lead --from-file test.json
# Expected: Validation error for missing fields

# Invalid data type
echo '{"title": 123}' > test.json
pantheon execute create-ticket --actor tech-lead --from-file test.json
# Expected: Type validation error

# Invalid ID format
pantheon execute get-ticket --actor developer --id invalid
# Expected: ID normalization or not found error
```

### Error Validation Checklist

- [ ] Missing required fields are caught
- [ ] Invalid data types are rejected
- [ ] Malformed JSON is detected
- [ ] Invalid IDs return clear errors
- [ ] Permission errors are informative
- [ ] Schema violations are reported clearly

## Regression Testing

### Version Control for Tests

```bash
# 1. Create test data fixtures
mkdir tests/fixtures/
echo '{"title": "Test", ...}' > tests/fixtures/valid-ticket.json

# 2. Create test scripts
cat > tests/test-create-ticket.sh << 'EOF'
#!/bin/bash
pantheon execute create-ticket \
  --actor tech-lead \
  --from-file tests/fixtures/valid-ticket.json
EOF

# 3. Run tests after process changes
bash tests/test-create-ticket.sh
```

### Regression Validation Checklist

- [ ] Existing test cases still pass
- [ ] New features don't break old workflows
- [ ] Profile changes don't break processes
- [ ] Schema updates remain backward compatible
- [ ] Template changes preserve output structure

## Best Practices

1. **Test Early and Often**: Validate schemas and templates during development
2. **Use Representative Data**: Test with realistic inputs, not just minimal examples
3. **Test Edge Cases**: Special characters, long strings, empty values
4. **Profile Testing**: Validate across all profiles your team uses
5. **Permission Testing**: Verify access control with all relevant actors
6. **Integration Testing**: Test complete workflows, not just individual operations
7. **Document Tests**: Keep test data and scripts version-controlled
8. **Automate**: Create test scripts for regression testing

## Troubleshooting

### Schema Compilation Errors

```bash
# Check Jsonnet syntax
pantheon get schema create-ticket --actor tech-lead
# Look for syntax errors, undefined variables
```

### Template Rendering Issues

```bash
# Test with minimal data
pantheon execute create-ticket --actor tech-lead --from-file minimal.json

# Add fields incrementally to isolate issue
```

### Permission Denials

```bash
# Check agent exists
ls pantheon-teams/<team>/agents/

# Check permissions file
cat pantheon-teams/<team>/processes/<process>/permissions.jsonnet
```

## Next Steps

- **Schema Design**: Master Jsonnet patterns and validation
- **Template Design**: Create robust, maintainable templates
- **Permission Design**: Implement effective access control
- **Integration Patterns**: Build complete workflows
