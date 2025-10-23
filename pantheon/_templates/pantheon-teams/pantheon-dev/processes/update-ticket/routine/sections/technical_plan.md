{% if pantheon_active_profile.read_documentation %}
Step {{ _current_step_index.num }}. **Get the architecture guide:** Use `pantheon execute get-architecture-guide --sections system-components,implementation-patterns,shared-services --actor <your_agent_name>` to get the the relevant sections of the architecture guide.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. (branch). **Check architecture guide response:** Perform a branch condition check. Check if the pantheon command returned section content in the JSON response:
  - Branch {{ _current_step_index.num }}-1 Step 1.  **No content returned:** If the JSON response shows empty sections or placeholder text, then check for additional documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
  - Branch {{ _current_step_index.num }}-1 Step 2. **Understand the Documentation Structure:** Leverage any README or INDEX files, the directory structure, and file names to understand the overall documentation structure.
  - Branch {{ _current_step_index.num }}-1 Step 3. **Read Existing Documentation:** Identify and read relevant documetations to build context. Make sure to read any architecture pattern or design principles doc.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Content returned:** If the JSON response contains section content (non-empty markdown text in the section fields), then use that content directly and continue to the next step.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% endif %}
Step {{ _current_step_index.num }}. **Analyze Foundation Infrastructure:** Systematically examine the existing codebase to understand current infrastructure and identify reusable components, focusing on modules, libraries, and architectural patterns relevant to the implementation.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% if pantheon_active_profile.enforce_tdd %}
{% if pantheon_active_profile.read_documentation %}

Step {{ _current_step_index.num }}. **Get the testing strategy:** Use `pantheon execute get-architecture-guide --sections testing-strategy --actor <your_agent_name>` to get the the testing strategy section.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. (branch). **Check testing strategy response:** Perform a branch condition check. Check if the pantheon command returned testing strategy content in the JSON response:
  - Branch {{ _current_step_index.num }}-1 Step 1.  **No content returned:** If the JSON response shows empty sections or placeholder text, then check for additional documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
  - Branch {{ _current_step_index.num }}-1 Step 2. **Understand the Documentation Structure:** Leverage any README or INDEX files, the directory structure, and file names to understand the overall documentation structure.
  - Branch {{ _current_step_index.num }}-1 Step 3. **Read Existing Documentation:** Identify and read documentation related to testing to build context.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Content returned:** If the JSON response contains testing strategy content (non-empty markdown text in the section fields), then use that content directly and continue to the next step.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% endif %} {# pantheon_active_profile.read_documentation #}
Step {{ _current_step_index.num }}. **Review Test Infrastructure:** Examine existing test files, fixtures, and framework setup to understand established patterns and reusable components before designing new tests.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Design Core Behavior Tests:** Identify essential behaviors to validate and plan validation approaches that align with existing test patterns, focusing on meaningful functionality and pragmatic cases.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Plan Test Implementation Strategy:** Determine which existing test components can be reused and justify any new components needed, ensuring maximum leverage of established infrastructure.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}

Step {{ _current_step_index.num }}. **Design High-Level Implementation Strategy:** Synthesize analysis findings into a coherent technical approach that explains the overall strategy, identifies key modules to modify or create, and justifies any proposed new libraries based on thorough codebase understanding.
{% set _current_step_index.num = _current_step_index.num + 1 %}

{% set _phases_to_skip = [] %}
{% set _skip_phases = "" %}
{% if pantheon_active_profile.enforce_tdd %}
    {% set _phases_to_skip = _phases_to_skip + ["testing"] %}
{% endif %}
{% if pantheon_active_profile.update_documentation %}
    {% set _phases_to_skip = _phases_to_skip + ["documentation"] %}
{% endif %}
{% if pantheon_active_profile.update_diagram %}
    {% set _phases_to_skip = _phases_to_skip + ["diagram"] %}
{% endif %}
{% if _phases_to_skip %}
    {% set _skip_phases = " Do NOT add a separate dedicated phases for " + _phases_to_skip|join(", ") + " -- a dedicated phase will automatically created by the template." %}
{% endif %}
Step {{ _current_step_index.num }}. (branch). **Assess Implementation Complexity:** Perform a branch condition check. Evaluate the implementation scope using these criteria: (1) Number of distinct modules/components affected (simple: 1-2, complex: 3+), (2) Type of changes required (simple: modifications to existing code, complex: new architectural patterns or cross-cutting changes), (3) Dependencies and integration points (simple: isolated changes, complex: multiple integration points or external dependencies). Determine whether this is a simple or complex implementation:
  - Branch {{ _current_step_index.num }}-1 Step 1. **Simple Implementation:** If the implementation affects 1-2 modules with isolated modifications to existing code, create a minimal execution plan with 1-2 broad phases that group related activities together. Each phase should represent a complete functional unit (e.g., "Core Implementation" covering all code changes). Avoid creating separate phases for naturally sequential activities.{{ _skip_phases }}
  - Branch {{ _current_step_index.num }}-2 Step 1. **Complex Implementation:** If the implementation affects 3+ modules, introduces new architectural patterns, or has multiple integration points, create a structured execution plan with appropriately-scoped phases. Each phase should represent a significant, self-contained milestone that delivers measurable progress (e.g., "Database Layer Implementation", "API Integration", "Frontend Components"). Avoid granular phases that represent individual tasks within a milestone (anti-pattern: separate phases for "Write Model", "Write Repository", "Write Service" when these are sequential steps within database layer work). Aim for 3-5 phases that represent major functional boundaries.{{ _skip_phases }}
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% if pantheon_active_profile.update_documentation %}

Step {{ _current_step_index.num }}. **Get the documentation standards:** Use `pantheon execute get-architecture-guide --sections documentation-standards --actor <your_agent_name>` to get the the documentation standards section.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. (branch). **Check documentation standards response:** Perform a branch condition check. Check if the pantheon command returned documentation standards content in the JSON response:
  - Branch {{ _current_step_index.num }}-1 Step 1.  **No content returned:** If the JSON response shows empty sections or placeholder text, then skip to the next step.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Content returned:** If the JSON response contains documentation standards content (non-empty markdown text in the section fields), then use that content directly and continue to the next step.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get Existing Documentation Path:** Get existing documentation path. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Identify Existing Documentation:**  Based on the README or INDEX file in the documentation path, the directory names, and file names, identify relevant existing documentation. 
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Determine whether to update or create:** Determine whether to update an existing documentation or to create a new one.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Plan Documentation Strategy:** Review current documentation state and plan comprehensive updates that align with implementation changes, ensuring documentation remains current and accurate.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}
{% if pantheon_active_profile.update_diagram %}
{% if not pantheon_active_profile.update_documentation %}

Step {{ _current_step_index.num }}. **Get the documentation standards:** Use `pantheon execute get-architecture-guide --sections documentation-standards --actor <your_agent_name>` to get the the documentation standards section.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. (branch). **Check documentation standards response:** Perform a branch condition check. Check if the pantheon command returned documentation standards content in the JSON response:
  - Branch {{ _current_step_index.num }}-1 Step 1.  **No content returned:** If the JSON response shows empty sections or placeholder text, then skip to the next step.
  - Branch {{ _current_step_index.num }}-2 Step 1. **Content returned:** If the JSON response contains documentation standards content (non-empty markdown text in the section fields), then use that content directly and continue to the next step.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Get Existing Documentation Path:** Get existing documentation path. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}

Step {{ _current_step_index.num }}. **Identify Existing Diagram:** Based on the README or INDEX file in the documentation path, the directory names, and file names, identify relevant existing Diagram. 
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Determine whether to update or create:** Determine whether to update an existing Diagram or to create a new one.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Plan Diagram Strategy:** Review current diagrams and plan comprehensive updates that reflect implementation changes, ensuring visual documentation remains current and accurate.
{% set _current_step_index.num = _current_step_index.num + 1 %}
{% endif %}

Step {{ _current_step_index.num }}. **Validate Plan Comprehensiveness:** Review the complete technical plan to ensure it provides systematic step-by-step guidance, builds upon existing infrastructure, and delivers a comprehensive implementation strategy that minimizes risk.
{% set _current_step_index.num = _current_step_index.num + 1 %}
