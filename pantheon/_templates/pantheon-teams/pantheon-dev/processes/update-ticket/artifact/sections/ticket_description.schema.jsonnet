{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "title",
    "acceptance_criteria",
    "assignee",
    "context",
    "objective",
    "priority"
  ],
  "properties": {
    "title": {
      "description_for_schema": "Brief, descriptive title of the ticket",
      "purpose": "Concise summary of what needs to be accomplished",
      "type": "string"
    },
    "acceptance_criteria": {
      "description_for_schema": "List of acceptance criteria in user story format",
      "items": {
        "properties": {
          "persona": {
            "description_for_schema": "The persona or user type (e.g., developer, user, admin)",
            "purpose": "Identifies who benefits from this criterion, , fitting into the following template: 'As a <persona>,'",
            "type": "string"
          },
          "action": {
            "description_for_schema": "The action the persona wants to perform",
            "purpose": "Specifies what the persona wants to do, fitting into the following template: 'I want to <action>,'",
            "type": "string"
          },
          "benefit": {
            "description_for_schema": "The benefit or outcome achieved",
            "purpose": "Explains the value delivered, fitting into the following template: 'so that <benefit>.'",
            "type": "string"
          }
        },
        "type": "object",
        "required": [
          "persona",
          "action",
          "benefit"
        ]
      },
      "purpose": "Defines measurable completion criteria",
      "type": "array"
    },
    "assignee": {
      "description_for_schema": "Name or handle of the person/agent assigned to this ticket",
      "purpose": "Identifies who is responsible for completing this work",
      "type": "string"
    },
    "constraints_and_anti_patterns": {
      "description_for_schema": "List of constraints and anti-patterns to avoid",
      "items": {
        "type": "string"
      },
      "purpose": "Prevents common mistakes and maintains quality",
      "type": "array"
    },
    "context": {
      "description_for_schema": "Additional context and background information",
      "purpose": "Provides background needed to understand the work",
      "type": "string"
    },
    "dependencies": {
      "description_for_schema": "Optional list of dependencies that must be completed first",
      "purpose": "Documents blocking relationships that affect scheduling",
      "type": "string"
    },
    "design_patterns": {
      "description_for_schema": "Key design patterns and principles to follow",
      "items": {
        "properties": {
          "pattern": {
            "description_for_schema": "Name of the design pattern",
            "purpose": "Name of the design pattern to follow",
            "type": "string"
          },
          "rationale": {
            "description_for_schema": "Explanation of why this pattern should be used",
            "purpose": "Explains why this pattern is important here",
            "type": "string"
          }
        },
        "type": "object",
        "required": [
          "pattern",
          "rationale"
        ]

      },
      "purpose": "Ensures consistency with architectural standards",
      "type": "array"
    },
    "objective": {
      "authoring_guidance": "Write 2-3 sentences clearly stating what should be accomplished",
      "description_for_schema": "Primary objective or goal of this ticket",
      "purpose": "Clear statement of the goal to prevent scope creep",
      "type": "string"
    },
    "priority": {
      "type": "integer",
      "description_for_schema": "Priority level. 0 = critical, 1 = high, 2 = medium, 3 = low.",
      "purpose": "Indicates urgency and importance for scheduling purposes",
      "enum": [0, 1, 2, 3]
    },
    "relevant_documentation": {
      "description_for_schema": "List of relevant documentation and diagrams",
      "items": {
        "properties": {
          "path": {
            "description_for_schema": "File path or Pantheon command to retrieve the documentation",
            "purpose": "Reference to the documentation - can be a file path, URL, or Pantheon retrieval command",
            "authoring_guidance": "Use one of these formats: (1) File path: 'docs/architecture.md', (2) Pantheon command: 'pantheon execute get-architecture-guide --sections high-level-overview --actor <your_agent_name>' (DO NOT invent fake file paths for Pantheon-managed content). Do not use online resources.",
            "type": "string"
          },
          "relevance": {
            "description_for_schema": "Brief explanation of how this doc relates to the ticket",
            "purpose": "Explains why this documentation is important",
            "type": "string"
          },
          "documentation_type": {
            "description_for_schema": "Wehther this documentation path is a file path or a pantheon command to run",
            "purpose": "The type determines how the path will be rendered correctly in the template",
            "type": "string",
            "enum": ["PATH", "COMMAND"]
          }
        },
        "type": "object",
        "required": [
          "path",
          "relevance",
          "documentation_type"
        ]
      },
      "purpose": "Links ticket work to existing knowledge base",
      "type": "array"
    },
    "senior_assignment_rationale": {
      "description_for_schema": "Optional explanation of why senior assignment is needed",
      "purpose": "Explains why this ticket requires senior-level expertise",
      "type": "string"
    },
    "sequence_number": {
      "description_for_schema": "Optional sequence number for grouping related tickets",
      "purpose": "Organizes tickets into logical sequence groups for large backlogs (4+ tickets)",
      "authoring_guidance": "Use when creating 4+ tickets, coordinating across agents, or when there are clear logical phases. Must be provided with sequence_description.",
      "type": "integer",
      "minimum": 1
    },
    "sequence_description": {
      "description_for_schema": "Optional sequence description (lowercase, single word, max 11 chars)",
      "purpose": "Provides meaningful name for sequence group directory (e.g., 'foundation', 'core', 'polish')",
      "authoring_guidance": "Use lowercase single words like 'foundation', 'core', 'polish'. Must be provided with sequence_number.",
      "type": "string",
      "maxLength": 11,
      "pattern": "^[a-z]+$"
    }
  },
  "dependentRequired": {
    "sequence_number": ["sequence_description"],
    "sequence_description": ["sequence_number"]
  }
}