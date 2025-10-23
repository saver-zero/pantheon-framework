{
  "type": "object",
  "properties": {
    "agent_list": {
      "description_for_schema": "List of agents available in this team",
      "items": {
        "properties": {
          "deliverables": {
            "description_for_schema": "List of artifacts or outcomes this agent creates",
            "items": {
              "type": "string"
            },
            "maxItems": 4,
            "purpose": "What the agent produces",
            "type": "array"
          },
          "expertise": {
            "description_for_schema": "One sentence describing the agent's area of expertise",
            "purpose": "The agent's domain of specialization",
            "type": "string"
          },
          "interaction_guide": {
            "authoring_guidance": "Include conversation starters and what information to provide. Target 50-100 words.",
            "description_for_schema": "2-3 sentences on how to effectively work with this agent",
            "purpose": "Practical guidance for communicating with this agent",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Agent name as users will reference it",
            "purpose": "The agent's identifier",
            "type": "string"
          },
          "when_to_use": {
            "authoring_guidance": "Be specific about triggers and decision points. Target 30-60 words.",
            "description_for_schema": "Specific scenarios or needs that warrant engaging this agent",
            "purpose": "Clear triggers for when to engage this agent",
            "type": "string"
          }
        },
        "required": [
          "name",
          "expertise",
          "when_to_use",
          "interaction_guide",
          "deliverables"
        ],
        "type": "object"
      },
      "purpose": "Comprehensive list of all team agents with their roles",
      "type": "array"
    },
    "agents_intro": {
      "authoring_guidance": "Briefly explain that each agent is a specialist. Target 25-50 words.",
      "description_for_schema": "1-2 sentences introducing the team's agents",
      "purpose": "Sets context for the agent roster",
      "type": "string"
    }
  },
  "required": [
    "agents_intro",
    "agent_list"
  ]
}