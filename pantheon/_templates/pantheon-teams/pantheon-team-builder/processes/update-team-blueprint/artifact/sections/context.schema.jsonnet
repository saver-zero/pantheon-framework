{
  "type": "object",
  "properties": {
    "core_capabilities": {
      "description": "A list of high-level capabilities, workflows, or 'verbs' that are enabled or described by this artifact.",
      "items": {
        "type": "string"
      },
      "type": "array"
    },
    "key_concepts": {
      "description": "A list of key concepts, terms, or 'nouns' relevant to this artifact and the project it is supporting, each with a definition. Helps establish a shared vocabulary.",
      "items": {
        "properties": {
          "concept": {
            "type": "string"
          },
          "definition": {
            "type": "string"
          }
        },
        "required": [
          "concept",
          "definition"
        ],
        "type": "object"
      },
      "type": "array"
    },
    "key_principles": {
      "description": "A list of guiding principles, design philosophies, or core tenets that inform the artifact's design and operation.",
      "items": {
        "type": "string"
      },
      "type": "array"
    },
    "project_context": {
      "description": "High level overview and context of the project this process and artifact is supporting. It should have enough details and explanation for someone with zero context can understand the overall picture and how this process and artifact fits in.",
      "type": "string"
    },
    "references": {
      "description": "A list of important reference materials (docs and diagrams) and a short summary of what it is and why it is important.",
      "items": {
        "properties": {
          "reference": {
            "description": "Link or location of the reference material.",
            "type": "string"
          },
          "summary": {
            "summary": "A short 2-3 sentence summary of what the reference material is and why it is important.",
            "type": "string"
          }
        },
        "required": [
          "reference",
          "summary"
        ],
        "type": "object"
      },
      "type": "array"
    }
  },
  "required": [
    "project_context",
    "key_concepts",
    "core_capabilities",
    "key_principles"
  ]
}