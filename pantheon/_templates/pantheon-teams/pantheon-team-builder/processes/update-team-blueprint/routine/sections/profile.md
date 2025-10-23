Step {{ _current_step_index.num }} (branch). **Evaluate Necessity & Cost:** Perform a branch condition check. Assume the blueprint will ship with no configurable properties. Add a property only if you can point to the exact schema branch or template condition it unlocks **and** the benefit outweighs the maintenance cost (extra schema logic, template branching, operator decisions, and test paths).
    - Branch {{ _current_step_index.num }}-1 Step 1. **Continue with configuration:** If a property is justified, proceed to the next step to design the supporting structures.
    - Branch {{ _current_step_index.num }}-2 Step 1. **Compose overview-only rationale:** If no property is justified, compose a concise `profile_overview` explaining why configuration is unnecessary.
    - Branch {{ _current_step_index.num }}-2 Step 2. **Assemble overview-only JSON:** Build a JSON object that contains only the `profile_overview` field.
    - Branch {{ _current_step_index.num }}-2 Step 3. **Get tempfile:** Use `pantheon get tempfile --process update-team-blueprint --actor <your_agent_name>`.
    - Branch {{ _current_step_index.num }}-2 Step 4. **Save overview-only JSON:** Write the JSON to the tempfile.
    - Branch {{ _current_step_index.num }}-2 Step 5 (finish). **Submit overview-only configuration:** Run `pantheon execute update-team-blueprint --sections profile --from-file "<tempfile>" --id <team-blueprint id> --actor <your_agent_name>`. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Design Property Structures:** Create the `property_definitions`, `profiles`, and `default_profile` entries needed to express the justified configuration.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }}. **Compose Profile Overview:** Draft the `profile_overview` text that explains the configuration or states why none is required.
{% set _current_step_index.num = _current_step_index.num + 1 %}

Step {{ _current_step_index.num }} (branch). **Check Configuration Value:** Perform a branch condition check to confirm that the configuration provides significant user value over having no configuration.
    - Branch {{ _current_step_index.num }}-1 Step 1. **Proceed with update:** If the configuration is valuable, continue to next step.
    - Branch {{ _current_step_index.num }}-2 Step 1  **Compose overview-only rationale:** If the configuration is not valuable, compose a concise `profile_overview` explaining why configuration is unnecessary.
    - Branch {{ _current_step_index.num }}-2 Step 2. **Assemble overview-only JSON:** Build a JSON object that contains only the `profile_overview` field.
{% set _current_step_index.num = _current_step_index.num + 1 %}