Step 1. **Get Schema:** Retrieve the structural contract for the {{ process_name }}. Use `pantheon get schema {{ process_name }} --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided.
  - Branch 2-1 Step 1. **Process References:** If reference material was provided, read the content of the primary reference document. Then, scan that document for any further nested references and read those as well to build a comprehensive context.
  - Branch 2-2 Step 1. **No References:** If no reference material was provided, proceed with the design based on the initial request.

Step 3. **High-Level Design:** Define the core content of {{ process_name }} using the schema. Follow each field's authoring_guidance so the routine stays concise and high leverage.

Step 4. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 5. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process {{ process_name }} --actor <your_agent_name>`.

Step 6. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 7 (finish). **Execute Process:** Execute {{ process_name }} with the fully assembled <tempfile>. Use `pantheon execute {{ process_name }} --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
