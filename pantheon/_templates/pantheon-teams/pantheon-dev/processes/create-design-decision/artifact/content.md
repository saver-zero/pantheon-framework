---
created_at: {{ pantheon_timestamp }}
---
{% set _include_decision_context = true %}
<!-- SECTION:START:DECISION_CONTEXT -->
{% if _include_decision_context %}
{% include 'artifact-template://update-design-decision/sections/decision_context' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:DECISION_CONTEXT -->

{% set _include_alternatives_considered = true %}
<!-- SECTION:START:ALTERNATIVES_CONSIDERED -->
{% if _include_alternatives_considered %}
{% include 'artifact-template://update-design-decision/sections/alternatives_considered' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:ALTERNATIVES_CONSIDERED -->

{% set _include_decision_details = true %}
<!-- SECTION:START:DECISION_DETAILS -->
{% if _include_decision_details %}
{% include 'artifact-template://update-design-decision/sections/decision_details' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:DECISION_DETAILS -->

{% set _include_consequences_and_rationale = true %}
<!-- SECTION:START:CONSEQUENCES_AND_RATIONALE -->
{% if _include_consequences_and_rationale %}
{% include 'artifact-template://update-design-decision/sections/consequences_and_rationale' %}
{% else %}
<!-- SECTION:PLACEHOLDER -->
{% endif %}
<!-- SECTION:END:CONSEQUENCES_AND_RATIONALE -->
