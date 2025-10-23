local _enforce_tdd = std.extVar('enforce_tdd');
local _update_documentation = std.extVar('update_documentation');
local _update_diagram = std.extVar('update_diagram');

local _join_topics(topics) =
  if std.length(topics) == 1 then topics[0]
  else if std.length(topics) == 2 then topics[0] + " and " + topics[1]
  else std.join(", ", topics[0:std.length(topics) - 1]) + ", and " + topics[std.length(topics) - 1];

local _phases_topics_to_skip = std.filter(
  function(topic) topic != null,
  [
    if _enforce_tdd then "testing" else null,
    if _update_documentation then "documentation" else null,
    if _update_diagram then "diagram" else null,
  ],
);

local _phases_authoring_guidance =
  if std.length(_phases_topics_to_skip) > 0 then
    "Exclude phases focused on "
    + _join_topics(_phases_topics_to_skip)
    + " because dedicated sections in this template already cover that work."
  else null;

local _conditional_required = std.filter(
  function(field) field != null,
  [
    if _enforce_tdd then "testing_phase" else null,
    if _update_documentation then "documentation_phase" else null,
    if _update_diagram then "diagram_phase" else null,
  ],
);

local _phases_schema = {
  "description_for_schema": "List of implementation phases with detailed steps",
  "items": {
    "properties": {
      "description": {
        "description_for_schema": "Detailed description of what will be accomplished in this phase",
        "purpose": "Detailed explanation of phase objectives",
        "type": "string"
      },
      "name": {
        "description_for_schema": "Brief name describing what this phase accomplishes",
        "purpose": "Descriptive name for the phase",
        "type": "string"
      },
      "number": {
        "description_for_schema": "Phase number (1, 2, 3, etc.)",
        "purpose": "Sequential phase identifier",
        "type": "integer"
      },
      "steps": {
        "description_for_schema": "List of specific steps to complete the phase",
        "items": {
          "properties": {
            "action": {
              "description_for_schema": "The specific action to be performed",
              "purpose": "Clear, actionable task description",
              "type": "string"
            },
            "description": {
              "description_for_schema": "Optional detailed description of the action",
              "purpose": "Additional context for the action",
              "type": "string"
            },
            "methodology": {
              "description_for_schema": "The methodology or approach to follow",
              "purpose": "Specific approach or technique to use",
              "type": "string"
            },
            "requirements": {
              "description_for_schema": "List of requirements that must be met",
              "items": {
                "type": "string"
              },
              "purpose": "Prerequisites or conditions for this step",
              "type": "array"
            }
          },
          "required": ["action"],
          "type": "object"
        },
        "purpose": "Actionable tasks within the phase",
        "type": "array"
      }
    },
    "required": ["name", "number", "description", "steps"],
    "type": "object"
  },
  "purpose": "Breaks work into manageable, sequential phases",
  "type": "array"
}
+ (
  if _phases_authoring_guidance != null then {
    "authoring_guidance": _phases_authoring_guidance
  } else {}
);

local base_schema = {
  "type": "object",
  "required": ["high_level_approach", "phases", "technical_summary"],
  "properties": {
    "high_level_approach": {
      "authoring_guidance": "Provide 2-3 paragraphs explaining the overall technical strategy",
      "description_for_schema": "High-level description of the implementation approach",
      "purpose": "Overall strategy for implementing the solution",
      "type": "string"
    },
    "phases": _phases_schema,
    "technical_summary": {
      "description_for_schema": "Summary of technical analysis and proposed approach",
      "properties": {
        "key_modules_impacted": {
          "description_for_schema": "List of modules that will be modified or created",
          "items": {
            "properties": {
              "path": {
                "description_for_schema": "Module file path",
                "purpose": "Path to the module file",
                "type": "string"
              },
              "purpose": {
                "description_for_schema": "Description of changes to this module",
                "purpose": "Explains what changes will be made",
                "type": "string"
              }
            },
            "type": "object"
          },
          "purpose": "Identifies which parts of the codebase will change",
          "type": "array"
        },
        "proposed_libraries": {
          "description_for_schema": "List of libraries or frameworks to be used",
          "items": {
            "properties": {
              "name": {
                "description_for_schema": "Library or framework name",
                "purpose": "Name of the library or framework",
                "type": "string"
              },
              "rationale": {
                "description_for_schema": "Justification for using this library",
                "purpose": "Explains why this library is needed",
                "type": "string"
              }
            },
            "type": "object"
          },
          "purpose": "Documents new dependencies to be added",
          "type": "array"
        },
        "relevant_code_analyzed": {
          "description_for_schema": "List of existing code files analyzed",
          "items": {
            "properties": {
              "path": {
                "description_for_schema": "Path to the code file",
                "purpose": "File path of analyzed code",
                "type": "string"
              },
              "relevance": {
                "description_for_schema": "Explanation of the code's relevance to the ticket",
                "purpose": "Explains why this code is relevant",
                "type": "string"
              }
            },
            "type": "object"
          },
          "purpose": "Documents existing code that was reviewed",
          "type": "array"
        }
      },
      "purpose": "High-level overview of technical approach and components",
      "required": [],
      "type": "object"
    }
  }
};

local tdd_phase = if _enforce_tdd then {
  "testing_phase": {
    "description_for_schema": "A dedicated testing phase for test-driven development plan based on existing patterns, documentation, and focusing on core behaviors",
    "properties": {
      "testing_context_analysis": {
        "description_for_schema": "Comprehensive analysis of testing infrastructure, patterns, and documentation",
        "properties": {
          "test_files_reviewed": {
            "description_for_schema": "Existing test files examined for patterns",
            "items": {
              "properties": {
                "path": {
                  "description_for_schema": "Path to the test file",
                  "purpose": "File path of test file examined",
                  "type": "string"
                },
                "patterns_observed": {
                  "description_for_schema": "Testing patterns, conventions, and approaches found",
                  "purpose": "Documents established testing patterns",
                  "type": "string"
                }
              },
              "required": ["path", "patterns_observed"],
              "type": "object"
            },
            "purpose": "Forces examination of existing test code",
            "type": "array",
            "authoring_guidance": "Review at least 2-3 existing test files relevant to this feature area"
          },
          "testing_documentation_reviewed": {
            "description_for_schema": "Testing documentation and guidelines examined",
            "items": {
              "properties": {
                "document_path": {
                  "description_for_schema": "Path to documentation file or section",
                  "purpose": "Reference to documentation examined",
                  "type": "string"
                },
                "key_insights": {
                  "description_for_schema": "Important testing principles or requirements found",
                  "purpose": "Documents key testing guidelines discovered",
                  "type": "string"
                }
              },
              "required": ["document_path", "key_insights"],
              "type": "object"
            },
            "purpose": "Ensures adherence to documented testing standards",
            "type": "array",
            "authoring_guidance": "Review README files, testing guides, CONTRIBUTING docs, or architecture decision records about testing"
          },
          "fixture_and_mock_patterns": {
            "description_for_schema": "Established patterns for test data, fixtures, and mocks",
            "purpose": "Documents existing test infrastructure patterns",
            "type": "string",
            "authoring_guidance": "Include both code patterns and documented conventions"
          },
          "testing_framework_setup": {
            "description_for_schema": "Testing framework, plugins, and configuration",
            "purpose": "Documents current testing infrastructure",
            "type": "string",
            "authoring_guidance": "Note pytest/unittest setup, conftest patterns, test runners, CI configuration"
          }
        },
        "required": ["test_files_reviewed", "fixture_and_mock_patterns", "testing_framework_setup"],
        "purpose": "Forces discovery before design",
        "type": "object"
      },
      "core_behaviors": {
        "description_for_schema": "Essential behaviors to validate, aligned with existing patterns",
        "items": {
          "properties": {
            "behavior": {
              "description_for_schema": "The specific behavior or requirement being tested",
              "purpose": "Clear description of functionality to validate",
              "type": "string"
            },
            "validation_approach": {
              "description_for_schema": "How to validate using established patterns",
              "purpose": "Testing approach consistent with existing code",
              "type": "string"
            },
            "similar_existing_test": {
              "description_for_schema": "Reference to similar test pattern if applicable",
              "purpose": "Links to existing patterns for consistency",
              "type": "string"
            }
          },
          "required": ["behavior", "validation_approach"],
          "type": "object"
        },
        "purpose": "Focuses on meaningful behaviors over edge cases",
        "type": "array",
        "authoring_guidance": "List 3-5 behaviors that represent distinct functionality"
      },
      "test_implementation_plan": {
        "description_for_schema": "How to implement tests following discovered patterns",
        "properties": {
          "reusable_components": {
            "description_for_schema": "Existing fixtures, utilities, or helpers to reuse",
            "items": {
              "type": "string"
            },
            "purpose": "Promotes reuse of existing test infrastructure",
            "type": "array"
          },
          "new_components_needed": {
            "description_for_schema": "New test components required with justification",
            "items": {
              "properties": {
                "component": {
                  "description_for_schema": "Name or description of new component",
                  "purpose": "Identifies new test infrastructure needed",
                  "type": "string"
                },
                "justification": {
                  "description_for_schema": "Why existing components don't suffice",
                  "purpose": "Prevents unnecessary creation of new patterns",
                  "type": "string"
                }
              },
              "required": ["component", "justification"],
              "type": "object"
            },
            "purpose": "Justifies deviation from existing patterns",
            "type": "array"
          }
        },
        "required": ["reusable_components"],
        "purpose": "Balances reuse with necessity",
        "type": "object"
      },
      "implementation_constraints": {
        "description_for_schema": "Design decisions the tests will enforce",
        "purpose": "How TDD will drive implementation design",
        "type": "string",
        "authoring_guidance": "Describe interface boundaries and architectural constraints tests will validate"
      }
    },
    "required": ["testing_context_analysis", "core_behaviors", "test_implementation_plan", "implementation_constraints"],
    "purpose": "Comprehensive test-driven development planning",
    "type": "object",
    "authoring_guidance": "Create a thoughtful TDD plan based on thorough analysis of existing patterns"
  }
} else {};

local documentation_phase = if _update_documentation then {
  "documentation_phase": {
    "description_for_schema": "A dedicated documentation phase to update documentation",
    "properties": {
      "existing_docs_analyzed": {
        "description_for_schema": "Existing documentation files reviewed",
        "items": {
          "properties": {
            "file_path": {
              "description_for_schema": "Path to documentation file examined",
              "purpose": "File path of documentation reviewed",
              "type": "string"
            },
            "current_status": {
              "description_for_schema": "Current state and accuracy of this documentation",
              "purpose": "Assessment of existing documentation quality",
              "type": "string"
            }
          },
          "required": ["file_path", "current_status"],
          "type": "object"
        },
        "purpose": "Forces examination of existing documentation",
        "type": "array",
        "authoring_guidance": "Review relevant existing documentation files to understand current state"
      },
      "docs_needing_updates": {
        "description_for_schema": "Existing documentation that needs updates",
        "items": {
          "properties": {
            "file_path": {
              "description_for_schema": "Path to documentation file",
              "purpose": "File path of documentation to update",
              "type": "string"
            },
            "changes_needed": {
              "description_for_schema": "Specific changes required for this file",
              "purpose": "Details what documentation changes are needed",
              "type": "string"
            }
          },
          "required": ["file_path", "changes_needed"],
          "type": "object"
        },
        "purpose": "Identifies existing docs requiring updates",
        "type": "array"
      },
      "new_docs_needed": {
        "description_for_schema": "New documentation that needs to be created",
        "items": {
          "properties": {
            "file_path": {
              "description_for_schema": "Path where new documentation should be created",
              "purpose": "Target location for new documentation",
              "type": "string"
            },
            "purpose": {
              "description_for_schema": "Why this new documentation is needed",
              "purpose": "Justifies the need for new documentation",
              "type": "string"
            },
            "content_outline": {
              "description_for_schema": "Brief outline of what this documentation should cover",
              "purpose": "Guides creation of new documentation",
              "type": "string"
            }
          },
          "required": ["file_path", "purpose", "content_outline"],
          "type": "object"
        },
        "purpose": "Identifies new documentation to create",
        "type": "array"
      },
      "update_summary": {
        "description_for_schema": "Overall summary and rationale for documentation changes",
        "purpose": "Explains the comprehensive documentation strategy",
        "type": "string",
        "authoring_guidance": "Provide high-level rationale for all documentation changes and additions"
      }
    },
    "purpose": "Comprehensive documentation update planning",
    "required": ["existing_docs_analyzed", "update_summary"],
    "type": "object",
    "authoring_guidance": "Identify all documentation that needs updating to remain current with implementation changes"
  }
} else {};

local diagram_updates = if _update_diagram then {
  "diagram_phase": {
    "description_for_schema": "A dedicated diagramming phase to update diagrams",
    "properties": {
      "existing_diagrams_analyzed": {
        "description_for_schema": "Existing diagrams reviewed for relevance",
        "items": {
          "properties": {
            "diagram_path": {
              "description_for_schema": "Path to diagram file examined",
              "purpose": "File path of diagram reviewed",
              "type": "string"
            },
            "current_accuracy": {
              "description_for_schema": "Current accuracy and relevance of this diagram",
              "purpose": "Assessment of existing diagram quality",
              "type": "string"
            }
          },
          "required": ["diagram_path", "current_accuracy"],
          "type": "object"
        },
        "purpose": "Forces examination of existing diagrams",
        "type": "array",
        "authoring_guidance": "Review relevant existing diagrams to understand current state"
      },
      "diagrams_needing_updates": {
        "description_for_schema": "Existing diagrams that need updates",
        "items": {
          "properties": {
            "diagram_path": {
              "description_for_schema": "Path to diagram file",
              "purpose": "File path of diagram to update",
              "type": "string"
            },
            "diagram_type": {
              "description_for_schema": "Type of PlantUML diagram",
              "purpose": "Specifies the diagram format for updates",
              "type": "string",
              "enum": ["sequence", "component", "activity", "deployment", "class", "use_case"]
            },
            "changes_needed": {
              "description_for_schema": "Specific changes required for this diagram",
              "purpose": "Details what diagram changes are needed",
              "type": "string"
            }
          },
          "required": ["diagram_path", "diagram_type", "changes_needed"],
          "type": "object"
        },
        "purpose": "Identifies existing diagrams requiring updates",
        "type": "array"
      },
      "new_diagrams_needed": {
        "description_for_schema": "New diagrams that need to be created",
        "items": {
          "properties": {
            "diagram_path": {
              "description_for_schema": "Path where new diagram should be created",
              "purpose": "Target location for new diagram",
              "type": "string"
            },
            "diagram_type": {
              "description_for_schema": "Type of PlantUML diagram to create",
              "purpose": "Specifies the diagram format",
              "type": "string",
              "enum": ["sequence", "component", "activity", "deployment", "class", "use_case"]
            },
            "purpose": {
              "description_for_schema": "Why this new diagram is needed",
              "purpose": "Justifies the need for new diagram",
              "type": "string"
            },
            "content_outline": {
              "description_for_schema": "Brief outline of what this diagram should show",
              "purpose": "Guides creation of new diagram",
              "type": "string"
            }
          },
          "required": ["diagram_path", "diagram_type", "purpose", "content_outline"],
          "type": "object"
        },
        "purpose": "Identifies new diagrams to create",
        "type": "array"
      },
      "update_summary": {
        "description_for_schema": "Overall summary and rationale for diagram changes",
        "purpose": "Explains the comprehensive diagram update strategy",
        "type": "string",
        "authoring_guidance": "Provide high-level rationale for all diagram changes and additions"
      }
    },
    "purpose": "Comprehensive diagram update planning",
    "required": ["existing_diagrams_analyzed", "update_summary"],
    "type": "object",
    "authoring_guidance": "Identify all architectural diagrams that need updating to remain current with implementation changes"
  }
} else {};

base_schema + {
  "properties": base_schema.properties + tdd_phase + documentation_phase + diagram_updates,
  "required": base_schema.required + _conditional_required,
}
