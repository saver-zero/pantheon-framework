## Workflow Examples

{{ examples_intro }}

{% for example in examples %}
### Example {{ loop.index }}: {{ example.title }}

**Scenario**: {{ example.scenario }}

**Step-by-Step Process**:

{% for step in example.steps %}
{{ loop.index }}. **{{ step.action }}**
   - {{ step.details }}
   {% if step.sample_prompt %}
   - Sample prompt: "{{ step.sample_prompt }}"
   {% endif %}
   {% if step.expected_outcome %}
   - Expected outcome: {{ step.expected_outcome }}
   {% endif %}

{% endfor %}

**Final Result**: {{ example.final_result }}

{% endfor %}