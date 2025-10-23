### {{ pantheon_timestamp }} Progress
Agent: {{ pantheon_actor }}

#### Summary
{{ progress_summary }}

{% if decisions %}
#### Key Decisions Made
{% for decision_item in decisions %}
* **Decision:** {{ decision_item.decision }}
{% if decision_item.get('impact') %}  - **Impact:** {{ decision_item.impact }}{% endif %}
{% if decision_item.get('alternatives') %}  - **Alternatives:** {% for alt in decision_item.alternatives %}{{ alt }}{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}
{% endfor %}
{% endif %}

{% if lessons_learned %}
#### Lessons Learned
{% for lesson_item in lessons_learned %}
* {{ lesson_item.lesson }}
{% endfor %}
{% endif %}

{% if assumptions %}
#### Assumptions Made
{% for assumption_item in assumptions %}
* {{ assumption_item.assumption }}
{% endfor %}
{% endif %}

{% if todos %}
#### TODOs
{% for todo in todos %}
- [ ] **Action:** {{ todo.action }}{% if todo.get('priority') %} (Priority: {{ todo.priority }}){% endif %}

  {% if todo.get('estimated_effort') %}
  - **Effort:** {{ todo.estimated_effort }}

  {% endif %}
  {% if todo.get('dependencies') %}
  - **Dependencies:** {% for dep in todo.dependencies %}{{ dep }}{% if not loop.last %}, {% endif %}{% endfor %}

  {% endif %}
{% endfor %}
{% endif %}

---
