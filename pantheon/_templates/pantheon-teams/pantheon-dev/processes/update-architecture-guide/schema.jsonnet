local sections = {
  "project-context": import "artifact/sections/project-context.schema.jsonnet",
  "high-level-overview": import "artifact/sections/high-level-overview.schema.jsonnet",
  "core-principles": import "artifact/sections/core-principles.schema.jsonnet",
  "technology-stack": import "artifact/sections/technology-stack.schema.jsonnet",
  "system-components": import "artifact/sections/system-components.schema.jsonnet",
  "shared-services": import "artifact/sections/shared-services.schema.jsonnet",
  "implementation-patterns": import "artifact/sections/implementation-patterns.schema.jsonnet",
  "testing-strategy": import "artifact/sections/testing-strategy.schema.jsonnet"
};

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  type: "object",
  properties: {
    section_updates: {
      type: "object",
      additionalProperties: false,
      properties: sections,
    },
    section_order: {
      type: "array",
      description: "Canonical ordering of sections for default workflows.",
      items: { type: "string" },
      default: ["project-context", "high-level-overview", "core-principles", "technology-stack", "system-components", "shared-services", "implementation-patterns", "testing-strategy", "documentation-standards", "diagramming-standards"],
    },
  },
  required: ["section_updates"],
}