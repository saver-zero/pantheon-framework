{% set team_name = team_name | slugify | remove_suffix("-team") %}
# {{ team_name }} Team

## Mission

{{ mission_statement }}

## Value Proposition

{{ value_proposition }}

## Key Capabilities

{% for capability in capabilities %}
- **{{ capability.name }}**: {{ capability.description }}
{% endfor %}

## When to Use This Team

{{ use_cases }}