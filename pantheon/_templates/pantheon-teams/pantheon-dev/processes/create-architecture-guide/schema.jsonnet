local sections = [
  {
    name: "project-context",
    schema: import "process-schema://update-architecture-guide/sections/project-context",
    enabled: true
  },
  {
    name: "high-level-overview",
    schema: import "process-schema://update-architecture-guide/sections/high-level-overview",
    enabled: true
  },
  {
    name: "core-principles",
    schema: import "process-schema://update-architecture-guide/sections/core-principles",
    enabled: true
  },
  {
    name: "technology-stack",
    schema: import "process-schema://update-architecture-guide/sections/technology-stack",
    enabled: true
  },
  {
    name: "system-components",
    schema: import "process-schema://update-architecture-guide/sections/system-components",
    enabled: false
  },
  {
    name: "shared-services",
    schema: import "process-schema://update-architecture-guide/sections/shared-services",
    enabled: false
  },
  {
    name: "implementation-patterns",
    schema: import "process-schema://update-architecture-guide/sections/implementation-patterns",
    enabled: false
  },
  {
    name: "testing-strategy",
    schema: import "process-schema://update-architecture-guide/sections/testing-strategy",
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