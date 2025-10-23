
{% set _current_step_index = namespace(num=1) %}
{% set _pantheon_sections_string = pantheon_sections | join(',') if pantheon_sections is defined else "" %}
{% set _pantheon_sections_param = " --sections " + _pantheon_sections_string if pantheon_sections is defined else "" %}
# Routine: update-retro-report {% if pantheon_sections is defined %}--sections {{ _pantheon_sections_string }}{% endif %}

**Objective:** To design and update retro-report {% if pantheon_sections is defined %}sections: {{ _pantheon_sections_string }}{% endif %}

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step {{ _current_step_index.num }}. **Get Schema:** Retrieve the structural contract for the retro-report{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}. Use `pantheon get schema update-retro-report{{ _pantheon_sections_param }} --actor <your_agent_name>`.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get Context** Retrieve the context for the retro-report. Use `pantheon execute get-retro-report --sections context,{{ initial_section }} --actor <your_agent_name> --id <retro-report id>`
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch {{ _current_step_index.num }}-1 Step 1. **Process References:** If reference material was provided, read the content of the relevant reference documents to build a comprehensive context.
  - Branch {{ _current_step_index.num }}-2 Step 1. **No References:** If no reference material was provided, proceed with the design based on the initial request.
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

Step {{ _current_step_index.num }}. **High-Level Design:** Define the core content of the retro-report{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} using the schema. Follow each field's authoring_guidance so every update stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
Step {{ _current_step_index.num }}. **Quality Review:** Revisit the updated content (lists, strings, nested objects) and trim redundant or low-impact entries before finalizing.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-retro-report --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content of the retro-report{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (finish). **Execute Process:** Execute the process to update retro-report{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} with the fully assembled <tempfile>. Use `pantheon execute update-retro-report{{ _pantheon_sections_param }} --from-file "<tempfile>" --id <retro-report id> --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.