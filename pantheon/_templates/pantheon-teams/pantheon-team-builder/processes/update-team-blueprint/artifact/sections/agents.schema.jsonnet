{
  "type": "object",
  "properties": {
    "agents": {
      "authoring_guidance": "More than five risks overlap. Start with 1 agent, and incrementally add agents only if necessary and high impact with clear separation of responsibilities.",
      "description_for_schema": "List the high-impact agents that constitute this team, ordered by the leverage they provide.",
      "items": {
        "description_for_schema": "Describe one agent's identity, focus, and workflows.",
        "properties": {
          "capabilities": {
            "authoring_guidance": "Aim for 2\u20134 capabilities (maximum 5) that justify this agent's existence.",
            "description_for_schema": "List the specialist capabilities or strengths this agent brings.",
            "items": {
              "description_for_schema": "State one capability in a concise phrase.",
              "purpose": "Signals the repeatable behaviours this agent should execute reliably.",
              "type": "string"
            },
            "maxItems": 5,
            "purpose": "Captures the skills that justify the agent's existence while avoiding bloated prompts.",
            "type": "array"
          },
          "manual_handoffs": {
            "authoring_guidance": "Include only unavoidable manual handoffs (maximum 5) and keep each concise.",
            "description_for_schema": "List the human-operated steps this agent coordinates (optional).",
            "items": {
              "description_for_schema": "Describe the manual action and why the agent requests it.",
              "purpose": "Keeps human responsibilities explicit instead of implying hidden automation.",
              "type": "string"
            },
            "maxItems": 5,
            "purpose": "Surfaces human-in-the-loop expectations so operators are never surprised.",
            "type": "array"
          },
          "name": {
            "description_for_schema": "Agent name (lowercase, hyphen-separated).",
            "authoring_guidance": "For non-technical teams, think from the user's perspective: what help or support do they need? Use friendly, approachable terms that reflect the user's goal rather than system architecture. For technical/software engineering teams, role-based names remain appropriate.",
            "purpose": "Provides a stable identifier for cross-referencing prompts and processes.",
            "type": "string"
          },
          "responsibilities": {
            "authoring_guidance": "Aim for 3\u20135 responsibilities (maximum 6) that truly differentiate this agent.",
            "description_for_schema": "List the core responsibilities this agent owns.",
            "items": {
              "description_for_schema": "Describe one responsibility in a short sentence.",
              "purpose": "Keeps tasks actionable and bounded so the agent prompt remains predictable.",
              "type": "string"
            },
            "maxItems": 6,
            "purpose": "Highlights only the duties that truly differentiate this agent.",
            "type": "array"
          },
          "role": {
            "authoring_guidance": "Target about 25 words, highlighting what makes this agent unique.",
            "description_for_schema": "Summarize the agent's role in a single sentence.",
            "purpose": "Clarifies why this agent exists so overlapping personas are avoided.",
            "type": "string"
          },
          "workflows": {
            "authoring_guidance": "Include only workflows this agent uniquely owns (maximum 4).",
            "description_for_schema": "List the Pantheon workflows this agent performs (CREATE/GET/UPDATE).",
            "items": {
              "description_for_schema": "Name the workflow and describe its operator-facing outcome.",
              "properties": {
                "description": {
                  "description_for_schema": "Summarize the value this workflow returns to the operator in one sentence.",
                  "purpose": "Keeps emphasis on the outcome delivered rather than the mechanics.",
                  "type": "string"
                },
                "name": {
                  "description_for_schema": "Workflow name (lowercase words or hyphenated).",
                  "purpose": "Provides a predictable label for routines and documentation.",
                  "type": "string"
                }
              },
              "required": [
                "name",
                "description"
              ],
              "purpose": "Makes each workflow's intent explicit so the blueprint avoids redundant or speculative processes.",
              "type": "object"
            },
            "maxItems": 4,
            "purpose": "Ensures each workflow is tied to a Pantheon verb, keeping automation inside the framework's boundaries.",
            "type": "array"
          }
        },
        "required": [
          "name",
          "role",
          "responsibilities",
          "capabilities",
          "workflows"
        ],
        "purpose": "Ensures each agent entry captures only the information needed to deploy the role effectively.",
        "type": "object"
      },
      "maxItems": 6,
      "purpose": "Keeps the roster focused on a small cadre of specialists that materially improve the workflow.",
      "type": "array"
    },
    "team_composition_overview": {
      "authoring_guidance": "Aim for about 150 words, emphasizing collaboration and handoffs.",
      "description_for_schema": "Summarize how these agents collaborate and hand off work inside Pantheon.",
      "purpose": "Explains why this particular mix of agents is necessary so future changes preserve the collaboration model.",
      "type": "string"
    }
  },
  "required": [
    "team_composition_overview",
    "agents"
  ]
}