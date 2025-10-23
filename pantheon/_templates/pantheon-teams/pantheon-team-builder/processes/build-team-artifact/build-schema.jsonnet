{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pantheon Process Family Build Specification",
  "description": "A complete specification for scaffolding a new process family.",
  // NOTE: build_mode controls toggle defaults, not rendering logic.
  // The build_mode parameter sets the initial state of section toggles in generated schemas
  // (enabled flags) and templates (_include_* variables). After generation, these toggle
  // values can be modified directly in the artifacts for runtime control without regenerating
  // the entire process family. This separates user intent (build_mode parameter) from
  // implementation mechanism (toggle pattern).
  "type": "object",
  "required": [
    "target_team",
    "artifact",
    "build_mode",
    "include_context",
    "artifact_sections",
    "initial_section",
    "section_template",
    "artifact_location"
  ],
  "properties": {
    "target_team": {
      "type": "string",
      "description": "The name of the team package where the generated process family will be installed. This ensures the new processes are placed in the correct, isolated team environment. Do NOT add the suffix 'team' in the team name, as this will result in duplicate 'team team'. "
    },
    "artifact": {
      "type": "string",
      "description": "The core noun that this process family operates on (e.g., 'ticket', 'document'). This name is used to generate conventional process names like 'create-ticket'."
    },
    "build_mode": {
      "type": "string",
      "description": "Controls the default toggle state for section inclusion in generated processes. Choose 'complete' to set all section enabled flags to true by default (all sections initially visible). Choose 'modular' to set only the initial section enabled flag to true by default (other sections initially hidden). These toggle defaults can be modified post-generation for runtime control without regenerating the process family.",
      "enum": ["complete", "modular"]
    },
    "include_context": {
      "type": "boolean",
      "description": "Determines if the artifact is a 'Process Artifact' (a plan/design for a task) or a 'Terminal Artifact' (the final output).",
      "authoring_guidance": "For Process Artifacts like design documents, project plans, or complex tickets that require additional background business and problem context, only set to true if other context fields don't already exist. Set to false for Terminal Artifacts like agent prompts, code files, or generated reports. When in doubt, default to false."
    },
    "artifact_sections": {
      "type": "array",
      "description": "Defines the logical, addressable parts of the artifact. Each section can be updated independently, enabling complex, multi-step workflows (e.g., a 'plan' section updated after a 'description' section is created).",
      "items": {"type": "string"}
    },
    "initial_section": {
      "type": "string",
      "description": "Specifies which section from the 'artifact_sections' list will be used to generate the initial 'create-<artifact>' process. This defines the entry point for the artifact's lifecycle."
    },
    "section_template": {
      "type": "array",
      "description": "An array that provides the complete blueprint for each section, bundling its data contract ('schema') with its presentation layer ('template').",
      "items": {"$ref": "#/$defs/sectionDefinition"}
    },
    "artifact_location": {
      "$ref": "#/$defs/artifactLocation",
      "description": "Defines the file system location and naming convention for generated artifacts, ensuring they are stored in a predictable and organized manner."
    },
    "permissions": {
      "$ref": "#/$defs/permissionsDefinition",
      "description": "Controls which agents can execute the generated processes. This provides a security layer, ensuring that only authorized agents can perform create, get, or update operations."
    }
  },
  "$defs": {
    "sectionDefinition": {
      "type": "object",
      "required": ["section", "section_description", "update_behavior", "template", "schema"],
      "properties": {
        "section": {
          "type": "string",
          "description": "The unique name for this section, which must match one of the names in the top-level 'artifact_sections' array."
        },
        "section_description": {
          "type": "string",
          "description": "A concise, user-friendly explanation of the section's purpose that will guide agents when selecting which portions of the artifact to work on."
        },
        "update_behavior": {
          "type": "string",
          "purpose": "Determines the correct update command to use for this section, ensuring content is modified in the appropriate way (replace, prepend, or append).",
          "description_for_schema": "Specifies how updates to this section should be applied (REPLACE, PREPEND, or APPEND).",
          "authoring_guidance": "Choose REPLACE for sections where entire content should be replaced each time (default behavior). Choose PREPEND for sections where latest updates should appear first (e.g., progress logs, activity feeds). Choose APPEND for sections where chronological order matters (e.g., historical records, sequential notes). When in doubt, use REPLACE.",
          "enum": ["REPLACE", "PREPEND", "APPEND"]
        },
        "template": {
          "type": "string",
          "description": "A Jinja2 template for the section's content. This template should contain only the raw markdown content for the section, without any surrounding elements like section headers or footers (e.g., no '<!-- Section: ... -->'). It uses variables from this section's 'schema' to produce the final, human-readable output."
        },
        "schema": {
          "type": "object",
          "description": "The data contract for this section. It defines the structured data the agent must provide. This schema is used both to validate the agent's input and to provide variables to the 'template'.",
          "properties": {
            "required": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Array of field names that are required for this section."
            }
          },
          "additionalProperties": {"$ref": "#/$defs/fieldDefinition"}
        }
      }
    },
    "fieldDefinition": {
          "type": "object",
          "description": "The rich definition for a single field within a section's schema.",
          "required": ["type", "purpose", "description_for_schema"],
          "properties": {
            "type": {
              "type": "string",
              "description": "The JSON schema type for this field (e.g., 'string', 'array', 'object')."
            },
            "purpose": {
              "type": "string",
              "description": "A detailed explanation of the architectural purpose of this field. Why does it exist and how does it fit into the overall data model?"
            },
            "description_for_schema": {
              "type": "string",
              "description": "A concise, agent-facing description that will be placed in the final generated JSON schema for the new process. This should guide the agent using that process."
            },
            "authoring_guidance": {
              "type": "string",
              "description": "Provide explicit writing constraints the agent must follow when filling this field. Use it when the field benefits from a target length, uniqueness rule, or quality bar (e.g., 'Aim for 3–5 items, ok to provide fewer, never exceed 6', or 'Target ~200 words, skip trivia'). Skip only if no extra guidance is needed beyond the schema type and description."
            },
            "items": {
              "type": "object",
              "description": "If the type is 'array', this object defines the schema of the items in the array, following this same rich structure."
            },
            "properties": {
              "type": "object",
              "description": "If the type is 'object', this defines the nested properties, where each property follows this same rich structure."
            },
            "maxLength": {
              "type": "integer",
              "description": "Optional: If the type is 'string', this specifies the maximum length of the string."
            },
            "maxItems": {
              "type": "integer",
              "description": "Optional: If the type is 'array', this specifies the maximum number of items in the array."
            },
            "required": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Optional: When the field being defined has type 'object', this array specifies which of the nested properties (defined in the 'properties' field) are required."
            }
          },
          "additionalProperties": false
        },
    "artifactLocation": {
      "type": "object",
      "required": ["filename_template"],
      "properties": {
        "filename_template": {
          "type": "string",
          "description_for_schema": "Jinja2 template for the generated artifact's filename. The framework automatically prepends a structured ID prefix like '[ACRONYM{{ pantheon_artifact_id }}]_' to this template.",
          "authoring_guidance": "DO NOT include artifact IDs or ID placeholders in this template - the framework automatically inserts them. Use only short descriptive variables from your schema. Good examples: '{{ project_name }}_project_doc.md' or '{{ title }}_ticket.md'. Bad example: '[AB{{ id_number }}]_{{ project_name }}_channel-project_doc.md' (the ID prefix will be duplicated)."
        }
      }
    },
    "permissionsDefinition": {
      "type": "object",
      "properties": {
        "create": {"$ref": "#/$defs/singlePermission"},
        "get": {"$ref": "#/$defs/singlePermission"},
        "update": {"$ref": "#/$defs/singlePermission"}
      }
    },
    "singlePermission": {
      "type": "object",
      "required": ["allow", "deny"],
      "properties": {
        "allow": {"type": "array", "items": {"type": "string"}},
        "deny": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
