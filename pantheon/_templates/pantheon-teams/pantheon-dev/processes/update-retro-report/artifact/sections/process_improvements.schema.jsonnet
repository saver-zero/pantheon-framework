{
  "type": "object",
  "properties": {
    "process_improvement_items": {
      "authoring_guidance": "Focus on workflow gaps and inefficiencies, aim for 3-5 items",
      "description_for_schema": "List of process routine improvements needed",
      "items": {
        "properties": {
          "affected_sections": {
            "authoring_guidance": "Include specific section names if the improvement is section-specific",
            "description_for_schema": "List of process sections that need updates (optional)",
            "items": {
              "type": "string"
            },
            "purpose": "Identifies specific sections requiring updates for targeted implementation",
            "type": "array"
          },
          "issue_description": {
            "authoring_guidance": "Be specific about gaps, inefficiencies, or missing steps",
            "description_for_schema": "Description of the workflow issue identified",
            "purpose": "Describes workflow inefficiency for context in routine updates",
            "type": "string"
          },
          "priority": {
            "authoring_guidance": "Use one of: critical, high, medium, low",
            "description_for_schema": "Priority level for this improvement",
            "purpose": "Prioritizes improvements for implementation planning and resource allocation",
            "type": "string"
          },
          "process_name": {
            "authoring_guidance": "Use exact process name (e.g., create-ticket, update-architecture-guide)",
            "description_for_schema": "Name of the process requiring improvement",
            "purpose": "Identifies which process needs improvement for targeted updates",
            "type": "string"
          },
          "recommended_changes": {
            "authoring_guidance": "Be actionable about what steps to add, modify, or remove",
            "description_for_schema": "Specific changes recommended for the process routine",
            "purpose": "Provides specific routine update guidance for implementation",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "Structures process-specific improvements for systematic routine updates and workflow optimization",
      "type": "array"
    }
  }
}