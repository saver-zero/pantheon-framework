{
  "required": [
    "introduction",
    "key_concepts", 
    "core_capabilities",
    "key_principles"
  ],
  "properties": {
    "introduction": {
      "type": "string",
      "description": "A 1-2 sentence introduction explaining the purpose and role of this artifact."
    },
    "key_concepts": {
      "type": "array",
      "description": "A list of key concepts, terms, or 'nouns' relevant to this artifact, each with a definition. Helps establish a shared vocabulary.",
      "items": {
        "type": "object",
        "required": [
          "concept",
          "definition"
        ],
        "properties": {
          "concept": {
            "type": "string"
          },
          "definition": {
            "type": "string"
          }
        }
      }
    },
    "core_capabilities": {
      "type": "array",
      "description": "A list of high-level capabilities, workflows, or 'verbs' that are enabled or described by this artifact.",
      "items": {
        "type": "string"
      }
    },
    "key_principles": {
      "type": "array",
      "description": "A list of guiding principles, design philosophies, or core tenets that inform the artifact's design and operation.",
      "items": {
        "type": "string"
      }
    },
    "references": {
      "type": "array",
      "description": "A list of important reference materials (docs and diagrams) and a short summary of what it is and why it is important.",
      "items": {
        "type": "object",
        "required": [
          "reference",
          "summary"
        ],
        "properties": {
          "reference": {
            "type": "string",
            "description": "Link or location of the reference material."
          },
          "summary": {
            "type": "string",
            "summary": "A short 2-3 sentence summary of what the reference material is and why it is important."
          }
        }
      }
    }
  }
}