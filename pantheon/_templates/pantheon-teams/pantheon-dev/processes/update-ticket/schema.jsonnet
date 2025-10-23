local sections = {
  ticket_description: import "artifact/sections/ticket_description.schema.jsonnet",
  baseline_commit: import "artifact/sections/baseline_commit.schema.jsonnet",
  technical_plan: import "artifact/sections/technical_plan.schema.jsonnet",
  progress_log: import "artifact/sections/progress_log.schema.jsonnet",
  code_review: import "artifact/sections/code_review.schema.jsonnet",
  commit_message: import "artifact/sections/commit_message.schema.jsonnet"
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
      default: ["ticket_description", "technical_plan", "progress_log", "code_review", "commit_message"],
    },
  },
  required: ["section_updates"],
}