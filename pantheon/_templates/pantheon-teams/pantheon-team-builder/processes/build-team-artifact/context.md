## Project Context

{{ project_context }}

### Key Concepts

{% for item in key_concepts %}
**{{ item.concept }}**: {{ item.definition }}

{% endfor %}

### Core Capabilities

{% for capability in core_capabilities %}
- {{ capability }}
{% endfor %}

### Key Principles

{% for principle in key_principles %}
- {{ principle }}
{% endfor %}

{% if references %}
### References

{% for item in references %}
- **{{ item.reference }}**: {{ item.summary }}
{% endfor %}
{% endif %}