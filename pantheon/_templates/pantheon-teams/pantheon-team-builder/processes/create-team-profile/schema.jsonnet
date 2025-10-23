// Team Configuration Schema for create-team-profile process
// This schema defines a structure for designing a team's profile configuration,
// including definitions for custom properties.

local profile = std.extVar('profile');

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Team Profile Design Schema",
  "description": "Schema for designing a team profile configuration. It allows for defining profile properties and then instantiating them in different profiles. The profile-related fields are optional.",
  "type": "object",
  "required": ["team_name", "team_description"],

  "properties": {
    "team_name": {
      "type": "string",
      "description": "Official name of the team being created.",
      "authoring_guidance": "Do NOT add the suffix 'team' in the team name, as this will result in duplicate 'team team'.",
      "pattern": "^[A-Za-z0-9\\s\\-_]+$"
    },

    "team_description": {
      "type": "string",
      "description": "A clear description of the new team's purpose, scope, and responsibilities.",
      "authoring_guidance": "Aim for 2-3 succinct sentences (roughly 100-150 words) that communicate mission, scope, and core responsibilities."
    },

    "property_definitions": {
      "type": "object",
      "description": "Definitions for all custom properties that will be used in the profiles. Each key is a property name.",
      "additionalProperties": { "$ref": "#/$defs/propertyDef" }
    },

    "active_profile": {
      "type": "string",
      "minLength": 1,
      "description": "Name of the default active profile for the new team. This must match one of the keys in the 'profiles' object."
    },

    "profiles": {
      "type": "object",
      "minProperties": 1,
      "description": "A collection of profile configurations. Each key is a custom profile name (e.g., 'development', 'production'), and the value is an object containing the settings for that profile.",
      "additionalProperties": { "$ref": "#/$defs/profileInstance" }
    }
  },

  "$defs": {
    "propertyDef": {
      "type": "object",
      "description": "The definition of a single profile property.",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["string", "boolean", "number", "array"],
          "description": "The data type of the property."
        },
        "description": {
          "type": "string",
          "description": "A description of what this property controls."
        },
        "enum": {
          "type": "array",
          "items": { "type": "string" },
          "description": "A list of allowed values (required for string type)."
        }
      },
      "required": ["type", "description"],
      "if": {
        "properties": { "type": { "const": "string" } }
      },
      "then": {
        "required": ["enum"]
      }
    },
    "profileInstance": {
      "type": "object",
      "description": "An instance of a profile. The keys should be property names defined in 'property_definitions', and the values should match the defined type.",
      "additionalProperties": {
        "anyOf": [
          { "type": "string" },
          { "type": "boolean" },
          { "type": "number" },
          { "type": "array", "items": { "type": "string" } }
        ]
      }
    }
  },

  "additionalProperties": false,

  // If profile configuration is provided, all related fields are required.
  "dependentRequired": {
    "property_definitions": ["profiles", "active_profile"],
    "profiles": ["property_definitions", "active_profile"],
    "active_profile": ["property_definitions", "profiles"]
  }
}
