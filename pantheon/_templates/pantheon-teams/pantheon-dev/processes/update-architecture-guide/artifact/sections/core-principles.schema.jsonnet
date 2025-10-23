{
  "type": "object",
  "required": [
    "principles",
    "antipatterns"
  ],
  "properties": {
    "antipatterns": {
      "description_for_schema": "List of anti-patterns to avoid",
      "items": {
        "description_for_schema": "An anti-pattern with its problems and alternatives",
        "properties": {
          "alternative": {
            "description_for_schema": "Recommended alternative approach",
            "purpose": "The correct approach to use instead",
            "type": "string"
          },
          "description": {
            "description_for_schema": "Description of the anti-pattern",
            "purpose": "What the anti-pattern looks like",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the anti-pattern",
            "purpose": "The anti-pattern's identifier",
            "type": "string"
          },
          "problems": {
            "description_for_schema": "Explanation of why this is problematic",
            "purpose": "Why this pattern causes issues",
            "type": "string"
          }
        },
        "purpose": "A pattern that should be avoided",
        "required": [
          "name",
          "description",
          "problems",
          "alternative"
        ],
        "type": "object"
      },
      "purpose": "Common mistakes and patterns to avoid",
      "type": "array"
    },
    "principles": {
      "description_for_schema": "List of core architectural principles",
      "items": {
        "description_for_schema": "An architectural principle with examples",
        "properties": {
          "examples": {
            "description_for_schema": "List of practical examples",
            "items": {
              "description_for_schema": "One example of applying this principle",
              "purpose": "A specific example",
              "type": "string"
            },
            "purpose": "Concrete applications of the principle",
            "type": "array"
          },
          "name": {
            "description_for_schema": "Short name of the principle",
            "purpose": "The principle's identifier",
            "type": "string"
          },
          "rationale": {
            "description_for_schema": "Explanation of why this principle is important",
            "purpose": "Why this principle matters",
            "type": "string"
          },
          "statement": {
            "description_for_schema": "Clear statement of the principle",
            "purpose": "The principle stated as a rule",
            "type": "string"
          }
        },
        "purpose": "A single architectural principle",
        "required": [
          "name",
          "statement",
          "rationale",
          "examples"
        ],
        "type": "object"
      },
      "purpose": "The fundamental design principles that guide all decisions",
      "type": "array"
    }
  }
}