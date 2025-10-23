local sections = {
  foundation: import "artifact/sections/foundation.schema.jsonnet",
  context: import "artifact/sections/context.schema.jsonnet",
  artifacts: import "artifact/sections/artifacts.schema.jsonnet",
  agents: import "artifact/sections/agents.schema.jsonnet",
  profile: import "artifact/sections/profile.schema.jsonnet"
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
      default: ["foundation", "context", "artifacts", "agents", "profile"],
    },
  },
  required: ["section_updates"],
}