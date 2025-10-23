local sections = [
  {
    name: "analysis_summary",
    schema: import "process-schema://update-retro-report/sections/analysis_summary",
    enabled: true
  },
  {
    name: "agent_improvements",
    schema: import "process-schema://update-retro-report/sections/agent_improvements",
    enabled: false
  },
  {
    name: "process_improvements",
    schema: import "process-schema://update-retro-report/sections/process_improvements",
    enabled: true
  },
  {
    name: "artifact_improvements",
    schema: import "process-schema://update-retro-report/sections/artifact_improvements",
    enabled: true
  },
  {
    name: "documentation_improvements",
    schema: import "process-schema://update-retro-report/sections/documentation_improvements",
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
