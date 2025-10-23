# Routine: create-architecture-guide

**Objective:** To design and create a complete architecture-guide.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

{% set _current_step_index = namespace(num=0) %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get Schema:** Retrieve the structural contract for the architecture-guide. Use `pantheon get schema create-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch {{ _current_step_index.num }}-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch {{ _current_step_index.num }}-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch {{ _current_step_index.num }}-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch {{ _current_step_index.num }}-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **High-Level Design:** Define the core content of the architecture-guide using the schema. Follow each field's authoring_guidance so every list or string stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Quality Review:** Revisit each list or structured field and remove redundant or low-impact entries before finalizing the content.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content of the architecture-guide designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Execute Process:** Execute the process to create the architecture-guide with the fully assembled <tempfile>. Use `pantheon execute create-architecture-guide --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get schema for system components and shared services:** Retrieve the structural contract for system components and shared-services. Use `pantheon get schema update-architecture-guide --actor <your_agent_name> --sections system-components,shared-services`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **System component and shared services design:** Define the core content of the system components and shared services using the schema. Follow each field's authoring_guidance so every list or string stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get a new temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content system components and shared services designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Execute Process:** Execute the process to update the architecture-guide with the fully assembled <tempfile>. Use `pantheon execute update-architecture-guide --from-file "<tempfile>" --actor <your_agent_name> --sections system-components,shared-services`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Create system diagram:** Create system diagram for the system components and shared serivces. Use `pantheon get process create-documentation --actor <your_agent_name>` and follow the steps.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get schema for implementation patterns:** Retrieve the structural contract for system components and shared-services. Use `pantheon get schema update-architecture-guide --actor <your_agent_name> --sections implementation-patterns`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Implementation patterns design:** Define the core content of the implementation patterns using the schema. Follow each field's authoring_guidance so every list or string stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get a new temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content implementation patterns designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Execute Process:** Execute the process to update the architecture-guide with the fully assembled <tempfile>. Use `pantheon execute update-architecture-guide --from-file "<tempfile>" --actor <your_agent_name> --sections implementation-patterns`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.

{% if pantheon_active_profile.enforce_tdd %}
{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get schema for testing strategy:** Retrieve the structural contract for system components and shared-services. Use `pantheon get schema update-architecture-guide --actor <your_agent_name> --sections testing-strategy`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Testing strategy design:** Define the core content of the testing strategy using the schema. Focus on a true unit test based Test Driven Development, writing tests as if implementation is working, failing naturally, following the Red-Green-Refactor approach. Before wrapping up work, all tests needs to be run to check for regression as well. Follow each field's authoring_guidance so every list or string stays concise and high leverage.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Get a new temp file location:** Get the temp file location. Use `pantheon get tempfile --process update-architecture-guide --actor <your_agent_name>`.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Save the JSON:** Write the content testing strategy designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }}. **Execute Process:** Execute the process to update the architecture-guide with the fully assembled <tempfile>. Use `pantheon execute update-architecture-guide --from-file "<tempfile>" --actor <your_agent_name> --sections testing-strategy`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.
{% endif %}

{% set _current_step_index.num = _current_step_index.num + 1 %}
Step {{ _current_step_index.num }} (finish). **Done:** You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.