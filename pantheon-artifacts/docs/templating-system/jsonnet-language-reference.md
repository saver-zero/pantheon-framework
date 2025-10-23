---
doc_id: jsonnet-language-reference
title: "Jsonnet Language Reference"
description: "Quick reference for Jsonnet language features including variables, functions, conditionals, object composition, and array operations used in Pantheon schemas."
keywords: [jsonnet, language-reference, variables, functions, conditionals, object-composition, arrays, std-library]
relevance: "Use this document as a quick reference for Jsonnet language syntax and features when writing dynamic schemas for Pantheon processes."
---

# Jsonnet Language Reference

This document provides a quick reference for Jsonnet language features used in Pantheon schema development.

## External Variables

External variables allow schemas to access team profile settings and other runtime context.

### Accessing External Variables

```jsonnet
local profile = std.extVar('profile');
local custom_setting = std.extVar('custom_setting');
```

### Common External Variables in Pantheon

- `profile`: Complete team profile object
- `enforce_tdd`: Boolean flag for test-driven development
- `verbosity`: Verbosity level (e.g., 'detailed', 'minimal')

### Using Profile Properties

```jsonnet
local profile = std.extVar('profile');

{
  properties: {
    field: {
      type: 'string',
      description: if profile.verbosity == 'detailed' then
        'Comprehensive description'
      else
        'Brief description'
    }
  }
}
```

## Variables and Functions

### Local Variables

```jsonnet
local baseProperties = {
  title: { type: 'string' },
  description: { type: 'string' }
};

local requiredFields = ['title', 'description'];

{
  type: 'object',
  properties: baseProperties,
  required: requiredFields
}
```

### Functions

```jsonnet
local createField(name, description) = {
  type: 'string',
  description: description
};

{
  properties: {
    title: createField('title', 'Document title'),
    summary: createField('summary', 'Brief summary')
  }
}
```

**Function with Default Parameters:**
```jsonnet
local createField(type='string', required=false) = {
  type: type,
  description: if required then 'Required field' else 'Optional field'
};
```

## Conditionals

### If-Then-Else Expression

```jsonnet
local includeDetails = std.extVar('verbosity') == 'detailed';

{
  properties: {
    title: { type: 'string' }
  } + if includeDetails then {
    details: { type: 'string' }
  } else {}
}
```

### Ternary Operator

```jsonnet
local profile = std.extVar('profile');

{
  description: if profile.verbosity == 'detailed' then
    'Comprehensive description'
  else
    'Brief description'
}
```

### Multiple Conditions

```jsonnet
local verbosity = std.extVar('verbosity');

{
  description:
    if verbosity == 'detailed' then 'Very detailed description'
    else if verbosity == 'normal' then 'Normal description'
    else 'Brief description'
}
```

## Object Composition

### Object Merge

```jsonnet
local base = { a: 1, b: 2 };
local extension = { c: 3 };
local result = base + extension;
// Result: { a: 1, b: 2, c: 3 }
```

### Object Override

```jsonnet
local base = { a: 1, b: 2 };
local override = { b: 20 };
local result = base + override;
// Result: { a: 1, b: 20 }
```

### Deep Merge with +: Operator

```jsonnet
local base = {
  properties: {
    field1: { type: 'string' }
  }
};

base + {
  properties+: {  // Note the + after properties
    field2: { type: 'number' }
  }
}
// Result: properties contains both field1 and field2
```

**Without +: (Override):**
```jsonnet
base + {
  properties: {  // No + means replace
    field2: { type: 'number' }
  }
}
// Result: properties contains only field2
```

### Conditional Object Properties

```jsonnet
local profile = std.extVar('profile');

{
  type: 'object',
  properties: {
    base_field: { type: 'string' }
  } + if profile.detailed then {
    extra_field: { type: 'string' }
  } else {}
}
```

## Array Operations

### Array Concatenation

```jsonnet
local base = ['a', 'b'];
local extended = base + ['c', 'd'];
// Result: ['a', 'b', 'c', 'd']
```

### Conditional Array Extension

```jsonnet
local baseRequired = ['title', 'description'];
local enforce_tdd = std.extVar('enforce_tdd');
local tddRequired = if enforce_tdd then ['test_file'] else [];

{
  required: baseRequired + tddRequired
}
```

### Array with +: Operator

```jsonnet
local base = {
  required: ['field1']
};

base + {
  required+: ['field2', 'field3']
}
// Result: required contains ['field1', 'field2', 'field3']
```

## Standard Library Functions

### std.extVar()

Access external variables:
```jsonnet
local profile = std.extVar('profile');
```

### std.foldl()

Fold (reduce) an array from left to right:
```jsonnet
local sections = [
  { name: 'plan', enabled: true, props: { a: 1 } },
  { name: 'status', enabled: false, props: { b: 2 } }
];

local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.props else acc,
  sections,
  {}
);
// Result: { a: 1 }
```

**Signature:**
```jsonnet
std.foldl(function(accumulator, element), array, initial_value)
```

### std.objectHas()

Check if object has a field:
```jsonnet
local obj = { field1: 'value' };
local hasField = std.objectHas(obj, 'field1');
// Result: true
```

### std.length()

Get length of array or string:
```jsonnet
local arr = [1, 2, 3];
local len = std.length(arr);
// Result: 3
```

### std.map()

Transform array elements:
```jsonnet
local numbers = [1, 2, 3];
local doubled = std.map(function(x) x * 2, numbers);
// Result: [2, 4, 6]
```

### std.filter()

Filter array elements:
```jsonnet
local sections = [
  { name: 'plan', enabled: true },
  { name: 'status', enabled: false }
];
local enabled = std.filter(function(s) s.enabled, sections);
// Result: [{ name: 'plan', enabled: true }]
```

## Imports

### Import from Relative Path

```jsonnet
local baseSchema = import 'sections/base.schema.jsonnet';
```

### Import from Semantic URI

```jsonnet
local createSchema = import "process-schema://create-ticket";
```

### Import with Composition

```jsonnet
local baseSchema = import "process-schema://create-ticket";

baseSchema + {
  properties+: {
    extra_field: { type: 'string' }
  }
}
```

## Common Patterns in Pantheon

### Profile-Based Conditional Fields

```jsonnet
local profile = std.extVar('profile');

local baseProperties = {
  title: { type: 'string' }
};

local detailedProperties = if profile.verbosity == 'detailed' then {
  technical_notes: { type: 'string' }
} else {};

{
  type: 'object',
  properties: baseProperties + detailedProperties
}
```

### Dynamic Required Fields

```jsonnet
local enforce_tdd = std.extVar('enforce_tdd');

local baseRequired = ['title', 'description'];
local tddRequired = if enforce_tdd then ['test_file', 'test_code'] else [];

{
  type: 'object',
  properties: {
    title: { type: 'string' },
    description: { type: 'string' },
    test_file: { type: 'string' },
    test_code: { type: 'string' }
  },
  required: baseRequired + tddRequired
}
```

### Section Composition with Fold

```jsonnet
local sections = [
  { name: "plan", enabled: true, schema: import "sections/plan.jsonnet" },
  { name: "status", enabled: false, schema: import "sections/status.jsonnet" }
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

### Schema Extension Pattern

```jsonnet
local baseSchema = import "process-schema://base-process";
local profile = std.extVar('profile');

local profileExtensions = if profile.extended_mode then {
  properties+: {
    extended_field: { type: 'string' }
  },
  required+: ['extended_field']
} else {};

baseSchema + profileExtensions
```

## Best Practices

### 1. Use Descriptive Variable Names

**Good:**
```jsonnet
local baseProperties = { ... };
local detailedProperties = { ... };
```

**Bad:**
```jsonnet
local bp = { ... };
local dp = { ... };
```

### 2. Extract Complex Logic into Functions

**Good:**
```jsonnet
local createFieldWithValidation(name, minLen, maxLen) = {
  type: 'string',
  minLength: minLen,
  maxLength: maxLen,
  description: 'Field: ' + name
};

{
  properties: {
    title: createFieldWithValidation('title', 10, 80),
    summary: createFieldWithValidation('summary', 20, 200)
  }
}
```

### 3. Use Local Variables for Readability

**Good:**
```jsonnet
local profile = std.extVar('profile');
local isDetailed = profile.verbosity == 'detailed';

{
  description: if isDetailed then 'Long description' else 'Short'
}
```

**Bad:**
```jsonnet
{
  description: if std.extVar('profile').verbosity == 'detailed' then 'Long description' else 'Short'
}
```

### 4. Keep Conditional Logic Clear

**Good:**
```jsonnet
local includeField = profile.feature_enabled && !profile.minimal_mode;

{
  properties: {} + if includeField then {
    optional_field: { type: 'string' }
  } else {}
}
```

## Related Documentation

- **[Jsonnet Schemas Guide](./jsonnet-schemas-guide.md)** - Comprehensive guide to schema composition
- **[JSON Schema Reference](./json-schema-reference.md)** - JSON Schema data types and constraints
- **[Schemas Development Guide](../team-packages/schemas-guide.md)** - Schema development for processes

---

This reference provides quick lookup for Jsonnet language features used in Pantheon schema development. For comprehensive schema composition patterns, see the Jsonnet Schemas Guide.
