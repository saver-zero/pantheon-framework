{% if pantheon_artifact_id is not string or not pantheon_artifact_id.startswith('T') %}
{% set pantheon_artifact_id = "KOT{:03d}".format(pantheon_artifact_id|int) %}
{% endif %}
# **Ticket {{ pantheon_artifact_id }}:** {{ title }}

## Metadata

*   **Ticket ID:** {{ pantheon_artifact_id }}
*   **Assigned to:** tech-lead
*   **Priority:** P{{ priority }}
*   **Last updated:** {{ pantheon_timestamp }}
*   **Updated by:** {{ pantheon_actor }}

---

## 🎯 Objective
{{ objective }}

### **1. Additional Context**

{{ context }}

### **2. Relevant Documentation & Diagrams**
{% if relevant_documentation %}{% for doc in relevant_documentation %}
*   **[{{ doc.path }}]({{ doc.path }})**: {{ doc.relevance }}
{% endfor %}{% else %}
*   *No specific documentation was flagged as essential for this ticket.*
{% endif %}

### **3. Acceptance Criteria**
*   **As a** developer, **I want to** understand the complete application architecture including component hierarchy, state management patterns, and data flow, **so that** so that I can implement features consistently without architectural conflicts.
*   **As a** tech-lead, **I want to** review an initial set of foundational backlog with tickets covering the initial critical foundational features across phases, **so that** so that the foundation is set for further development.
*   **As a** developer, **I want to** understand the implementation sequence with clear dependencies between tickets, **so that** so that I can work efficiently without blocking on prerequisites.
{% if acceptance_criteria %}{% for ac in acceptance_criteria %}
*   **As a** {{ ac.persona }}, **I want to** {{ ac.action }}, **so that** {{ ac.benefit }}.
{% endfor %}{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
*   **As an** agent working on this task, **I want to** submit a progress log for each Phase completed, **so that** I can keep track of my progress and review it with the team.
{% endif %}
---

## Execution Plan
{% set _current_step = namespace(value = 0) %}

### Phase 1: Create the architecture guide

{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Create the architecture guide**
Based on the context and relevant documentation provided, create the architecture guide. Use `pantheon get process create-architecture-guide --actor tech-lead` and follow the step-by-step instructions given.

{% if pantheon_active_profile.draft_commit_message %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Draft a commit message**

Kickoff Ticket ID: {{ pantheon_artifact_id }}

Draft a commit message, without commiting or staging any files. Use `pantheon get process update-kickoff-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit messge is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log**

Kickoff Ticket ID: {{ pantheon_artifact_id }}

Submit a progress log. Use `pantheon get process update-kickoff-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log is submitted.

{% endif %}

### Phase 2: Create the initial backlog

{% set _current_step.value = 1 %}
**Step {{ _current_step.value }}. Identify the critical technical foundation and core MVP features**
Based on the context and relevant documentation provided, identify the critical technical foundation and core MVP features that need to be built.


{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Organize workstreams**
Orgnize the work into distinct workstreams with clear phases and sequencing.


{% set _current_step.value = _current_step.value + 1 %}
**Step {{ _current_step.value }}. Create tickets individually**
Create tickets for all workstreams and phases one by one, considering the phased workstreams and sequencing of the tickets within each workstream. Use `pantheon get process create-ticket --actor tech-lead` to create each ticket one by one. Do NOT create tickets in batch with a singel command, that is not supported.

  *Requirements:*
  - Tickets are created for all identified initial workstream and phases.

{% if pantheon_active_profile.draft_commit_message %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Draft a commit message**

Kickoff Ticket ID: {{ pantheon_artifact_id }}

Draft a commit message, without commiting or staging any files. Use `pantheon get process update-kickoff-ticket --sections commit_message --actor <your_agent_name>`. This ensures the commit message will be drafted without files being committed or staged. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Commit message is drafted using the Pantheon tool, without commiting or staging any files.

{% endif %}
{% if pantheon_active_profile.enable_progress_log %}
{% set _current_step.value = _current_step.value + 1 %}

**Step {{ _current_step.value }}. Submit a progress log**

Kickoff Ticket ID: {{ pantheon_artifact_id }}

Submit a progress log. Use `pantheon get process update-kickoff-ticket --sections progress_log --actor <your_agent_name>`. <your_agent_name> is your authentic identity executing this work. Do not simply use the ticket's "Assigned to" field unless you ARE that agent. Examples: claude-code, codex, gemini, or <agent-role-name> (i.e backend-engineer, only if explicitly instantiated as that agent).

  *Requirements:*
  - Progress log is submitted.

{% endif %}