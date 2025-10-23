{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Create Ticket Schema",
  "description": "Schema for creating new ticket artifacts with minimal required fields",
  "required": ["title", "description", "plan"],
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the ticket",
      "minLength": 10,
      "maxLength": 50
    },
    "description": {
      "type": "string",
      "description": "Description of the ticket or issue",
      "minLength": 100,
      "maxLength": 300
    },
    "plan": {
      "type": "string",
      "description": "Implementation plan or approach for addressing the ticket",
      "minLength": 100,
      "maxLength": 500
    },
    "assignee": {
      "type": "string",
      "description": "Person or agent assigned to this ticket"
    },
    "sequence_number": {
      "type": "integer",
      "description": "Optional sequence number for grouping related tickets",
      "minimum": 1
    },
    "sequence_description": {
      "type": "string",
      "description": "Optional sequence description (lowercase, single word, max 11 chars)",
      "maxLength": 11,
      "pattern": "^[a-z]+$"
    }
  },
  "dependentRequired": {
    "sequence_number": ["sequence_description"],
    "sequence_description": ["sequence_number"]
  },
  "additionalProperties": false
}