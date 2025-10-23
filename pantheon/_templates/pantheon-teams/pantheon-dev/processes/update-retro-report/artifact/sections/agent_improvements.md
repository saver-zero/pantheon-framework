{% for improvement in agent_improvement_items %}**Agent**: {{ improvement.agent_name }}
**Issue**: {{ improvement.issue_description }}

**Recommended Changes**: {{ improvement.recommended_changes }}

**Priority**: {{ improvement.priority }}
{% if improvement.example_feedback %}**Example Feedback**: {{ improvement.example_feedback }}{% endif %}

{% endfor %}