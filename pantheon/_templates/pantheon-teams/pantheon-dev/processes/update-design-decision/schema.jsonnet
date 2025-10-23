local sections = {
  decision_context: import "artifact/sections/decision_context.schema.jsonnet",
  alternatives_considered: import "artifact/sections/alternatives_considered.schema.jsonnet",
  decision_details: import "artifact/sections/decision_details.schema.jsonnet",
  consequences_and_rationale: import "artifact/sections/consequences_and_rationale.schema.jsonnet"
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
      default: ["decision_context", "alternatives_considered", "decision_details", "consequences_and_rationale"],
    },
  },
  required: ["section_updates"],
}