## Shared Services
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

{% for service in services %}
### {{ service.name }}

**Purpose**: {{ service.purpose }}

#### Usage Pattern

```{{ service.language }}

{{ service.usage_example }}

```

#### Configuration

{% for config in service.configuration %}
- **{{ config.key }}**: {{ config.description }} (Default: `{{ config.default }}`)
{% endfor %}

#### Best Practices

{% for practice in service.best_practices %}
- {{ practice }}
{% endfor %}

---

{% endfor %}