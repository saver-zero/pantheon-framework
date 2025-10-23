{
  "type": "object",
  "properties": {
    "architecture_overview": {
      "authoring_guidance": "Target roughly 120 words and focus on how the processes reinforce each other.",
      "description_for_schema": "Summarize how the team's Pantheon processes interlock.",
      "purpose": "Explains why these processes belong together so downstream designers preserve the intended workflow rationale.",
      "type": "string"
    },
    "artifacts": {
      "authoring_guidance": "Aim for 1\u20132 artifacts (maximum 4). Only include artifacts that the source workflow explicitly names or clearly implies.",
      "description_for_schema": "Enumerate the artifact types that provide the greatest leverage for this team.",
      "items": {
        "description_for_schema": "Describe one artifact that genuinely reduces ambiguity for operators.",
        "properties": {
          "build_mode": {
            "description_for_schema": "Determines the artifact's build strategy. Choose 'complete' for simple, self-contained documents created all at once (e.g., an agent prompt). Choose 'modular' for complex documents built collaboratively over time (e.g., a team blueprint).",
            "purpose": "Guides implementation approach for the artifact.",
            "type": "string"
          },
          "external_inputs": {
            "authoring_guidance": "Include only the external inputs that truly matter (maximum 4) and explain their ingestion clearly.",
            "description_for_schema": "List the external inputs and how each is canonicalized inside Pantheon before use.",
            "items": {
              "properties": {
                "input": {
                  "description_for_schema": "A single, concise description of an external input and its canonicalization process.",
                  "purpose": "Documents how external data enters the controlled Pantheon workflow.",
                  "type": "string"
                }
              },
              "type": "object"
            },
            "maxItems": 4,
            "purpose": "Forces explicit ingestion planning so no step depends on uncontrolled context.",
            "type": "array"
          },
          "manual_actions_required": {
            "authoring_guidance": "Capture only the unavoidable manual follow-ups (maximum 6) and keep each concise.",
            "description_for_schema": "List the manual follow-up steps the human operator must perform.",
            "items": {
              "properties": {
                "action": {
                  "description_for_schema": "A single, concise manual action required by the operator.",
                  "purpose": "Documents essential human steps that remain outside automation.",
                  "type": "string"
                }
              },
              "type": "object"
            },
            "maxItems": 6,
            "purpose": "Keeps expectations realistic by separating guidance from automation.",
            "type": "array"
          },
          "name": {
            "description_for_schema": "Artifact name (singular, lowercase).",
            "authoring_guidance": "For non-technical teams, focus on what the user is creating or achieving, use outcome-oriented language that is user friendly. For technical teams, technical terminology is appropriate.",
            "purpose": "Provides a stable label so CREATE/GET/UPDATE processes can reference the artifact unambiguously.",
            "type": "string"
          },
          "operations": {
            "authoring_guidance": "Include only the operations that materially support operators (maximum 3).",
            "description_for_schema": "Specify the Pantheon operations (CREATE/GET/UPDATE) that exist for this artifact.",
            "items": {
              "description_for_schema": "Describe one operation and the operator benefit it delivers.",
              "properties": {
                "description": {
                  "description_for_schema": "Summarize what the operation returns to the operator in one sentence.",
                  "purpose": "Keeps focus on the outcome so unnecessary processes are not introduced.",
                  "type": "string"
                },
                "type": {
                  "description_for_schema": "Operation verb (CREATE, GET, UPDATE).",
                  "purpose": "Signals which Pantheon capability enforces the contract for this artifact.",
                  "enum": ["CREATE", "GET", "UPDATE"],
                  "type": "string"
                }
              },
              "required": [
                "type",
                "description"
              ],
              "purpose": "Ensures each operation exists to deliver clear value, not just to mirror external workflows.",
              "type": "object"
            },
            "maxItems": 3,
            "purpose": "Prevents process sprawl by documenting only the verbs that materially support operators.",
            "type": "array"
          },
          "purpose": {
            "description_for_schema": "Explain in one or two sentences why this artifact exists.",
            "purpose": "Keeps the blueprint minimal by justifying the artifact's value to the workflow.",
            "type": "string"
          },
          "section_sequence": {
            "authoring_guidance": "List the steps in execution order. Reference a section name, specify the action (e.g., create, review, update), and explain why that step happens before the next.",
            "description_for_schema": "Describe the order in which sections should be created, reviewed, or updated.",
            "items": {
              "description_for_schema": "Define one step in the section workflow.",
              "properties": {
                "action": {
                  "description_for_schema": "Short verb describing the step (e.g., create, review, update).",
                  "purpose": "Clarifies what the operator or primary LLM should do at this point in the workflow.",
                  "type": "string"
                },
                "description": {
                  "description_for_schema": "Explain why this step happens now and what outcome it produces.",
                  "purpose": "Gives operators and downstream agents the reasoning behind the sequence.",
                  "type": "string"
                },
                "section": {
                  "description_for_schema": "Name of the section this step references (must match a section defined below).",
                  "purpose": "Ensures every step maps to a concrete section of the artifact.",
                  "type": "string"
                }
              },
              "purpose": "Provides an actionable workflow sequence instead of abstract lifecycle labels.",
              "type": "object"
            },
            "maxItems": 8,
            "purpose": "Forces the designer to articulate the practical order in which sections are populated and reviewed.",
            "type": "array"
          },
          "sections": {
            "authoring_guidance": "Aim for 2\u20134 sections (maximum 6). Each section must capture information that can be populated manually--avoid live metrics or real-time monitoring data.",
            "description_for_schema": "List the sections that make this artifact actionable.",
            "items": {
              "description_for_schema": "Describe why this section is captured and the insight it provides.",
              "properties": {
                "name": {
                  "description_for_schema": "Section name.",
                  "purpose": "Allows downstream agents to target this slice of data precisely.",
                  "type": "string"
                },
                "purpose": {
                  "description_for_schema": "Explain the value of this section in one sentence.",
                  "purpose": "Ensures every section earns its place by reducing ambiguity or rework.",
                  "type": "string"
                },
                "update_behavior": {
                  "description_for_schema": "Whether updating this section should replace, prepend, or append existing content.",
                  "authoring guidance": "Most of the time, content should be replaced upon updating. But there cases like progress logs or on-going notes that may be better to prepend the content with latest content first. Appending might be better when chronological order is more important than the most recent updates.",
                  "purpose": "Sets the correct command to use for updating the section",
                  "type": "string",
                  "enum": ["REPLACE", "PREPEND", "APPEND"]
                }
              },
              "required": [
                "name",
                "purpose",
                "update_behavior"
              ],
              "purpose": "Prevents bloated artifacts by requiring an explicit reason for each section.",
              "type": "object"
            },
            "maxItems": 6,
            "purpose": "Encourages surgical artifacts that contain only the data operators truly need.",
            "type": "array"
          },
          "source_reference": {
            "authoring_guidance": "If you cannot cite the workflow, remove or demote the artifact to operator guidance instead of keeping it here.",
            "description_for_schema": "Cite the portion of the reference workflow that justifies this artifact (quote or summarize the exact section).",
            "purpose": "Links every artifact to an explicit source so speculative additions are avoided.",
            "type": "string"
          }
        },
        "required": [
          "name",
          "purpose",
          "build_mode",
          "source_reference",
          "sections",
          "operations"
        ],
        "purpose": "Each entry keeps the focus on artifacts that deliver measurable leverage to the team.",
        "type": "object"
      },
      "maxItems": 6,
      "purpose": "Curates the artifact set so the blueprint remains executable and high impact.",
      "type": "array"
    },
    "operator_notes": {
      "authoring_guidance": "Keep this around 120 words and focus on why the manual guidance matters.",
      "description_for_schema": "Provide concise guidance for manual follow-up that lies outside Pantheon's automation surface area.",
      "purpose": "Explains why the manual guidance matters so operators understand the risk they are mitigating.",
      "type": "string"
    },
    "process_interactions": {
      "authoring_guidance": "Keep this under 150 words and emphasize how each hand-off protects the closed loop.",
      "description_for_schema": "Describe the Pantheon-only data flow between CREATE/GET/UPDATE processes.",
      "purpose": "Reinforces the closed loop by clarifying why each hand-off exists and how it protects the workflow.",
      "type": "string"
    }
  },
  "required": [
    "architecture_overview",
    "artifacts",
    "process_interactions",
    "operator_notes"
  ]
}