## Alternatives Considered
updated: {{ pantheon_timestamp }}

{% for alternative in alternatives %}
### {{ alternative.name }}

**Description**: {{ alternative.description }}

**Pros**:
{% for pro in alternative.pros %}
- {{ pro }}
{% endfor %}

**Cons**:
{% for con in alternative.cons %}
- {{ con }}
{% endfor %}

**Implementation Effort**: {{ alternative.implementation_effort }}

**Risk Assessment**: {{ alternative.risk_assessment }}

---
{% endfor %}