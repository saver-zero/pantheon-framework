# Routine: Scaffold New Process Family

**Objective:** To design and submit a complete `build-spec.json` for generating a new process family (CREATE, GET, UPDATE).

---

Step 1. **Get Blueprint:** Retrieve the structural contract for a `build-spec` file. Use `pantheon get schema build-team-process --actor <your_agent_name>`.

Step 2. **High-Level Design:** Define the core identity of the new process family. This includes the `target_team`, the `artifact` name (e.g., "ticket"), the full list of `sections`, and the `initial_section`.

Step 3 (branch). **Evaluate Profile Schema Requirement:** Perform a branch condition check. Determine if templates require conditional logic.
    - Branch 3-1 Step 1. **Continue (No Profile Logic):** If templates do not require conditional logic, continue to the next step.
    - Branch 3-2 Step 1. **Get Profile Schema:** If templates require conditional logic, retrieve that team's profile schema to get the exact variables and options available. Use `pantheon execute get-team-profile-schema --param team=<target_team> --actor <your_agent_name>`.
    - Branch 3-2 Step 2 (branch). **Validate Profile Schema:** Perform a branch condition check. After retrieving the schema, validate that the necessary variables and options for the template logic exist:
        - Branch 3-2-1 Step 1. **Continue (Variables Exist):** If the necessary variables and options exist, continue to the next step.
        - Branch 3-2-2 Step 1 (terminate). **Terminate (Insufficient Configs):** If the necessary variables and options do not exist, report to the user on the required additional configs and the reasons why. You are now done, report back to the user.

Step 4. **Design Artifact Context:** Design the single, overarching `artifact_context` object from the schema. This provides the narrative and conceptual explanation for the entire artifact and is crucial for making it understandable.

Step 5. **Design Section Schemas and Templates:** For each section defined in Step 2, design its `schema` (the data contract) and its `template` string.

Step 6. **Define Artifact Location:** Specify the `artifact_location` object, including the `directory` and `filename_template`.

Step 7. **Define Permissions:** Specify the operation-specific `permissions` for `create`, `get`, and `update`. This field is optional.

Step 8. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process build-team-process --actor <your_agent_name>`.

Step 9. **Assemble Build-Spec JSON:** Combine all the components designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 10 (finish). **Execute Build:** Execute the build process with the fully assembled <tempfile>. Use `pantheon execute build-team-process --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done. Stop. Report the result to the user. Do not do anything else.