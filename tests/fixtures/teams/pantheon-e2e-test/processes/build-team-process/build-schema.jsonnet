{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pantheon Process Family Build Specification",
  "description": "A complete specification for scaffolding a new process family.",
  "type": "object",
  "required": [
    "target_team",
    "artifact",
    "artifact_sections",
    "initial_section",
    "section_template",
    "artifact_location"
  ],
  "properties": {
    "target_team": {
      "type": "string",
      "description": "The name of the team package where the generated process family will be installed. This ensures the new processes are placed in the correct, isolated team environment."
    },
    "artifact": {
      "type": "string",
      "description": "The core noun that this process family operates on (e.g., 'ticket', 'document'). This name is used to generate conventional process names like 'create-ticket'."
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
      "required": ["section", "template", "schema"],
      "properties": {
        "section": {
          "type": "string",
          "description": "The unique name for this section, which must match one of the names in the top-level 'artifact_sections' array."
        },
        "template": {
          "type": "string",
          "description": "A Jinja2 template for the section's content. This template should contain only the raw markdown content for the section, without any surrounding elements like section headers or footers (e.g., no '<!-- Section: ... -->'). It uses variables from this section's 'schema' to produce the final, human-readable output."
        },
        "schema": {
          "type": "object",
          "description": "The data contract for this section. It defines the structured data the agent must provide. This schema is used both to validate the agent's input and to provide variables to the 'template'.",
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
            }
          },
          "additionalProperties": false
        },
    "artifactLocation": {
      "type": "object",
      "required": ["directory", "filename_template"],
      "properties": {
        "directory": {"type": "string"},
        "filename_template": {"type": "string"}
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
