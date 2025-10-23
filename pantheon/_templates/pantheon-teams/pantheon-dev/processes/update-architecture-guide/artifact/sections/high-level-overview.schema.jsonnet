{
  "type": "object",
  "required": [
    "system_function",
    "architectural_approach",
    "key_technologies"
  ],
  "properties": {
    "architectural_approach": {
      "authoring_guidance": "Write a paragraph about the architecture style and major design decisions, aim for 3-5 sentences",
      "description_for_schema": "One paragraph describing the core architectural approach",
      "purpose": "Explains the fundamental architectural decisions and patterns",
      "type": "string"
    },
    "key_technologies": {
      "authoring_guidance": "Write a paragraph mentioning the main technologies and why they were chosen, aim for 3-5 sentences",
      "description_for_schema": "One paragraph listing the key technologies used",
      "purpose": "Summarizes the technology choices that enable the architecture",
      "type": "string"
    },
    "system_function": {
      "authoring_guidance": "Write a clear paragraph about what the system does, aim for 3-5 sentences",
      "description_for_schema": "One paragraph describing the system's primary function",
      "purpose": "Describes what the system does at the highest level",
      "type": "string"
    }
  }
}