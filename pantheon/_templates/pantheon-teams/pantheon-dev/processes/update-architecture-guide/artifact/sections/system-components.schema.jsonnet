{
  "type": "object",
  "required": [
    "components"
  ],
  "properties": {
    "components": {
      "description_for_schema": "Array of all major system components",
      "items": {
        "description_for_schema": "A system component with its details",
        "properties": {
          "data_flows": {
            "description_for_schema": "List of data flows for this component",
            "items": {
              "description_for_schema": "A single data flow",
              "properties": {
                "description": {
                  "description_for_schema": "Description of what data flows and to/from where",
                  "purpose": "What data is flowing and where",
                  "type": "string"
                },
                "direction": {
                  "description_for_schema": "Direction of data flow (Input/Output/Bidirectional)",
                  "purpose": "Whether data flows in or out",
                  "type": "string"
                }
              },
              "purpose": "A data flow definition",
              "required": [
                "direction",
                "description"
              ],
              "type": "object"
            },
            "purpose": "How data moves in and out of this component",
            "type": "array"
          },
          "dependencies": {
            "description_for_schema": "List of component dependencies",
            "items": {
              "description_for_schema": "A dependency with its reason",
              "properties": {
                "component": {
                  "description_for_schema": "Name of the component this depends on",
                  "purpose": "Name of the depended-upon component",
                  "type": "string"
                },
                "reason": {
                  "description_for_schema": "Brief explanation of why this dependency is needed",
                  "purpose": "Why this dependency exists",
                  "type": "string"
                }
              },
              "purpose": "A dependency relationship",
              "required": [
                "component",
                "reason"
              ],
              "type": "object"
            },
            "purpose": "Other components this component depends on",
            "type": "array"
          },
          "name": {
            "description_for_schema": "Name of the component",
            "purpose": "The component's identifier",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "Brief statement of the component's purpose",
            "purpose": "High-level description of why this component exists",
            "type": "string"
          },
          "responsibilities": {
            "description_for_schema": "List of specific responsibilities",
            "items": {
              "description_for_schema": "One specific responsibility",
              "purpose": "A single responsibility",
              "type": "string"
            },
            "purpose": "Specific duties this component performs",
            "type": "array"
          }
        },
        "purpose": "Complete definition of a single system component",
        "required": [
          "name",
          "purpose",
          "responsibilities",
          "dependencies",
          "data_flows"
        ],
        "type": "object"
      },
      "purpose": "Comprehensive list of all system components with their relationships",
      "type": "array"
    }
  }
}