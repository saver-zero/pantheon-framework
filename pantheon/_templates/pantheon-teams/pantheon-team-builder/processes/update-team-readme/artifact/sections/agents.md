## Available Agents

{{ agents_intro }}

{% for agent in agent_list %}
### {{ agent.name }}

**Expertise**: {{ agent.expertise }}

**When to Engage**: {{ agent.when_to_use }}

**How to Interact**:

{{ agent.interaction_guide }}

**What {{ agent.name }} Delivers**:
{% for deliverable in agent.deliverables %}
- {{ deliverable }}
{% endfor %}

{% endfor %}