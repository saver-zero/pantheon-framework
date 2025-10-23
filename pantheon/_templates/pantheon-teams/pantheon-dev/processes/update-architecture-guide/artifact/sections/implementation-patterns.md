## Implementation Patterns
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

{% for pattern in patterns %}
### {{ pattern.name }}

**Category**: {{ pattern.category }}

**Problem**: {{ pattern.problem }}

**Solution**: {{ pattern.solution }}

#### Implementation

```{{ pattern.code_language }}

{{ pattern.implementation_example }}

```

#### When to Use

{% for scenario in pattern.when_to_use %}
- {{ scenario }}
{% endfor %}

#### When NOT to Use

{% for scenario in pattern.when_not_to_use %}
- {{ scenario }}
{% endfor %}

---

{% endfor %}