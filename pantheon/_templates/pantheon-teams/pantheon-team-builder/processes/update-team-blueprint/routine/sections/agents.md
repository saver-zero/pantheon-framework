Step {{ _current_step_index.num }}. **Deconstruct the Workflow into Operator Actions:** Review the source workflow described in the blueprint's context. Identify and list the **manual actions** the human operator must perform. For each action, describe the desired outcome.
*Examples: 'Execute a batch of 3-5 tasks', 'Commit code to Git', 'Reset the context window'.*
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Identify High-Leverage Assistant Tasks:** For each operator action identified in the previous step, determine if an AI agent can assist by **preparing or updating an artifact**. Discard any assistance tasks that do not produce or modify a concrete Pantheon artifact.
*Example: To help the operator 'assign a batch of tasks', an agent can 'Prepare a plan artifact with the next task chunk'.*
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Design Agents to Perform Assistant Tasks:** Based on the assistant tasks, design a minimal set of agents. The agent's role must be to create or update an artifact for the human operator.
*Example: Instead of an 'executor' agent, create a 'planner' agent whose role is to 'Prepare the plan artifact for the operator to assign'.*
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Apply Naming Philosophy Based on Project Type:** Perform a branch condition check. Determine the appropriate naming approach for each agent based on the team's domain.
- Branch {{ _current_step_index.num }}-1 Step 1. **Non-technical/domain-specific team:** If this team serves non-technical users (e.g., travel planning, event organizing, content creation), then name agents from the user's perspective. Think: "What help does the user need?" rather than "What system function does this perform?" Use approachable, friendly terms that reflect the user's goal. Avoid architecture-focused suffixes.
- Branch {{ _current_step_index.num }}-2 Step 1. **Technical/software engineering team:** If this team is for software development or technical infrastructure, then role-based names are appropriate and clear.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Define Agent Details:** For each agent, define its `name`, `role`, `responsibilities`, `capabilities`, and `workflows`, ensuring they adhere to the schema and the Framework Guardrails in your core prompt.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Document Manual Handoffs:** For each agent, explicitly list the manual operator actions from Step 2 that it supports. This list should populate the `manual_handoffs` section for that agent.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Design Review:** Review the complete agent design.
- Confirm that no agent is named 'executor', 'coordinator', 'orchestrator', or 'monitor'.
- Verify that every agent's primary purpose is to create or update a Pantheon artifact.
- Ensure the total number of agents is within the schema limits (3-5).
{% set _current_step_index.num = _current_step_index.num + 1 %}