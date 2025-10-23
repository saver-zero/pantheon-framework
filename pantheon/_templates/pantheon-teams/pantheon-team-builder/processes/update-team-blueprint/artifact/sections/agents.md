## Agent Architecture
updated_at: {{ pantheon_timestamp }}

### Team Composition

{{ team_composition_overview }}

### Agent Definitions

{% for agent in agents %}
#### {{ agent.name }}

**Role**: {{ agent.role }}

**Core Responsibilities**:
{% for responsibility in agent.responsibilities %}
- {{ responsibility }}
{% endfor %}

**Key Capabilities**:
{% for capability in agent.capabilities %}
- {{ capability }}
{% endfor %}

**Pantheon Workflows**:
{% for workflow in agent.workflows %}
- **{{ workflow.name }}**: {{ workflow.description }}
{% endfor %}

{% if agent.manual_handoffs %}
**Manual Handoffs**:
{% for item in agent.manual_handoffs %}
- {{ item }}
{% endfor %}

{% endif %}

{% endfor %}