
{% set _current_step_index = namespace(num=1) %}
{% set _pantheon_sections_string = pantheon_sections | join(',') if pantheon_sections is defined else "" %}
{% set _pantheon_sections_param = " --sections " + _pantheon_sections_string if pantheon_sections is defined else "" %}
{% if _pantheon_sections_string == "artifacts" %}
  {% set additional_sections = ",artifacts" %}
{% elif _pantheon_sections_string == "agents" %}
  {% set additional_sections = ",artifacts,agents" %}
{% elif _pantheon_sections_string == "profile" %}
  {% set additional_sections = ",artifacts,profile" %}
{% else %}
  {% set additional_sections = "" %}
{% endif %}
# Routine: update-team-blueprint {% if pantheon_sections is defined %}--sections {{ _pantheon_sections_string }}{% endif %}

**Objective:** To design and update team-blueprint {% if pantheon_sections is defined %}sections: {{ _pantheon_sections_string }}{% endif %}

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step {{ _current_step_index.num }}. **Get Schema:** Retrieve the structural contract for the team-blueprint{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}. Use `pantheon get schema update-team-blueprint{{ _pantheon_sections_param }} --actor <your_agent_name>`.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get Context** Retrieve the context for the team-blueprint. Use `pantheon execute get-team-blueprint --sections context,{{ initial_section }}{{ additional_sections }} --actor <your_agent_name> --id <team-blueprint id>`
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

Step {{ _current_step_index.num }}. **High-Level Design:** Define the core content of the team-blueprint{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} using the schema. Follow each field's authoring_guidance so every update stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
Step {{ _current_step_index.num }}. **Quality Review:** Revisit the updated content (lists, strings, nested objects) and trim redundant or low-impact entries before finalizing.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-team-blueprint --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content of the team-blueprint{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %} designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (branch). **Check Insert Mode:** Perform a branch condition check. Determine if content should be appended to existing items or replace them:
  - Branch {{ _current_step_index.num }}-1 Step 1 (finish). **Append Content:** If you need to simply add to an existing section without replacing or changing the existing content in the section, then execute the process in append mode. Use `pantheon execute update-team-blueprint{{ _pantheon_sections_param }} --from-file "<tempfile>" --id <team-blueprint id> --insert-mode append --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
  - Branch {{ _current_step_index.num }}-2 Step 1 (finish). **Replace Content:** If you need to update or replace existing section content entirely, then execute the process in replace mode. Use `pantheon execute update-team-blueprint{{ _pantheon_sections_param }} --from-file "<tempfile>" --id <team-blueprint id> --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.