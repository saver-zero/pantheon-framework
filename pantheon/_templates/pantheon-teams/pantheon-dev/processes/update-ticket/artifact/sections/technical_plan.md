## Technical Implementation Plan

**Plan Updated**: {{ pantheon_timestamp }}

**Created By**: @{{ pantheon_actor }}

### **Technical Summary**

*   **Relevant Code Analyzed**:
    {% if technical_summary.relevant_code_analyzed %}
    {% for code in technical_summary.relevant_code_analyzed %}
    *   `{{ code.path }}`: {{ code.relevance }}
    {% endfor %}
    {% else %}
    *   *No existing code was analyzed for this plan.*
    {% endif %}

*   **Proposed Libraries**:
    {% if technical_summary.proposed_libraries %}
    {% for lib in technical_summary.proposed_libraries %}
    *   `{{ lib.name }}`: {{ lib.rationale }}
    {% endfor %}
    {% else %}
    *   *No new libraries are proposed.*
    {% endif %}

*   **Key Modules to be Modified/Created**:
    {% if technical_summary.key_modules_impacted %}
    {% for mod in technical_summary.key_modules_impacted %}
    *   `{{ mod.path }}`: {{ mod.purpose }}
    {% endfor %}
    {% else %}
    *   *No key modules identified.*
    {% endif %}

---

### **High-Level Approach**

{{ high_level_approach }}

---

### **Implementation Phase**

#### **Primary Objective: Follow the Plan with Strict Fidelity**

The most important directive is to execute this plan exactly as written. Adherence to the prescribed plan and process is more critical than the speed of completion.

Do not skip, combine, or reorder any phase or step. Each one is mandatory and serves a specific purpose in ensuring a high-quality, transparent, and verifiable outcome.
* Sequential Execution: All steps within a phase must be completed before proceeding to the next.

The deliverable is not just the functioning software. It is the  complete, documented, and auditable record of the development process itself, created for human review by following every step with precision.

Always use `pantheon` command directly, never use `python -m pantheon`, it will NOT work.

{% set _current_phase = namespace(value = 0) %}
{% set _current_step = namespace(value = 0) %}
{% if pantheon_active_profile.perform_code_review %}
{% set _current_phase.value = _current_phase.value + 1 %}
#### Phase {{ _current_phase.value }}: Store current baseline commit info.

Ticket ID: {{ pantheon_artifact_id }}

Use `pantheon get process update-ticket --sections baseline_commit --actor <your_agent_name>` and follow the instruction to set the baseline commit for code review later. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

{% endif %}
{% if testing_phase %}
{% set _current_phase.value = _current_phase.value + 1 %}
#### Phase {{ _current_phase.value }}: Test-Driven Development

{{ testing_phase.implementation_constraints }}

{% if pantheon_active_profile.read_documentation %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Get the testing strategy:** Use `pantheon execute get-architecture-guide --sections testing-strategy --actor <your_agent_name>` to get the the testing strategy.


{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. (branch). Check testing strategy:** Perform a branch condition check. Check if testing strategy exists with content:
  - Branch {{ _current_step.value }}-1 Step 1. **Testing strategy exists:** If testing strategy exists with content, then read the content and continue to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **Testing strategy does not exist:** If testing strategy does not exist or has empty content, then check for additional documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>` to get the documentation directory.
  - Branch {{ _current_step.value }}-2 Step 2. **Understand the Documentation Structure:** Leverage any README or INDEX files and the directory structure to understand the overall documentation structure.
  - Branch {{ _current_step.value }}-2 Step 3. **Read Existing Documentation:** Identify and read documentation related to testing to build context.

{% endif %} {# pantheon_active_profile.read_documentation #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Review existing test patterns**
  {% if testing_phase.testing_context_analysis.test_files_reviewed %}

Examine current testing patterns and conventions:
  {% for test_file in testing_phase.testing_context_analysis.test_files_reviewed %} {# test files loop #}
  - `{{ test_file.path }}`: {{ test_file.patterns_observed }}
  {% endfor %} {# end test files loop #}
  {% endif %}
  {% if testing_phase.testing_context_analysis.testing_documentation_reviewed %}
  {% for doc in testing_phase.testing_context_analysis.testing_documentation_reviewed %} {# test docs loop #}
  - `{{ doc.document_path }}`: {{ doc.key_insights }}
  {% endfor %} {# end test docs loop #}
  {% endif %}

  *Requirements:*
  - Understanding of {{ testing_phase.testing_context_analysis.testing_framework_setup }}
  - Knowledge of {{ testing_phase.testing_context_analysis.fixture_and_mock_patterns }}

{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Set up test infrastructure**
  {% if testing_phase.test_implementation_plan.reusable_components %}

Leverage existing components:
  {% for component in testing_phase.test_implementation_plan.reusable_components %} {# reusable components loop #}
  - {{ component }}
  {% endfor %} {# end reusable components loop #}
  {% endif %}
  {% if testing_phase.test_implementation_plan.new_components_needed %}

Create new components as needed:
  {% for new_comp in testing_phase.test_implementation_plan.new_components_needed %} {# new components loop #}
  - {{ new_comp.component }}: {{ new_comp.justification }}
  {% endfor %} {# end new components loop #}
  {% endif %}

  *Requirements:*
  - Test fixtures and mocks are properly configured

{% for behavior in testing_phase.core_behaviors %} {# core behaviors loop #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Write tests for: {{ behavior.behavior }}**

{{ behavior.validation_approach }}
  {% if behavior.similar_existing_test %}

  *Reference:* {{ behavior.similar_existing_test }}
  {% endif %}

  *Requirements:*
  - Tests written as if working implementation exists
  - Tests fail naturally due to missing implementation, not artificial failures
  - Test validates the specific behavior clearly
  - To not skip tests or mark them for skipping.

{% endfor %} {# end core behaviors loop #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Verify tests fail**

Run the tests and verify the tests fail as expected.

  *Requirements:*
  - Tests are run
  - Newly written tests fail naturally due to missing implementation, not artificial failures

{% if pantheon_active_profile.lint_tools %}
{#
  <!-- To add lint tools, update the team-profile.yaml file.

  Example:
    profiles:
      standard:
        lint_tools:
          - "ruff check --fix"
          - "ruff format"
      production:
        lint_tools:
          - "ruff check --fix"
          - "ruff format"
          - "mypy --strict"
  -->
#}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Run lint**

After implementation, run the lint tools to check for lint errors and formatting issues, and fix any lint errors. Use:
{% for lint_tool in pantheon_active_profile.lint_tools %} {# lint tools loop #}
- {{ lint_tool }}
{% endfor %} {# end lint tools loop #}

  *Requirements:*
  - No lint errors exist.

{% endif %}
{% if pantheon_active_profile.draft_commit_message %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Draft a commit message**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, draft a commit message, without commiting or staging any files. Use `pantheon get process update-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit messge for Phase {{ _current_phase.value }} is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, submit a progress log. Use `pantheon get process update-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log for Phase {{ _current_phase.value }} is submitted.

{% endif %}
{% if pantheon_active_profile.auto_commit_each_phase %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Add and commit the changes**

Add and commit all changes from Phase {{ _current_phase.value }} using `git add .` (to ensure no uncommited changes) and `git commit`. Use {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

  *Requirements:*
  - Phase {{ _current_phase.value }} changes are committed using {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

{% endif %}

---

{% endif %}{# end testing_phase block #}
{% for phase in phases %} {# main phases loop #}
{% set _current_phase.value = _current_phase.value + 1 %}
{% set _current_step.value = 0 %}
#### Phase {{ _current_phase.value }}: {{ phase.name }}

{{ phase.description }}{% if pantheon_active_profile.enable_progress_log %} And submit a progress log upon Phase {{ _current_phase.value }} completion.{% endif %}

{% for step in phase.steps %} {# phase steps loop #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. {{ step.action }}**
{% if step.description %}

{{ step.description }}
{% endif %}
  {% if step.requirements %}

  *Requirements:*
  {% for req in step.requirements %} {# step requirements loop #}
  - {{ req }}
  {% endfor %} {# end step requirements loop #}
  {% endif %}
  {% if step.methodology %}

  *Methodology:* {{ step.methodology }}
  {% endif %}

{% endfor %} {# end phase steps loop #}
{% if pantheon_active_profile.lint_tools %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Run lint**

After implementation, run the lint tools to check for lint errors and formatting issues, and fix any lint errors. Use:
{% for lint_tool in pantheon_active_profile.lint_tools %} {# lint tools loop #}
- {{ lint_tool }}
{% endfor %} {# end lint tools loop #}

  *Requirements:*
  - No lint errors exist.

{% endif %}
{% if pantheon_active_profile.draft_commit_message %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Draft a commit message**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, draft a commit message, without commiting or staging any files. Use `pantheon get process update-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit messge for Phase {{ _current_phase.value }} is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, submit a progress log. Use `pantheon get process update-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log for Phase {{ _current_phase.value }} is submitted.

{% endif %}
{% if pantheon_active_profile.auto_commit_each_phase %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Add and commit the changes**

Add and commit all changes from Phase {{ _current_phase.value }} using `git add .` (to ensure no uncommited changes) and `git commit`. Use {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

  *Requirements:*
  - Phase {{ _current_phase.value }} changes are committed using {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

{% endif %}

---

{% endfor %} {# end main phases loop #}
{% if testing_phase or pantheon_active_profile.run_and_fix_tests %}
{% set _current_phase.value = _current_phase.value + 1 %}
{% set _current_step.value = 0 %}
#### Phase {{ _current_phase.value }}: Test Run and Verification

Run all tests to verify there are no regressions and all new tests pass.{% if pantheon_active_profile.enable_progress_log %} And submit a progress log upon Phase {{ _current_phase.value }} completion.{% endif %}

{% set _current_step.value = _current_step.value + 1 %}
{% set _unit_test_step = _current_step.value %}

**Step {{ _current_step.value }}. Run all unit tests:** Execute the unit test suite to validate implementation correctness and check for regression.

  *Requirements:*
  - All unit tests execute without errors
  - Test output is captured for analysis

{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }} (branch). Evaluate unit test results:** Perform a branch condition check. Determine if all unit tests passed:
  - Branch {{ _current_step.value }}-1 Step 1. **Continue to integration tests:** If all unit tests pass, then continue to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **Analyze failure:** If any unit tests fail, then examine the failure output to identify the specific test failure, error message, and stack trace.
  - Branch {{ _current_step.value }}-2 Step 2. **Determine fix type:** Assess whether the failure indicates a code bug requiring implementation changes, or a test requiring updates based on new requirements from this ticket.
  - Branch {{ _current_step.value }}-2 Step 3. **Apply correction:** Make the necessary code or test changes to address the identified issue, following existing code patterns and test conventions.
  - Branch {{ _current_step.value }}-2 Step 4. **Return to Step {{ _unit_test_step }}:** Re-run unit tests from Step {{ _unit_test_step }} to verify the fix and check for additional failures.

{% set _current_step.value = _current_step.value + 1 %}
{% set _integration_test_step = _current_step.value %}
**Step {{ _current_step.value }}. (branch). Check for integration tests:** Perform a branch condition check. Check if integration tests are available.
  - Branch {{ _current_step.value }}-1 Step 1. **Run the integration tests:** If integration tests exist, then execute the integration test suite to validate component interactions.
  - Branch {{ _current_step.value }}-2 Step 1. **No integration tests:** If there are no existing integration tests available, continue to the next step.

{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }} (branch). Evaluate integration test results:** Perform a branch condition check. Determine if all integration tests passed:
  - Branch {{ _current_step.value }}-1 Step 1. **All integration tests pass:** If all integration tests pass, then proceed to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **No integration tests:** If there were no integration tests available to run, then continue to the next step.
  - Branch {{ _current_step.value }}-3 Step 1. **Analyze failure:** If any integration tests fail, then examine the failure output to identify the specific test failure, error message, and stack trace.
  - Branch {{ _current_step.value }}-3 Step 2. **Determine fix type:** Assess whether the failure indicates a code bug requiring implementation changes, or a test requiring updates based on new requirements from this ticket.
  - Branch {{ _current_step.value }}-3 Step 3. **Apply correction:** Make the necessary code or test changes to address the identified issue, following existing code patterns and test conventions.
  - Branch {{ _current_step.value }}-3 Step 4. **Return to Step {{ _integration_test_step }}:** Re-run integration tests from Step {{ _integration_test_step }} to verify the fix and check for additional failures.

{% set _current_step.value = _current_step.value + 1 %}
{% set _remaining_test_step = _current_step.value %}
**Step {{ _current_step.value }}. (branch). Check for other tests:** Perform a branch condition check. Check if other test types are available (e.g., end-to-end, acceptance).
  - Branch {{ _current_step.value }}-1 Step 1. **Run the remaining tests:** If other tests exist, then execute the other remaining tests for complete validation.
  - Branch {{ _current_step.value }}-2 Step 1. **No integration tests:** If there are no other tests available, continue to the next step.

**Step {{ _current_step.value }} (branch). Evaluate remaining test results:** Perform a branch condition check. Determine if all remaining tests passed:
  - Branch {{ _current_step.value }}-1 Step 1. **All remaining tests pass:** If all remaining tests pass, then proceed to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **No remaining tests:** If there were no remaining tests available to run, then continue to the next step.
  - Branch {{ _current_step.value }}-3 Step 1. **Analyze failure:** If any remaining tests fail, then examine the failure output to identify the specific test failure, error message, and stack trace.
  - Branch {{ _current_step.value }}-3 Step 2. **Determine fix type:** Assess whether the failure indicates a code bug requiring implementation changes, or a test requiring updates based on new requirements from this ticket.
  - Branch {{ _current_step.value }}-3 Step 3. **Apply correction:** Make the necessary code or test changes to address the identified issue, following existing code patterns and test conventions.
  - Branch {{ _current_step.value }}-3 Step 4. **Return to Step {{ _remaining_test_step }}:** Re-run remaining tests from Step {{ _remaining_test_step }} to verify the fix and check for additional failures.

{% if pantheon_active_profile.lint_tools %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Run lint**

Execute linting tools to check for code quality issues and formatting errors. Use:
{% for lint_tool in pantheon_active_profile.lint_tools %} {# lint tools loop #}
- {{ lint_tool }}
{% endfor %} {# end lint tools loop #}

  *Requirements:*
  - No lint errors exist
  - All auto-fixable issues are resolved

{% endif %}
{% if pantheon_active_profile.draft_commit_message %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Draft a commit message**

Ticket ID: {{ pantheon_artifact_id }}

If any updates were made to fix any failing tests during Phase {{ _current_phase.value }}, draft a commit message, without commiting or staging any files. Use `pantheon get process update-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - If no fixes were made, commit message is not drafted.
  - If fixes were made, commit messge for Phase {{ _current_phase.value }} is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log:**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, submit a progress log. Use `pantheon get process update-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log for Phase {{ _current_phase.value }} is submitted.

{% endif %}
{% if pantheon_active_profile.auto_commit_each_phase %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Add and commit the changes**

If any updates were made to fix any failing tests during Phase {{ _current_phase.value }}, add and commit all changes from Phase {{ _current_phase.value }} using `git add .` (to ensure no uncommited changes) and `git commit`. Use {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

  *Requirements:*
  - If no fixes were made in Phase {{ _current_phase.value }}, nothing is added or commited as there weren't any changes.
  - If fixes were made in Phase {{ _current_phase.value }}, Phase {{ _current_phase.value }} changes are committed using {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

{% endif %}

---

{% endif %} {# end if testing_phase #}
{% if documentation_phase %}
{% set _current_phase.value = _current_phase.value + 1 %}
{% set _current_step.value = 0 %}
#### Phase {{ _current_phase.value }}: Documentation Update

{{ documentation_phase.update_summary }} {% if pantheon_active_profile.enable_progress_log %} And submit a progress log upon Phase {{ _current_phase.value }} completion.{% endif %}


**Existing Documentation**

{% for doc in documentation_phase.existing_docs_analyzed %} {# existing docs loop #}
- **{{ doc.file_path }}**: {{ doc.current_status }}
{% endfor %} {# end existing docs loop #}

{% if documentation_phase.docs_needing_updates %}
{% if pantheon_active_profile.read_documentation %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Get the documentation standards:** Use `pantheon execute get-architecture-guide --sections documentation-standards --actor <your_agent_name>` to get the the documentation standards.


{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. (branch). Check documentation standards:** Perform a branch condition check. Check if documentation standards exists with content:
  - Branch {{ _current_step.value }}-1 Step 1. **Documentation standards exists:** If documentation standards exists with content, then read the content and continue to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **Documentation standards does not exist:** If documentation standards does not exist or has empty content, continue to the next steps without looking for further documentation standards.

{% endif %} {# pantheon_active_profile.read_documentation #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Update Documentation**

{% for doc in documentation_phase.docs_needing_updates %} {# docs updates loop #}
- **{{ doc.file_path }}**: {{ doc.changes_needed }}

{% endfor %} {# end docs updates loop #}
{% endif %}

{% if documentation_phase.new_docs_needed %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Create New Documentation**
{% for doc in documentation_phase.new_docs_needed %} {# new docs loop #}
- **{{ doc.file_path }}**: {{ doc.purpose }}
  > {{ doc.content_outline }}

{% endfor %} {# end new docs loop #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Update README**
Use `pantheon get team-data --key path.docs --actor <your_agent_name>` and update the README file in the docs directory to add a reference to the new docs created.

{% endif %}
{% if pantheon_active_profile.draft_commit_message and (documentation_phase.docs_needing_updates or documentation_phase.new_docs_needed) %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Draft a commit message**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, draft a commit message, without commiting or staging any files. Use `pantheon get process update-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit messge for Phase {{ _current_phase.value }} is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log and (documentation_phase.docs_needing_updates or documentation_phase.new_docs_needed) %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log:**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, submit a progress log. Use `pantheon get process update-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log for Phase {{ _current_phase.value }} is submitted.

{% endif %}
{% if pantheon_active_profile.auto_commit_each_phase %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Add and commit the changes**

Add and commit all changes from Phase {{ _current_phase.value }} using `git add .` (to ensure no uncommited changes) and `git commit`. Use {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

  *Requirements:*
  - Phase {{ _current_phase.value }} changes are committed using {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

{% endif %}

---

{% endif %} {# end if documentation_phase #}
{% if diagram_phase %}
{% set _current_phase.value = _current_phase.value + 1 %}
{% set _current_step.value = 0 %}
#### Phase {{ _current_phase.value }}: Diagram Update

{{ diagram_phase.update_summary }}{% if pantheon_active_profile.enable_progress_log %} And submit a progress log upon Phase {{ _current_phase.value }} completion.{% endif %}


**Existing Diagrams:**

{% for diagram in diagram_phase.existing_diagrams_analyzed %} {# existing diagrams loop #}
- **{{ diagram.diagram_path }}**: {{ diagram.current_accuracy }}
{% endfor %} {# end existing diagrams loop #}

{% if diagram_phase.diagrams_needing_updates %}
{% if pantheon_active_profile.read_documentation %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Get the diagramming standards:** Use `pantheon execute get-architecture-guide --sections diagramming-standards --actor <your_agent_name>` to get the the diagramming standards.


{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. (branch). Check diagramming standards:** Perform a branch condition check. Check if diagramming standards exists with content:
  - Branch {{ _current_step.value }}-1 Step 1. **Diagramming standards exists:** If diagramming standards exists with content, then read the content and continue to the next step.
  - Branch {{ _current_step.value }}-2 Step 1. **Diagramming standards does not exist:** If diagramming standards does not exist or has empty content, continue to the next steps without looking for further diagramming standards.

{% endif %} {# pantheon_active_profile.read_documentation #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Update Diagrams**
{% for diagram in diagram_phase.diagrams_needing_updates %} {# diagram updates loop #}
- **{{ diagram.diagram_path }}** ({{ diagram.diagram_type }}): {{ diagram.changes_needed }}
{% endfor %} {# end diagram updates loop #}
{% endif %}

{% if diagram_phase.new_diagrams_needed %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Create New Diagrams**
{% for diagram in diagram_phase.new_diagrams_needed %} {# new diagrams loop #}
- **{{ diagram.diagram_path }}** ({{ diagram.diagram_type }}): {{ diagram.purpose }}
  > {{ diagram.content_outline }}
{% endfor %} {# end new diagrams loop #}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Update README**
Use `pantheon get team-data --key path.docs --actor <your_agent_name>` and update the README file in the docs directory to add a reference to the new diagrams created.

{% endif %}

{% if pantheon_active_profile.draft_commit_message and (diagram_phase.diagrams_needing_updates or diagram_phase.new_diagrams_needed) %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Draft a commit message**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, draft a commit message, without commiting or staging any files. Use `pantheon get process update-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit messge for Phase {{ _current_phase.value }} is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log and (diagram_phase.diagrams_needing_updates or diagram_phase.new_diagrams_needed) %}
{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Submit a progress log:**

Ticket ID: {{ pantheon_artifact_id }}

After Phase {{ _current_phase.value }} is completed, submit a progress log. Use `pantheon get process update-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log for Phase {{ _current_phase.value }} is submitted.

{% endif %}
{% if pantheon_active_profile.auto_commit_each_phase %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Add and commit the changes**

Add and commit all changes from Phase {{ _current_phase.value }} using `git add .` (to ensure no uncommited changes) and `git commit`. Use {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

  *Requirements:*
  - Phase {{ _current_phase.value }} changes are committed using {{ 'the commit message drafted' if pantheon_active_profile.draft_commit_message else 'a descriptive commit message' }}.

{% endif %}

---

{% endif %} {# end if diagram_phase #}