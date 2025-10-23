## Consequences and Rationale
updated: {{ pantheon_timestamp }}

### Primary Rationale

{{ primary_rationale }}

### Expected Positive Consequences
{% for consequence in positive_consequences %}
- **{{ consequence.area }}**: {{ consequence.description }}
{% endfor %}

### Expected Negative Consequences
{% for consequence in negative_consequences %}
- **{{ consequence.area }}**: {{ consequence.description }} - *Mitigation: {{ consequence.mitigation }}*
{% endfor %}

### Key Trade-offs
{% for tradeoff in key_tradeoffs %}
- **{{ tradeoff.aspect }}**: {{ tradeoff.description }}
{% endfor %}

### Future Validation Points
{% for validation in validation_points %}
- **{{ validation.timeline }}**: {{ validation.criteria }}
{% endfor %}