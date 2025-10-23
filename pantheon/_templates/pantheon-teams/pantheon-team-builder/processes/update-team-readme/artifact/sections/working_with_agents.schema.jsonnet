{
  "type": "object",
  "properties": {
    "best_practices": {
      "description_for_schema": "List of communication best practices",
      "items": {
        "properties": {
          "explanation": {
            "description_for_schema": "One sentence explaining the principle's application",
            "purpose": "Why and how to apply this principle",
            "type": "string"
          },
          "principle": {
            "description_for_schema": "Brief principle name (2-5 words)",
            "purpose": "The core principle to follow",
            "type": "string"
          }
        },
        "required": [
          "principle",
          "explanation"
        ],
        "type": "object"
      },
      "maxItems": 5,
      "purpose": "Actionable tips for effective agent communication",
      "type": "array"
    },
    "human_role": {
      "authoring_guidance": "Focus on vision, feedback, and decision-making. Reassure that procedural complexity is handled. Target 75-150 words.",
      "description_for_schema": "1-2 paragraphs describing the human's responsibilities and contributions",
      "purpose": "Clarifies what humans contribute to the collaboration",
      "type": "string"
    },
    "team_name": {
      "description_for_schema": "The name of the Pantheon team",
      "purpose": "Team name for context in section headers",
      "type": "string"
    },
    "artifact_types": {
      "description_for_schema": "List of artifact types this team creates",
      "items": {
        "properties": {
          "name": {
            "description_for_schema": "Name of the artifact type",
            "purpose": "Artifact type name",
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "purpose": "Artifact types the team produces",
      "type": "array"
    }
  },
  "required": [
    "team_name",
    "artifact_types",
    "human_role",
    "best_practices"
  ]
}