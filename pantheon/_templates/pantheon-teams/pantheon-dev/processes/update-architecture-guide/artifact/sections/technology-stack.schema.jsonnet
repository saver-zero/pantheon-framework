{
  "type": "object",
  "required": [
    "core_technologies",
    "framework_categories",
    "development_tools"
  ],
  "properties": {
    "core_technologies": {
      "description_for_schema": "List of core technologies",
      "items": {
        "description_for_schema": "A core technology with version and purpose",
        "properties": {
          "alternatives_considered": {
            "description_for_schema": "Technologies considered but not chosen (optional)",
            "purpose": "Other options that were evaluated",
            "type": "string"
          },
          "license": {
            "description_for_schema": "License under which this technology is used",
            "purpose": "License type",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the technology",
            "purpose": "Technology name",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "Brief explanation of what this technology provides",
            "purpose": "Why this technology is used",
            "type": "string"
          },
          "version": {
            "description_for_schema": "Version requirement (e.g., '3.9+', '~14.0')",
            "purpose": "Required version or range",
            "type": "string"
          }
        },
        "purpose": "A core technology definition",
        "required": [
          "name",
          "version",
          "purpose",
          "license"
        ],
        "type": "object"
      },
      "purpose": "Primary technologies that form the foundation of the system",
      "type": "array"
    },
    "development_tools": {
      "description_for_schema": "List of development tools",
      "items": {
        "description_for_schema": "A development tool specification",
        "properties": {
          "name": {
            "description_for_schema": "Name of the tool",
            "purpose": "Tool name",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "Brief description of the tool's purpose",
            "purpose": "What the tool is used for",
            "type": "string"
          },
          "required": {
            "description_for_schema": "Whether this tool is required (Yes/No/Optional)",
            "purpose": "Whether the tool is mandatory",
            "type": "string"
          }
        },
        "purpose": "A development tool",
        "required": [
          "name",
          "purpose",
          "required"
        ],
        "type": "object"
      },
      "purpose": "Tools used in the development process",
      "type": "array"
    },
    "framework_categories": {
      "description_for_schema": "Categorized list of frameworks and libraries",
      "items": {
        "description_for_schema": "A category with its libraries",
        "properties": {
          "category": {
            "description_for_schema": "Name of the category (e.g., 'Testing', 'Data Processing')",
            "purpose": "Category name",
            "type": "string"
          },
          "libraries": {
            "description_for_schema": "List of libraries in this category",
            "items": {
              "description_for_schema": "A library with version and purpose",
              "properties": {
                "name": {
                  "description_for_schema": "Name of the library",
                  "purpose": "Library name",
                  "type": "string"
                },
                "purpose": {
                  "description_for_schema": "Brief description of library's use",
                  "purpose": "What the library is used for",
                  "type": "string"
                },
                "version": {
                  "description_for_schema": "Version requirement",
                  "purpose": "Version requirement",
                  "type": "string"
                }
              },
              "purpose": "A library definition",
              "required": [
                "name",
                "version",
                "purpose"
              ],
              "type": "object"
            },
            "purpose": "Libraries in this category",
            "type": "array"
          }
        },
        "purpose": "A category of related libraries",
        "required": [
          "category",
          "libraries"
        ],
        "type": "object"
      },
      "purpose": "Organized categories of frameworks and libraries",
      "type": "array"
    }
  }
}