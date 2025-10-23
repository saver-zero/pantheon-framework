# Routine: create-retro-report

**Objective:** To design and create a complete retro-report.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the retro-report. Use `pantheon get schema create-retro-report --actor <your_agent_name>`.

Step 2. **Get Feedback Data:** Get the logged feedback data. List the files in directory {{ pantheon_artifacts_root }}/feedback/data

Step 3 (branch). **Check feedback data:** Perform a branch condition check. Check if feedback data is available.
  - Branch 2-1 Step 1. **Feedback data is available:** If feedback data is available, continue to the next step.
  - Branch 2-2 Step 1 (finish). **Feedback data is not available:** If no feedback data is availabe, report to the user that there is no feedback to process.You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.

Step 4 (branch). **Assess Feedback Volume:** Perform a branch condition check. Check if sufficient feedback exists for meaningful pattern analysis.:
  - Branch 4-1 Step 1. **Proceed with Analysis:** If feedback count is 3 or higher, then Continue with comprehensive pattern analysis using the available feedback data.
  - Branch 4-2 Step 1. **Limited Analysis:** If feedback count is 1-2 entries, then Proceed with limited analysis noting the small sample size in all assessments.

Step 5. **Identify Primary Patterns:** Analyze all feedback entries to identify the most significant recurring patterns, prioritizing by both frequency of occurrence and impact on team effectiveness.

Step 6. **Generate Strategic Assessment:** Create a balanced 200-word overall assessment covering team strengths and improvement areas, then identify 3-4 priority areas ordered by urgency and strategic importance.

Step 7. **Categorize Process Improvements:** Identify workflow gaps and inefficiencies in process routines, specifying which processes and sections need updates along with concrete recommendations for adding, modifying, or removing steps.

Step 8. **Categorize Artifact Improvements:** Analyze feedback for data capture gaps and structural issues in schemas and templates, specifying whether schema updates, template updates, or both are needed for each identified artifact problem.

Step 9. **Prioritize All Improvements:** Review all categorized improvements and assign priority levels (critical, high, medium, low) based on impact on team effectiveness and implementation urgency, ensuring balanced resource allocation.

Step 10. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 11. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-retro-report --actor <your_agent_name>`.

Step 12. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 13. **Execute Process:** Execute create-retro-report with the fully assembled <tempfile>. Use `pantheon execute create-retro-report --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues.

Step 14 (finish). **Archive the reviewed feedback:** Move the reviewed feedback from {{ pantheon_artifacts_root }}/feedback/data/ to {{ pantheon_artifacts_root }}/feedback/data/archive/ . You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.