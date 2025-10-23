{
  "type": "object",
  "required": [
    "constraints",
    "driving_forces",
    "problem_statement",
    "success_criteria"
  ],
  "properties": {
    "constraints": {
      "authoring_guidance": "List concrete constraints that limit solution options. Include technical, business, regulatory, timeline, and resource constraints. Aim for 2-5 key constraints.",
      "description_for_schema": "List of constraints and limitations that must be considered in the decision.",
      "items": {
        "properties": {
          "description": {
            "type": "string"
          },
          "type": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 8,
      "purpose": "Documents the specific limitations, boundaries, and non-negotiable requirements that must be respected in any solution, establishing the decision boundaries.",
      "type": "array"
    },
    "driving_forces": {
      "authoring_guidance": "Include 3-7 key driving forces. Categories might include: business requirements, technical constraints, performance needs, scalability requirements, team capabilities, timeline pressures, etc.",
      "description_for_schema": "List of factors, pressures, and requirements that are driving this architectural decision.",
      "items": {
        "properties": {
          "category": {
            "type": "string"
          },
          "description": {
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 10,
      "purpose": "Captures the various factors, pressures, and requirements that influence the architectural decision, helping future readers understand the full context of constraints and motivations.",
      "type": "array"
    },
    "problem_statement": {
      "authoring_guidance": "Focus on the core problem without jumping to solutions. Aim for 1-2 sentences that clearly articulate what needs to be decided and why.",
      "description_for_schema": "A clear, concise statement of the architectural problem or challenge that necessitates this decision.",
      "purpose": "Clearly articulates the specific architectural problem or challenge that requires a decision, providing the foundational context for why this decision process was initiated.",
      "type": "string"
    },
    "success_criteria": {
      "authoring_guidance": "Define 3-6 specific, measurable criteria that will indicate decision success. Focus on outcomes rather than implementation details.",
      "description_for_schema": "List of criteria that will be used to evaluate the success of this decision.",
      "items": {
        "type": "string"
      },
      "maxItems": 8,
      "purpose": "Defines the measurable outcomes and conditions that will determine whether the architectural decision was successful, enabling future validation.",
      "type": "array"
    }
  }
}