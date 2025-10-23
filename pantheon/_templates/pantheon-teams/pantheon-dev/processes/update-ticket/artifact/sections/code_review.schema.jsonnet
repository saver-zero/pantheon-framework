{
  "type": "object",
  "required": [
    "review_status",
    "summary"
  ],
  "properties": {
    "findings": {
      "description_for_schema": "List of specific findings from the code review",
      "items": {
        "type": "object",
        "required": [
          "code_location",
          "description",
          "pillar",
          "recommendation",
          "severity",
          "title"
        ],
        "properties": {
          "code_location": {
            "description_for_schema": "Optional code location reference",
            "purpose": "Where in the code the issue exists",
            "type": "string"
          },
          "description": {
            "description_for_schema": "Detailed description of the finding",
            "purpose": "Detailed explanation of the issue",
            "type": "string"
          },
          "impact_analysis": {
            "description_for_schema": "Optional analysis of the impact if not resolved",
            "purpose": "Potential consequences if not addressed",
            "type": "string"
          },
          "pillar": {
            "purpose": "Category of the finding for organization",
            "type": "string",
            "enum": ["Security", "Performance", "Maintainability", "Correctness", "Architecture"]
          },
          "recommendation": {
            "description_for_schema": "Recommended action to resolve the issue",
            "purpose": "Specific action to address the finding",
            "type": "string"
          },
          "severity": {
            "purpose": "Impact level of the finding for prioritization",
            "type": "string",
            "enum": ["Critical", "High", "Medium", "Low"]
          },
          "title": {
            "description_for_schema": "Brief title describing the finding",
            "purpose": "Concise name for the finding",
            "type": "string"
          }
        }
      },
      "purpose": "Detailed list of issues and recommendations found",
      "type": "array"
    },
    "review_status": {
      "description_for_schema": "Review status",
      "purpose": "Overall assessment of the code quality",
      "type": "string",
      "enum": ["Approved", "Needs Changes", "Rejected"]
    },
    "summary": {
      "authoring_guidance": "Provide 2-3 sentences summarizing the overall quality and key findings",
      "description_for_schema": "Summary of the code review results",
      "purpose": "High-level overview of review findings",
      "type": "string"
    }
  }
}