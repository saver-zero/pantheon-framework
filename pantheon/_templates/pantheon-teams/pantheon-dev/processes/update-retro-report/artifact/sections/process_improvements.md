{% for improvement in process_improvement_items %}**Process**: {{ improvement.process_name }}
**Issue**: {{ improvement.issue_description }}

**Recommended Changes**: {{ improvement.recommended_changes }}

**Priority**: {{ improvement.priority }}
{% if improvement.affected_sections %}**Affected Sections**: {{ improvement.affected_sections | join(', ') }}{% endif %}

{% endfor %}