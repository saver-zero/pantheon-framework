# Routine: create-feedback-log

**Objective:** To design and create a complete feedback-log.

**IMPORTANT:** To ensure success, you must follow the steps below exactly as outlined and in order. Each step provides unique context required for the next, and deviating from this sequence will prevent you from achieving the optimal outcome.

---

Step 1. **Get Schema:** Retrieve the structural contract for the feedback-log. Use `pantheon get schema create-feedback-log --actor <your_agent_name>`.

Step 2 (branch). **Analyze References:** Perform a branch condition check. Check if reference material (like a document or diagram) was provided in the context.
  - Branch 2-1 Step 1. **Process primary reference:** If reference material was provided, then read the content of the primary reference document to capture key constraints.
  - Branch 2-1 Step 2. **Identify nested references:** Scan the primary reference to identify additional nested references.
  - Branch 2-1 Step 3. **Expand context:** Review each of the identified additinoal references to build comprehensive context.
  - Branch 2-2 Step 1. **No references available:** If no reference material was provided, then proceed with the design using only the initial request context.

Step 3. **Analyze Context:** Examine the conversation history to understand the situation before feedback was given, focusing on what was happening, what task was being worked on, and what the user was trying to accomplish.

Step 4 (branch). **Determine Target Agent:** Perform a branch condition check. Identify who the user's feedback was directed toward.:
  - Branch 4-1 Step 1. **Explicit Target:** If user explicitly mentioned a specific agent name in their feedback, then Use the explicitly mentioned agent name as the target_agent.
  - Branch 4-2 Step 1. **Infer Target:** If no specific agent was mentioned in the feedback, then Identify the last agent who spoke or took action before the user provided feedback and use that as the target_agent.

Step 5. **Extract Agent Behavior:** Identify and summarize the specific action or behavior the target agent demonstrated that prompted the user's feedback, focusing on what the agent did rather than what they should have done.

Step 6 (branch). **Process Code Content:** Perform a branch condition check. Determine if the user's feedback contains multi-line code snippets that need summarization.:
  - Branch 6-1 Step 1. **Contains Code:** If user feedback contains more than 5 lines of code, then Preserve the user's natural language exactly but replace the code block with a concise one-sentence summary in brackets describing the code's purpose.
  - Branch 6-1 Step 2. **Set Code Flag:** Set contains_code to true to indicate the original feedback had code that was summarized.
  - Branch 6-2 Step 1. **No Code:** If user feedback contains no code or only short code snippets, then Preserve the user's feedback verbatim without any modifications.
  - Branch 6-2 Step 2. **Set Code Flag:** Set contains_code to false to indicate no code summarization was needed.

Step 7. **Analyze User Sentiment:** Focus solely on the emotional tone of the user's feedback by examining word choice, punctuation, and capitalization to classify as appreciative, constructive, frustrated, inquisitive, or directive.

Step 8. **Classify Feedback Type:** Determine the user's primary intent by asking 'What is the goal of their message?' and classify as correction, suggestion, bug_report, process_feedback, clarification_request, affirmation, project_guideline, or general_comment.

Step 9. **Assess Severity:** Evaluate the impact and urgency by asking 'What is the consequence of ignoring this?' and classify as critical (system-breaking), high (major failure), medium (minor failure), or low (cosmetic issue).

Step 10. **Document Action Taken:** Summarize the corrective action that was taken in response to the user's feedback, focusing on what was actually done to address their concern.

Step 11. **Generate Title:** Create a concise title of maximum 6 words that captures the essence of this feedback incident for use as a filename identifier.

Step 12. **Quality Review:** Revisit the drafted content and remove redundant or low-impact entries before finalizing the content.

Step 13. **Get temp file location:** Get the temp file location. Use `pantheon get tempfile --process create-feedback-log --actor <your_agent_name>`.

Step 14. **Save the JSON:** Write the content designed in the previous steps into a single, valid JSON file, writing it to the <tempfile>.

Step 15 (finish). **Execute Process:** Execute create-feedback-log with the fully assembled <tempfile>. Use `pantheon execute create-feedback-log --from-file "<tempfile>" --actor <your_agent_name>`. Having quotes around <tempfile> is critical to prevent any shell parsing issues. You are now done with this routine. Stop. Do not do anything else for this routine. Do not search, list, verify anything else for this routine.