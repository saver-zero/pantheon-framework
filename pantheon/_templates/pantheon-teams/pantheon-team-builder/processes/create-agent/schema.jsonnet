{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "target_team": {
      "type": "string",
      "description": "The name of the team the agent belongs to. This ensures the new agent definition is placed in the correct directory.",
      "authoring_guidance": "Do NOT add the suffix 'team' in the team name, as this will result in duplicate 'team team'."
    },
    "agent_name": {
      "description_for_schema": "The agent's name as it will appear in the system (e.g., 'artifact-designer', 'profile-designer')",
      "authoring_guidance": "For non-technical agents serving domain users, use friendly names that reflect what help or support the user needs, not system architecture. For technical agents (software engineering roles), role-based names are appropriate.",
      "purpose": "To provide a machine-readable identifier for the agent. This name is used in the `--actor` flag for CLI commands and is critical for the framework's permission and validation systems.",
      "type": "string"
    },
    "agent_description": {
      "description_for_schema": "A brief explanation of the agent's primary purpose and when it should be used. To encourage more proactive agent use, include phrases like 'use PROACTIVELY' or 'MUST BE USED'",
      "purpose": "To enable effective agent discovery. This description is used by humans and other agents (like a `tech-lead`) to understand which agent is the correct specialist for a given task.",
      "authoring_guidance": "Do not include descriptions that state this is a Pantheon specialist agent, as that will be automatically included by the template.",
      "type": "string"
    },
    "competencies": {
      "description_for_schema": "An array of competency objects defining the agent's areas of expertise",
      "items": {
        "properties": {
          "area": {
            "description_for_schema": "A concise label for this area of expertise",
            "purpose": "To provide a clear, semantic label for a specific skill, making the agent's list of competencies easy to scan and understand.",
            "type": "string"
          },
          "description": {
            "description_for_schema": "A comprehensive description of what the agent can do in this competency area",
            "purpose": "To provide a concrete explanation of what the agent can do within a skill area. This detail is crucial for clarifying the agent's abilities and limitations.",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "To explicitly define the agent's skills and knowledge boundaries. This structured list makes the agent's capabilities transparent and predictable, helping to ensure it is assigned appropriate tasks.",
      "type": "array"
    },
    "philosophy_principles": {
      "description_for_schema": "An array of principles that define the agent's approach to problem-solving and decision-making",
      "items": {
        "properties": {
          "description": {
            "description_for_schema": "A comprehensive description of how this principle manifests in the agent's work",
            "purpose": "To explain how an abstract principle translates into concrete actions and behaviors. This is vital for ensuring the agent's philosophy has a practical impact on its work.",
            "type": "string"
          },
          "name": {
            "description_for_schema": "A concise label for this guiding principle",
            "purpose": "To give a memorable name to a core principle, making the agent's philosophy easier to reference and understand.",
            "type": "string"
          }
        },
        "type": "object"
      },
      "purpose": "To shape the agent's 'way of thinking.' These principles guide the agent's decision-making and reasoning process, ensuring its behavior is aligned with the team's desired approach and values.",
      "type": "array"
    },
    "role_statement": {
      "description_for_schema": "A clear, concise statement that captures the essence of what this agent is and does",
      "purpose": "To establish the agent's core identity and persona. This single sentence is the most critical part of the prompt, as it sets the agent's high-level goal and frames all subsequent instructions.",
      "type": "string"
    },
    "technical_understanding": {
      "description_for_schema": "An object that outlines the agent's technical knowledge, broken down into topics. This is critical for grounding the agent in its operational context.",
      "properties": {
        "introduction": {
          "description_for_schema": "A high-level summary of the agent's technical world and its core function within it.",
          "purpose": "To provide a high-level summary of the agent's technical world. This initial context-setting is critical for priming the agent on its core function and the environment it lives in before diving into specific topics.",
          "type": "string"
        },
        "topics": {
          "description_for_schema": "A list of specific technical topics, each with a title, description, and a list of key points.",
          "items": {
            "properties": {
              "description": {
                "description_for_schema": "A narrative explanation of the topic's core lesson and why it is important.",
                "purpose": "To explain the core lesson of the topic. This narrative context is vital for the agent to understand not just the 'what' but the 'why' behind each technical point, leading to better decision-making.",
                "type": "string"
              },
              "points": {
                "description_for_schema": "A list of concrete, explicit details or rules for this topic.",
                "items": {
                  "type": "string"
                },
                "purpose": "To provide concrete, explicit details for a topic. These bullet points serve as the agent's 'rules' or 'facts' about the system, minimizing ambiguity and reducing the chance of hallucination.",
                "type": "array"
              },
              "title": {
                "description_for_schema": "The title of the technical topic (e.g., 'How Profiles Actually Work').",
                "purpose": "To give each technical concept a clear, semantic handle. This allows the agent to categorize and recall specific pieces of its technical understanding.",
                "type": "string"
              }
            },
            "type": "object"
          },
          "maxItems": 5,
          "purpose": "To break down the agent's complex technical context into discrete, digestible concepts. This structured approach prevents cognitive overload and allows the agent to reference specific aspects of its 'knowledge base' when performing tasks.",
          "type": "array"
        }
      },
      "purpose": "To ground the agent in its specific operational context. This section acts as the agent's 'mental model' of the system, ensuring it understands the architectural constraints and principles it must operate within, leading to more reliable and correct behavior.",
      "type": "object"
    },
    "create_workflows": {
      "description_for_schema": "Array of workflow objects for CREATE operations. Each workflow follows a two-step pattern: get instructions, then follow them.",
      "purpose": "Defines the agent's CREATE workflows using the RAE pattern, ensuring predictable execution flow for creating new artifacts.",
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "when_to_use", "get_instructions_description", "get_instructions_process"],
        "properties": {
          "name": {
            "type": "string",
            "description_for_schema": "A clear, concise name that identifies this workflow (e.g., 'Creating a new ticket').",
            "purpose": "To give a clear, human-readable name to a specific workflow or 'recipe' that the agent can follow."
          },
          "when_to_use": {
            "type": "string",
            "description_for_schema": "Clear guidance on when this workflow is appropriate to use.",
            "purpose": "To provide explicit criteria that help the agent decide which workflow is appropriate for a given request."
          },
          "get_instructions_description": {
            "type": "string",
            "description_for_schema": "A short phrase describing the task, e.g., 'creating a team config'.",
            "purpose": "To describe the specific artifact or task for which instructions are being retrieved."
          },
          "get_instructions_process": {
            "type": "string",
            "description_for_schema": "The name of the process to call in the `pantheon get process` command.",
            "purpose": "To specify the exact `pantheon` process to call to retrieve the instructions."
          }
        }
      }
    },
    "update_workflows": {
      "description_for_schema": "Array of workflow objects for UPDATE operations. Each workflow targets a specific section with defined update behavior.",
      "purpose": "Defines the agent's UPDATE workflows with explicit section targeting, ensuring efficient execution without unnecessary section discovery steps.",
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "when_to_use", "get_instructions_description", "get_instructions_process", "section", "insert_mode"],
        "properties": {
          "name": {
            "type": "string",
            "description_for_schema": "A clear, concise name that identifies this workflow (e.g., 'Updating progress log').",
            "purpose": "To give a clear, human-readable name to a specific workflow or 'recipe' that the agent can follow."
          },
          "when_to_use": {
            "type": "string",
            "description_for_schema": "Clear guidance on when this workflow is appropriate to use.",
            "purpose": "To provide explicit criteria that help the agent decide which workflow is appropriate for a given request."
          },
          "get_instructions_description": {
            "type": "string",
            "description_for_schema": "A short phrase describing the task, e.g., 'updating the progress log'.",
            "purpose": "To describe the specific artifact section for which instructions are being retrieved."
          },
          "get_instructions_process": {
            "type": "string",
            "description_for_schema": "The name of the process to call in the `pantheon get process` command.",
            "purpose": "To specify the exact `pantheon` process to call to retrieve the instructions."
          },
          "section": {
            "type": "string",
            "description_for_schema": "The specific section to update (e.g., 'progress_log', 'technical_plan').",
            "purpose": "Specifies which section of the artifact this workflow updates, eliminating the need for section discovery."
          },
          "insert_mode": {
            "type": "string",
            "description_for_schema": "How to insert content when updating this section.",
            "purpose": "Determines the correct update command behavior, matching the artifact section's update_behavior setting.",
            "authoring_guidance": "Use REPLACE for sections where content should be completely replaced. Use PREPEND for sections where latest updates appear first (e.g., progress logs). Use APPEND for chronological order (e.g., historical records).",
            "enum": ["REPLACE", "PREPEND", "APPEND"]
          }
        }
      }
    }
  }
}