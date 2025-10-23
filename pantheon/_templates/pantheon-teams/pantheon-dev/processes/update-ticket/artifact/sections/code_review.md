### Code review - {{ pantheon_timestamp }}

**Reviewed by:** {{ pantheon_actor }}

**Reviewed:** {{ pantheon_timestamp }}

**Status:** {{ review_status }}

### Summary
{{ summary }}

### Findings
{% if findings %}
{% for finding in findings %}

**{{ loop.index }}. {{ finding.title }}** 

Pillar: {{ finding.pillar }}
Severity: {{ finding.severity }}

{{ finding.description }}

*Recommendation:* {{ finding.recommendation }}

{% if finding.get('code_location') %}
*Code Location:* {{ finding.code_location }}

{% endif %}
{% if finding.get('impact_analysis') %}
*Impact Analysis:* {{ finding.impact_analysis }}

{% endif %}
{% endfor %}
{% else %}
No significant issues found in this review.
{% endif %}
---
