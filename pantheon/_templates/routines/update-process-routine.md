{% raw %}
{% set _current_step_index = namespace(num=1) %}
{% set _pantheon_sections_string = pantheon_sections | join(',') if pantheon_sections is defined else "" %}
{% set _pantheon_sections_param = " --sections " + _pantheon_sections_string if pantheon_sections is defined else "" %}
{% endraw %}{# Generate insert-mode logic based on section update_behavior #}
{% if section_template %}
{% set sections_with_behavior = [] %}
{% for section_def in section_template %}
  {% if section_def.update_behavior and section_def.update_behavior != 'REPLACE' %}
    {% set _ = sections_with_behavior.append(section_def) %}
  {% endif %}
{% endfor %}
{% raw %}{% set _insert_mode = "" %}
{% endraw %}{% if sections_with_behavior|length > 0 %}
{% for section_def in sections_with_behavior %}{% if loop.first %}{% raw %}{% if _pantheon_sections_string == '{% endraw %}{{ section_def.section }}{% raw %}' %}
  {% set _insert_mode = " --insert-mode {% endraw %}{{ section_def.update_behavior|lower }}{% raw %}" %}{% endraw %}{% else %}{% raw %}
{% elif _pantheon_sections_string == '{% endraw %}{{ section_def.section }}{% raw %}' %}
  {% set _insert_mode = " --insert-mode {% endraw %}{{ section_def.update_behavior|lower }}{% raw %}" %}{% endraw %}{% endif %}{% endfor %}{% raw %}
{% endif %}{% endraw %}
{% endif %}
{% endif %}
# Routine: update-{{ artifact }} {% raw %}{% if pantheon_sections is defined %}--sections {{ _pantheon_sections_string }}{% endif %}{% endraw %}


**Objective:** To design and update {{ artifact }} {% raw %}{% if pantheon_sections is defined %}sections: {{ _pantheon_sections_string }}{% endif %}{% endraw %}

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **Get Schema:** Retrieve the structural contract for the {{ artifact }}{% raw %}{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}{% endraw %}. Use `pantheon get schema update-{{ artifact }}{% raw %}{{ _pantheon_sections_param }}{% endraw %} --actor <your_agent_name>`.
{% raw %}{% set _current_step_index.num = _current_step_index.num + 1 %}{% endraw %}


Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **Get Context** Retrieve the context for the {{ artifact }}. Use `pantheon execute get-{{ artifact }} --sections context,{% raw %}{{ initial_section }}{% endraw %} --actor <your_agent_name> --id <{{ artifact }} id>`
{% raw %}{% set _current_step_index.num = _current_step_index.num + 1 %}{% endraw %}

Step {% raw %}{{ _current_step_index.num }}{% endraw %} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch {% raw %}{{ _current_step_index.num }}{% endraw %}-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch {% raw %}{{ _current_step_index.num }}{% endraw %}-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch {% raw %}{{ _current_step_index.num }}{% endraw %}-1 Step 3. **Expand context:** Review each of the identified additional references to build comprehensive context.
  - Branch {% raw %}{{ _current_step_index.num }}{% endraw %}-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.
{% raw %}{% set _current_step_index.num = _current_step_index.num + 1 %}{% endraw %}
{% raw %}
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
{% endraw %}

Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **High-Level Design:** Define the core content of the {{ artifact }}{% raw %}{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}{% endraw %} using the schema. Follow each field's authoring_guidance so every update stays concise and high leverage.
{% raw %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
{% endraw %}
Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **Quality Review:** Revisit the updated content (lists, strings, nested objects) and trim redundant or low-impact entries before finalizing.
{% raw %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endraw %}
Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-{{ artifact }} --actor <your_agent_name>`.
{% raw %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endraw %}
Step {% raw %}{{ _current_step_index.num }}{% endraw %}. **Save the JSON:** Write the content of the {{ artifact }}{% raw %}{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}{% endraw %} designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.
{% raw %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endraw %}
Step {% raw %}{{ _current_step_index.num }}{% endraw %} (finish). **Execute Process:** Execute the process to update {{ artifact }}{% raw %}{% if pantheon_sections is defined %} sections: {{ _pantheon_sections_string }}{% endif %}{% endraw %} with the fully assembled <tempfile>. Use `pantheon execute update-{{ artifact }}{% raw %}{{ _pantheon_sections_param }}{% endraw %} --from-file "<tempfile>" --id <{{ artifact }} id> --actor <your_agent_name>{% raw %}{{ _insert_mode }}{% endraw %}`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.