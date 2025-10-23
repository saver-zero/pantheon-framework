## Decision Context
updated: {{ pantheon_timestamp }}

### Problem Statement

{{ problem_statement }}

### Driving Forces
{% for force in driving_forces %}
- **{{ force.category }}**: {{ force.description }}
{% endfor %}

### Constraints
{% for constraint in constraints %}
- **{{ constraint.type }}**: {{ constraint.description }}
{% endfor %}

### Success Criteria
{% for criterion in success_criteria %}
- {{ criterion }}
{% endfor %}