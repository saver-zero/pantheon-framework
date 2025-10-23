---
created_at: {{ pantheon_timestamp }}
---
<!-- SECTION:START:ROUTINE -->
# Routine: {{ process_name }}

**Objective:** {{ objective }}

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

{% if process_type == 'create' %}
    {% include 'artifact-template://create-basic-routine/create_routine' %}
{% elif process_type == 'get' %}
    {% include 'artifact-template://create-basic-routine/get_routine' %}
{% elif process_type == 'update' %}
    {% include 'artifact-template://create-basic-routine/update_routine' %}
{% else %}
    ERROR: Invalid process_type specified. Must be 'create', 'get', or 'update'.
{% endif %}

<!-- SECTION:END:ROUTINE -->
