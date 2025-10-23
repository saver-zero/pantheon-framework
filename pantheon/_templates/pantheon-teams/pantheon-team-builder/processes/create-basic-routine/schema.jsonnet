{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "process_name": {
      "type": "string",
      "description_for_schema": "The kebab-case name of the process this routine is for (e.g., 'create-new-ticket', 'review-plan')",
      "purpose": "The name of the process for which this routine is being created. This will be displayed as the main heading of the routine."
    },
    "objective": {
      "type": "string",
      "description_for_schema": "A one-sentence description of what this routine achieves",
      "purpose": "A clear, concise statement of what this routine accomplishes."
    },
    "process_type": {
      "type": "string",
      "description_for_schema": "The type of process routine to generate.",
      "purpose": "Determines which template to use for the routine.",
      "enum": ["create", "get", "update"]
    }
  },
  "required": ["process_name", "objective", "process_type"]
}