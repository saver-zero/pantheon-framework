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

Step 3. **Get Current Agents:** Get the current list of agents to prevent redundant agents with similar roles. Use `pantheon get team-data --actor <your_agent_name> --key agents`

Step 4 (branch). **Check if additional agents are needed:** Perform a branch condition check. Determine if additional agents are needed beyond the current list of agents:
  - Branch 4-1 Step 1. **Additional agents are need:** If additional agents are needed, continue to the next step.
  - Branch 4-2 Step 1 (finish). **Additional agents are not needed:** If additional agents are not needed, then report back the rationale on why additional agents are not needed based on the currenst list of agents. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.

Step 5. **Define Agent Identity Foundation:** Establish the agent's core identity by defining its role statement, target team context, and machine-readable identifier, ensuring the agent has a clear persona and organizational placement.

Step 6. **Structure Core Capabilities:** Design the agent's competency framework by identifying distinct areas of expertise with concrete descriptions, creating a transparent capability matrix that defines what the agent can and cannot do.

Step 7. **Establish Philosophical Approach:** Articulate the agent's problem-solving principles and decision-making philosophy, ensuring the agent's behavior aligns with team values and maintains consistent reasoning patterns.

Step 8 (branch). **Technical Context Requirements:** Perform a branch condition check. Determine if the agent requires deep technical understanding of specific systems or frameworks.:
  - Branch 8-1 Step 1. **Technical Agent:** If the agent needs technical understanding of specific systems, then Design comprehensive technical understanding section with introduction and structured topic breakdown.
  - Branch 8-1 Step 2. **Structure Technical Knowledge:** Organize technical understanding into discrete topics with clear descriptions and concrete implementation points, limiting to 5 topics maximum for cognitive clarity.
  - Branch 8-2 Step 1. **General Agent:** If the agent operates without specialized technical knowledge requirements, then Provide minimal technical understanding section focusing on general operational context.

Step 9. **Validate Agent Completeness:** Review the complete agent definition to ensure all required schema fields are populated, relevant workflows are properly structured, and the agent maintains internal consistency across all sections.

Step 10 **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 11. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-agent --actor <your_agent_name>`.

Step 12. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 13. **Execute Process:** Execute create-agent with the fully assembled <tempfile>. Use `pantheon execute create-agent --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.

Step 14 (branch). **Check create-agent CLI result:** Perform a branch condition check. Check the create-agent CLI result message:
  - Branch 14-1 Step 1. **create-agent was successful:** If the CLI returned a successful message for create-agent, then update the team data to add the created agent. Use `pantheon set team-data --actor <your_agent_name> --set agents.<agent_name>="<agent_description>"`
  - Branch 14-2 Step 1. **create-agent was NOT successful:** If the CLI did not return a successful message for create-agent, then continue to the next step.
  
Step 15 (finish). **Finish:** You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine. Report the CLI results to the user.