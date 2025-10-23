{
  "type": "object",
  "properties": {
    "examples": {
      "description_for_schema": "List of detailed workflow examples",
      "items": {
        "properties": {
          "final_result": {
            "authoring_guidance": "Focus on the tangible outcome. Target 20-40 words.",
            "description_for_schema": "Description of what you have after completing the workflow",
            "purpose": "The workflow's end state",
            "type": "string"
          },
          "scenario": {
            "authoring_guidance": "Make it relatable and specific. Target 25-50 words.",
            "description_for_schema": "1-2 sentences describing the situation and goal",
            "purpose": "Sets up the use case context",
            "type": "string"
          },
          "steps": {
            "description_for_schema": "Sequential steps to complete the workflow",
            "items": {
              "properties": {
                "action": {
                  "description_for_schema": "Brief action description (3-7 words)",
                  "purpose": "What the user does",
                  "type": "string"
                },
                "details": {
                  "description_for_schema": "Detailed explanation of what happens in this step",
                  "purpose": "Explains the action",
                  "type": "string"
                },
                "expected_outcome": {
                  "description_for_schema": "Optional description of expected result",
                  "purpose": "What should happen",
                  "type": "string"
                },
                "sample_prompt": {
                  "description_for_schema": "Optional example prompt to the agent",
                  "purpose": "Example of what to say",
                  "type": "string"
                }
              },
              "required": [
                "action",
                "details"
              ],
              "type": "object"
            },
            "maxItems": 6,
            "purpose": "The actual workflow steps",
            "type": "array"
          },
          "title": {
            "description_for_schema": "Brief title describing the workflow (3-7 words)",
            "purpose": "Descriptive name for the example",
            "type": "string"
          }
        },
        "required": [
          "title",
          "scenario",
          "steps",
          "final_result"
        ],
        "type": "object"
      },
      "maxItems": 3,
      "purpose": "Concrete scenarios demonstrating team usage",
      "type": "array"
    },
    "examples_intro": {
      "authoring_guidance": "Explain that these are real, executable scenarios. Target 25-50 words.",
      "description_for_schema": "Brief introduction to the workflow examples section",
      "purpose": "Sets expectations for the workflow examples",
      "type": "string"
    }
  },
  "required": [
    "examples_intro",
    "examples"
  ]
}