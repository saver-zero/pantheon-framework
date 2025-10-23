## System Components
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

{% for component in components %}
### {{ component.name }}

**Purpose**: {{ component.purpose }}

#### Responsibilities
{% for resp in component.responsibilities %}
- {{ resp }}
{% endfor %}

#### Dependencies
{% if component.dependencies %}
{% for dep in component.dependencies %}
- **{{ dep.component }}**: {{ dep.reason }}
{% endfor %}
{% else %}
- None (standalone component)
{% endif %}

#### Data Flows
{% for flow in component.data_flows %}
- **{{ flow.direction }}**: {{ flow.description }}
{% endfor %}

---

{% endfor %}