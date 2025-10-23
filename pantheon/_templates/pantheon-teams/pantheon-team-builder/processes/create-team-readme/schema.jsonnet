local sections = [
  {
    name: "overview",
    schema: import "process-schema://update-team-readme/sections/overview",
    enabled: true
  },
  {
    name: "working_with_agents",
    schema: import "process-schema://update-team-readme/sections/working_with_agents",
    enabled: true
  },
  {
    name: "agents",
    schema: import "process-schema://update-team-readme/sections/agents",
    enabled: true
  },
  {
    name: "artifacts",
    schema: import "process-schema://update-team-readme/sections/artifacts",
    enabled: true
  },
  {
    name: "getting_started",
    schema: import "process-schema://update-team-readme/sections/getting_started",
    enabled: true
  },
  {
    name: "workflow_examples",
    schema: import "process-schema://update-team-readme/sections/workflow_examples",
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
