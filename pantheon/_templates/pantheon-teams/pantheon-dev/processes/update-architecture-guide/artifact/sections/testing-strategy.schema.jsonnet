{
  "type": "object",
  "required": [
    "testing_philosophy",
    "test_types",
    "best_practices"
  ],
  "properties": {
    "best_practices": {
      "description_for_schema": "List of testing best practices",
      "items": {
        "description_for_schema": "A best practice with example",
        "properties": {
          "description": {
            "description_for_schema": "Description of the best practice",
            "purpose": "Explanation of the practice",
            "type": "string"
          },
          "example_code": {
            "description_for_schema": "Example code showing the practice",
            "purpose": "Code demonstrating the practice",
            "type": "string"
          },
          "example_language": {
            "description_for_schema": "Programming language for the example",
            "purpose": "Language for the example",
            "type": "string"
          },
          "name": {
            "description_for_schema": "Name of the best practice",
            "purpose": "Practice name",
            "type": "string"
          }
        },
        "purpose": "A testing best practice",
        "required": [
          "name",
          "description",
          "example_language",
          "example_code"
        ],
        "type": "object"
      },
      "purpose": "Recommended practices for writing tests",
      "type": "array"
    },
    "test_types": {
      "description_for_schema": "List of test types with their purposes and patterns",
      "items": {
        "description_for_schema": "A test type definition",
        "properties": {
          "coverage_target": {
            "description_for_schema": "Target coverage percentage as a number",
            "purpose": "Target code coverage percentage",
            "type": "string"
          },
          "example_code": {
            "description_for_schema": "Example test code",
            "purpose": "Code showing test structure",
            "type": "string"
          },
          "example_language": {
            "description_for_schema": "Programming language for the example",
            "purpose": "Language for the example",
            "type": "string"
          },
          "key_patterns": {
            "description_for_schema": "List of key patterns to follow",
            "items": {
              "description_for_schema": "One key pattern for this test type",
              "purpose": "A testing pattern",
              "type": "string"
            },
            "purpose": "Important patterns for this test type",
            "type": "array"
          },
          "name": {
            "description_for_schema": "Name of the test type (e.g., 'Unit Tests', 'Integration Tests')",
            "purpose": "Test type name",
            "type": "string"
          },
          "purpose": {
            "description_for_schema": "Description of what this test type is for",
            "purpose": "What this test type validates",
            "type": "string"
          }
        },
        "purpose": "A type of test",
        "required": [
          "name",
          "purpose",
          "coverage_target",
          "key_patterns",
          "example_language",
          "example_code"
        ],
        "type": "object"
      },
      "purpose": "Different categories of tests used in the project",
      "type": "array"
    },
    "testing_philosophy": {
      "authoring_guidance": "Write 2-3 sentences about the overall testing approach",
      "description_for_schema": "Statement of the testing philosophy and goals",
      "purpose": "Overall approach to testing in the project",
      "type": "string"
    }
  }
}