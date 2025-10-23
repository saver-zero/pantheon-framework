---
doc_id: process-model-get
title: "GET Processes"
description: "GET process behavior, artifact location, and section extraction workflows"
keywords: [get, process-model, artifact-retrieval, locator, parser, sections]
relevance: "Use this document to understand GET process structure and how existing artifacts are located and parsed"
---

# GET Processes

GET processes find and parse existing artifacts, returning structured JSON data.

## File Requirements

### Required Files
- **`artifact/locator.jsonnet`** - Configuration for finding artifacts
- **`routine.md`** - Step-by-step instructions
- **`permissions.jsonnet`** - Access control rules

### Optional Files
- **`artifact/parser.jsonnet`** - ID normalization (presence determines multi-artifact mode)
- **`artifact/sections.jsonnet`** - Section markers (presence enables section extraction)
- **`schema.jsonnet`** - Only needed for custom parameters beyond `--id` and `--sections`

## Multi-Artifact vs Singleton

### Multi-Artifact (Has `parser.jsonnet`)
- **Requires** `--id` flag to identify specific artifact
- Uses `parser.jsonnet` to normalize fuzzy IDs
- `locator.jsonnet` uses `std.extVar("pantheon_artifact_id")`
- Example: `pantheon execute get-ticket --id T001 --sections plan --actor engineer`

### Singleton (No `parser.jsonnet`)
- **Does not require** `--id` flag (ignored if provided)
- Expects exactly **one** artifact matching pattern
- `locator.jsonnet` uses fixed pattern
- Example: `pantheon execute get-architecture-guide --sections overview --actor tech-lead`

## Single-Section vs Multi-Section

### Single-Section (No `sections.jsonnet`)
- Returns entire document content
- `--sections` flag not applicable
- Simpler structure for simple artifacts

### Multi-Section (Has `sections.jsonnet`)
- Can extract specific sections using `--sections` flag
- Supports section-aware parsing
- Filters placeholder sections automatically

## Workflow

1. Agent executes: `pantheon execute get-ticket --id T001 --sections plan,status --actor engineer`
2. Framework normalizes ID using `parser.jsonnet` (if present)
3. Framework locates artifact using `locator.jsonnet` pattern
4. Framework parses sections using `sections.jsonnet` markers (if present)
5. Framework filters placeholder sections
6. Framework outputs JSON to stdout

## Built-in CLI Support

GET processes can use built-in flags without requiring `schema.jsonnet`:
- `--id <value>` - Artifact identifier (for multi-artifact processes)
- `--sections <comma-separated>` - Section names to extract (for multi-section processes)

---

**Related:** [Process Model Overview](overview.md) | [UPDATE Processes](update-processes.md) | [Single-Section Simplification](single-section-simplification.md)
