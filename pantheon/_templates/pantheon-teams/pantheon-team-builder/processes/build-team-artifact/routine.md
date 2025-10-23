# Routine: Build team artifact

**Objective:** To design and submit a complete schema-compliant JSON for generating a new team artifact and process family (CREATE, GET, UPDATE) to support it.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the building the team artifact. Use `pantheon get schema build-team-artifact --actor <your_agent_name>`.

Step 2 (branch). **Check Team Blueprint ID:** Perform a branch condition check. Check if a full file path of the blueprint or a standalone team blueprint ID (i.e. `TB12`) was given.
  - Branch 2-1 Step 1. **Full file path was given:** If a full file path of the team blueprint ID was given, read the doc.
  - Branch 2-2 Step 1. **Only Team Blueprint ID was given:** If only a team blueprint ID was given, retrieve the context from the team blueprint. Use `pantheon execute get-team-blueprint --actor <your_agent_name> --id <team-blueprint id>`
  - Branch 2-3 Step 1. **Neither was given:**  If no blueprint file path or id was given, continue to the next step.

Step 3 (branch). **Analyze References:** Perform a branch condition check. Check if additional reference material (like a document or diagram) was provided in the context.
  - Branch 3-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 3-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 3-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 3-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 4. **High-Level Design:** Define the core identity of the new team artifact. This includes the `target_team`, the `artifact` name (e.g., "ticket"), the full list of `sections`, and the `initial_section`.

Step 5. **Choose Build Mode:** Based on the artifact's purpose, determine the appropriate `build_mode`. For simple, self-contained documents, choose `complete`. For complex documents that require collaborative, multi-stage updates, choose `modular`.

Step 6 (branch). **Classify Artifact and Decide on Context:** Perform a branch condition check. Classify the artifact's primary audience and purpose: Is it a Process Artifact (designed to guide subsequent work by agents/team members) or a Terminal Artifact (the final deliverable for end-users or downstream systems)?
    - Branch 6-1 Step 1. **Process Artifact:** If the artifact's primary purpose is to guide subsequent work by agents or team members (e.g., internal planning documents, design briefs for teams, methodology guides for analysts), set the `include_context` flag to true to provide stable background information.
    - Branch 6-2 Step 1. **Terminal Artifact:** If the artifact's primary purpose is to serve as the final deliverable to end-users or downstream systems (e.g., client deliverables, published content, generated code files, final reports), set the `include_context` flag to false since the output should be self-contained without project management context. When in doubt, choose this path.

Step 7 (branch). **Evaluate Profile Schema Requirement:** Perform a branch condition check. Determine if templates require conditional logic. Unless explicitly stated by the users or in the team blueprint, templates do not require conditional logics by default.
    - Branch 7-1 Step 1. **Continue (No Profile Logic):** If templates do not require conditional logic, continue to the next step.
    - Branch 7-2 Step 1. **Get Team Profile:** If templates require conditional logic, retrieve that team's profile to get the exact variables and options available. Use `pantheon execute get-team-profile --id <team_profile id> --actor <your_agent_name>`.
    - Branch 7-2 Step 2 (branch). **Validate Profile Schema:** Perform a branch condition check. After retrieving the schema, validate that the necessary variables and options for the template logic exist:
        - Branch 7-2-1 Step 1. **Continue (Variables Exist):** If the necessary variables and options exist, continue to the next step.
        - Branch 7-2-2 Step 1 (terminate). **Terminate (Insufficient Configs):** If the necessary variables and options do not exist, report to the user on the required additional configs and the reasons why. You are now done, report back to the user.

Step 8. **Design Section Schemas and Templates:** For each section defined in Step 2, design its `schema` (the data contract) and its `template` string. For template content needing datestamp or timestamp, use the built-in pantheon variables `{{ pantheon_datestamp }}` and `{{ pantheon_timestamp }}`. For content needing author/creator, use the built-in pantheon variable `{{ pantheon_actor }}`.

Step 9. **Set the required fields:** Make sure all required fields are represented in the 'required' array of the schema.

Step 10. **Wrap optional fields in Jinja conditionals:** Make sure all optional fields and sections are wrapped in Jinja conditionals in the template.

Step 11. **Define Artifact Filename:** Specify the `filename_template` with Jinja2 syntax like `my-artifact_{{ title }}.md` using schema fields from the initial section template.

Step 12. **Define Permissions:** Specify the operation-specific `permissions` for `create`, `get`, and `update`. This field is optional.

Step 13. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process build-team-artifact --actor <your_agent_name>`.

Step 14. **Assemble Build-Spec JSON:** Combine all the components designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 15 (finish). **Execute Build:** Execute the build process with the fully assembled <tempfile>. Use `pantheon execute build-team-artifact --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Do not do anything else. Do not search, list, verify anything else.