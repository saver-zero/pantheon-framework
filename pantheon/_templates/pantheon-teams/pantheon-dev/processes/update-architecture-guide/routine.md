
{% set _current_step_index = namespace(num=1) %}
{% set _pantheon_sections_string = pantheon_sections | join(',') if pantheon_sections is defined else "" %}
{% set _pantheon_sections_param = " --sections " + _pantheon_sections_string if pantheon_sections is defined else "" %}
# Routine: update-architecture-guide {% if pantheon_sections is defined %}--sections {{ _pantheon_sections_string }}{% endif %}

**Objective:** To design and update architecture-guide {% if pantheon_sections is defined %}sections: {{ _pantheon_sections_string }}{% endif %}
**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step {{ _current_step_index.num }}. **Get Schema:** Retrieve the structural contract for the architecture-guide{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}. Use `pantheon get schema update-architecture-guide{{ _pantheon_sections_param }} --actor <your_agent_name>`.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get Context** Retrieve the context for the architecture-guide. Use `pantheon execute get-architecture-guide --sections context,{{ initial_section }} --actor <your_agent_name>`
{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch {{ _current_step_index.num }}-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch {{ _current_step_index.num }}-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch {{ _current_step_index.num }}-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch {{ _current_step_index.num }}-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% set section_content %}
{% if pantheon_sections is defined %}
{% for section in pantheon_sections %}

    {% set snippet = "routine/sections/" ~ section ~ ".md" %}
    {% include snippet ignore missing with context %}
{% endfor %}
{% endif %}
{% endset %}
{% if section_content and section_content|trim %}
{{ section_content }}
{% else %}

Step {{ _current_step_index.num }}. **High-Level Design:** Define the core content of the architecture-guide{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} using the schema. Follow each field's authoring_guidance so every update stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
Step {{ _current_step_index.num }}. **Quality Review:** Revisit the updated content (lists, strings, nested objects) and trim redundant or low-impact entries before finalizing.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content of the architecture-guide{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (finish). **Execute Process:** Execute the process to update architecture-guide{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} with the fully assembled <tempfile>. Use `pantheon execute update-architecture-guide{{ _pantheon_sections_param }} --from-file "<tempfile>" --id <architecture-guide id> --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.