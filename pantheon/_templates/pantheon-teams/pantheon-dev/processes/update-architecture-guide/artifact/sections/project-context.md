## Project Context
last updated: {{ pantheon_timestamp }}
updated by: {{ pantheon_actor }}

### Problem Statement

{{ problem_statement }}

### Business Outcomes

{% for outcome in business_outcomes %}
- {{ outcome }}
{% endfor %}

### Key Features

{% for feature in key_features %}
- **{{ feature.name }}**: {{ feature.description }}
{% endfor %}