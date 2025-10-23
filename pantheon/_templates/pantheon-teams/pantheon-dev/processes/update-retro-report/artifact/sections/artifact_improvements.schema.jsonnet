{
  "type": "object",
  "properties": {
    "artifact_improvement_items": {
      "authoring_guidance": "Focus on data capture gaps and structural issues, aim for 3-5 items",
      "description_for_schema": "List of artifact schema and template improvements needed",
      "items": {
        "properties": {
          "affected_sections": {
            "authoring_guidance": "Include specific section names if the improvement is section-specific",
            "description_for_schema": "List of artifact sections that need updates (optional)",
            "items": {
              "type": "string"
            },
            "purpose": "Identifies specific sections requiring updates for targeted implementation",
            "type": "array"
          },
          "artifact_name": {
            "authoring_guidance": "Use exact artifact name (e.g., ticket, feedback-log, architecture-guide)",
            "description_for_schema": "Name of the artifact requiring improvement",
            "purpose": "Identifies which artifact needs improvement for targeted updates",
            "type": "string"
          },
          "change_type": {
            "authoring_guidance": "Use one of: schema_update, template_update, both",
            "description_for_schema": "Type of change needed for this artifact",
            "purpose": "Categorizes the type of change needed for implementation planning",
            "type": "string"
          },
          "issue_description": {
            "authoring_guidance": "Be specific about missing fields, structural problems, or template issues",
            "description_for_schema": "Description of the artifact issue identified",
            "purpose": "Describes data capture or structural issue for context in updates",
            "type": "string"
          },
          "priority": {
            "authoring_guidance": "Use one of: critical, high, medium, low",
            "description_for_schema": "Priority level for this improvement",
            "purpose": "Prioritizes improvements for implementation planning and resource allocation",
            "type": "string"
          },
          "recommended_changes": {
            "authoring_guidance": "Be actionable about what fields to add/modify or template changes needed",
            "description_for_schema": "Specific changes recommended for the artifact schema or template",
            "purpose": "Provides specific schema/template update guidance for implementation",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "Structures artifact-specific improvements for systematic schema and template updates",
      "type": "array"
    }
  }
}