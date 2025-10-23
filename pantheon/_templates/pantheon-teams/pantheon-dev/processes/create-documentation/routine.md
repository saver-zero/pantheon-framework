# Routine: create-documentation

**Objective:** To create AI-retrievable documentation assets that follow structural standards for topic orthogonality, metadata completeness, and high-signal content guidance.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1 (branch). **Determine Asset Category:** Perform a branch condition check. Check whether the documentation asset being created is a text article or a diagram.:
  - Branch 3-1 Step 1. **Text Article Path:** If the asset is a text article, then Prepare to design a Markdown article with YAML frontmatter metadata.
  - Branch 3-2 Step 1. **Diagram Path:** If the asset is a diagram, then Prepare to design a PlantUML diagram with block comment metadata.

Step 2. **Get documentation standards:** Get the documentation guidelines and standards. Use `pantheon execute get-architecture-guide --sections documentation-standards -actor <your_agent_name>`.

Step 3. **Get path to documentation:** Retrieve the path to documentation. Use `pantheon get team-data --key path.docs --actor <your_agent_name>`. 

Step 4. **Understand existing documentation coverage:** Read the README.md and list the directories and files under the documentation path to understand the existing directory structure and topics covered.

Step 5 (branch). **Determine whether to create or update::** Perform a branch condition check. Determine whether to update existing documentation or create a new one, based on existing documentation.
  - Branch 8-1 Step 1. **Create new documentation:** If there is no existing documentation candidate to update, then determine the folder name and the file name to use for the new documentation.
  - Branch 8-2 Step 1. **Update new documentation:** If there is an existing documentation to update, then determine which documentation to update and how to update it - whether to create new sections, replace existing section, or update existing section.
  
Step 6. **Design Metadata Foundation:** Create the complete metadata structure including a globally unique doc_id, formal title, concise one-sentence description, comprehensive keyword list mixing general and specific terms, and a natural language relevance statement that directly answers when to use this asset.

Step 7. **Establish Topic Organization:** Apply the orthogonality litmus test to determine the correct topic directory, verify the concept can be fully explained without extensively detailing other topics, decide on directory structure using kebab-case naming with maximum one-level nesting, and confirm co-location of all related assets within the same directory.

Step 8 (branch). **Apply Content Guidelines:** Perform a branch condition check. Check whether the asset requires diagram-specific guidance or general content design principles.:
  - Branch 8-1 Step 1. **Design Diagram Content:** If the asset is a diagram, then Use the decision matrix to select the appropriate diagram type based on what needs to be shown: system/container for component relationships, sequence for step-by-step flows, or component for internal module structure.
  - Branch 8-1 Step 2. **Ensure jebbs Compatibility:** Design the diagram syntax to use block notes with 'note over X end note' or inline notes with backslash-n for newlines, attach notes to participants, avoid 'note as name' or floating notes, and include the shared style with '!include ../_includes/plantuml-style.puml'.
  - Branch 8-2 Step 1. **Design Text Content:** If the asset is a text article, then Follow the high-signal philosophy by documenting the why not the what, focusing on architectural decisions and trade-offs, explaining non-obvious logic and critical side-effects, defining clear contracts and boundaries, and avoiding any paraphrasing of code into English.

Step 9. **Optimize for Discoverability:** Implement cross-referencing using relative paths for portability, design keyword lists with both general and specific terms including asset type and core concepts, craft the relevance field as a direct answer to when the asset should be used, and ensure the metadata enables precise retrieval patterns like searching by keywords, status, or owner.

Step 10. **Assemble Complete Asset:** Combine the metadata structure with the content design into a single complete asset, ensuring text articles begin with YAML frontmatter containing all required metadata fields and diagrams begin with block comment metadata using the at-symbol notation, then validate that all structural requirements including SSoT principle, co-location rules, and topic orthogonality are satisfied.

Step 11. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 12. **Make Updates:** Based on existing documentation, create a new documentation or update existing documentation.

Step 13. **Update Readme:** Update or create the README.md file under the documentation path per the documentation standards, for the newly created/updated documention. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.