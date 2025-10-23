{
  "type": "object",
  "properties": {
    "default_profile": {
      "authoring_guidance": "Provide this only when profiles are defined. Use the exact descriptive profile name operators should select by default.",
      "description_for_schema": "The name of the profile that should be activated by default when multiple profiles are available.",
      "purpose": "Specifies the recommended starting configuration for new team deployments.",
      "type": "string"
    },
    "profile_overview": {
      "authoring_guidance": "Keep it concise (~75 words). State whether configuration is needed; if not, explain why. When profiles exist, articulate the operating modes that justify them.",
      "description_for_schema": "High-level description of the team's configuration strategy, including the purpose of the different profiles.",
      "purpose": "Explains the team's configuration approach and when different operational modes are needed.",
      "type": "string"
    },
    "profiles": {
      "authoring_guidance": "Define profiles only when properties are present. Provide a minimal set of descriptively named profiles that reflect distinct operating modes. If no properties are defined, provide an empty object.",
      "description_for_schema": "Profiles that bundle concrete values for the properties defined above. Only required when at least one property exists.",
      "purpose": "Provides pre-configured operational modes that bundle property values for common use cases.",
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "profile_description": {
            "type": "string",
            "description": "Description of this profile's purpose and when to use it"
          }
        },
        "additionalProperties": true
      }
    },
    "property_definitions": {
      "authoring_guidance": "Most teams should leave this empty or define a single property. Every additional property adds schema branches, template conditions, operator choices, and testing paths-only add one when the payoff clearly outweighs that cost.",
      "description_for_schema": "Definitions for a small, justified set of concrete, enforceable properties. Each property must have a clear and direct effect on the schema of a specific process within this team.",
      "purpose": "Defines configurable properties that adapt team behavior for different operational contexts.",
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "property_type": {
            "type": "string",
            "enum": ["string", "boolean", "number"],
            "description": "The data type of this property"
          },
          "property_description": {
            "type": "string",
            "description": "Human-readable description of what this property controls"
          },
          "options": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "value": {
                  "type": "string",
                  "description": "The option value"
                },
                "description": {
                  "type": "string",
                  "description": "Description of what this option does"
                }
              },
              "required": ["value", "description"],
              "additionalProperties": false
            },
            "description": "Available options for the property with explicit value and description structure"
          }
        },
        "required": ["property_type", "property_description", "options"],
        "additionalProperties": false
      }
    }
  },
  "required": [
    "profile_overview"
  ]
}