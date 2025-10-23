# Routine: create-agent

**Objective:** To design and create a complete agent.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the create-agent. Use `pantheon get schema create-agent --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch 2-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 2-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 2-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 2-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 3. **Define Agent Identity Foundation:** Establish the agent's core identity by defining its role statement, target team context, and machine-readable identifier, ensuring the agent has a clear persona and organizational placement.

Step 4 (branch). **Validate Agent Naming Approach:** Perform a branch condition check. Determine the appropriate naming philosophy based on the agent's domain and audience.
  - Branch 4-1 Step 1. **Non-technical/domain-specific agent:** If this agent serves non-technical users or domain-specific tasks (e.g., travel planning, content creation, event organizing), then ensure the agent name reflects what help the user needs. Think from the user's perspective: "What problem am I trying to solve?" rather than "What technical function does this perform?" Use approachable, friendly terms.
  - Branch 4-2 Step 1. **Technical/software engineering agent:** If this agent performs technical software development or infrastructure work, then role-based names are clear and appropriate.

Step 5. **Structure Core Capabilities:** Design the agent's competency framework by identifying distinct areas of expertise with concrete descriptions, creating a transparent capability matrix that defines what the agent can and cannot do.

Step 6. **Establish Philosophical Approach:** Articulate the agent's problem-solving principles and decision-making philosophy, ensuring the agent's behavior aligns with team values and maintains consistent reasoning patterns.

Step 7 (branch). **Technical Context Requirements:** Perform a branch condition check. Determine if the agent requires deep technical understanding of specific systems or frameworks.:
  - Branch 7-1 Step 1. **Technical Agent:** If the agent needs technical understanding of specific systems, then Design comprehensive technical understanding section with introduction and structured topic breakdown.
  - Branch 7-1 Step 2. **Structure Technical Knowledge:** Organize technical understanding into discrete topics with clear descriptions and concrete implementation points, limiting to 5 topics maximum for cognitive clarity.
  - Branch 7-2 Step 1. **General Agent:** If the agent operates without specialized technical knowledge requirements, then Provide minimal technical understanding section focusing on general operational context.

Step 8 (branch). **Pantheon CLI usage:** Perform a branch condition check. Determine if the agent need to create or update Pantheon artifacts using Pantheon CLI commands:
  - Branch 8-1 Step 1. **Pantheon CLI used:** If the agent needs to create or update Pantheon artifacts using Panthoen CLI commads, then leverage the provided references and remember the Pantheon commands associated with each artifact.
  - Branch 8-1 Step 2. **Design Workflow Framework:** Create structured workflows that follow the mandatory two-step RAE pattern (Get Instructions, Follow Instructions), ensuring each workflow has clear triggers and Pantheon CLI Command references. Make sure CREATE workflows have corresponding UPDATE workflows.
  - Branch 8-2 Step 1. **Pantheon CLI is not used:** If the agent operates without Pantheon CLI commands, then skip the workflow design.

Step 9. **Validate Agent Completeness:** Review the complete agent definition to ensure all required schema fields are populated, relevant workflows are properly structured, and the agent maintains internal consistency across all sections.

Step 10. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content. Double check CREATE workflows have corresponding UPDATE workflows.

Step 11. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-agent --actor <your_agent_name>`.

Step 12. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 13 (finish). **Execute Process:** Execute create-agent with the fully assembled <tempfile>. Use `pantheon execute create-agent --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.