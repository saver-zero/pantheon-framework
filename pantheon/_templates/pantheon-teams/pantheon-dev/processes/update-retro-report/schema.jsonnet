local sections = {
  analysis_summary: import "artifact/sections/analysis_summary.schema.jsonnet",
  agent_improvements: import "artifact/sections/agent_improvements.schema.jsonnet",
  process_improvements: import "artifact/sections/process_improvements.schema.jsonnet",
  artifact_improvements: import "artifact/sections/artifact_improvements.schema.jsonnet",
  documentation_improvements: import "artifact/sections/documentation_improvements.schema.jsonnet"
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
      default: ["analysis_summary", "agent_improvements", "process_improvements", "artifact_improvements", "documentation_improvements"],
    },
  },
  required: ["section_updates"],
}