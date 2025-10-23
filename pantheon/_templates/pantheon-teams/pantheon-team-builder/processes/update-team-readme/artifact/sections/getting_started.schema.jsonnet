{
  "type": "object",
  "properties": {
    "common_questions": {
      "description_for_schema": "FAQ entries for new users",
      "items": {
        "properties": {
          "answer": {
            "authoring_guidance": "Be direct and reassuring. Target 25-75 words.",
            "description_for_schema": "Concise answer to the question",
            "purpose": "Clear, helpful answer",
            "type": "string"
          },
          "question": {
            "description_for_schema": "Common question from new users",
            "purpose": "The FAQ question",
            "type": "string"
          }
        },
        "required": [
          "question",
          "answer"
        ],
        "type": "object"
      },
      "maxItems": 5,
      "purpose": "Addresses typical new user concerns",
      "type": "array"
    },
    "first_steps": {
      "description_for_schema": "Sequential steps for first successful interaction",
      "items": {
        "properties": {
          "example": {
            "description_for_schema": "Optional example text or prompt",
            "purpose": "Concrete example",
            "type": "string"
          },
          "instruction": {
            "authoring_guidance": "Be specific and actionable. Target 25-75 words.",
            "description_for_schema": "Clear instruction for this step",
            "purpose": "What to do",
            "type": "string"
          },
          "tip": {
            "description_for_schema": "Optional tip for success",
            "purpose": "Helpful advice",
            "type": "string"
          },
          "title": {
            "description_for_schema": "Brief step title (3-6 words)",
            "purpose": "Step name",
            "type": "string"
          }
        },
        "required": [
          "title",
          "instruction"
        ],
        "type": "object"
      },
      "maxItems": 4,
      "purpose": "The minimal viable interaction sequence",
      "type": "array"
    },
    "next_steps": {
      "authoring_guidance": "Suggest natural progression paths. Target 75-150 words.",
      "description_for_schema": "1-2 paragraphs on what to explore next",
      "purpose": "Guides users after initial success",
      "type": "string"
    },
    "prerequisites": {
      "description_for_schema": "List of prerequisites or requirements",
      "items": {
        "type": "string"
      },
      "maxItems": 4,
      "purpose": "What users need before starting",
      "type": "array"
    },
    "quick_start_intro": {
      "authoring_guidance": "Be welcoming and reassuring. Target 30-60 words.",
      "description_for_schema": "Brief, encouraging introduction to getting started",
      "purpose": "Welcomes new users and sets expectations",
      "type": "string"
    }
  },
  "required": [
    "quick_start_intro",
    "prerequisites",
    "first_steps",
    "next_steps",
    "common_questions"
  ]
}