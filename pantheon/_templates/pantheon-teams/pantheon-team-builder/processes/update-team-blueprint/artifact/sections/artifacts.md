## Artifact Design
updated_at: {{ pantheon_timestamp }}

### Process Architecture Overview

{{ architecture_overview }}

### Core Artifacts

{% for artifact in artifacts %}
{% set artifact_name = artifact.name | slugify %}
#### {{ artifact_name }} Artifact

**Purpose**: {{ artifact.purpose }}

**Build Mode**: `{{ artifact.build_mode }}`

**Source Reference**: {{ artifact.source_reference }}

**Pantheon Commands**
- To get the instructions for creating {{ artifact_name }}, use `pantheon get process create-{{ artifact_name }} --actor <your_agent_name>`
{% for section in artifact.sections %}
{% set _insert_mode = "" %}
{% if section.update_behavior == 'PREPEND' %}
  {% set _insert_mode = " --insert-mode prepend" %}
{% elif section.update_behavior == 'APPEND' %}
  {% set _insert_mode = " --insert-mode append" %}
{% endif %}
- To get the instructions for updating {{ section.name }} section of {{ artifact_name }}, use `pantheon get process update-{{ artifact_name }} --id <{{ artifact_name }} id> --sections {{ section.name }}{{ _insert_mode }} --actor <your_agent_name>`
{% endfor %}

**Sections**:
{% for section in artifact.sections %}
- **{{ section.name }}**: {{ section.purpose }}.
{% endfor %}

{% if artifact.section_sequence %}
**Section Workflow**:
{% for step in artifact.section_sequence %}
- **{{ step.section }} ({{ step.action }})**: {{ step.description }}
{% endfor %}

{% endif %}
**Process Operations**:
{% for operation in artifact.operations %}
- **{{ operation.type }}**: {{ operation.description }}
{% endfor %}

{% if artifact.external_inputs %}
**External Inputs & Canonicalization**:
{% for item in artifact.external_inputs %}
- {{ item.input }}
{% endfor %}

{% endif %}
{% if artifact.manual_actions_required %}
**Manual Operator Actions**:
{% for item in artifact.manual_actions_required %}
- {{ item.action }}
{% endfor %}

{% endif %}

{% endfor %}

### Process Interactions

{{ process_interactions }}

### Operator Notes

{{ operator_notes }}