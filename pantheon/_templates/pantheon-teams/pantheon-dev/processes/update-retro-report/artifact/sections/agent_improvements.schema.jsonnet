{
  "type": "object",
  "properties": {
    "agent_improvement_items": {
      "authoring_guidance": "Focus on actionable prompt changes, aim for 3-6 items",
      "description_for_schema": "List of agent-specific improvements needed",
      "items": {
        "properties": {
          "agent_name": {
            "authoring_guidance": "Use exact agent name from team definition",
            "description_for_schema": "Name of the agent requiring improvement",
            "purpose": "Identifies which agent needs improvement for targeted updates",
            "type": "string"
          },
          "example_feedback": {
            "authoring_guidance": "Include representative user feedback that illustrates the issue",
            "description_for_schema": "Example feedback that demonstrates this issue (optional)",
            "purpose": "Provides concrete examples to support improvement recommendations",
            "type": "string"
          },
          "issue_description": {
            "authoring_guidance": "Be specific about the problem behavior or output quality issue",
            "description_for_schema": "Description of the behavioral issue identified",
            "purpose": "Describes the behavioral issue for context in prompt updates",
            "type": "string"
          },
          "priority": {
            "authoring_guidance": "Use one of: critical, high, medium, low",
            "description_for_schema": "Priority level for this improvement",
            "purpose": "Prioritizes improvements for implementation planning and resource allocation",
            "type": "string"
          },
          "recommended_changes": {
            "authoring_guidance": "Be actionable and specific about what to change in the prompt",
            "description_for_schema": "Specific changes recommended for the agent prompt",
            "purpose": "Provides specific prompt update guidance for implementation",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "Structures agent-specific improvements for systematic prompt updates and behavioral corrections",
      "type": "array"
    }
  }
}