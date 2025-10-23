---
created_at: {{ pantheon_timestamp }}
---
<!-- SECTION:START:OBJECTIVE -->
# Routine: {{ process_name }}

**Objective:** {{ objective }}

**Process Type:** {{ process_type }}

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---
<!-- SECTION:END:OBJECTIVE -->

<!-- SECTION:START:STEPS -->
{% if process_type == 'create' %}
    {% include 'artifact-template://create-custom-routine/create_routine' %}
{% elif process_type == 'get' %}
    {% include 'artifact-template://create-custom-routine/get_routine' %}
{% elif process_type == 'update' %}
    {% include 'artifact-template://create-custom-routine/update_routine' %}
{% else %}
    ERROR: Invalid process_type specified. Must be 'create', 'get', or 'update'.
{% endif %}
<!-- SECTION:END:STEPS -->
