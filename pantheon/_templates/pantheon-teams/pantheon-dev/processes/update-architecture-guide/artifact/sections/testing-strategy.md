## Testing
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

### Testing Philosophy

{{ testing_philosophy }}

### Test Types

{% for test_type in test_types %}
#### {{ test_type.name }}

**Purpose**: {{ test_type.purpose }}

**Coverage Target**: {{ test_type.coverage_target | remove_suffix('%') }}%

**Key Patterns**:
{% for pattern in test_type.key_patterns %}
- {{ pattern }}
{% endfor %}

**Example**:

```{{ test_type.example_language }}

{{ test_type.example_code }}

```

{% endfor %}

### Testing Best Practices

{% for practice in best_practices %}
#### {{ practice.name }}

{{ practice.description }}

**Example**:

```{{ practice.example_language }}

{{ practice.example_code }}

```

{% endfor %}