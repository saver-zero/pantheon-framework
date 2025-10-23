{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Update Plan Schema",
  "description": "Schema for updating ticket artifacts with plan information",
  "required": ["technical_summary", "implementation_approach"],
  "properties": {
    "technical_summary": {
      "type": "string",
      "description": "Technical summary of the implementation plan",
      "minLength": 20,
      "maxLength": 500
    },
    "implementation_approach": {
      "type": "string", 
      "description": "Detailed implementation approach and strategy",
      "minLength": 20,
      "maxLength": 500
    },
    "key_components": {
      "type": "array",
      "description": "Key components or modules to be implemented",
      "items": {
        "type": "string",
        "minLength": 5,
        "maxLength": 100
      }
    },
    "testing_strategy": {
      "type": "string",
      "description": "Testing approach and strategy",
      "minLength": 10,
      "maxLength": 300
    }
  },
  "additionalProperties": false
}