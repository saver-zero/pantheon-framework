{
  "type": "object",
  "required": [
    "services"
  ],
  "properties": {
    "services": {
      "description_for_schema": "List of shared services",
      "items": {
        "description_for_schema": "A shared service with usage details",
        "properties": {
          "best_practices": {
            "description_for_schema": "List of best practices when using this service",
            "items": {
              "description_for_schema": "One best practice recommendation",
              "purpose": "A single best practice",
              "type": "string"
            },
            "purpose": "Recommended usage patterns",
            "type": "array"
          },
          "configuration": {
            "description_for_schema": "List of configuration options",
            "items": {
              "description_for_schema": "A single configuration option",
              "properties": {
                "default": {
                  "description_for_schema": "Default value for this configuration",
                  "purpose": "Default value if not specified",
                  "type": "string"
                },
                "description": {
                  "description_for_schema": "Description of what this configuration does",
                  "purpose": "What the configuration controls",
                  "type": "string"
                },
                "key": {
                  "description_for_schema": "Name of the configuration key",
                  "purpose": "Configuration parameter name",
                  "type": "string"
                }
              },
              "purpose": "A configuration option",
              "required": [
                "key",
                "description",
                "default"
              ],
              "type": "object"
            },
            "purpose": "Available configuration options",
            "type": "array"
          },
          "language": {
            "description_for_schema": "Programming language for the usage example (e.g., python, javascript)",
            "purpose": "Programming language for examples",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the shared service",
            "purpose": "The service's identifier",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "Brief description of what this service does",
            "purpose": "What the service provides",
            "type": "string"
          },
          "usage_example": {
            "description_for_schema": "Code example demonstrating service usage",
            "purpose": "Code showing how to use the service",
            "type": "string"
          }
        },
        "purpose": "A single shared service definition",
        "required": [
          "name",
          "purpose",
          "language",
          "usage_example",
          "configuration",
          "best_practices"
        ],
        "type": "object"
      },
      "purpose": "Definition of all shared services available system-wide",
      "type": "array"
    }
  }
}