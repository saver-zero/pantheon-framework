# Routine: create-routine

**Objective:** To design and create a complete routine.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the routine. Use `pantheon get schema create-basic-routine --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided.
    - Branch 2-1 Step 1. **Process References:** If reference material was provided, read the content of the primary reference document. Then, scan that document for any further nested references and read those as well to build a comprehensive context.
    - Branch 2-2 Step 1. **No References:** If no reference material was provided, proceed with the design based on the initial request.

Step 3. **High-Level Design:** Define the core content of the routine using the schema.

Step 4. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-basic-routine --actor <your_agent_name>`.

Step 5. **Save the JSON:** Write the content of the routine designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 6 (finish). **Execute Process:** Execute the process to create the routine with the fully assembled <tempfile>. Use `pantheon execute create-basic-routine --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
