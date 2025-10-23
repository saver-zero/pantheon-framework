{
  "type": "object",
  "required": [
    "progress_summary",
    "decisions",
    "lessons_learned",
    "assumptions"
  ],
  "properties": {
    "progress_summary": {
      "description_for_schema": "One paragraph summary of progress including completed items and what's remaining.",
      "purpose": "Concise overview of current progress state",
      "type": "string"
    },
    "decisions": {
      "type": "array",
      "maxItems": 3,
      "description_for_schema": "Key decisions made during work",
      "items": {
        "type": "object",
        "required": [
          "decision"
        ],
        "properties": {
          "decision": {
            "type": "string",
            "authoring_guidance": "Target around 5 sentences explaning the situation, rationale, and impact.",
            "description_for_schema": "Decision made and rationale"
          }
        }
      }
    },
    "lessons_learned": {
      "type": "array",
      "maxItems": 3,
      "description_for_schema": "Key insights and learning from this work session",
      "items": {
        "type": "object",
        "required": [
          "lesson"
        ],
        "properties": {
          "lesson": {
            "type": "string",
            "authoring_guidance": "Keep it short. Target around 3 sentences.",
            "description_for_schema": "Insight gained and how it applies to future work."
          }
        }
      }
    },
    "assumptions": {
      "type": "array",
      "maxItems": 3,
      "description_for_schema": "Any assumptions made during this work session",
      "items": {
        "type": "object",
        "required": [
          "assumption"
        ],
        "properties": {
          "assumption": {
            "type": "string",
            "authoring_guidance": "Keep it short. Target around 3 sentences.",
            "description_for_schema": "Assumption made and how it applied to the work done."
          }
        }
      }
    },
    "todos": {
      "type": "array",
      "maxItems": 3,
      "description_for_schema": "Remaining steps",
      "items": {
        "type": "object",
        "required": [
          "action"
        ],
        "properties": {
          "action": {
            "type": "string",
            "description_for_schema": "Any remaining phases or steps to do."
          }
        }
      }
    }
  }
}