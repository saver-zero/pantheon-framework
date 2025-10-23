{
  "type": "object",
  "properties": {
    "documentation_improvement_items": {
      "authoring_guidance": "Focus on knowledge gaps and confusion points, aim for 3-4 items",
      "description_for_schema": "List of documentation improvements needed",
      "items": {
        "properties": {
          "document_name": {
            "authoring_guidance": "Use specific document name or path (e.g., team README, process guide)",
            "description_for_schema": "Name or path of the documentation requiring improvement",
            "purpose": "Identifies which documentation needs improvement for targeted updates",
            "type": "string"
          },
          "document_type": {
            "authoring_guidance": "Use one of: guide, diagram, reference, readme, process_doc",
            "description_for_schema": "Type of documentation requiring update",
            "purpose": "Categorizes documentation type for appropriate update handling",
            "type": "string"
          },
          "issue_description": {
            "authoring_guidance": "Be specific about missing information, outdated content, or unclear explanations",
            "description_for_schema": "Description of the documentation issue identified",
            "purpose": "Describes knowledge gap or confusion for context in documentation updates",
            "type": "string"
          },
          "priority": {
            "authoring_guidance": "Use one of: critical, high, medium, low",
            "description_for_schema": "Priority level for this improvement",
            "purpose": "Prioritizes improvements for implementation planning and resource allocation",
            "type": "string"
          },
          "recommended_changes": {
            "authoring_guidance": "Be actionable about what content to add, update, or clarify",
            "description_for_schema": "Specific changes recommended for the documentation",
            "purpose": "Provides specific documentation update guidance for implementation",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "Structures documentation-specific improvements for systematic guide and reference updates",
      "type": "array"
    }
  }
}