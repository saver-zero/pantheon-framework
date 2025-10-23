---
doc_id: json-schema-reference
title: "JSON Schema Reference"
description: "Quick reference for JSON Schema data types, validation constraints, and complex type definitions used in Pantheon Jsonnet schemas."
keywords: [json-schema, data-types, validation, constraints, primitives, arrays, objects, enums]
relevance: "Use this document as a quick reference for JSON Schema data types and validation constraints when writing Jsonnet schemas."
---

# JSON Schema Reference

This document provides a quick reference for JSON Schema data types and validation constraints used in Pantheon Jsonnet schemas.

## Primitive Types

### String

```jsonnet
{
  type: 'string',
  minLength: 1,
  maxLength: 100,
  pattern: '^[A-Z][a-z]+$',  // Regex validation
  description: 'Capitalized word'
}
```

**Common Constraints:**
- `minLength`: Minimum string length
- `maxLength`: Maximum string length
- `pattern`: Regular expression pattern
- `format`: Semantic format (email, date, date-time, uri)

**Format Examples:**
```jsonnet
{
  email: { type: 'string', format: 'email' },
  date: { type: 'string', format: 'date' },
  datetime: { type: 'string', format: 'date-time' },
  url: { type: 'string', format: 'uri' }
}
```

### Number

```jsonnet
{
  type: 'number',
  minimum: 0,
  maximum: 100,
  multipleOf: 5,
  description: 'Score between 0 and 100, multiples of 5'
}
```

**Common Constraints:**
- `minimum`: Minimum value (inclusive)
- `maximum`: Maximum value (inclusive)
- `exclusiveMinimum`: Minimum value (exclusive)
- `exclusiveMaximum`: Maximum value (exclusive)
- `multipleOf`: Value must be multiple of this number

### Integer

```jsonnet
{
  type: 'integer',
  minimum: 1,
  description: 'Positive integer'
}
```

**Note:** Integers use the same constraints as numbers but enforce whole number values.

### Boolean

```jsonnet
{
  type: 'boolean',
  description: 'True or false flag'
}
```

## Complex Types

### Array

**Basic Array:**
```jsonnet
{
  type: 'array',
  items: {
    type: 'string',
    description: 'Individual step description'
  },
  minItems: 1,
  description: 'List of implementation steps'
}
```

**Common Constraints:**
- `items`: Schema for array elements
- `minItems`: Minimum number of items
- `maxItems`: Maximum number of items
- `uniqueItems`: Require unique elements (true/false)

**Array with Multiple Types:**
```jsonnet
{
  type: 'array',
  items: {
    anyOf: [
      { type: 'string' },
      { type: 'number' }
    ]
  }
}
```

**Array with Unique Items:**
```jsonnet
{
  type: 'array',
  items: { type: 'string' },
  uniqueItems: true,
  description: 'List of unique tags'
}
```

### Object

**Basic Object:**
```jsonnet
{
  type: 'object',
  properties: {
    name: { type: 'string' },
    age: { type: 'integer' }
  },
  required: ['name'],
  additionalProperties: false
}
```

**Common Constraints:**
- `properties`: Property definitions
- `required`: Array of required property names
- `additionalProperties`: Allow/disallow undefined properties (boolean or schema)

**Object with Additional Properties:**
```jsonnet
{
  type: 'object',
  properties: {
    id: { type: 'string' }
  },
  additionalProperties: {
    type: 'string'  // Additional properties must be strings
  }
}
```

### Enum

```jsonnet
{
  type: 'string',
  enum: ['planning', 'implementation', 'testing', 'complete'],
  description: 'Current ticket status'
}
```

**Numeric Enum:**
```jsonnet
{
  type: 'integer',
  enum: [1, 2, 3, 4, 5],
  description: 'Priority level'
}
```

### Union Types

**Optional Field (String or Null):**
```jsonnet
{
  anyOf: [
    { type: 'string' },
    { type: 'null' }
  ],
  description: 'Optional string field'
}
```

**Multiple Type Options:**
```jsonnet
{
  anyOf: [
    { type: 'string' },
    { type: 'number' },
    { type: 'boolean' }
  ],
  description: 'Flexible value field'
}
```

**Alternative: oneOf (Exactly One Match):**
```jsonnet
{
  oneOf: [
    { type: 'string', minLength: 1 },
    { type: 'number', minimum: 0 }
  ]
}
```

## Validation Constraint Summary

### String Constraints
| Constraint | Type | Description | Example |
|------------|------|-------------|---------|
| `minLength` | integer | Minimum string length | `minLength: 1` |
| `maxLength` | integer | Maximum string length | `maxLength: 80` |
| `pattern` | string | Regex pattern | `pattern: '^[A-Z]'` |
| `format` | string | Semantic format | `format: 'email'` |

### Numeric Constraints
| Constraint | Type | Description | Example |
|------------|------|-------------|---------|
| `minimum` | number | Minimum value (inclusive) | `minimum: 0` |
| `maximum` | number | Maximum value (inclusive) | `maximum: 100` |
| `exclusiveMinimum` | number | Minimum value (exclusive) | `exclusiveMinimum: 0` |
| `exclusiveMaximum` | number | Maximum value (exclusive) | `exclusiveMaximum: 100` |
| `multipleOf` | number | Value must be multiple | `multipleOf: 5` |

### Array Constraints
| Constraint | Type | Description | Example |
|------------|------|-------------|---------|
| `items` | schema | Schema for elements | `items: { type: 'string' }` |
| `minItems` | integer | Minimum items | `minItems: 1` |
| `maxItems` | integer | Maximum items | `maxItems: 10` |
| `uniqueItems` | boolean | Require unique elements | `uniqueItems: true` |

### Object Constraints
| Constraint | Type | Description | Example |
|------------|------|-------------|---------|
| `properties` | object | Property definitions | `properties: { ... }` |
| `required` | array | Required property names | `required: ['field1']` |
| `additionalProperties` | boolean/schema | Allow undefined properties | `additionalProperties: false` |

## Common Patterns

### Optional Field Pattern
```jsonnet
{
  type: 'object',
  properties: {
    required_field: { type: 'string' },
    optional_field: { type: 'string' }
  },
  required: ['required_field']
}
```

### Nested Object Pattern
```jsonnet
{
  type: 'object',
  properties: {
    user: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        email: { type: 'string', format: 'email' }
      },
      required: ['name', 'email']
    }
  }
}
```

### Array of Objects Pattern
```jsonnet
{
  type: 'array',
  items: {
    type: 'object',
    properties: {
      step_number: { type: 'integer', minimum: 1 },
      description: { type: 'string' }
    },
    required: ['step_number', 'description']
  }
}
```

### Conditional Validation Pattern
```jsonnet
{
  type: 'object',
  properties: {
    type: { type: 'string', enum: ['user', 'admin'] },
    permissions: { type: 'array', items: { type: 'string' } }
  },
  if: {
    properties: { type: { const: 'admin' } }
  },
  then: {
    required: ['permissions']
  }
}
```

### Pattern Validation Examples

**Ticket ID Format (T001, T002, etc.):**
```jsonnet
{
  type: 'string',
  pattern: '^T[0-9]{3}$',
  description: 'Ticket ID in format T###'
}
```

**Capitalized Title:**
```jsonnet
{
  type: 'string',
  pattern: '^[A-Z]',
  description: 'Title starting with capital letter'
}
```

**Email Pattern:**
```jsonnet
{
  type: 'string',
  format: 'email',
  description: 'Valid email address'
}
```

## Related Documentation

- **[Jsonnet Schemas Guide](./jsonnet-schemas-guide.md)** - Comprehensive guide to Jsonnet schema composition
- **[Jsonnet Language Reference](./jsonnet-language-reference.md)** - Jsonnet language features
- **[Schemas Development Guide](../team-packages/schemas-guide.md)** - Schema development for processes

---

This reference provides quick lookup for JSON Schema types and constraints when writing Pantheon Jsonnet schemas. For comprehensive schema composition patterns and best practices, see the Jsonnet Schemas Guide.
