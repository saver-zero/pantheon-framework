local sections = {
  overview: import "artifact/sections/overview.schema.jsonnet",
  working_with_agents: import "artifact/sections/working_with_agents.schema.jsonnet",
  agents: import "artifact/sections/agents.schema.jsonnet",
  workflow_examples: import "artifact/sections/workflow_examples.schema.jsonnet",
  getting_started: import "artifact/sections/getting_started.schema.jsonnet",
  artifacts: import "artifact/sections/artifacts.schema.jsonnet"
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
      default: ["overview", "working_with_agents", "agents", "workflow_examples", "getting_started", "artifacts"],
    },
  },
  required: ["section_updates"],
}