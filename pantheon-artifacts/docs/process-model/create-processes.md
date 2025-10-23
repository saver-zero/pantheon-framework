---
doc_id: process-model-create
title: "CREATE Processes"
description: "CREATE process behavior, file requirements, and workflow for generating new artifacts"
keywords: [create, process-model, artifact-generation, content-template, placement, naming]
relevance: "Use this document to understand CREATE process structure and how new artifacts are generated from templates"
---

# CREATE Processes

CREATE processes generate and save new formatted artifacts to disk.

## File Requirements

### Required Files
- **`artifact/content.md`** - Jinja2 template for artifact content
- **`artifact/placement.jinja`** - Directory template for artifact placement
- **`artifact/naming.jinja`** - Filename template for artifact naming
- **`schema.jsonnet`** - Data contract defining input parameters
- **`routine.md`** - Step-by-step instructions for agents
- **`permissions.jsonnet`** - Access control rules

### Optional Files
- **`artifact/jsonl_placement.jinja`** - Directory for JSONL logging
- **`artifact/jsonl_naming.jinja`** - Filename for JSONL logging

## Process Structure Example

```bash
processes/create-ticket/
├── routine.md
├── permissions.jsonnet
├── schema.jsonnet
└── artifact/
    ├── content.md
    ├── placement.jinja
    └── naming.jinja
```

## Workflow

1. Agent retrieves schema: `pantheon get schema create-ticket --actor engineer`
2. Agent creates JSON input file with required data
3. Agent executes: `pantheon execute create-ticket --from-file ticket.json --actor engineer`
4. Framework renders `content.md` template with input data
5. Framework renders `placement.jinja` and `naming.jinja` to determine output path
6. Framework saves new artifact to `pantheon-artifacts/<placement>/<naming>`

## Built-in Template Variables

All CREATE templates have access to:
- `{{ pantheon_actor }}` - The agent executing the process
- `{{ pantheon_timestamp }}` - Current timestamp
- `{{ pantheon_datestamp }}` - Current date
- `{{ pantheon_artifact_id }}` - Auto-incrementing or CLI-provided ID
- `{{ pantheon_profile }}` - Active team profile configuration
- `{{ pantheon_project_root }}` - Absolute path to project root
- `{{ pantheon_artifacts_root }}` - Absolute path to artifacts directory

## JSONL Logging Support

CREATE processes can optionally log structured data alongside artifacts:
- Define `jsonl_placement.jinja` and `jsonl_naming.jinja`
- Framework automatically appends JSON line containing input data
- Enables analytics workflows with preserved structured data

---

**Related:** [Process Model Overview](overview.md) | [UPDATE Processes](update-processes.md) | [GET Processes](get-processes.md)
