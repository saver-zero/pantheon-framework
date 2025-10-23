{
  "type": "object",
  "required": [
    "key_tradeoffs",
    "negative_consequences",
    "positive_consequences",
    "primary_rationale",
    "validation_points"
  ],
  "properties": {
    "key_tradeoffs": {
      "authoring_guidance": "Identify 2-4 key trade-offs where the solution excels in one area but may be weaker in another. Be explicit about what was prioritized and what was sacrificed.",
      "description_for_schema": "List of key trade-offs made in selecting this solution.",
      "items": {
        "properties": {
          "aspect": {
            "type": "string"
          },
          "description": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 6,
      "purpose": "Explicitly documents the trade-offs inherent in the chosen solution, helping future decision-makers understand what was sacrificed and why those trade-offs were acceptable.",
      "type": "array"
    },
    "negative_consequences": {
      "authoring_guidance": "Honestly assess 2-5 negative consequences or risks. Include mitigation plans for each. This prevents future surprises and shows thorough analysis.",
      "description_for_schema": "List of negative outcomes or risks expected from this decision, along with mitigation strategies.",
      "items": {
        "properties": {
          "area": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "mitigation": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 6,
      "purpose": "Acknowledges the downsides and risks of the chosen solution along with planned mitigation strategies, ensuring informed decision-making and proactive risk management.",
      "type": "array"
    },
    "positive_consequences": {
      "authoring_guidance": "List 3-6 expected positive outcomes. Organize by area of impact (performance, maintainability, scalability, etc.). Be specific about expected benefits.",
      "description_for_schema": "List of positive outcomes expected to result from this decision.",
      "items": {
        "properties": {
          "area": {
            "type": "string"
          },
          "description": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 8,
      "purpose": "Documents the beneficial outcomes expected from this decision, enabling future measurement of decision success and identification of realized benefits.",
      "type": "array"
    },
    "primary_rationale": {
      "authoring_guidance": "Explain the primary reasons this solution was chosen. Focus on how it best addresses the driving forces and constraints. Target ~150-250 words.",
      "description_for_schema": "The main reasoning behind why this solution was selected over the alternatives.",
      "purpose": "Captures the core reasoning behind why this specific solution was chosen over alternatives, providing the fundamental justification for the decision.",
      "type": "string"
    },
    "validation_points": {
      "authoring_guidance": "Define 2-4 specific future points to evaluate decision success. Include timeline and measurable criteria. This enables learning and course correction.",
      "description_for_schema": "List of future checkpoints to validate the success of this decision.",
      "items": {
        "properties": {
          "criteria": {
            "type": "string"
          },
          "timeline": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 5,
      "purpose": "Establishes specific checkpoints and criteria for evaluating whether the decision achieved its intended outcomes, enabling systematic learning and future decision improvement.",
      "type": "array"
    }
  }
}