{% for improvement in documentation_improvement_items %}**Documentation**: {{ improvement.document_name }}
**Issue**: {{ improvement.issue_description }}

**Recommended Changes**: {{ improvement.recommended_changes }}

**Priority**: {{ improvement.priority }}

**Document Type**: {{ improvement.document_type }}

{% endfor %}