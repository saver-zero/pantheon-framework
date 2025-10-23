{
  "type": "object",
  "required": [
    "problem_statement",
    "business_outcomes",
    "key_features"
  ],
  "properties": {
    "business_outcomes": {
      "description_for_schema": "List of desired business outcomes from this project",
      "items": {
        "description_for_schema": "One specific business outcome",
        "purpose": "A single business outcome",
        "type": "string"
      },
      "purpose": "Lists the measurable business goals and benefits expected from the project",
      "type": "array"
    },
    "key_features": {
      "description_for_schema": "List of key features with names and descriptions",
      "items": {
        "description_for_schema": "A single feature with name and description",
        "properties": {
          "description": {
            "description_for_schema": "Brief description of the feature's functionality",
            "purpose": "Explains what the feature does",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Short name of the feature",
            "purpose": "The feature's identifier",
            "type": "string"
          }
        },
        "purpose": "A feature definition",
        "required": [
          "name",
          "description"
        ],
        "type": "object"
      },
      "purpose": "Enumerates the main functional capabilities the system will provide",
      "type": "array"
    },
    "problem_statement": {
      "authoring_guidance": "Write a concise problem statement in 1-3 sentences",
      "description_for_schema": "A clear statement of the problem this project solves",
      "purpose": "Articulates the core business or technical problem that this project addresses",
      "type": "string"
    }
  }
}