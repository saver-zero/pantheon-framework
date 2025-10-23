{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "target_agent",
    "situation_before",
    "agent_behavior_before",
    "user_feedback",
    "contains_code",
    "agent_action_taken",
    "user_sentiment",
    "feedback_type",
    "severity"
  ],
  "properties": {
    "target_agent": {
      "type": "string",
      "pattern": "^@?[a-zA-Z0-9_-]+$",
      "description_for_schema": "Target agent identifier. Who was the user feedback for? If unclear, use the last agent who spoke before the user."
    },
    "situation_before": {
      "type": "string",
      "description_for_schema": "A concise, agent-generated summary of the context before the user gave feedback.",
      "example":"User was testing a new login endpoint and it returned a generic '500 Internal Server Error' for a bad password."
    },
    "agent_behavior_before": {
      "type": "string",
      "description_for_schema": "A concise, agent-generated summary of the specific action the target agent took.",
      "example":"Agent implemented the login endpoint but did not handle authentication failures correctly."
    },
    "user_feedback": {
      "type": "string",
      "description_for_schema": "The user's verbatim natural language, with a crucial modification for large code blocks. If the feedback contains more than5 lines of code snippet, the natural language portion must be preserved exactly. The code block itself must be replaced by a concise, one-sentence LLM-generated summary that describes its purpose (e.g., '[CODE SUMMARY: A corrected implementation of the login function with proper error handling.]'). This preserves the user's intent without bloating the log with raw code.",
      "example": "The login logic is buggy, it doesn't handle database errors at all. It should be something like this instead: [CODE SUMMARY: A corrected Python login function that includes a try/except block for database errors.] You need a try/except block."
    },
    "contains_code": {
      "type": "boolean",
      "description_for_schema": "Set to true if the original, unprocessed feedback contained a multi-line code snippet which was then summarized in the 'user_feedback' field.",
      "example": true
    },
    "agent_action_taken": {
      "type": "string",
      "description_for_schema": "A concise, agent-generated summary of the corrective action the agent took in response to the feedback.",
      "example":"Agent updated the endpoint to catch the specific authentication error and return a proper 401 status code with the correct error message."
    },
    "user_sentiment": {
      "type": "string",
      "enum": ["appreciative", "constructive", "frustrated", "inquisitive", "directive"],
      "description_for_schema": "Analyze the emotional tone of the user's feedback, focusing on word choice, punctuation, and capitalization. Classify the sentiment into one of the following categories: [appreciative, constructive, frustrated, inquisitive, directive]. Focus *only* on the emotional tone, not the subject matter or its importance."
    },
    "feedback_type": {
      "type": "string",
      "enum": ["correction", "suggestion", "bug_report", "process_feedback", "clarification_request", "affirmation", "project_guideline", "general_comment"],
      "description_for_schema": "Analyze the user's primary intent. What is the goal of their message? Classify the intent into one of the following: [correction (to fix a factual or logical error), suggestion (to propose an improvement or alternative), bug_report (to report a functional failure), process_feedback (to comment on the agent's workflow), clarification_request (to ask a question for more info), affirmation (to confirm correctness or express approval), project_guideline (to provide a rule, architectural principle, or convention), general_comment (for non-specific, qualitative, or ambiguous feedback)]."
    },
    "severity": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"],
      "description_for_schema": "Assess the impact and urgency of the feedback by answering: 'What is the consequence of ignoring this?' Classify the impact into one of the following: [critical (system-breaking issue, security vulnerability, or data loss), high (major feature failure with no easy workaround), medium (minor feature failure or significant deviation from requirements), low (cosmetic issue, typo, or minor inconvenience)]."
    }
  }
}