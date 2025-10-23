<!-- SECTION:START:ROUTINE -->
# Routine: create-team-profile

**Objective:** To design and create a complete team profile defining a Pantheon AI team's identity, capabilities, and configuration.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the create-team-profile. Use `pantheon get schema create-team-profile --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch 2-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 2-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 2-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 2-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 3. **High-Level Design:** Define the core content of create-team-profile using the schema.

Step 4. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-team-profile --actor <your_agent_name>`.

Step 5. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 6 (finish). **Execute Process:** Execute create-team-profile with the fully assembled <tempfile>. Use `pantheon execute create-team-profile --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
<!-- SECTION:END:ROUTINE -->
