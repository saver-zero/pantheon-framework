# Routine: create-custom-routine

**Objective:** To design the core logical steps for a new custom routine.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the routine. Use `pantheon get schema create-custom-routine --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch 2-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 2-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 2-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 2-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 3. **Deconstruct the Goal into Thematic Buckets:** First, break down the routine's overall objective into 3-5 high-level thematic sections or 'buckets' of work. Analyze the target process's schema and especially its artifact content template (if available) to identify these logical groupings. For example, a `create-team-blueprint` routine might be bucketed into 'Foundation', 'Artifacts', and 'Agents'.

Step 4. **Draft a High-Level Path for Each Bucket:** For each thematic bucket, draft a single cognitive step that guides the agent on what to think about for that section. The description for this step should summarize the goal of the bucket and list the key schema fields to consider, but it should not create a separate step for each individual field.

Step 5. **Identify Decision Points:** Review the high-level path and identify any points where conditional logic is required. For each point, define the condition to be checked and the different paths that result. This is where you will design `branch` nodes. Crucially, use `branchfinishnode` only for paths that represent an early exit or failure condition (e.g., 'invalid input'). A path that successfully completes its logic should simply continue, allowing the routine to continue to the subsequent review and execution steps.

Step 6. **Assemble Core Logic:** Using the schema as a guide, formally structure the path and decision points into a valid JSON object for the `steps` array. Ensure each step is a single instruction and use `branchfinishnode` to terminate any conditional paths that should not proceed. You MUST NOT use any direct field names to make sure you stay high level.

Step 7. **Quality Review:** Revisit the generated `steps` array. Ensure the routine provides high-level cognitive guidance and is not just a mechanical checklist of schema fields. The routine should guide the *thought process*, not the data entry. Verify that the number of steps is small and focused on thematic buckets. Rewrite any steps that use direct field names or list of fields, which is a sign of a micro-checklist.

Step 8. **Compliance Check:** Review the `steps` array again to confirm it contains no setup or wrap-up steps. Specifically, verify there are no steps for 'Get Schema', 'Get Context', 'Get temp file', 'Save JSON', or 'Execute Process'. Also confirm that the final step is not a top-level `finish` node.

Step 9. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-custom-routine --actor <your_agent_name>`.

Step 10. **Save the JSON:** Write the content of the routine designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 11 (finish). **Execute Process:** Execute the process to create the routine with the fully assembled <tempfile>. Use `pantheon execute create-custom-routine --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
