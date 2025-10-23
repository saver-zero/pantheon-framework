{% for improvement in artifact_improvement_items %}**Artifact**: {{ improvement.artifact_name }}
**Issue**: {{ improvement.issue_description }}

**Recommended Changes**: {{ improvement.recommended_changes }}

**Priority**: {{ improvement.priority }}

**Change Type**: {{ improvement.change_type }}
{% if improvement.affected_sections %}**Affected Sections**: {{ improvement.affected_sections | join(', ') }}{% endif %}

{% endfor %}