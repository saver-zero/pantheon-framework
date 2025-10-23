{% set team_name = target_team | slugify | remove_suffix("-team") %}
{% if pantheon_artifact_id is not string or not pantheon_artifact_id.startswith('TB') %}
{% set pantheon_artifact_id = "TB{:02d}".format(pantheon_artifact_id|int) %}
{% endif %}
# {{ pantheon_artifact_id }} - {{ team_name }} Team Blueprint

## Team Foundation
updated_at: {{ pantheon_timestamp }}

**Team Name**: {{ team_name }}

### Mission Statement

{{ mission }}

### Strategic Goals
{% for goal in goals %}
- {{ goal }}
{% endfor %}

### Key Objectives
{% for objective in objectives %}
- {{ objective }}
{% endfor %}

## System Boundary

### Pantheon Framework Responsibilities
{% for item in system_boundary.pantheon_responsibilities %}
- {{ item }}
{% endfor %}

### Human Operator Responsibilities
{% for item in system_boundary.operator_responsibilities %}
- {{ item }}
{% endfor %}

### High-Leverage Artifacts
{% for item in high_leverage_artifacts %}
- **{{ item.artifact_name }}**: {{ item.description }}
{% endfor %}

### Critical Manual Checkpoints
{% for item in manual_checkpoints %}
- {{ item }}
{% endfor %}