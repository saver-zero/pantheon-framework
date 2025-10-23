{
  "type": "object",
  "properties": {
    "analysis_period": {
      "authoring_guidance": "Use format 'YYYY-MM-DD to YYYY-MM-DD' or 'Last N days/weeks'",
      "description_for_schema": "Time period covered by this retro analysis",
      "purpose": "Defines the time range analyzed to provide context for pattern identification",
      "type": "string"
    },
    "feedback_count": {
      "authoring_guidance": "Count all feedback logs included in analysis",
      "description_for_schema": "Total number of feedback entries analyzed",
      "purpose": "Provides data scope context for statistical significance of patterns identified",
      "type": "integer"
    },
    "overall_assessment": {
      "authoring_guidance": "Target ~200 words, balance strengths and improvement areas",
      "description_for_schema": "High-level assessment of team performance based on feedback analysis",
      "purpose": "Provides holistic view of team performance for strategic improvement planning",
      "type": "string"
    },
    "primary_patterns": {
      "authoring_guidance": "Focus on 3-5 most important patterns, prioritize by frequency and impact",
      "description_for_schema": "List of the most significant patterns identified in feedback",
      "items": {
        "type": "string"
      },
      "maxItems": 5,
      "purpose": "Highlights most significant recurring issues for focused improvement efforts",
      "type": "array"
    },
    "priority_areas": {
      "authoring_guidance": "List 3-4 highest impact areas, order by urgency and importance",
      "description_for_schema": "Priority areas requiring immediate attention",
      "items": {
        "type": "string"
      },
      "maxItems": 4,
      "purpose": "Identifies areas requiring immediate attention for resource allocation and planning",
      "type": "array"
    }
  }
}