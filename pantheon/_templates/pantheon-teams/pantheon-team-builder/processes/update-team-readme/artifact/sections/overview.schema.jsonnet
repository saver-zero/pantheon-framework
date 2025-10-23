{
  "type": "object",
  "properties": {
    "capabilities": {
      "description_for_schema": "List of key capabilities the team provides",
      "items": {
        "properties": {
          "description": {
            "description_for_schema": "One sentence describing what users can do with this capability",
            "purpose": "Explains what this capability enables",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Brief capability name (2-4 words)",
            "purpose": "Short name for the capability",
            "type": "string"
          }
        },
        "required": [
          "name",
          "description"
        ],
        "type": "object"
      },
      "maxItems": 6,
      "purpose": "Lists the core things users can accomplish with this team",
      "type": "array"
    },
    "mission_statement": {
      "authoring_guidance": "Focus on the outcome the team delivers, not the technical implementation. Target 30-50 words.",
      "description_for_schema": "A 1-2 sentence statement describing the team's fundamental purpose",
      "purpose": "A clear, concise statement of the team's core purpose that immediately tells users why this team exists",
      "type": "string"
    },
    "team_name": {
      "authoring_guidance": "Use title case and make it immediately recognizable",
      "description_for_schema": "The name of the Pantheon team (e.g., 'Pantheon Team Builder')",
      "purpose": "The human-friendly name of the team that appears in the README title",
      "type": "string"
    },
    "use_cases": {
      "authoring_guidance": "Include specific scenarios and decision criteria. Help users recognize when this team is the right choice. Target 100-200 words.",
      "description_for_schema": "2-3 paragraph description of when and why to use this team",
      "purpose": "Provides concrete scenarios where users would engage this team",
      "type": "string"
    },
    "value_proposition": {
      "authoring_guidance": "Address user pain points directly. Explain benefits in terms users care about. Target 50-100 words.",
      "description_for_schema": "2-3 sentences explaining what problems the team solves and its unique benefits",
      "purpose": "Explains the specific problems this team solves and why users should adopt it",
      "type": "string"
    }
  },
  "required": [
    "team_name",
    "mission_statement",
    "value_proposition",
    "capabilities",
    "use_cases"
  ]
}