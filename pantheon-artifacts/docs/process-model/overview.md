---
doc_id: process-model-overview
title: "Process Model Overview"
description: "Overview of Pantheon's Unified Execute Model and how process types are determined by file combinations"
keywords: [process-model, unified-execute, create, update, get, build, operation-detection]
relevance: "Use this document to understand how Pantheon determines process types (CREATE, UPDATE, GET, BUILD) through convention-based file combinations"
---

# Process Model Overview

The Pantheon Framework uses a single, unified `execute` command for all processes. The behavior of a process—whether it creates new artifacts, gets existing ones, or updates specific sections—is determined by the operation-specific file combinations within its artifact directory.

## Process Behavior by File Convention

The **combination of files in the `artifact/` directory** determines the operation type. This self-documenting approach makes process intent transparent through file organization alone.

The framework detects process types in the following precedence order:
1. **BUILD**: Presence of `build-schema.jsonnet` at process root
2. **CREATE**: `content.md` + `placement.jinja` + `naming.jinja`
3. **UPDATE**: `patch.md` + GET files (with optional `target.jsonnet`)
4. **GET**: `locator.jsonnet` + `parser.jsonnet` (default)

## Process Type Characteristics

### BUILD Processes
- **Examples:** `build-team-process`, `scaffold-process-family`
- **Behavior:** Generates complete process families (CREATE, GET, UPDATE) from declarative specifications
- **Output:** Bundle of process directories staged in `pantheon-artifacts/` for review
- **Files Required:** `build-schema.jsonnet`, `routine.md`, `permissions.jsonnet`
- **Files Optional:** `directory.jinja` for bundle output location

### CREATE Processes
- **Examples:** `create-ticket`, `create-document`
- **Behavior:** Generates and saves new formatted artifacts to disk
- **Output:** New file written to the configured output directory
- **Files Required:** `content.md`, `placement.jinja`, `naming.jinja`

### GET Processes
- **Examples:** `get-ticket` (multi-artifact), `get-architecture-guide` (singleton)
- **Behavior:** Finds and parses existing artifacts, returns structured JSON data
- **Output:** JSON printed to stdout
- **Built-in CLI Support:** Can use `--id` and `--sections` flags without requiring `schema.jsonnet`
- **Files Required:** `locator.jsonnet`
- **Files Optional:** `parser.jsonnet`, `sections.jsonnet`, `schema.jsonnet`

### UPDATE Processes
- **Examples:** `update-plan`, `update-ticket-status`
- **Behavior:** Locates existing artifacts and modifies specific sections
- **Output:** Modified file written to the same location
- **Files Required:** `locator.jsonnet`, `parser.jsonnet`, `patch.md`
- **Files Optional:** `target.jsonnet`, `sections/<section>.md`

## Multi-Artifact vs Singleton Behavior

The presence of `parser.jsonnet` determines whether a process expects multiple artifacts or a single artifact:

### Multi-Artifact Mode (with `parser.jsonnet`)
- Requires `--id` flag to identify specific artifact
- Uses `parser.jsonnet` to normalize fuzzy IDs (e.g., "  T001.md  " → "T001")
- `locator.jsonnet` uses `std.extVar("pantheon_artifact_id")` for ID injection
- Example: `pantheon execute get-ticket --id T001 --sections plan --actor engineer`

### Singleton Mode (no `parser.jsonnet`)
- Does **not** require `--id` flag (ignored if provided)
- Expects exactly **one** artifact matching the pattern
- `locator.jsonnet` uses fixed pattern without ID placeholder
- Returns error if 0 or multiple artifacts found
- Example: `pantheon execute get-architecture-guide --sections overview --actor tech-lead`

## Single-Section vs Multi-Section Behavior

The presence of section-related files determines document complexity:

### Single-Section Processes
- **GET:** No `sections.jsonnet` → returns entire content
- **UPDATE:** No `target.jsonnet` → performs whole document replacement
- **CREATE:** No section markers in `content.md` → simple template
- Simpler schemas, cleaner artifacts, less boilerplate

### Multi-Section Processes
- **GET:** Has `sections.jsonnet` → can extract specific sections
- **UPDATE:** Has `target.jsonnet` → performs targeted section updates
- **CREATE:** Section markers in `content.md` → structured template
- Nested schemas, section-aware workflows, granular updates

## Benefits of the Unified Model

### Glass Box Transparency
- Single command pattern: `execute <process-name>`
- Operation intent is self-evident from artifact file combinations
- File names self-document their purpose
- Built-in flags simplify common operations (`--id`, `--sections`)

### Architectural Clarity
- Each operation has distinct, non-overlapping file combinations
- Convention-based dispatch with clear branching logic
- Consistent error handling across all operation types

### Developer Experience
- Self-documenting processes
- Autocomplete-friendly enum-based constants
- Predictable behavior from file organization

### Extensibility
- New processes automatically work with existing infrastructure
- Process type can be changed by modifying the file combination
- Shared components between UPDATE and GET operations
- No central registry or configuration updates needed

---

**Related:** [CREATE Processes](create-processes.md) | [UPDATE Processes](update-processes.md) | [GET Processes](get-processes.md) | [BUILD Processes](build-processes.md) | [Single-Section Simplification](single-section-simplification.md)
