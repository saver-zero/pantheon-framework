# Routine: create-ticket

**Objective:** To design and create a complete ticket.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

{% set _current_step = namespace(value = 0) %}
{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Get Schema:** Retrieve the structural contract for the ticket. Use `pantheon get schema create-ticket --actor <your_agent_name>`.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }} (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided.
  - Branch {{ _current_step.value }}-1 Step 1. **Process References:** If reference material was provided, read the content of the primary reference document. Then, scan that document for any further nested references and read those as well to build a comprehensive context.
  - Branch {{ _current_step.value }}-2 Step 1. **No References:** If no reference material was provided, proceed with the design based on the initial request.
{% if pantheon_active_profile.read_documentation %}

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Get the architecture guide:** Use `pantheon execute get-architecture-guide --sections project_context, high-level-overview,core-principles --actor <your_agent_name>` to get the the relevant sections of the architecture guide.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. (branch). **Check architecture guide response:** Perform a branch condition check. Check if the pantheon command returned section content in the JSON response:
  - Branch {{ _current_step.value }}-1 Step 1. **Content returned:** If the JSON response contains section content (non-empty markdown text in the section fields), then use that content directly and continue to the next step.
  - Branch {{ _current_step.value }}-2 Step 1.  **No content returned:** If the JSON response shows empty sections or placeholder text, then check for additional documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
  - Branch {{ _current_step.value }}-2 Step 2. **Understand the Documentation Structure:** Leverage any README or INDEX files, the directory structure, and file names to understand the overall documentation structure.
  - Branch {{ _current_step.value }}-2 Step 3. **Read Existing Documentation:** Identify and read relevant documetations to build context. Make sure to read any architecture pattern or design principles doc.
{% endif %}

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **High-Level Design:** Define the core content of the ticket using the schema. Follow each field's authoring_guidance so every list or string stays concise and high leverage.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Consider Sequence Grouping (Optional):** When creating 4+ tickets, coordinating work across multiple agents, or organizing tickets into clear logical phases, use the optional sequence_number and sequence_description fields to group related tickets. Both fields must be provided together (e.g., sequence_number=1 with sequence_description="foundation", sequence_number=2 with sequence_description="core"). This creates organized directory structures like tickets/0_backlog/S01-foundation/{assignee}/ and tickets/0_backlog/S02-core/{assignee}/. Use lowercase single-word descriptions such as "foundation", "core", "polish", "testing", or "deployment".

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Get Current Agents:** Get the current list of agents to assign it to the most appropriate agent. Use `pantheon get team-data --actor <your_agent_name> --key agents`

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Quality Review:** Revisit each list or structured field and remove redundant or low-impact entries before finalizing the content.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-ticket --actor <your_agent_name>`.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }}. **Save the JSON:** Write the content of the ticket designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

{% set _current_step.value = _current_step.value + 1 %}
Step {{ _current_step.value }} (finish). **Execute Process:** Execute the process to create the ticket with the fully assembled <tempfile>. Use `pantheon execute create-ticket --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
