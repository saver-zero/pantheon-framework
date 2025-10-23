local sections = [
  {
    name: "foundation",
    schema: import "process-schema://update-team-blueprint/sections/foundation",
    enabled: true
  },
  {
    name: "context",
    schema: import "process-schema://update-team-blueprint/sections/context",
    enabled: true
  },
  {
    name: "artifacts",
    schema: import "process-schema://update-team-blueprint/sections/artifacts",
    enabled: false
  },
  {
    name: "agents",
    schema: import "process-schema://update-team-blueprint/sections/agents",
    enabled: false
  },
  {
    name: "profile",
    schema: import "process-schema://update-team-blueprint/sections/profile",
    enabled: false
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
