{
  "type": "object",
  "required": [
      "alternatives",
  ],
  "properties": {
    "alternatives": {
      "authoring_guidance": "Include all serious alternatives considered, typically 2-5 options. Each alternative should have a clear name, description, and balanced pros/cons analysis.",
      "description_for_schema": "List of alternative approaches that were evaluated for this decision.",
      "items": {
        "properties": {
          "cons": {
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "description": {
            "type": "string"
          },
          "implementation_effort": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "pros": {
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "risk_assessment": {
            "type": "string"
          }
        },
        "type": "object",
        "required": [
          "cons",
          "description",
          "implementation_effort",
          "name",
          "pros",
          "risk_assessment"
        ]
      },
      "maxItems": 8,
      "purpose": "Comprehensively documents all viable alternatives that were seriously considered, along with their trade-offs, to provide complete context for why the chosen solution was selected over other options.",
      "type": "array"
    }
  }
}