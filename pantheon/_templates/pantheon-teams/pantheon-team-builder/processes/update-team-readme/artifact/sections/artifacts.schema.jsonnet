{
  "type": "object",
  "properties": {
    "artifact_types": {
      "description_for_schema": "List of artifact types this team creates",
      "items": {
        "properties": {
          "example_snippet": {
            "description_for_schema": "Optional brief example of the artifact format",
            "purpose": "Sample artifact content",
            "type": "string"
          },
          "format": {
            "description_for_schema": "Brief description of format (e.g., 'Markdown document', 'JSON specification')",
            "purpose": "The artifact's structure",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the artifact type",
            "purpose": "Artifact type name",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "One sentence describing the artifact's purpose",
            "purpose": "Why this artifact exists",
            "type": "string"
          },
          "usage_guide": {
            "authoring_guidance": "Include concrete actions users can take. Target 50-100 words.",
            "description_for_schema": "2-3 sentences on how to use this artifact type",
            "purpose": "How to work with this artifact",
            "type": "string"
          }
        },
        "required": [
          "name",
          "purpose",
          "format",
          "usage_guide"
        ],
        "type": "object"
      },
      "purpose": "Documents each type of artifact the team produces",
      "type": "array"
    },
    "artifacts_intro": {
      "authoring_guidance": "Explain artifacts as team outputs and their value. Target 75-150 words.",
      "description_for_schema": "1-2 paragraphs introducing team artifacts",
      "purpose": "Explains what artifacts are and their role",
      "type": "string"
    },
    "consumption_tips": {
      "description_for_schema": "List of tips for artifact consumption",
      "items": {
        "properties": {
          "guidance": {
            "description_for_schema": "Specific guidance for this topic",
            "purpose": "The actual tip",
            "type": "string"
          },
          "topic": {
            "description_for_schema": "Brief topic (2-4 words)",
            "purpose": "Tip category",
            "type": "string"
          }
        },
        "required": [
          "topic",
          "guidance"
        ],
        "type": "object"
      },
      "maxItems": 4,
      "purpose": "Best practices for using artifacts effectively",
      "type": "array"
    },
    "integration_guide": {
      "authoring_guidance": "Focus on practical integration with tools like Claude. Target 150-250 words.",
      "description_for_schema": "2-3 paragraphs on integrating artifacts with implementation LLMs",
      "purpose": "Explains how to incorporate artifacts into broader workflows",
      "type": "string"
    }
  },
  "required": [
    "artifacts_intro",
    "artifact_types",
    "integration_guide",
    "consumption_tips"
  ]
}