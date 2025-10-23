{
  "type": "object",
  "properties": {
    "goals": {
      "authoring_guidance": "Aim for 2\u20134 high-impact goals (maximum 5). It's acceptable to provide fewer if only a couple truly matter.",
      "description_for_schema": "List the strategic goals the team will pursue.",
      "items": {
        "description_for_schema": "State one measurable goal in a single sentence.",
        "purpose": "Keeps each goal crisp so agents can trace work back to clear success criteria.",
        "type": "string"
      },
      "maxItems": 5,
      "purpose": "Captures the big outcomes that justify why the team exists, guiding all subsequent design choices.",
      "type": "array"
    },
    "high_leverage_artifacts": {
      "authoring_guidance": "Focus on artifacts that materially reduce ambiguity or rework. Maximum 4 items.",
      "description_for_schema": "List the 1-3 critical artifacts that provide the most leverage for this workflow.",
      "items": {
        "properties": {
          "artifact_name": {
            "purpose": "Provides a stable label for referencing the artifact.",
            "authoring_guidance": "For non-technical teams, focus on what the user is creating or achieving, use outcome-oriented language that is user friendly. For technical teams, technical terminology is appropriate.",
            "type": "string"
          },
          "description": {
            "description_for_schema": "Explain how this artifact makes the human operator more effective.",
            "purpose": "Justifies the artifact's inclusion by showing its value.",
            "type": "string"
          }
        },
        "type": "object"
      },
      "maxItems": 4,
      "purpose": "Identifies the key deliverables that drive the team's effectiveness.",
      "type": "array"
    },
    "manual_checkpoints": {
      "authoring_guidance": "Include only essential manual verification or approval steps. Maximum 5 items.",
      "description_for_schema": "List the critical, non-negotiable manual steps the human operator must perform.",
      "items": {
        "description_for_schema": "A single manual action or verification step (e.g., 'Manually run tests and verify results before merging').",
        "purpose": "Captures specific manual actions required for workflow success.",
        "type": "string"
      },
      "maxItems": 5,
      "purpose": "Identifies human oversight points that ensure quality and compliance.",
      "type": "array"
    },
    "mission": {
      "authoring_guidance": "Target roughly 40 words -- enough to convey purpose without drifting into details best captured elsewhere.",
      "description_for_schema": "Write a concise mission statement describing the team's purpose and value.",
      "purpose": "Provides the north star that shapes every artifact, agent, and process defined later.",
      "type": "string"
    },
    "objectives": {
      "authoring_guidance": "Aim for 3\u20135 actionable objectives (maximum 6). Provide fewer when only a couple deliver real leverage.",
      "description_for_schema": "List the concrete objectives that support the goals.",
      "items": {
        "description_for_schema": "State one actionable objective in a single sentence.",
        "purpose": "Ensures downstream plans reference specific deliverables rather than vague aspirations.",
        "type": "string"
      },
      "maxItems": 6,
      "purpose": "Translates strategy into actionable commitments that can be tracked and validated.",
      "type": "array"
    },
    "system_boundary": {
      "description_for_schema": "Explicitly define the separation of concerns between the Pantheon framework and the human operator/external tools.",
      "properties": {
        "operator_responsibilities": {
          "description_for_schema": "List what the human operator is responsible for (e.g., 'Executing code', 'Running tests', 'Committing to Git').",
          "items": {
            "type": "string"
          },
          "purpose": "Identifies manual steps that remain under human control.",
          "type": "array"
        },
        "pantheon_responsibilities": {
          "description_for_schema": "List what the Pantheon process is responsible for (e.g., 'Generating specification artifacts').",
          "items": {
            "type": "string"
          },
          "purpose": "Defines what the framework will automate to set clear boundaries.",
          "type": "array"
        }
      },
      "required": [
        "pantheon_responsibilities",
        "operator_responsibilities"
      ],
      "purpose": "Clarifies automation boundaries to prevent scope creep and ensure realistic expectations.",
      "type": "object"
    },
    "target_team": {
      "description_for_schema": "Provide the exact name of the team this blueprint serves.",
      "authoring_guidance": "For non-technical teams, focus on what the user is creating or achieving, using a user friendly name targeting non-technical users that is easy to understand and obvious. For technical teams, technical terminology is appropriate.",
      "purpose": "Anchors the blueprint to a concrete team so every downstream artifact stays scoped correctly.",
      "type": "string"
    }
  },
  "required": [
    "target_team",
    "mission",
    "goals",
    "objectives",
    "system_boundary",
    "high_leverage_artifacts",
    "manual_checkpoints"
  ]
}