{% set _current_step_index = namespace(num=1) %}

Step {{ _current_step_index.num }}. **Get Schema:** Retrieve the structural contract for the {{ process_name }}. Use `pantheon get schema {{ process_name }} --actor <your_agent_name>`.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch {{ _current_step_index.num }}-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch {{ _current_step_index.num }}-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch {{ _current_step_index.num }}-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch {{ _current_step_index.num }}-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% for routine_step in steps | default([], true) %}

{% if routine_step.node_type == 'node' %}
Step {{ _current_step_index.num }}. **{{ routine_step.name }}:** {{ routine_step.description }}{% if routine_step.tool %}. Use `{{ routine_step.tool }}`{% endif %}
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% elif routine_step.node_type == 'branch' %}
Step {{ _current_step_index.num }} (branch). **{{ routine_step.name }}:** Perform a branch condition check. {{ routine_step.description }}:
{% for path in routine_step.paths %}
{% set branch_num = loop.index %}
{% set branch_start = path.start %}
  - Branch {{ _current_step_index.num }}-{{ branch_num }} Step 1. **{{ branch_start.name }}:** If {{ branch_start.condition }}, then {{ branch_start.action }}{% if branch_start.tool %}. Use `{{ branch_start.tool }}`{% endif %}
{% if path.steps %}{% for branch_step in path.steps %}
{% if branch_step.node_type == 'branchnode' %}

  - Branch {{ _current_step_index.num }}-{{ branch_num }} Step {{ loop.index + 1 }}. **{{ branch_step.name }}:** {{ branch_step.description }}{% if branch_step.tool %}. Use `{{ branch_step.tool }}`{% endif %}
{% elif branch_step.node_type == 'branchfinishnode' %}

  - Branch {{ _current_step_index.num }}-{{ branch_num }} Step {{ loop.index + 1 }} (terminate). **{{ branch_step.name }}:** {{ branch_step.description }}{% if branch_step.tool %}. Use `{{ branch_step.tool }}`{% endif %}. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.{% endif %}
{% endfor %}{% endif %}

{% endfor %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% elif routine_step.node_type == 'finish' %}

Step {{ _current_step_index.num }} (finish). **{{ routine_step.name }}:** {{ routine_step.description }}{% if routine_step.tool %}. Use `{{ routine_step.tool }}`{% endif %}. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
{% endfor %}

Step {{ _current_step_index.num }}. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process {{ process_name }} --actor <your_agent_name>`.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (finish). **Execute Process:** Execute {{ process_name }} with the fully assembled <tempfile>. Use `pantheon execute {{ process_name }} --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
