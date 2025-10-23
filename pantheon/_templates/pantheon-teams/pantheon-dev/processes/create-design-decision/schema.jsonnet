local sections = [
  {
    name: "decision_context",
    schema: import "process-schema://update-design-decision/sections/decision_context",
    enabled: true
  },
  {
    name: "alternatives_considered",
    schema: import "process-schema://update-design-decision/sections/alternatives_considered",
    enabled: true
  },
  {
    name: "decision_details",
    schema: import "process-schema://update-design-decision/sections/decision_details",
    enabled: true
  },
  {
    name: "consequences_and_rationale",
    schema: import "process-schema://update-design-decision/sections/consequences_and_rationale",
    enabled: true
  }
];

local properties = std.foldl(
  function(acc, sec)
    if sec.enabled then acc + sec.schema.properties else acc,
  sections,
  {}
);

local required = std.foldl(
  function(acc, sec)
    if sec.enabled && std.objectHas(sec.schema, 'required')
    then acc + sec.schema.required
    else acc,
  sections,
  []
);

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": properties,
  "required": required
}
