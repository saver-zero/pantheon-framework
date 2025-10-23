## Tech Stack
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

{% for tech in core_technologies %}
### {{ tech.name }}

- **Version**: {{ tech.version }}

- **Purpose**: {{ tech.purpose }}

- **License**: {{ tech.license }}
{% if tech.alternatives_considered %}
- **Why Chosen Over**: {{ tech.alternatives_considered }}
{% endif %}

{% endfor %}

### Frameworks and Libraries

{% for category in framework_categories %}
#### {{ category.category }}

{% for lib in category.libraries %}
- **{{ lib.name }}** (v{{ lib.version }}): {{ lib.purpose }}
{% endfor %}

{% endfor %}

### Development Tools

{% for tool in development_tools %}
- **{{ tool.name }}**: {{ tool.purpose }} (Required: {{ tool.required }})
{% endfor %}