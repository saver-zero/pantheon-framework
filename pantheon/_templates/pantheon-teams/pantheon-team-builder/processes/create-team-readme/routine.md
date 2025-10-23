---
created_at: 2025-09-22 HH:MM PM PDT
---
<!-- SECTION:START:OBJECTIVE -->
# Routine: create-team-readme

**Objective:** To generate comprehensive team README documentation that effectively onboards users to AI team capabilities and workflows.

**Process Type:** create

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---
<!-- SECTION:END:OBJECTIVE -->

<!-- SECTION:START:STEPS -->

Step 1. **Get Schema:** Retrieve the structural contract for the create-team-readme. Use `pantheon get schema create-team-readme --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch 2-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 2-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 2-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 2-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 3 (branch). **Analyze Context:** Perform a branch condition check. Check if additional context material (team documentation, existing processes, or reference materials) was provided to inform the README content.:
  - Branch 3-1 Step 1. **Process References:** If reference material was provided, then Read and analyze all provided reference materials to extract team-specific context, existing processes, and established patterns.
  - Branch 3-1 Step 2. **Extract Key Insights:** Identify the team's unique characteristics, established workflows, and specific language or terminology used by the team from the reference materials.
  - Branch 3-2 Step 1. **Use Base Context:** If no reference material was provided, then Proceed with README design using only the initial request context and schema guidance.

Step 4. **Understand artifacts and commands:** Understand the artifacts and available Pantheon commands for the team from the given context and references. Think about how the agents will use the commands for the artifacts, and also think about the natural language the user will have to use to instruct the agents. For example, the user will need to say "update ticket T123 with your implementation plan", or "create an architecture guide". Create commands don't need an ID but update commands need an artifact id or the artifact file path.

Step 5. **Design Team Foundation:** Craft the core team identity elements including mission statement, value proposition, key capabilities list, and use case scenarios, ensuring each element follows the schema's authoring guidance for clarity and conciseness.

Step 6. **Structure Agent Interaction Model:** Define how humans work with agents by articulating the human role and communication best practices that guide effective collaboration.

Step 7. **Document Agent Roster:** Create comprehensive profiles for each team agent including their expertise, when to engage them, interaction guides, and deliverables, ensuring each profile provides actionable guidance for users.

Step 8 (branch). **Validate Agent Coverage:** Perform a branch condition check. Verify that the agent roster comprehensively covers the team's stated capabilities and that each capability maps to specific agents.:
  - Branch 8-1 Step 1. **Coverage Gap Found:** If capabilities exist without corresponding agents, then Either add missing agent profiles or revise the capabilities list to align with available agents.
  - Branch 8-2 Step 1. **Coverage Complete:** If all capabilities have corresponding agent coverage, then Proceed with the current agent roster configuration.

Step 9. **Develop Workflow Examples:** Create concrete, executable workflow examples that demonstrate real team usage scenarios with step-by-step processes, sample prompts, and expected outcomes that users can follow immediately.

Step 10. **Design Onboarding Experience:** Structure the getting started section with prerequisites, first interaction steps, next steps guidance, and common questions that address typical new user concerns and accelerate adoption.

Step 11. **Define Artifact Ecosystem:** Document all artifact types the team produces, their purposes, formats, usage guides, and integration guidance, along with consumption tips that help users effectively leverage team outputs.

Step 12. **Conduct Comprehensive Review:** Review the complete README structure for consistency, clarity, and completeness, ensuring all schema fields are populated with high-quality content that follows authoring guidance and creates an effective user experience.

Step 13. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 14. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-team-readme --actor <your_agent_name>`.

Step 15. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 16 (finish). **Execute Process:** Execute create-team-readme with the fully assembled <tempfile>. Use `pantheon execute create-team-readme --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.
<!-- SECTION:END:STEPS -->
