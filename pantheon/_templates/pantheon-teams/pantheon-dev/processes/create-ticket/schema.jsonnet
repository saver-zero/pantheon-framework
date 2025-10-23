local sections = [
  {
    name: "ticket_description",
    schema: import "process-schema://update-ticket/sections/ticket_description",
    enabled: true
  },
  {
    name: "baseline_commit",
    schema: import "process-schema://update-ticket/sections/baseline_commit",
    enabled: false
  },
  {
    name: "technical_plan",
    schema: import "process-schema://update-ticket/sections/technical_plan",
    enabled: false
  },
  {
    name: "progress_log",
    schema: import "process-schema://update-ticket/sections/progress_log",
    enabled: false
  },
  {
    name: "commit_message",
    schema: import "process-schema://update-ticket/sections/commit_message",
    enabled: false
  },
  {
    name: "code_review",
    schema: import "process-schema://update-ticket/sections/code_review",
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