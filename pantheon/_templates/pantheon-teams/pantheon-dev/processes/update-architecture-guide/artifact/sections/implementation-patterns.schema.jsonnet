{
  "type": "object",
  "required": [
    "patterns"
  ],
  "properties": {
    "patterns": {
      "description_for_schema": "List of implementation patterns",
      "items": {
        "description_for_schema": "An implementation pattern with examples",
        "properties": {
          "category": {
            "description_for_schema": "Category (e.g., 'Architectural', 'Behavioral', 'Structural')",
            "purpose": "Type of pattern",
            "type": "string"
          },
          "code_language": {
            "description_for_schema": "Programming language for the example",
            "purpose": "Language for the example",
            "type": "string"
          },
          "implementation_example": {
            "description_for_schema": "Code example showing the pattern implementation",
            "purpose": "Code demonstrating the pattern",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the pattern",
            "purpose": "Pattern identifier",
            "type": "string"
          },
          "problem": {
            "description_for_schema": "Description of the problem this pattern addresses",
            "purpose": "The problem this pattern solves",
            "type": "string"
          },
          "solution": {
            "description_for_schema": "Description of the solution approach",
            "purpose": "How the pattern solves the problem",
            "type": "string"
          },
          "when_not_to_use": {
            "description_for_schema": "Scenarios where this pattern should be avoided",
            "items": {
              "description_for_schema": "One scenario where this pattern is inappropriate",
              "purpose": "A scenario to avoid",
              "type": "string"
            },
            "purpose": "Inappropriate use cases",
            "type": "array"
          },
          "when_to_use": {
            "description_for_schema": "Scenarios where this pattern should be used",
            "items": {
              "description_for_schema": "One scenario for using this pattern",
              "purpose": "A use case",
              "type": "string"
            },
            "purpose": "Appropriate use cases",
            "type": "array"
          }
        },
        "purpose": "A reusable solution pattern",
        "required": [
          "name",
          "category",
          "problem",
          "solution",
          "code_language",
          "implementation_example",
          "when_to_use",
          "when_not_to_use"
        ],
        "type": "object"
      },
      "purpose": "Collection of approved design and implementation patterns",
      "type": "array"
    }
  }
}