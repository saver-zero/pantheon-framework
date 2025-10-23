{
  "type": "object",
  "properties": {
    "commit_type": {
      "description_for_schema": "Conventional commit type (e.g., feat, fix, docs, refactor, test)",
      "purpose": "Categorizes the type of change made",
      "type": "string"
    },
    "implementation_phase" : {
      "description_for_schema": "The current implementation phase number related to the file changes. If unknown, skip.",
      "purpose": "Used for the title of the commit",
      "type": "number"
    },
    "implementation_phase_name" : {
      "description_for_schema": "The current implementation phase name. If unknown, skip.",
      "purpose": "Used for the title of the commit",
      "type": "string"
    },
    "commit_description": {
      "authoring_guidance": "Keep under 88 characters, use imperative mood",
      "description_for_schema": "Short description of the change",
      "maxLength": 88,
      "purpose": "Used for the title of the commit if implementation phase and name is unkown and skipped.",
      "type": "string"
    },
    "body": {
      "description_for_schema": "Optional detailed description of the change",
      "purpose": "Detailed explanation of the change if needed",
      "type": "string"
    }
  },
  "required": ["commit_type", "body"],
  "anyOf": [
    {
      "required": ["implementation_phase", "implementation_phase_name"]
    },
    {
      "required": ["commit_description"]
    }
  ]
}